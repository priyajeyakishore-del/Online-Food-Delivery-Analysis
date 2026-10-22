# ============================================================
# CREATE TABLES
# Online Food Delivery Analysis
# ============================================================

from pathlib import Path
import sys

from sqlalchemy import text, inspect

# Add src directory to Python path
SRC_DIR = Path(__file__).resolve().parents[1]

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from database.connection import create_db_engine


def create_food_delivery_table():
    """Create the food_delivery_data table if it does not exist."""

    engine = create_db_engine()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS food_delivery_data (
        Order_ID VARCHAR(50) PRIMARY KEY,
        Customer_ID VARCHAR(50),
        Customer_Age INT,
        Customer_Gender VARCHAR(20),
        City VARCHAR(100),
        Area VARCHAR(100),
        Restaurant_ID VARCHAR(50),
        Restaurant_Name VARCHAR(255),
        Cuisine_Type VARCHAR(100),
        Order_Date DATETIME,
        Order_Time VARCHAR(20),
        Delivery_Time_Min FLOAT,
        Distance_km FLOAT,
        Order_Value DECIMAL(12, 2),
        Discount_Applied DECIMAL(12, 2),
        Final_Amount DECIMAL(12, 2),
        Payment_Mode VARCHAR(50),
        Order_Status VARCHAR(30),
        Cancellation_Reason VARCHAR(255),
        Delivery_Partner_ID VARCHAR(50),
        Delivery_Rating FLOAT,
        Restaurant_Rating FLOAT,
        Order_Day VARCHAR(20),
        Peak_Hour BOOLEAN,
        Profit_Margin DECIMAL(8, 2),
        Order_Year INT,
        Order_Month INT,
        Order_Month_Name VARCHAR(20),
        Order_Weekday VARCHAR(20),
        Is_Weekend BOOLEAN,
        Distance_Category VARCHAR(50),
        Delivery_Time_Category VARCHAR(50),
        Order_Value_Category VARCHAR(50),
        Discount_Percentage FLOAT,
        Rating_Category VARCHAR(50)
    );
    """

    try:
        with engine.begin() as connection:
            connection.execute(text(create_table_query))

        print("=" * 65)
        print("TABLE CREATION")
        print("=" * 65)
        print(f"Database: {engine.url.database}")
        print("Table 'food_delivery_data' is ready.")

        # Display table columns
        inspector = inspect(engine)
        columns = inspector.get_columns("food_delivery_data")

        print(f"\nTotal columns: {len(columns)}")
        print("\nColumn names:")

        for column in columns:
            print(f"- {column['name']}")

    except Exception as error:
        print(f"Error creating table: {error}")
        raise

    finally:
        engine.dispose()


if __name__ == "__main__":
    create_food_delivery_table()