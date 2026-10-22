# ============================================================
# MYSQL DATABASE CONFIGURATION
# PROJECT: ONLINE FOOD DELIVERY ANALYSIS
# FILE: database/db_config.py
# ============================================================

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import URL


# ============================================================
# 1. LOAD ENVIRONMENT VARIABLES
# ============================================================

# Project root is two levels above this file:
# project_root/src/database/db_config.py

PROJECT_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_DIR / ".env"

load_dotenv(ENV_FILE)


# ============================================================
# 2. MYSQL SETTINGS
# ============================================================

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))

DATABASE_NAME = os.getenv(
    "DATABASE_NAME",
    "online_food_delivery_db"
)


# ============================================================
# 3. VALIDATE CONFIGURATION
# ============================================================

if not DB_PASSWORD:
    raise ValueError(
        f"MySQL password is missing. Please configure DB_PASSWORD "
        f"in your .env file: {ENV_FILE}"
    )


# ============================================================
# 4. BUILD SQLALCHEMY DATABASE URL
# ============================================================

def get_database_url(include_database=True):
    """
    Build a MySQL connection URL.

    include_database=False:
        Connect to the MySQL server without selecting a database.

    include_database=True:
        Connect to the project database.
    """

    return URL.create(
        drivername="mysql+pymysql",
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DATABASE_NAME if include_database else None
    )