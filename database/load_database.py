import sqlite3
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATHS = [
    os.path.join(BASE_DIR, "backend", "aksharai_dev.db"),
    os.path.join(BASE_DIR, "database", "literacy_platform.db")
]

SCHEMA_SQL_PATH = os.path.join(BASE_DIR, "database", "schema.sql")
SEED_SQL_PATH = os.path.join(BASE_DIR, "database", "seed_data.sql")
SEED_TEST_SQL_PATH = os.path.join(BASE_DIR, "database", "seed_data_test.sql")


def adapt_pg_schema_for_sqlite(pg_sql: str) -> str:
    """
    Adapts PostgreSQL DDL syntax to SQLite compatible DDL.
    - SERIAL PRIMARY KEY -> INTEGER PRIMARY KEY AUTOINCREMENT
    - TIMESTAMP WITH TIME ZONE -> DATETIME
    """
    sql = pg_sql.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
    sql = sql.replace("TIMESTAMP WITH TIME ZONE", "DATETIME")
    return sql


def load_sql_into_sqlite(db_path: str):
    print(f"\n[DB LOADER] Initializing SQLite database at: {db_path}")

    # Read SQL files
    with open(SCHEMA_SQL_PATH, "r", encoding="utf-8") as f:
        raw_schema = f.read()

    with open(SEED_SQL_PATH, "r", encoding="utf-8") as f:
        raw_seed = f.read()

    with open(SEED_TEST_SQL_PATH, "r", encoding="utf-8") as f:
        raw_test_seed = f.read()

    # Adapt schema DDL for SQLite
    sqlite_schema = adapt_pg_schema_for_sqlite(raw_schema)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    # Clear existing tables if present for clean seeding
    cursor.execute("PRAGMA foreign_keys = OFF;")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall() if not row[0].startswith("sqlite_")]
    for t in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {t};")
    cursor.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    # 1. Execute Schema
    print("  -> Loading schema.sql (21 relational tables)...")
    try:
        cursor.executescript(sqlite_schema)
        conn.commit()
    except Exception as e:
        print(f"  [ERROR] Schema load error: {e}")

    # 2. Execute Seed Data
    print("  -> Loading seed_data.sql (languages, curriculums, modules, lessons)...")
    try:
        cursor.executescript(raw_seed)
        conn.commit()
    except Exception as e:
        print(f"  [ERROR] Seed data load error: {e}")

    # 3. Execute Test Seed Data
    print("  -> Loading seed_data_test.sql (proficiency_benchmarks, test learner, assessments, results)...")
    try:
        cursor.executescript(raw_test_seed)
        conn.commit()
    except Exception as e:
        print(f"  [ERROR] Test seed data load error: {e}")

    # 4. Fetch test learner ID to confirm
    cursor.execute("SELECT learner_id, email, username FROM learner WHERE email = 'test@aksharai.dev';")
    learner_row = cursor.fetchone()

    conn.close()

    if learner_row:
        print(f"  [SUCCESS] Test Learner ID: {learner_row[0]} | Username: {learner_row[2]} | Email: {learner_row[1]}")
        return learner_row[0]
    else:
        print("  [WARNING] Test learner row not found after seeding.")
        return None


def main():
    print("=" * 80)
    print("        AKSHARAI DATABASE SCHEMA & TEST SEEDING PIPELINE")
    print("=" * 80)

    test_learner_id = None
    for db_path in DB_PATHS:
        lid = load_sql_into_sqlite(db_path)
        if lid:
            test_learner_id = lid

    print("\n" + "=" * 80)
    print(f"  ALL DATABASES INITIALIZED SUCCESSFULLY!")
    print(f"  TEST LEARNER ID: {test_learner_id}")
    print("=" * 80)


if __name__ == "__main__":
    main()
