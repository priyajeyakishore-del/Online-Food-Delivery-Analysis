# ============================================================
# RESTAURANT PERFORMANCE ANALYSIS
# Project: Online Food Delivery Analysis
# Database: online_food_delivery_db
# Table: food_delivery_data
# ============================================================

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import text

from database.connection import create_db_engine


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

REPORT_DIR = (
    PROJECT_ROOT / "output" / "sql_analysis" / "reports" / "restaurant"
)
GRAPH_DIR = (
    PROJECT_ROOT / "output" / "sql_analysis" / "graphs" / "restaurant"
)

REPORT_DIR.mkdir(parents=True, exist_ok=True)
GRAPH_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# REUSABLE FUNCTIONS
# ============================================================

def run_query(query):
    """Execute SQL and return a DataFrame."""
    engine = create_db_engine()

    try:
        with engine.connect() as connection:
            return pd.read_sql_query(text(query), connection)
    finally:
        engine.dispose()


def save_report(df, filename, columns=None):
    """Always save a CSV, including its headers when there are no rows."""
    if df is None:
        df = pd.DataFrame(columns=columns or [])

    if df.empty and columns:
        df = pd.DataFrame(columns=columns)

    output_path = REPORT_DIR / filename
    df.to_csv(output_path, index=False)
    print(f"Report saved: {output_path}")

    return df


def save_graph(filename):
    """Save and close the current graph."""
    output_path = GRAPH_DIR / filename
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Graph saved: {output_path}")


def print_summary(title, df):
    """Print results in a readable format."""
    print("\n" + "=" * 85)
    print(title)
    print("=" * 85)

    if df is None or df.empty:
        print("No matching records. An empty report will still be saved.")
    else:
        print(df.to_string(index=False))


def save_no_data_graph(filename, title, message):
    """Save a placeholder graph when no rows are available."""
    plt.figure(figsize=(10, 5))
    plt.axis("off")
    plt.title(title, fontsize=14)
    plt.text(
        0.5, 0.5, message,
        ha="center", va="center",
        transform=plt.gca().transAxes,
        wrap=True
    )
    save_graph(filename)


def restaurant_label(df):
    """Create readable labels, falling back to the restaurant ID."""
    names = df["Restaurant_Name"].fillna("").astype(str).str.strip()
    ids = df["Restaurant_ID"].fillna("").astype(str).str.strip()

    labels = names.where(names.ne(""), ids)
    return labels.where(labels.ne(""), "Unknown restaurant")


# ============================================================
# 10. TOP-RATED RESTAURANTS
# ============================================================

def analyze_top_rated_restaurants():
    """
    Rank restaurants by average rating.
    Restaurants with at least one valid rating are included.
    Restaurant names are used as the grouping key when available,
    with the ID as a fallback.
    """

    query = """
        SELECT
            COALESCE(
                NULLIF(TRIM(Restaurant_Name), ''),
                NULLIF(TRIM(CAST(Restaurant_ID AS CHAR)), ''),
                'Unknown restaurant'
            ) AS Restaurant_Name,

            MIN(Restaurant_ID) AS Restaurant_ID,

            COUNT(
                CASE
                    WHEN Restaurant_Rating BETWEEN 1 AND 5
                    THEN 1
                END
            ) AS Number_of_Ratings,

            ROUND(
                AVG(
                    CASE
                        WHEN Restaurant_Rating BETWEEN 1 AND 5
                        THEN Restaurant_Rating
                    END
                ),
                2
            ) AS Average_Restaurant_Rating,

            COUNT(*) AS Total_Orders

        FROM food_delivery_data

        WHERE Restaurant_Name IS NOT NULL
           OR Restaurant_ID IS NOT NULL

        GROUP BY COALESCE(
            NULLIF(TRIM(Restaurant_Name), ''),
            NULLIF(TRIM(CAST(Restaurant_ID AS CHAR)), ''),
            'Unknown restaurant'
        )

        HAVING COUNT(
            CASE
                WHEN Restaurant_Rating BETWEEN 1 AND 5
                THEN 1
            END
        ) >= 1

        ORDER BY
            Average_Restaurant_Rating DESC,
            Number_of_Ratings DESC

        LIMIT 20
    """

    columns = [
        "Restaurant_Name",
        "Restaurant_ID",
        "Number_of_Ratings",
        "Average_Restaurant_Rating",
        "Total_Orders"
    ]

    df = run_query(query)
    df = save_report(df, "top_rated_restaurants.csv", columns)
    print_summary("10. TOP-RATED RESTAURANTS", df)

    if df.empty:
        save_no_data_graph(
            "top_rated_restaurants.png",
            "Top-Rated Restaurants",
            "No valid restaurant ratings are available."
        )
        return df

    plot_df = df.sort_values("Average_Restaurant_Rating")
    labels = restaurant_label(plot_df)

    plt.figure(figsize=(12, max(6, len(plot_df) * 0.35)))
    plt.barh(labels, plot_df["Average_Restaurant_Rating"])
    plt.xlabel("Average Restaurant Rating (1–5)")
    plt.ylabel("Restaurant")
    plt.title("Top 20 Rated Restaurants")
    plt.xlim(0, 5)
    plt.grid(axis="x", linestyle="--", alpha=0.4)

    save_graph("top_rated_restaurants.png")
    return df


# ============================================================
# 11. CANCELLATION RATE BY RESTAURANT
# ============================================================

def analyze_cancellation_rate_by_restaurant():
    """
    Calculate cancellation rate per restaurant.
    Includes restaurants with at least one eligible order.
    Only Delivered and Cancelled orders are included.
    """

    query = """
        SELECT
            COALESCE(
                NULLIF(TRIM(Restaurant_Name), ''),
                NULLIF(TRIM(CAST(Restaurant_ID AS CHAR)), ''),
                'Unknown restaurant'
            ) AS Restaurant_Name,

            MIN(Restaurant_ID) AS Restaurant_ID,

            COUNT(*) AS Total_Orders,

            SUM(
                CASE
                    WHEN Order_Status = 'Cancelled' THEN 1
                    ELSE 0
                END
            ) AS Cancelled_Orders,

            SUM(
                CASE
                    WHEN Order_Status = 'Delivered' THEN 1
                    ELSE 0
                END
            ) AS Delivered_Orders,

            ROUND(
                100.0 * SUM(
                    CASE
                        WHEN Order_Status = 'Cancelled' THEN 1
                        ELSE 0
                    END
                ) / NULLIF(COUNT(*), 0),
                2
            ) AS Cancellation_Rate_Percent

        FROM food_delivery_data

        WHERE Order_Status IN ('Delivered', 'Cancelled')
          AND (
              Restaurant_Name IS NOT NULL
              OR Restaurant_ID IS NOT NULL
          )

        GROUP BY COALESCE(
            NULLIF(TRIM(Restaurant_Name), ''),
            NULLIF(TRIM(CAST(Restaurant_ID AS CHAR)), ''),
            'Unknown restaurant'
        )

        ORDER BY
            Cancellation_Rate_Percent DESC,
            Total_Orders DESC
    """

    columns = [
        "Restaurant_Name",
        "Restaurant_ID",
        "Total_Orders",
        "Cancelled_Orders",
        "Delivered_Orders",
        "Cancellation_Rate_Percent"
    ]

    df = run_query(query)
    df = save_report(
        df, "cancellation_rate_by_restaurant.csv", columns
    )
    print_summary("11. CANCELLATION RATE BY RESTAURANT", df)

    if df.empty:
        save_no_data_graph(
            "cancellation_rate_by_restaurant.png",
            "Cancellation Rate by Restaurant",
            "No eligible restaurant orders are available."
        )
        return df

    # Show the 15 restaurants with the highest cancellation rates.
    plot_df = (
        df.nlargest(15, "Cancellation_Rate_Percent")
        .sort_values("Cancellation_Rate_Percent")
    )

    labels = restaurant_label(plot_df)

    plt.figure(figsize=(12, max(6, len(plot_df) * 0.4)))
    plt.barh(labels, plot_df["Cancellation_Rate_Percent"])
    plt.xlabel("Cancellation Rate (%)")
    plt.ylabel("Restaurant")
    plt.title("Restaurants with Highest Cancellation Rates")
    plt.grid(axis="x", linestyle="--", alpha=0.4)

    save_graph("cancellation_rate_by_restaurant.png")
    return df


# ============================================================
# 12. CUISINE-WISE PERFORMANCE
# ============================================================

def analyze_cuisine_wise_performance():
    """Compare cuisine order volume, revenue, ratings and delivery time."""

    query = """
        SELECT
            Cuisine_Type,

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
                        THEN COALESCE(Final_Amount, 0)
                        ELSE 0
                    END
                ),
                2
            ) AS Delivered_Revenue,

            ROUND(
                AVG(
                    CASE
                        WHEN Restaurant_Rating BETWEEN 1 AND 5
                        THEN Restaurant_Rating
                    END
                ),
                2
            ) AS Average_Restaurant_Rating,

            ROUND(
                AVG(
                    CASE
                        WHEN Order_Status = 'Delivered'
                         AND Delivery_Time_Min > 0
                        THEN Delivery_Time_Min
                    END
                ),
                2
            ) AS Average_Delivery_Time_Min

        FROM food_delivery_data

        WHERE Cuisine_Type IS NOT NULL
          AND TRIM(Cuisine_Type) <> ''
          AND Order_Status IN ('Delivered', 'Cancelled')

        GROUP BY Cuisine_Type
        ORDER BY Delivered_Revenue DESC
    """

    columns = [
        "Cuisine_Type",
        "Total_Orders",
        "Delivered_Orders",
        "Cancelled_Orders",
        "Cancellation_Rate_Percent",
        "Delivered_Revenue",
        "Average_Restaurant_Rating",
        "Average_Delivery_Time_Min"
    ]

    df = run_query(query)
    df = save_report(df, "cuisine_wise_performance.csv", columns)
    print_summary("12. CUISINE-WISE PERFORMANCE", df)

    # --------------------------------------------------------
    # Graph 1: Delivered revenue by cuisine
    # --------------------------------------------------------

    if df.empty:
        save_no_data_graph(
            "cuisine_wise_delivered_revenue.png",
            "Delivered Revenue by Cuisine",
            "No cuisine revenue data is available."
        )
    else:
        plot_df = df.sort_values("Delivered_Revenue")

        plt.figure(figsize=(11, max(6, len(plot_df) * 0.4)))
        plt.barh(
            plot_df["Cuisine_Type"].astype(str),
            plot_df["Delivered_Revenue"]
        )
        plt.xlabel("Delivered Revenue")
        plt.ylabel("Cuisine")
        plt.title("Delivered Revenue by Cuisine")
        plt.grid(axis="x", linestyle="--", alpha=0.4)

        save_graph("cuisine_wise_delivered_revenue.png")

    # --------------------------------------------------------
    # Graph 2: Cancellation rate by cuisine
    # --------------------------------------------------------

    if df.empty:
        save_no_data_graph(
            "cuisine_wise_cancellation_rate.png",
            "Cancellation Rate by Cuisine",
            "No cuisine cancellation data is available."
        )
    else:
        plot_df = df.sort_values("Cancellation_Rate_Percent")

        plt.figure(figsize=(11, max(6, len(plot_df) * 0.4)))
        plt.barh(
            plot_df["Cuisine_Type"].astype(str),
            plot_df["Cancellation_Rate_Percent"]
        )
        plt.xlabel("Cancellation Rate (%)")
        plt.ylabel("Cuisine")
        plt.title("Cancellation Rate by Cuisine")
        plt.grid(axis="x", linestyle="--", alpha=0.4)

        save_graph("cuisine_wise_cancellation_rate.png")

    # --------------------------------------------------------
    # Graph 3: Average restaurant rating by cuisine
    # --------------------------------------------------------

    rating_df = df.dropna(
        subset=["Average_Restaurant_Rating"]
    ).copy() if not df.empty else pd.DataFrame()

    if rating_df.empty:
        save_no_data_graph(
            "cuisine_wise_average_rating.png",
            "Average Restaurant Rating by Cuisine",
            "No valid restaurant ratings are available."
        )
    else:
        rating_df = rating_df.sort_values(
            "Average_Restaurant_Rating"
        )

        plt.figure(figsize=(11, max(6, len(rating_df) * 0.4)))
        plt.barh(
            rating_df["Cuisine_Type"].astype(str),
            rating_df["Average_Restaurant_Rating"]
        )
        plt.xlabel("Average Restaurant Rating (1–5)")
        plt.ylabel("Cuisine")
        plt.title("Average Restaurant Rating by Cuisine")
        plt.xlim(0, 5)
        plt.grid(axis="x", linestyle="--", alpha=0.4)

        save_graph("cuisine_wise_average_rating.png")

    return df


# ============================================================
# RUN ALL RESTAURANT PERFORMANCE ANALYSES
# ============================================================

def run_restaurant_performance_analysis():
    """Run restaurant analyses 10, 11 and 12."""

    print("\n" + "#" * 85)
    print("RESTAURANT PERFORMANCE ANALYSIS")
    print("#" * 85)

    analyses = [
        ("Top-rated restaurants", analyze_top_rated_restaurants),
        ("Cancellation rate by restaurant",
         analyze_cancellation_rate_by_restaurant),
        ("Cuisine-wise performance", analyze_cuisine_wise_performance)
    ]

    failures = []

    for name, analysis_function in analyses:
        try:
            analysis_function()
        except Exception as error:
            failures.append((name, str(error)))
            print(f"\nERROR in {name}: {error}")

    print("\n" + "#" * 85)
    print("RESTAURANT PERFORMANCE ANALYSIS FINISHED")
    print("#" * 85)

    if failures:
        print("\nAnalyses with errors:")
        for name, error in failures:
            print(f"- {name}: {error}")
    else:
        print("All restaurant analyses completed without errors.")


if __name__ == "__main__":
    run_restaurant_performance_analysis()