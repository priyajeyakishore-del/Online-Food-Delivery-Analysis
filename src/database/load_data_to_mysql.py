# ============================================================
# LOAD FEATURE-ENGINEERED DATA INTO MYSQL
# Project: Online Food Delivery Analysis
# ============================================================

from pathlib import Path
import sys

import pandas as pd
from sqlalchemy import inspect, text

# ------------------------------------------------------------
# 1. Configure project paths
# ------------------------------------------------------------

SRC_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = SRC_DIR.parent

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from database.connection import create_db_engine


# ------------------------------------------------------------
# 2. File and table configuration
# ------------------------------------------------------------

CSV_PATH = (
    PROJECT_DIR
    / "output"
    / "feature_engineering"
    / "feature_engineered_dataset.csv"
)

TABLE_NAME = "food_delivery_data"


# ------------------------------------------------------------
# 3. Load CSV into MySQL
# ------------------------------------------------------------

def load_data_to_mysql():
    engine = create_db_engine()

    try:
        print("=" * 65)
        print("LOAD DATA INTO MYSQL")
        print("=" * 65)

        print(f"\nDatabase: {engine.url.database}")
        print(f"CSV file: {CSV_PATH}")

        # Check whether the CSV exists
        if not CSV_PATH.exists():
            raise FileNotFoundError(
                f"CSV file not found:\n{CSV_PATH}"
            )

        # Read the feature-engineered dataset
        df = pd.read_csv(CSV_PATH, low_memory=False)

        print(f"\nCSV rows: {len(df):,}")
        print(f"CSV columns: {len(df.columns)}")

        if df.empty:
            raise ValueError("The CSV file contains no rows.")

        # Clean column names
        df.columns = df.columns.str.strip()

        # Check for duplicate column names
        if df.columns.duplicated().any():
            duplicates = df.columns[df.columns.duplicated()].tolist()
            raise ValueError(
                f"Duplicate column names found: {duplicates}"
            )

        # Convert date column when present
        if "Order_Date" in df.columns:
            df["Order_Date"] = pd.to_datetime(
                df["Order_Date"],
                errors="coerce"
            )

        # Convert missing values to SQL NULL
        df = df.astype(object).where(pd.notna(df), None)

        # Check whether the target table exists
        inspector = inspect(engine)
        table_exists = inspector.has_table(TABLE_NAME)

        if table_exists:
            # Check whether the existing table is empty
            with engine.connect() as connection:
                existing_rows = connection.execute(
                    text(f"SELECT COUNT(*) FROM `{TABLE_NAME}`")
                ).scalar_one()

            if existing_rows > 0:
                print(
                    f"\nTable '{TABLE_NAME}' already contains "
                    f"{existing_rows:,} rows."
                )
                print(
                    "Loading cancelled to prevent duplicate records."
                )
                print(
                    "If you need to reload the data, confirm the "
                    "table contents before clearing or replacing it."
                )
                return

            print(
                f"\nUsing existing empty table: {TABLE_NAME}"
            )

            # Ensure CSV columns match the existing table
            database_columns = {
                column["name"]
                for column in inspector.get_columns(TABLE_NAME)
            }

            csv_columns = set(df.columns)

            missing_in_csv = database_columns - csv_columns
            extra_in_csv = csv_columns - database_columns

            if missing_in_csv or extra_in_csv:
                raise ValueError(
                    "CSV/table column mismatch.\n"
                    f"Columns missing from CSV: {sorted(missing_in_csv)}\n"
                    f"Columns not in table: {sorted(extra_in_csv)}"
                )

        else:
            # Create a table automatically if it doesn't exist.
            print(
                f"\nTable '{TABLE_NAME}' does not exist."
            )
            print("Creating the table from CSV column types.")

        # Insert data in batches.
        # Existing tables are preserved; no replace/drop operation.
        df.to_sql(
            name=TABLE_NAME,
            con=engine,
            if_exists="append" if table_exists else "fail",
            index=False,
            chunksize=1000
        )

        # Verify the inserted row count
        with engine.connect() as connection:
            total_rows = connection.execute(
                text(f"SELECT COUNT(*) FROM `{TABLE_NAME}`")
            ).scalar_one()

        print("\n" + "=" * 65)
        print("DATA LOADING COMPLETED")
        print("=" * 65)
        print(f"Rows in CSV: {len(df):,}")
        print(f"Rows now in MySQL table: {total_rows:,}")
        print(f"Target table: {TABLE_NAME}")
        print(f"Database: {engine.url.database}")

    except Exception as error:
        print("\nDATA LOADING FAILED")
        print(f"Reason: {error}")
        raise

    finally:
        engine.dispose()


# ------------------------------------------------------------
# 4. Run the script
# ------------------------------------------------------------

if __name__ == "__main__":
    load_data_to_mysql()