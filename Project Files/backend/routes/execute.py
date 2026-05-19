"""
Execute route — runs validated SQL against PostgreSQL and returns results.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from models.database import get_db, engine, QueryHistory
from middleware.sql_validator import validate_sql

router = APIRouter(prefix="/api", tags=["Execute"])


# ── Request/Response schemas ──────────────────────────────────

class ExecuteRequest(BaseModel):
    sql: str
    query_id: int | None = None  # Link back to the generate history entry


class ExecuteResponse(BaseModel):
    columns: list[str]
    rows: list[list]
    row_count: int
    query_id: int | None = None


# ── Routes ────────────────────────────────────────────────────

@router.post("/execute", response_model=ExecuteResponse)
def execute_query(
    req: ExecuteRequest,
    db: Session = Depends(get_db),
):
    """
    Execute a validated SQL query against PostgreSQL.
    Returns column headers and row data.
    """
    # 1. Validate the SQL for injection/dangerous patterns
    validation = validate_sql(req.sql)
    if not validation["is_safe"]:
        raise HTTPException(
            status_code=400,
            detail=f"Query blocked: {validation['reason']}",
        )

    # 2. Execute the query
    try:
        with engine.connect() as conn:
            result = conn.execute(text(req.sql))
            columns = list(result.keys())
            rows = [list(row) for row in result.fetchall()]

        # 3. Update history entry if query_id provided
        if req.query_id:
            history_entry = db.query(QueryHistory).filter(
                QueryHistory.id == req.query_id
            ).first()
            if history_entry:
                history_entry.executed = True
                history_entry.results = {"columns": columns, "rows": rows[:50]}  # Store first 50 rows
                db.commit()

        return ExecuteResponse(
            columns=columns,
            rows=rows,
            row_count=len(rows),
            query_id=req.query_id,
        )

    except Exception as e:
        error_msg = str(e)

        # Update history with the error
        if req.query_id:
            history_entry = db.query(QueryHistory).filter(
                QueryHistory.id == req.query_id
            ).first()
            if history_entry:
                history_entry.executed = True
                history_entry.error = error_msg
                db.commit()

        # Return a user-friendly error
        raise HTTPException(
            status_code=400,
            detail=f"Query execution failed: {_friendly_error(error_msg)}",
        )


def _friendly_error(error: str) -> str:
    """Convert raw PostgreSQL errors into plain English."""
    error_lower = error.lower()

    if "relation" in error_lower and "does not exist" in error_lower:
        return "The table referenced in the query does not exist in the database."
    elif "column" in error_lower and "does not exist" in error_lower:
        return "One or more columns referenced in the query do not exist."
    elif "syntax error" in error_lower:
        return "The SQL query has a syntax error and cannot be executed."
    elif "permission denied" in error_lower:
        return "Permission denied to access the requested data."
    elif "connection" in error_lower:
        return "Could not connect to the database. Please try again."
    else:
        return error
