
# ============================================================
# MULTIVARIATE ANALYSIS: CITY + CUISINE + ORDER STATUS
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================
# 1. OUTPUT DIRECTORY CONFIGURATION
# ============================================================

BASE_DIR = Path(
    r"C:\Users\Priya Jeyakishore\OneDrive\Desktop\GUVI_Data_Science_ZenClass\Online_Food_Delivery_Analysis\output"
)

REPORT_DIR = (
    BASE_DIR
    / "reports"
    / "multivariate_analysis"
)

GRAPH_DIR = (
    BASE_DIR
    / "graphs"
    / "multivariate_analysis"
)

# Create output directories if they do not exist
REPORT_DIR.mkdir(parents=True, exist_ok=True)
GRAPH_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. REUSABLE ANALYSIS FUNCTION
# ============================================================

def grouped_business_analysis(df):
    """
    Analyze cancellation rates by City, Cuisine_Type,
    and Order_Status.

    Returns:
        pd.DataFrame: Complete city-cuisine cancellation report.
    """

    print("\n" + "=" * 70)
    print("MULTIVARIATE ANALYSIS: CITY + CUISINE + ORDER STATUS")
    print("=" * 70)

    # --------------------------------------------------------
    # 2.1 Validate required columns
    # --------------------------------------------------------

    required_cols = [
        "City",
        "Cuisine_Type",
        "Order_Status"
    ]

    missing_cols = [
        col for col in required_cols
        if col not in df.columns
    ]

    if missing_cols:
        print("Missing required columns:", missing_cols)
        return pd.DataFrame()

    # --------------------------------------------------------
    # 2.2 Select required columns
    # --------------------------------------------------------

    data = df[required_cols].copy()

    # Remove records missing required grouping information
    data = data.dropna(subset=required_cols)

    # Retain only relevant order statuses
    data = data[
        data["Order_Status"].isin(
            ["Delivered", "Cancelled"]
        )
    ]

    if data.empty:
        print("No valid records available for analysis.")
        return pd.DataFrame()

    # --------------------------------------------------------
    # 2.3 Group by City, Cuisine, and Order Status
    # --------------------------------------------------------

    grouped = (
        data.groupby(
            ["City", "Cuisine_Type", "Order_Status"]
        )
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )

    # Ensure both status columns exist
    for status in ["Delivered", "Cancelled"]:
        if status not in grouped.columns:
            grouped[status] = 0

    # --------------------------------------------------------
    # 2.4 Calculate total orders and cancellation rate
    # --------------------------------------------------------

    grouped["Total_Orders"] = (
        grouped["Delivered"]
        + grouped["Cancelled"]
    )

    grouped["Cancellation_Rate_Percent"] = (
        grouped["Cancelled"]
        / grouped["Total_Orders"]
        * 100
    )

    # Rank all combinations by cancellation rate
    grouped = grouped.sort_values(
        "Cancellation_Rate_Percent",
        ascending=False
    ).reset_index(drop=True)

    # --------------------------------------------------------
    # 2.5 Display top 15 combinations
    # --------------------------------------------------------

    print("\nTop 15 city-cuisine combinations by cancellation rate:")

    print(
        grouped.head(15).round(2).to_string(index=False)
    )

    # --------------------------------------------------------
    # 2.6 Save complete CSV report
    # --------------------------------------------------------

    report_path = (
        REPORT_DIR
        / "city_cuisine_cancellation_analysis.csv"
    )

    grouped.to_csv(report_path, index=False)

    print(f"\nComplete report saved: {report_path}")

    # --------------------------------------------------------
    # 2.7 Filter groups with at least 100 orders
    #     for visualization
    # --------------------------------------------------------

    top_groups = grouped[
        grouped["Total_Orders"] >= 100
    ].head(15).copy()

    if top_groups.empty:
        print(
            "No city-cuisine combinations have "
            "at least 100 orders. Graph not generated."
        )
        return grouped

    # Prepare labels for the graph
    top_groups["City_Cuisine"] = (
        top_groups["City"].astype(str)
        + " - "
        + top_groups["Cuisine_Type"].astype(str)
    )

    # Display the highest rates at the top of the chart
    top_groups = top_groups.sort_values(
        "Cancellation_Rate_Percent",
        ascending=True
    )

    # --------------------------------------------------------
    # 2.8 Create horizontal bar chart
    # --------------------------------------------------------

    plt.figure(figsize=(12, 7))

    plt.barh(
        top_groups["City_Cuisine"],
        top_groups["Cancellation_Rate_Percent"]
    )

    plt.xlabel("Cancellation Rate (%)")
    plt.ylabel("City - Cuisine")

    plt.title(
        "Top 15 City-Cuisine Combinations "
        "by Cancellation Rate\n"
        "(Minimum 100 Orders per Combination)"
    )

    plt.tight_layout()

    # --------------------------------------------------------
    # 2.9 Save graph
    # --------------------------------------------------------

    graph_path = (
        GRAPH_DIR
        / "city_cuisine_cancellation_rates.png"
    )

    plt.savefig(
        graph_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()
    plt.close()

    print(f"Graph saved: {graph_path}")

    # --------------------------------------------------------
    # 2.10 Return complete report
    # --------------------------------------------------------

    return grouped
