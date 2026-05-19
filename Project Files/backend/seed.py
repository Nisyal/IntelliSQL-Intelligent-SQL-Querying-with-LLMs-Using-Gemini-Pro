"""
Seed the PostgreSQL database with the sample Students table and records.
Migrated from the original SQLite sql.py — preserves the exact same schema
and data so the core NL-to-SQL prompting logic continues to work.

Usage:
    python seed.py
"""

from sqlalchemy import text
from models.database import engine, init_db


def seed():
    """Create the Students demo table and insert sample data."""

    # Ensure ORM tables (users, query_history) exist
    init_db()

    with engine.connect() as conn:
        # ── Create the demo Students table ────────────────────
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS Students (
                name    VARCHAR(30),
                class   VARCHAR(10),
                marks   INT,
                company VARCHAR(30)
            )
        """))

        # ── Check if data already exists to avoid duplicates ──
        result = conn.execute(text("SELECT COUNT(*) FROM Students"))
        count = result.scalar()

        if count == 0:
            conn.execute(text("""
                INSERT INTO Students (name, class, marks, company) VALUES
                ('Sijo',   'BTech', 75, 'JSW'),
                ('Lijo',   'MTech', 69, 'TCS'),
                ('Rijo',   'BSc',   79, 'WIPRO'),
                ('Sibin',  'MSc',   89, 'INFOSYS'),
                ('Dilsha', 'MCom',  99, 'Cyient')
            """))
            print("[OK] Seeded 5 student records.")
        else:
            print(f"[INFO] Students table already has {count} records - skipping seed.")

        conn.commit()

        # ── Verify ────────────────────────────────────────────
        rows = conn.execute(text("SELECT * FROM Students")).fetchall()
        print("\nCurrent Students table:")
        for row in rows:
            print(f"   {row}")


if __name__ == "__main__":
    seed()
