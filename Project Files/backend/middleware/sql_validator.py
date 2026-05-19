"""
SQL injection prevention middleware.
Validates generated SQL before execution to ensure safety.
"""

import re

# ── Dangerous SQL patterns ────────────────────────────────────

BLOCKED_KEYWORDS = [
    "DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "TRUNCATE",
    "CREATE", "GRANT", "REVOKE", "EXEC", "EXECUTE",
    "MERGE", "CALL", "COPY", "LOAD", "REPLACE",
]

BLOCKED_PATTERNS = [
    r";\s*\w",             # Multiple statements (statement chaining)
    r"--",                  # SQL line comments
    r"/\*",                 # SQL block comments
    r"xp_",                 # Extended stored procedures
    r"sp_",                 # System stored procedures
    r"\\x[0-9a-fA-F]",     # Hex-encoded characters
]


def validate_sql(sql: str) -> dict:
    """
    Check a SQL string for injection patterns and dangerous operations.

    Args:
        sql: The SQL query to validate.

    Returns:
        dict with keys:
            is_safe (bool),
            reason (str or None) — only present when unsafe
    """
    if not sql or not sql.strip():
        return {"is_safe": False, "reason": "Empty SQL query."}

    sql_stripped = sql.strip()
    sql_upper = sql_stripped.upper()

    # 1. Must start with SELECT or WITH (CTE)
    first_word = sql_upper.split()[0] if sql_upper.split() else ""
    if first_word not in ("SELECT", "WITH"):
        return {
            "is_safe": False,
            "reason": f"Only SELECT queries are allowed. Query starts with '{first_word}'.",
        }

    # 2. Check for blocked keywords
    for keyword in BLOCKED_KEYWORDS:
        # Match as whole word to avoid false positives (e.g., "UPDATED" in a column name)
        pattern = r'\b' + keyword + r'\b'
        if re.search(pattern, sql_upper):
            return {
                "is_safe": False,
                "reason": f"Blocked keyword detected: {keyword}. Only read-only queries are allowed.",
            }

    # 3. Check for dangerous patterns
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, sql_stripped):
            return {
                "is_safe": False,
                "reason": f"Potentially dangerous SQL pattern detected.",
            }

    # 4. Check for semicolons (prevent statement chaining)
    # Allow a single trailing semicolon but not multiple statements
    clean = sql_stripped.rstrip(";").strip()
    if ";" in clean:
        return {
            "is_safe": False,
            "reason": "Multiple SQL statements detected. Only single queries are allowed.",
        }

    return {"is_safe": True}
