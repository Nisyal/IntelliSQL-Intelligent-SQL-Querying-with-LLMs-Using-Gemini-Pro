"""
Confidence scoring service — evaluates the quality of generated SQL.

Scoring breakdown (100 points total):
  - Syntactic validity:  40 points — is the SQL parseable?
  - Schema accuracy:     40 points — do all tables/columns exist in the DB?
  - Intent match:        20 points — does the query type match the question?
"""

import re
import sqlparse
from services.schema_service import get_all_columns


# ── Intent keywords mapped to expected SQL clauses ────────────

INTENT_PATTERNS = {
    "count": {"keywords": ["how many", "count", "total number", "number of"], "clause": "COUNT"},
    "average": {"keywords": ["average", "avg", "mean"], "clause": "AVG"},
    "maximum": {"keywords": ["maximum", "max", "highest", "most", "top", "best"], "clause": "MAX"},
    "minimum": {"keywords": ["minimum", "min", "lowest", "least", "worst"], "clause": "MIN"},
    "sum": {"keywords": ["sum", "total", "add up"], "clause": "SUM"},
    "list": {"keywords": ["list", "show", "display", "get", "tell", "find", "all"], "clause": "SELECT"},
    "sort": {"keywords": ["sort", "order", "rank", "arrange"], "clause": "ORDER BY"},
    "group": {"keywords": ["group", "per", "each", "by category", "breakdown"], "clause": "GROUP BY"},
}


def calculate_confidence(sql: str, question: str) -> dict:
    """
    Score generated SQL on three dimensions and return a detailed result.

    Args:
        sql: The generated SQL query string.
        question: The original natural language question.

    Returns:
        dict with keys:
            score (int 0-100),
            explanation (str),
            breakdown: { syntax, schema, intent }
    """
    syntax_score, syntax_note = _check_syntax(sql)
    schema_score, schema_note = _check_schema(sql)
    intent_score, intent_note = _check_intent(sql, question)

    total = syntax_score + schema_score + intent_score

    explanation_parts = []
    if syntax_note:
        explanation_parts.append(syntax_note)
    if schema_note:
        explanation_parts.append(schema_note)
    if intent_note:
        explanation_parts.append(intent_note)

    return {
        "score": total,
        "explanation": " | ".join(explanation_parts) if explanation_parts else "All checks passed.",
        "breakdown": {
            "syntax": {"score": syntax_score, "max": 40, "note": syntax_note},
            "schema": {"score": schema_score, "max": 40, "note": schema_note},
            "intent": {"score": intent_score, "max": 20, "note": intent_note},
        },
    }


# ── Dimension 1: Syntactic Validity (40 pts) ─────────────────

def _check_syntax(sql: str) -> tuple[int, str]:
    """
    Parse the SQL string and verify it's syntactically reasonable.
    Uses sqlparse for tokenization and basic validation.
    """
    if not sql or not sql.strip():
        return 0, "Empty SQL query."

    try:
        parsed = sqlparse.parse(sql)
        if not parsed:
            return 0, "SQL could not be parsed."

        stmt = parsed[0]
        tokens = [t for t in stmt.tokens if not t.is_whitespace]

        if not tokens:
            return 0, "No meaningful SQL tokens found."

        # Check it starts with SELECT (we only allow reads)
        first_keyword = tokens[0].ttype
        first_value = tokens[0].value.upper()

        if first_value not in ("SELECT", "WITH"):
            return 10, f"Query starts with '{first_value}' instead of SELECT."

        # Check for balanced parentheses
        open_parens = sql.count("(")
        close_parens = sql.count(")")
        if open_parens != close_parens:
            return 20, "Unbalanced parentheses detected."

        # Check for basic clause structure
        sql_upper = sql.upper()
        has_from = "FROM" in sql_upper
        if not has_from and "SELECT" in sql_upper:
            # Could be a simple SELECT 1 or SELECT expression
            return 30, "Query has no FROM clause (may be intentional)."

        return 40, "SQL syntax is valid."

    except Exception as e:
        return 10, f"Syntax check error: {str(e)}"


# ── Dimension 2: Schema Accuracy (40 pts) ────────────────────

def _check_schema(sql: str) -> tuple[int, str]:
    """
    Verify that table and column names referenced in the SQL
    actually exist in the database schema.
    """
    try:
        schema = get_all_columns()  # {"students": ["name", "class", ...], ...}

        if not schema:
            return 20, "Could not read database schema for validation."

        all_tables = {t.lower() for t in schema.keys()}
        all_columns = set()
        for cols in schema.values():
            for c in cols:
                all_columns.add(c.lower())

        sql_upper = sql.upper()
        sql_lower = sql.lower()

        # Extract table references after FROM and JOIN
        table_pattern = r'(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        referenced_tables = re.findall(table_pattern, sql, re.IGNORECASE)

        # Extract column-like identifiers (simplified)
        # Look for identifiers in SELECT, WHERE, ORDER BY, GROUP BY
        ident_pattern = r'(?:SELECT|WHERE|ON|BY|SET|AND|OR|,)\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?)'
        raw_idents = re.findall(ident_pattern, sql, re.IGNORECASE)

        # Separate table.column references
        referenced_columns = []
        for ident in raw_idents:
            if "." in ident:
                parts = ident.split(".")
                referenced_columns.append(parts[1].lower())
            else:
                col = ident.lower()
                # Skip SQL keywords
                sql_keywords = {
                    "select", "from", "where", "and", "or", "not", "in", "like",
                    "ilike", "between", "is", "null", "as", "on", "join", "left",
                    "right", "inner", "outer", "cross", "count", "sum", "avg",
                    "max", "min", "distinct", "all", "order", "group", "by",
                    "having", "limit", "offset", "asc", "desc", "case", "when",
                    "then", "else", "end", "exists", "true", "false", "upper",
                    "lower", "cast", "coalesce",
                }
                if col not in sql_keywords:
                    referenced_columns.append(col)

        # Score tables
        table_issues = []
        for t in referenced_tables:
            if t.lower() not in all_tables:
                table_issues.append(t)

        # Score columns
        col_issues = []
        for c in referenced_columns:
            if c not in all_columns and c != "*":
                col_issues.append(c)

        issues = []
        score = 40

        if table_issues:
            score -= 20
            issues.append(f"Unknown table(s): {', '.join(table_issues)}")

        if col_issues:
            penalty = min(20, len(col_issues) * 5)
            score -= penalty
            issues.append(f"Unrecognized column(s): {', '.join(col_issues[:5])}")

        score = max(0, score)
        note = " | ".join(issues) if issues else "All tables and columns verified."
        return score, note

    except Exception as e:
        return 20, f"Schema check error: {str(e)}"


# ── Dimension 3: Intent Match (20 pts) ───────────────────────

def _check_intent(sql: str, question: str) -> tuple[int, str]:
    """
    Check if the SQL query type aligns with the user's question intent.
    """
    question_lower = question.lower()
    sql_upper = sql.upper()

    matched_intents = []
    matched_clauses = []

    for intent_name, config in INTENT_PATTERNS.items():
        for keyword in config["keywords"]:
            if keyword in question_lower:
                matched_intents.append(intent_name)
                matched_clauses.append(config["clause"])
                break

    if not matched_intents:
        # No strong intent detected — give benefit of the doubt
        return 15, "No strong intent pattern detected; query appears reasonable."

    # Check if at least one matched clause is in the SQL
    clauses_found = [c for c in matched_clauses if c in sql_upper]

    if clauses_found:
        return 20, f"Query intent matches: {', '.join(set(matched_intents))}"
    else:
        return 5, f"Expected {'/'.join(set(matched_clauses))} for intent '{', '.join(set(matched_intents))}' but not found in SQL."
