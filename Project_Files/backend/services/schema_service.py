"""
Schema extraction service — reads PostgreSQL table/column metadata
and formats it as a prompt-ready string for LLM injection.
"""

from sqlalchemy import text, inspect
from models.database import engine


def get_schema_string() -> str:
    """
    Introspect the connected PostgreSQL database and return a formatted
    schema description suitable for injecting into an LLM prompt.

    Returns a string like:
        Table: students
        Columns: name (VARCHAR), class (VARCHAR), marks (INTEGER), company (VARCHAR)
    """
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    if not table_names:
        return "No tables found in the database."

    schema_parts = []
    for table in table_names:
        columns = inspector.get_columns(table)
        col_descriptions = []
        for col in columns:
            col_type = str(col["type"])
            nullable = "nullable" if col.get("nullable", True) else "not null"
            col_descriptions.append(f"{col['name']} ({col_type}, {nullable})")

        # Also grab primary keys
        pk = inspector.get_pk_constraint(table)
        pk_cols = pk.get("constrained_columns", []) if pk else []

        schema_parts.append(
            f"Table: {table}\n"
            f"  Columns: {', '.join(col_descriptions)}\n"
            f"  Primary Key: {', '.join(pk_cols) if pk_cols else 'none'}"
        )

    return "\n\n".join(schema_parts)


def get_table_names() -> list[str]:
    """Return a list of all table names in the database."""
    inspector = inspect(engine)
    return inspector.get_table_names()


def get_column_names(table_name: str) -> list[str]:
    """Return a list of column names for a specific table."""
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    return [col["name"] for col in columns]


def get_all_columns() -> dict[str, list[str]]:
    """Return a dict mapping each table name to its list of column names."""
    inspector = inspect(engine)
    result = {}
    for table in inspector.get_table_names():
        columns = inspector.get_columns(table)
        result[table] = [col["name"] for col in columns]
    return result
