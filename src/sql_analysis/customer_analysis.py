# ============================================================
# CUSTOMER & ORDER ANALYSIS
# File: src/sql_analysis/customer_analysis.py
#
# Analyses:
# 1. Top-spending customers
# 2. Age group vs order value
# 3. Weekend vs weekday order patterns
# ============================================================

from pathlib import Path
import sys

import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import text

# ============================================================
# 1. PROJECT PATH CONFIGURATION
# ============================================================

SRC_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = SRC_DIR.parent

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from database.connection import create_db_engine


# ============================================================
# 2. OUTPUT DIRECTORY CONFIGURATION
# ============================================================

OUTPUT_DIR = PROJECT_DIR / "output" / "sql_analysis"
REPORT_DIR = OUTPUT_DIR / "reports" / "customer"
GRAPH_DIR = OUTPUT_DIR / "graphs" / "customer"

REPORT_DIR.mkdir(parents=True, exist_ok=True)
GRAPH_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# 3. REUSABLE SQL QUERY FUNCTION
# ============================================================

def run_query(query):
    """Execute a SQL query and return the result as a DataFrame."""

    engine = create_db_engine()

    try:
        with engine.connect() as connection:
            df = pd.read_sql_query(text(query), connection)
        return df

    finally:
        engine.dispose()

# ============================================================
# 4. REUSABLE REPORT-SAVING FUNCTION
# ============================================================

def save_report(df, filename):
    """Save analysis results as a CSV report."""

    output_file = REPORT_DIR / filename
    df.to_csv(output_file, index=False)

    print(f"Report saved: {output_file}")

    return output_file


# ============================================================
# 5. REUSABLE GRAPH-SAVING FUNCTION
# ============================================================

def save_graph(filename):
    """Save the current Matplotlib figure."""

    output_file = GRAPH_DIR / filename

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Graph saved: {output_file}")

    return output_file

# ============================================================
# 6. TOP-SPENDING CUSTOMERS
# ============================================================

def analyze_top_spending_customers():
    """
    Identify the top 20 customers by spending on delivered orders.

    Missing Final_Amount values are excluded from the spending sum
    and average by SQL aggregate functions.
    """

    print("\n" + "=" * 65)
    print("1. TOP-SPENDING CUSTOMERS")
    print("=" * 65)

    query = """
        SELECT
            Customer_ID,
            COUNT(*) AS Delivered_Orders,
            COUNT(Final_Amount) AS Orders_With_Amount,
            ROUND(SUM(Final_Amount), 2) AS Total_Spending,
            ROUND(AVG(Final_Amount), 2) AS Average_Order_Value
        FROM food_delivery_data
        WHERE Order_Status = 'Delivered'
        GROUP BY Customer_ID
        ORDER BY Total_Spending DESC
        LIMIT 20;
    """

    df = run_query(query)

    if df.empty:
        print("No matching customer records found.")
        return df

    print(df.to_string(index=False))

    save_report(df, "top_spending_customers.csv")

    # Visualize top 10 customers
    plot_df = df.head(10).sort_values("Total_Spending")

    plt.figure(figsize=(11, 6))
    plt.barh(
        plot_df["Customer_ID"].astype(str),
        plot_df["Total_Spending"]
    )

    plt.title("Top 10 Customers by Total Spending")
    plt.xlabel("Total Spending")
    plt.ylabel("Customer ID")
    save_graph("top_spending_customers.png")

    return df

# ============================================================
# 7. AGE GROUP VS ORDER VALUE
# ============================================================

def analyze_age_group_order_value():
    """
    Compare average order value and total spending across age groups.
    Uses delivered orders with valid customer age and Final_Amount.
    """

    print("\n" + "=" * 65)
    print("2. AGE GROUP VS ORDER VALUE")
    print("=" * 65)

    query = """
        SELECT
            CASE
                WHEN Customer_Age BETWEEN 18 AND 24 THEN '18-24'
                WHEN Customer_Age BETWEEN 25 AND 34 THEN '25-34'
                WHEN Customer_Age BETWEEN 35 AND 44 THEN '35-44'
                WHEN Customer_Age BETWEEN 45 AND 54 THEN '45-54'
                WHEN Customer_Age >= 55 THEN '55+'
            END AS Age_Group,

            COUNT(*) AS Total_Orders,
            COUNT(DISTINCT Customer_ID) AS Unique_Customers,
            ROUND(AVG(Final_Amount), 2) AS Average_Order_Value,
            ROUND(SUM(Final_Amount), 2) AS Total_Spending

        FROM food_delivery_data

        WHERE Order_Status = 'Delivered'
          AND Customer_Age BETWEEN 18 AND 120
          AND Final_Amount IS NOT NULL

        GROUP BY
            CASE
                WHEN Customer_Age BETWEEN 18 AND 24 THEN '18-24'
                WHEN Customer_Age BETWEEN 25 AND 34 THEN '25-34'
                WHEN Customer_Age BETWEEN 35 AND 44 THEN '35-44'
                WHEN Customer_Age BETWEEN 45 AND 54 THEN '45-54'
                WHEN Customer_Age >= 55 THEN '55+'
            END

        ORDER BY MIN(Customer_Age);
    """

    df = run_query(query)

    if df.empty:
        print("No valid age and order-value records found.")
        return df

    print(df.to_string(index=False))

    save_report(df, "age_group_order_value.csv")

    # Visualize average order value by age group
    plt.figure(figsize=(10, 6))
    plt.bar(
        df["Age_Group"],
        df["Average_Order_Value"]
    )

    plt.title("Average Order Value by Age Group")
    plt.xlabel("Age Group")
    plt.ylabel("Average Order Value")
    save_graph("age_group_average_order_value.png")

    # Visualize total spending by age group
    plt.figure(figsize=(10, 6))
    plt.bar(
        df["Age_Group"],
        df["Total_Spending"]
    )

    plt.title("Total Customer Spending by Age Group")
    plt.xlabel("Age Group")
    plt.ylabel("Total Spending")
    save_graph("age_group_total_spending.png")

    return df

# ============================================================
# 8. WEEKEND VS WEEKDAY ORDER PATTERNS
# ============================================================

def analyze_weekend_weekday_patterns():
    """
    Compare order counts, delivery/cancellation counts, cancellation
    rate, and delivered-order revenue for weekends and weekdays.

    Uses the engineered Is_Weekend column when available.
    Otherwise, derives the day type from Order_Date.
    """

    print("\n" + "=" * 65)
    print("3. WEEKEND VS WEEKDAY ORDER PATTERNS")
    print("=" * 65)

    # Detect whether the engineered column exists.
    column_query = """
        SELECT COUNT(*) AS Column_Exists
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'food_delivery_data'
          AND COLUMN_NAME = 'Is_Weekend';
    """

    column_result = run_query(column_query)
    has_is_weekend = (
        not column_result.empty
        and int(column_result.loc[0, "Column_Exists"]) > 0
    )

    if has_is_weekend:
        day_expression = """
            CASE
                WHEN Is_Weekend = 1 THEN 'Weekend'
                WHEN Is_Weekend = 0 THEN 'Weekday'
                ELSE NULL
            END
        """
    else:
        day_expression = """
            CASE
                WHEN DAYOFWEEK(Order_Date) IN (1, 7) THEN 'Weekend'
                ELSE 'Weekday'
            END
        """

    query = f"""
        SELECT
            {day_expression} AS Day_Type,

            COUNT(*) AS Total_Orders,

            SUM(
                CASE WHEN Order_Status = 'Delivered'
                     THEN 1 ELSE 0 END
            ) AS Delivered_Orders,

            SUM(
                CASE WHEN Order_Status = 'Cancelled'
                     THEN 1 ELSE 0 END
            ) AS Cancelled_Orders,

            ROUND(
                100.0 * SUM(
                    CASE WHEN Order_Status = 'Cancelled'
                         THEN 1 ELSE 0 END
                ) / NULLIF(COUNT(*), 0),
                2
            ) AS Cancellation_Rate_Percent,

            ROUND(
                SUM(
                    CASE
                        WHEN Order_Status = 'Delivered'
                        THEN Final_Amount
                        ELSE 0
                    END
                ),
                2
            ) AS Delivered_Revenue,

            ROUND(
                AVG(
                    CASE
                        WHEN Order_Status = 'Delivered'
                        THEN Final_Amount
                    END
                ),
                2
            ) AS Average_Delivered_Order_Value

        FROM food_delivery_data

        WHERE {day_expression} IS NOT NULL

        GROUP BY Day_Type

        ORDER BY
            CASE
                WHEN Day_Type = 'Weekday' THEN 1
                WHEN Day_Type = 'Weekend' THEN 2
                ELSE 3
            END;
    """

    df = run_query(query)

    if df.empty:
        print("No valid order-date/day-type records found.")
        return df

    print(df.to_string(index=False))

    save_report(df, "weekend_weekday_order_patterns.csv")

    # Compare total, delivered, and cancelled orders
    plot_df = df.set_index("Day_Type")[
        ["Total_Orders", "Delivered_Orders", "Cancelled_Orders"]
    ]

    plot_df.plot(
        kind="bar",
        figsize=(10, 6)
    )

    plt.title("Weekend vs Weekday Order Counts")
    plt.xlabel("Day Type")
    plt.ylabel("Number of Orders")
    plt.xticks(rotation=0)
    save_graph("weekend_weekday_order_counts.png")

    # Compare cancellation rates
    plt.figure(figsize=(8, 5))
    plt.bar(
        df["Day_Type"],
        df["Cancellation_Rate_Percent"]
    )

    plt.title("Cancellation Rate: Weekend vs Weekday")
    plt.xlabel("Day Type")
    plt.ylabel("Cancellation Rate (%)")
    save_graph("weekend_weekday_cancellation_rate.png")

    # Compare delivered revenue
    plt.figure(figsize=(8, 5))
    plt.bar(
        df["Day_Type"],
        df["Delivered_Revenue"]
    )

    plt.title("Delivered Revenue: Weekend vs Weekday")
    plt.xlabel("Day Type")
    plt.ylabel("Delivered Revenue")
    save_graph("weekend_weekday_delivered_revenue.png")

    return df

# ============================================================
# 9. RUN ALL CUSTOMER ANALYSES
# ============================================================

def run_customer_analysis():
    """Run all customer and order analysis functions."""

    print("\n" + "=" * 65)
    print("CUSTOMER & ORDER ANALYSIS")
    print("=" * 65)

    analyze_top_spending_customers()
    analyze_age_group_order_value()
    analyze_weekend_weekday_patterns()

    print("\nCustomer and order analysis completed.")

