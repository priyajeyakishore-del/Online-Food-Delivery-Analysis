# ============================================================
# REVENUE & PROFIT ANALYSIS
# Online Food Delivery Analysis
# Python | Pandas | MySQL | Matplotlib
# ============================================================

from pathlib import Path
import sys

import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import text

# ------------------------------------------------------------
# 1. PROJECT CONFIGURATION
# ------------------------------------------------------------

SRC_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = SRC_DIR.parent

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from database.connection import create_db_engine

REPORT_DIR = PROJECT_DIR / "output" / "sql_analysis" / "reports" / "revenue"
GRAPH_DIR = PROJECT_DIR / "output" / "sql_analysis" / "graphs" / "revenue"

REPORT_DIR.mkdir(parents=True, exist_ok=True)
GRAPH_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# 2. REUSABLE DATABASE FUNCTION
# ------------------------------------------------------------

def run_query(query):
    """Execute a SQL query and return a Pandas DataFrame."""

    engine = create_db_engine()

    try:
        with engine.connect() as connection:
            return pd.read_sql_query(text(query), connection)
    finally:
        engine.dispose()


# ------------------------------------------------------------
# 3. REUSABLE REPORT FUNCTION
# ------------------------------------------------------------

def save_report(df, filename):
    """Save analysis results as a CSV report."""

    file_path = REPORT_DIR / filename
    df.to_csv(file_path, index=False)

    print(f"Report saved: {file_path}")


# ------------------------------------------------------------
# 4. REUSABLE GRAPH FUNCTION
# ------------------------------------------------------------

def save_graph(filename):
    """Save the current Matplotlib graph."""

    file_path = GRAPH_DIR / filename

    plt.tight_layout()
    plt.savefig(file_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Graph saved: {file_path}")


# ============================================================
# ANALYSIS 4: MONTHLY REVENUE TRENDS
# ============================================================

def analyze_monthly_revenue_trends():

    print("\n" + "=" * 65)
    print("4. MONTHLY REVENUE TRENDS")
    print("=" * 65)

    query = """
        SELECT
            YEAR(Order_Date) AS Order_Year,
            MONTH(Order_Date) AS Order_Month,
            DATE_FORMAT(Order_Date, '%%Y-%%m') AS Revenue_Month,
            COUNT(*) AS Delivered_Orders,
            ROUND(SUM(Final_Amount), 2) AS Monthly_Revenue,
            ROUND(AVG(Final_Amount), 2) AS Average_Order_Value
        FROM food_delivery_data
        WHERE Order_Status = 'Delivered'
        AND Order_Date IS NOT NULL
        AND Final_Amount IS NOT NULL
        GROUP BY
            YEAR(Order_Date),
            MONTH(Order_Date),
            DATE_FORMAT(Order_Date, '%%Y-%%m')
        ORDER BY Order_Year, Order_Month
    """

    df = run_query(query)

    if df.empty:
        print("No valid monthly revenue records found.")
        return

    print(df.to_string(index=False))

    save_report(df, "monthly_revenue_trends.csv")

    # Monthly revenue trend
    df["Revenue_Month"] = df["Revenue_Month"].astype(str)

    plt.figure(figsize=(12, 6))
    plt.plot(
        df["Revenue_Month"],
        df["Monthly_Revenue"],
        marker="o",
        linewidth=2
    )

    plt.title("Monthly Delivered Revenue Trends")
    plt.xlabel("Month")
    plt.ylabel("Delivered Revenue")
    plt.xticks(rotation=45, ha="right")
    plt.grid(True, linestyle="--", alpha=0.4)

    save_graph("monthly_revenue_trends.png")

    # Monthly order volume
    plt.figure(figsize=(12, 6))
    plt.bar(
        df["Revenue_Month"],
        df["Delivered_Orders"]
    )

    plt.title("Monthly Delivered Order Volume")
    plt.xlabel("Month")
    plt.ylabel("Number of Delivered Orders")
    plt.xticks(rotation=45, ha="right")
    plt.grid(axis="y", linestyle="--", alpha=0.4)

    save_graph("monthly_delivered_orders.png")


# ============================================================
# ANALYSIS 5: IMPACT OF DISCOUNTS ON PROFIT
# ============================================================

def analyze_discount_impact_on_profit():

    print("\n" + "=" * 65)
    print("5. IMPACT OF DISCOUNTS ON PROFIT")
    print("=" * 65)

    query = """
        SELECT
            Discount_Applied,
            COUNT(*) AS Delivered_Orders,
            ROUND(AVG(Discount_Applied), 2) AS Average_Discount,
            ROUND(SUM(Final_Amount), 2) AS Delivered_Revenue,
            ROUND(AVG(Final_Amount), 2) AS Average_Order_Value,
            ROUND(AVG(Profit_Margin), 2) AS Average_Profit_Margin,
            ROUND(SUM(Profit_Margin), 2) AS Total_Profit_Margin
        FROM food_delivery_data
        WHERE Order_Status = 'Delivered'
          AND Discount_Applied IS NOT NULL
        GROUP BY Discount_Applied
        ORDER BY Discount_Applied;
    """

    df = run_query(query)

    if df.empty:
        print("No valid discount analysis records found.")
        return

    print(df.to_string(index=False))

    save_report(df, "discount_impact_on_profit.csv")

    # Revenue by discount amount
    plt.figure(figsize=(10, 6))
    plt.bar(
        df["Discount_Applied"].astype(str),
        df["Delivered_Revenue"]
    )

    plt.title("Delivered Revenue by Discount Amount")
    plt.xlabel("Discount Applied")
    plt.ylabel("Delivered Revenue")
    plt.grid(axis="y", linestyle="--", alpha=0.4)

    save_graph("revenue_by_discount.png")

    # Profit margin by discount amount
    plt.figure(figsize=(10, 6))
    plt.bar(
        df["Discount_Applied"].astype(str),
        df["Average_Profit_Margin"]
    )

    plt.title("Average Profit Margin by Discount Amount")
    plt.xlabel("Discount Applied")
    plt.ylabel("Average Profit Margin")
    plt.grid(axis="y", linestyle="--", alpha=0.4)

    save_graph("profit_margin_by_discount.png")


# ============================================================
# ANALYSIS 6A: HIGH-REVENUE CITIES
# ============================================================

def analyze_high_revenue_cities():

    print("\n" + "=" * 65)
    print("6A. HIGH-REVENUE CITIES")
    print("=" * 65)

    query = """
        SELECT
            City,
            COUNT(*) AS Delivered_Orders,
            ROUND(SUM(Final_Amount), 2) AS Total_Revenue,
            ROUND(AVG(Final_Amount), 2) AS Average_Order_Value,
            ROUND(SUM(Profit_Margin), 2) AS Total_Profit_Margin
        FROM food_delivery_data
        WHERE Order_Status = 'Delivered'
          AND City IS NOT NULL
          AND TRIM(City) <> ''
          AND Final_Amount IS NOT NULL
        GROUP BY City
        ORDER BY Total_Revenue DESC
        LIMIT 15;
    """

    df = run_query(query)

    if df.empty:
        print("No valid city revenue records found.")
        return

    print(df.to_string(index=False))

    save_report(df, "high_revenue_cities.csv")

    # Horizontal bar chart
    df = df.sort_values("Total_Revenue", ascending=True)

    plt.figure(figsize=(11, 7))
    plt.barh(
        df["City"],
        df["Total_Revenue"]
    )

    plt.title("Top 15 Cities by Delivered Revenue")
    plt.xlabel("Delivered Revenue")
    plt.ylabel("City")
    plt.grid(axis="x", linestyle="--", alpha=0.4)

    save_graph("high_revenue_cities.png")


# ============================================================
# ANALYSIS 6B: HIGH-REVENUE CUISINES
# ============================================================

def analyze_high_revenue_cuisines():

    print("\n" + "=" * 65)
    print("6B. HIGH-REVENUE CUISINES")
    print("=" * 65)

    query = """
        SELECT
            Cuisine_Type,
            COUNT(*) AS Delivered_Orders,
            ROUND(SUM(Final_Amount), 2) AS Total_Revenue,
            ROUND(AVG(Final_Amount), 2) AS Average_Order_Value,
            ROUND(SUM(Profit_Margin), 2) AS Total_Profit_Margin
        FROM food_delivery_data
        WHERE Order_Status = 'Delivered'
          AND Cuisine_Type IS NOT NULL
          AND TRIM(Cuisine_Type) <> ''
          AND Final_Amount IS NOT NULL
        GROUP BY Cuisine_Type
        ORDER BY Total_Revenue DESC
        LIMIT 15;
    """

    df = run_query(query)

    if df.empty:
        print("No valid cuisine revenue records found.")
        return

    print(df.to_string(index=False))

    save_report(df, "high_revenue_cuisines.csv")

    # Horizontal bar chart
    df = df.sort_values("Total_Revenue", ascending=True)

    plt.figure(figsize=(11, 7))
    plt.barh(
        df["Cuisine_Type"],
        df["Total_Revenue"]
    )

    plt.title("Top Cuisines by Delivered Revenue")
    plt.xlabel("Delivered Revenue")
    plt.ylabel("Cuisine Type")
    plt.grid(axis="x", linestyle="--", alpha=0.4)

    save_graph("high_revenue_cuisines.png")


# ============================================================
# MAIN FUNCTION
# ============================================================

def run_revenue_profit_analysis():

    print("\n" + "=" * 65)
    print("REVENUE & PROFIT ANALYSIS")
    print("=" * 65)

    analyze_monthly_revenue_trends()
    analyze_discount_impact_on_profit()
    analyze_high_revenue_cities()
    analyze_high_revenue_cuisines()

    print("\nRevenue and profit analysis completed.")


if __name__ == "__main__":
    run_revenue_profit_analysis()