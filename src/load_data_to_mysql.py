# ============================================================
# LOAD FEATURE-ENGINEERED CSV INTO MYSQL
# PROJECT: ONLINE FOOD DELIVERY ANALYSIS
# FILE: load_data_to_mysql.py
# ============================================================

from pathlib import Path

import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from database.connection import create_database, get_engine


# ============================================================
# 1. PATH AND TABLE CONFIGURATION
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parents[1]

CSV_FILE = (
    PROJECT_DIR
    / "output"
    / "feature_engineering"
    / "feature_engineered_dataset.csv"
)

TABLE_NAME = "feature_engineered_data"


# ============================================================
# 2. LOAD CSV FILE
# ============================================================

def load_csv():
    """Load the feature-engineered CSV into a DataFrame."""

    if not CSV_FILE.exists():
        raise FileNotFoundError(
            f"CSV file not found:\n{CSV_FILE}"
        )

    df = pd.read_csv(CSV_FILE, low_memory=False)

    if df.empty:
        raise ValueError("The CSV file contains no records.")

    if len(df.columns) != len(set(df.columns)):
        raise ValueError("The CSV contains duplicate column names.")

    print("=" * 60)
    print("CSV FILE LOADED SUCCESSFULLY")
    print("=" * 60)
    print(f"File: {CSV_FILE}")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns):,}")

    return df


# ============================================================
# 3. CHECK WHETHER MYSQL TABLE EXISTS
# ============================================================

def table_exists(engine):
    """Check whether the destination table already exists."""

    query = text("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = :database_name
          AND table_name = :table_name
    """)

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {
                "database_name": "online_food_delivery_db",
                "table_name": TABLE_NAME
            }
        ).scalar_one()

    return result > 0


# ============================================================
# 4. IMPORT CSV DATA INTO MYSQL
# ============================================================

def import_to_mysql(df):
    """Import CSV records without overwriting an existing table."""

    create_database()
    engine = get_engine()

    try:
        if table_exists(engine):
            print(
                f"\nTable '{TABLE_NAME}' already exists. "
                "Import cancelled to prevent duplicate data "
                "or accidental overwriting."
            )
            return

        print("\nImporting data into MySQL...")

        df.to_sql(
            name=TABLE_NAME,
            con=engine,
            if_exists="fail",
            index=False,
            chunksize=1000,
            method="multi"
        )

        print("\nData imported successfully!")

        # Verify the imported record count.
        with engine.connect() as connection:
            row_count = connection.execute(
                text(f"SELECT COUNT(*) FROM `{TABLE_NAME}`")
            ).scalar_one()

        print(f"Database: online_food_delivery_db")
        print(f"Table: {TABLE_NAME}")
        print(f"CSV rows: {len(df):,}")
        print(f"MySQL rows: {row_count:,}")

    finally:
        engine.dispose()


# ============================================================
# 5. MAIN EXECUTION
# ============================================================

if __name__ == "__main__":

    try:
        dataframe = load_csv()
        import_to_mysql(dataframe)

    except (FileNotFoundError, ValueError) as error:
        print(f"\nInput error: {error}")

    except SQLAlchemyError as error:
        print(f"\nMySQL error: {error}")

    except Exception as error:
        print(f"\nUnexpected error: {error}")