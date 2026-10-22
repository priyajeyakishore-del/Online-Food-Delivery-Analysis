# ============================================================
# MYSQL DATABASE CONNECTION
# File: src/database/connection.py
# ============================================================

from pathlib import Path
import sys

from sqlalchemy import create_engine, text

# ============================================================
# 1. ADD SRC DIRECTORY TO PYTHON PATH
# ============================================================

SRC_DIR = Path(__file__).resolve().parents[1]

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


# ============================================================
# 2. IMPORT DATABASE CONFIGURATION
# ============================================================

from database.db_config import get_database_url


# ============================================================
# 3. CREATE DATABASE ENGINE
# ============================================================

def create_db_engine():
    """Create and return the MySQL SQLAlchemy engine."""

    return create_engine(
        get_database_url(),
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=False
    )


# ============================================================
# 4. TEST DATABASE CONNECTION
# ============================================================

def test_db_connection():
    """Verify that MySQL and the configured database are accessible."""

    engine = create_db_engine()

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            print("MySQL database connection successful!")

    finally:
        engine.dispose()


# ============================================================
# 5. EXECUTION ENTRY POINT
# ============================================================

if __name__ == "__main__":
    test_db_connection()