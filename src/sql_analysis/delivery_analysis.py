
# ============================================================
# DELIVERY PERFORMANCE ANALYSIS
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

REPORT_DIR = PROJECT_ROOT / "output" / "sql_analysis" / "reports" / "delivery"
GRAPH_DIR = PROJECT_ROOT / "output" / "sql_analysis" / "graphs" / "delivery"

REPORT_DIR.mkdir(parents=True, exist_ok=True)
GRAPH_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# DATABASE CONNECTION AND REUSABLE FUNCTIONS
# ============================================================

def run_query(query):
    """Execute a SQL query and return the result as a DataFrame."""
    engine = create_db_engine()

    try:
        with engine.connect() as connection:
            return pd.read_sql_query(text(query), connection)
    finally:
        engine.dispose()


def save_report(df, filename):
    """Save an analysis DataFrame as a CSV report."""
    output_path = REPORT_DIR / filename
    df.to_csv(output_path, index=False)
    print(f"Report saved: {output_path}")
    return output_path


def save_graph(filename):
    """Save the current Matplotlib figure."""
    output_path = GRAPH_DIR / filename
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Graph saved: {output_path}")


def print_summary(title, df):
    """Print a readable analysis summary."""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

    if df.empty:
        print("No records available for this analysis.")
    else:
        print(df.to_string(index=False))


# ============================================================
# 7. AVERAGE DELIVERY TIME BY CITY
# ============================================================

def analyze_average_delivery_time_by_city():
    """
    Compare average delivery time across cities.
    Uses delivered orders with valid delivery times.
    Cities with fewer than 100 qualifying orders are excluded.
    """

    query = """
        SELECT
            City,
            COUNT(*) AS Delivered_Orders,
            ROUND(AVG(Delivery_Time_Min), 2)
                AS Average_Delivery_Time_Min,
            ROUND(MIN(Delivery_Time_Min), 2)
                AS Minimum_Delivery_Time_Min,
            ROUND(MAX(Delivery_Time_Min), 2)
                AS Maximum_Delivery_Time_Min
        FROM food_delivery_data
        WHERE Order_Status = 'Delivered'
          AND City IS NOT NULL
          AND TRIM(City) <> ''
          AND Delivery_Time_Min IS NOT NULL
          AND Delivery_Time_Min > 0
        GROUP BY City
        HAVING COUNT(*) >= 100
        ORDER BY Average_Delivery_Time_Min DESC
    """

    df = run_query(query)

    print_summary("7. AVERAGE DELIVERY TIME BY CITY", df)

    if df.empty:
        print("No eligible city data found.")
        return df

    save_report(df, "average_delivery_time_by_city.csv")

    # Plot cities from slowest to fastest.
    plot_df = df.sort_values(
        "Average_Delivery_Time_Min",
        ascending=True
    )

    plt.figure(figsize=(12, max(6, len(plot_df) * 0.35)))

    plt.barh(
        plot_df["City"].astype(str),
        plot_df["Average_Delivery_Time_Min"]
    )

    plt.xlabel("Average Delivery Time (minutes)")
    plt.ylabel("City")
    plt.title("Average Delivery Time by City")
    plt.grid(axis="x", linestyle="--", alpha=0.4)

    save_graph("average_delivery_time_by_city.png")

    print("\nInterpretation:")
    print("Cities at the top of the CSV report have longer average delivery times.")
    print("Compare order counts before drawing conclusions about each city.")

    return df


# ============================================================
# 8. DISTANCE VS DELIVERY TIME / POTENTIAL DELAY
# ============================================================

def analyze_distance_vs_delivery_time():
    """
    Investigate the relationship between delivery distance
    and actual delivery time.

    Note:
    The dataset does not contain a promised delivery time or
    expected delivery time column. Therefore, this analysis
    measures actual delivery duration, not confirmed lateness.
    """

    query = """
        SELECT
            Distance_km,
            Delivery_Time_Min,
            City,
            Order_Status
        FROM food_delivery_data
        WHERE Order_Status = 'Delivered'
          AND Distance_km IS NOT NULL
          AND Distance_km >= 0
          AND Delivery_Time_Min IS NOT NULL
          AND Delivery_Time_Min > 0
    """

    df = run_query(query)

    print("\n" + "=" * 80)
    print("8. DISTANCE VS DELIVERY TIME")
    print("=" * 80)

    if df.empty:
        print("No eligible delivery records found.")
        return df

    # Ensure numeric values.
    df["Distance_km"] = pd.to_numeric(
        df["Distance_km"], errors="coerce"
    )
    df["Delivery_Time_Min"] = pd.to_numeric(
        df["Delivery_Time_Min"], errors="coerce"
    )

    df = df.dropna(
        subset=["Distance_km", "Delivery_Time_Min"]
    )

    # Correlation between distance and actual delivery duration.
    correlation = df["Distance_km"].corr(
        df["Delivery_Time_Min"]
    )

    print(f"Valid delivered orders: {len(df):,}")
    print(f"Distance-time correlation: {correlation:.3f}")

    if pd.isna(correlation):
        print("Correlation could not be calculated.")
    elif correlation > 0.5:
        print("Interpretation: Strong positive linear relationship.")
    elif correlation > 0.3:
        print("Interpretation: Moderate positive linear relationship.")
    elif correlation > 0:
        print("Interpretation: Weak positive linear relationship.")
    elif correlation < -0.3:
        print("Interpretation: Negative relationship.")
    else:
        print("Interpretation: Little or no linear relationship.")

    # --------------------------------------------------------
    # Group delivery distances into understandable categories.
    # --------------------------------------------------------

    distance_bins = [-0.001, 2, 5, 10, float("inf")]
    distance_labels = [
        "0–2 km",
        "2–5 km",
        "5–10 km",
        "Above 10 km"
    ]

    df["Distance_Category"] = pd.cut(
        df["Distance_km"],
        bins=distance_bins,
        labels=distance_labels,
        right=True,
        include_lowest=True
    )

    grouped = (
        df.groupby("Distance_Category", observed=False)
        .agg(
            Delivered_Orders=("Delivery_Time_Min", "count"),
            Average_Distance_km=("Distance_km", "mean"),
            Average_Delivery_Time_Min=("Delivery_Time_Min", "mean"),
            Median_Delivery_Time_Min=("Delivery_Time_Min", "median")
        )
        .reset_index()
    )

    numeric_columns = [
        "Average_Distance_km",
        "Average_Delivery_Time_Min",
        "Median_Delivery_Time_Min"
    ]

    grouped[numeric_columns] = grouped[numeric_columns].round(2)

    print_summary("DELIVERY TIME BY DISTANCE CATEGORY", grouped)

    save_report(
        grouped,
        "distance_vs_delivery_time.csv"
    )

    # --------------------------------------------------------
    # Graph 1: Distance vs delivery duration (sampled scatter).
    # --------------------------------------------------------

    plot_df = df.sample(
        n=min(len(df), 5000),
        random_state=42
    )

    plt.figure(figsize=(10, 6))

    plt.scatter(
        plot_df["Distance_km"],
        plot_df["Delivery_Time_Min"],
        alpha=0.35
    )

    plt.xlabel("Delivery Distance (km)")
    plt.ylabel("Actual Delivery Time (minutes)")
    plt.title("Delivery Distance vs Actual Delivery Time")
    plt.grid(linestyle="--", alpha=0.3)

    save_graph("distance_vs_delivery_time_scatter.png")

    # --------------------------------------------------------
    # Graph 2: Average duration by distance category.
    # --------------------------------------------------------

    chart_df = grouped.dropna(
        subset=["Average_Delivery_Time_Min"]
    )

    plt.figure(figsize=(10, 6))

    plt.bar(
        chart_df["Distance_Category"].astype(str),
        chart_df["Average_Delivery_Time_Min"]
    )

    plt.xlabel("Distance Category")
    plt.ylabel("Average Delivery Time (minutes)")
    plt.title("Average Delivery Time by Distance Category")
    plt.grid(axis="y", linestyle="--", alpha=0.4)

    save_graph("average_delivery_time_by_distance_category.png")

    return grouped


# ============================================================
# 9. DELIVERY RATING VS DELIVERY TIME
# ============================================================

def analyze_delivery_rating_vs_delivery_time():
    """
    Examine how delivery ratings vary with actual delivery time.
    Uses delivered orders with valid ratings and delivery times.
    """

    query = """
        SELECT
            Delivery_Rating,
            Delivery_Time_Min,
            City
        FROM food_delivery_data
        WHERE Order_Status = 'Delivered'
          AND Delivery_Rating IS NOT NULL
          AND Delivery_Rating BETWEEN 1 AND 5
          AND Delivery_Time_Min IS NOT NULL
          AND Delivery_Time_Min > 0
    """

    df = run_query(query)

    print("\n" + "=" * 80)
    print("9. DELIVERY RATING VS DELIVERY TIME")
    print("=" * 80)

    if df.empty:
        print("No eligible ratings and delivery times found.")
        return df

    df["Delivery_Rating"] = pd.to_numeric(
        df["Delivery_Rating"], errors="coerce"
    )
    df["Delivery_Time_Min"] = pd.to_numeric(
        df["Delivery_Time_Min"], errors="coerce"
    )

    df = df.dropna(
        subset=["Delivery_Rating", "Delivery_Time_Min"]
    )

    if df.empty:
        print("No valid numeric ratings and delivery times found.")
        return df

    # --------------------------------------------------------
    # Summary by rating.
    # --------------------------------------------------------

    grouped = (
        df.groupby("Delivery_Rating")
        .agg(
            Number_of_Orders=("Delivery_Time_Min", "count"),
            Average_Delivery_Time_Min=("Delivery_Time_Min", "mean"),
            Median_Delivery_Time_Min=("Delivery_Time_Min", "median"),
            Minimum_Delivery_Time_Min=("Delivery_Time_Min", "min"),
            Maximum_Delivery_Time_Min=("Delivery_Time_Min", "max")
        )
        .reset_index()
        .sort_values("Delivery_Rating")
    )

    time_columns = [
        "Average_Delivery_Time_Min",
        "Median_Delivery_Time_Min",
        "Minimum_Delivery_Time_Min",
        "Maximum_Delivery_Time_Min"
    ]

    grouped[time_columns] = grouped[time_columns].round(2)

    print_summary("DELIVERY TIME BY CUSTOMER RATING", grouped)

    save_report(
        grouped,
        "delivery_rating_vs_delivery_time.csv"
    )

    # --------------------------------------------------------
    # Correlation between rating and delivery time.
    # --------------------------------------------------------

    correlation = df["Delivery_Rating"].corr(
        df["Delivery_Time_Min"],
        method="spearman"
    )

    print(
        "\nSpearman correlation between rating and delivery time: "
        f"{correlation:.3f}"
    )

    if pd.isna(correlation):
        print("Correlation could not be calculated.")
    elif correlation < -0.3:
        print(
            "Interpretation: Longer delivery times tend to be "
            "associated with lower ratings."
        )
    elif correlation > 0.3:
        print(
            "Interpretation: Longer delivery times tend to be "
            "associated with higher ratings."
        )
    else:
        print(
            "Interpretation: The rating-time association is weak "
            "or limited in this dataset."
        )

    # --------------------------------------------------------
    # Graph 1: Average delivery time for each rating.
    # --------------------------------------------------------

    plt.figure(figsize=(9, 6))

    plt.bar(
        grouped["Delivery_Rating"].astype(str),
        grouped["Average_Delivery_Time_Min"]
    )

    plt.xlabel("Delivery Rating")
    plt.ylabel("Average Delivery Time (minutes)")
    plt.title("Average Delivery Time by Delivery Rating")
    plt.grid(axis="y", linestyle="--", alpha=0.4)

    save_graph("average_delivery_time_by_rating.png")

    # --------------------------------------------------------
    # Graph 2: Delivery time distribution by rating.
    # --------------------------------------------------------

    ratings = sorted(df["Delivery_Rating"].unique())

    boxplot_data = [
        df.loc[
            df["Delivery_Rating"] == rating,
            "Delivery_Time_Min"
        ].values
        for rating in ratings
    ]

    plt.figure(figsize=(10, 6))

    plt.boxplot(
        boxplot_data,
        tick_labels=[str(rating) for rating in ratings],
        showfliers=False
    )

    plt.xlabel("Delivery Rating")
    plt.ylabel("Delivery Time (minutes)")
    plt.title("Delivery Time Distribution by Rating")
    plt.grid(axis="y", linestyle="--", alpha=0.4)

    save_graph("delivery_time_distribution_by_rating.png")

    return grouped


# ============================================================
# RUN ALL DELIVERY PERFORMANCE ANALYSES
# ============================================================

def run_delivery_performance_analysis():
    """Run analyses 7, 8, and 9."""

    print("\n" + "#" * 80)
    print("DELIVERY PERFORMANCE ANALYSIS")
    print("#" * 80)

    analyze_average_delivery_time_by_city()
    analyze_distance_vs_delivery_time()
    analyze_delivery_rating_vs_delivery_time()

    print("\n" + "#" * 80)
    print("DELIVERY PERFORMANCE ANALYSIS COMPLETED")
    print("#" * 80)


if __name__ == "__main__":
    run_delivery_performance_analysis()
