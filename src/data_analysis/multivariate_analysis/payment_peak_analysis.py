# ============================================================
# MULTIVARIATE ANALYSIS: PAYMENT + PEAK HOUR + DELIVERY
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

REPORT_DIR.mkdir(parents=True, exist_ok=True)
GRAPH_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# 2. REUSABLE DATA PREPARATION FUNCTION
# ============================================================

def prepare_analysis_data(df, required_cols):
    """
    Validate columns and prepare a copy of the dataset
    for multivariate analysis.
    """

    missing_cols = [
        col for col in required_cols
        if col not in df.columns
    ]

    if missing_cols:
        print("Missing required columns:", missing_cols)
        return pd.DataFrame()

    data = df[required_cols].copy()

    # Clean categorical columns
    categorical_cols = data.select_dtypes(
        include=["object", "string", "category"]
    ).columns

    for col in categorical_cols:
        data[col] = (
            data[col]
            .astype("string")
            .str.strip()
            .replace("", pd.NA)
        )

    # Standardize Peak_Hour values
    if "Peak_Hour" in data.columns:
        data["Peak_Hour"] = (
            data["Peak_Hour"]
            .astype("string")
            .str.lower()
            .replace({
                "true": "Peak",
                "false": "Non-Peak",
                "1": "Peak",
                "0": "Non-Peak"
            })
        )

    # Convert numerical columns safely
    numeric_cols = [
        "Delivery_Time_Min",
        "Distance_km",
        "Order_Value",
        "Final_Amount",
        "Discount_Applied"
    ]

    for col in numeric_cols:
        if col in data.columns:
            data[col] = pd.to_numeric(
                data[col],
                errors="coerce"
            )

    return data

# ============================================================
# 3. REUSABLE CATEGORICAL MULTIVARIATE ANALYSIS
# ============================================================

def payment_peak_status_analysis(df):
    """
    Analyze cancellation and delivery rates by
    Payment_Mode, Peak_Hour, and Order_Status.
    """

    print("\n" + "=" * 70)
    print("1. PAYMENT MODE + PEAK HOUR + ORDER STATUS")
    print("=" * 70)

    required_cols = [
        "Payment_Mode",
        "Peak_Hour",
        "Order_Status"
    ]

    data = prepare_analysis_data(df, required_cols)

    if data.empty:
        return pd.DataFrame()

    data = data.dropna(subset=required_cols)

    data = data[
        data["Order_Status"].isin(
            ["Delivered", "Cancelled"]
        )
    ].copy()

    if data.empty:
        print("No valid delivered or cancelled orders.")
        return pd.DataFrame()

    grouped = (
        data.groupby(
            [
                "Payment_Mode",
                "Peak_Hour",
                "Order_Status"
            ],
            observed=True
        )
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )

    for status in ["Delivered", "Cancelled"]:
        if status not in grouped.columns:
            grouped[status] = 0

    grouped["Total_Orders"] = (
        grouped["Delivered"] + grouped["Cancelled"]
    )

    grouped["Cancellation_Rate_Percent"] = (
        grouped["Cancelled"]
        / grouped["Total_Orders"]
        * 100
    ).round(2)

    grouped["Delivery_Rate_Percent"] = (
        grouped["Delivered"]
        / grouped["Total_Orders"]
        * 100
    ).round(2)

    grouped = grouped.sort_values(
        ["Cancellation_Rate_Percent", "Total_Orders"],
        ascending=[False, False]
    ).reset_index(drop=True)

    print("\nCancellation rates by payment and peak hour:")
    print(grouped.round(2).to_string(index=False))

    report_path = (
        REPORT_DIR / "payment_peak_status_analysis.csv"
    )

    grouped.to_csv(report_path, index=False)
    print("\nReport saved:", report_path)

    # Visualize groups with at least 100 orders
    top_groups = (
        grouped[grouped["Total_Orders"] >= 100]
        .head(15)
        .copy()
    )

    if not top_groups.empty:
        top_groups["Payment_Peak"] = (
            top_groups["Payment_Mode"].astype(str)
            + " - "
            + top_groups["Peak_Hour"].astype(str)
        )

        top_groups = top_groups.sort_values(
            "Cancellation_Rate_Percent",
            ascending=True
        )

        plt.figure(figsize=(12, 7))

        bars = plt.barh(
            top_groups["Payment_Peak"],
            top_groups["Cancellation_Rate_Percent"]
        )

        plt.bar_label(bars, fmt="%.2f%%", padding=3)
        plt.xlabel("Cancellation Rate (%)")
        plt.ylabel("Payment Mode - Peak Hour")
        plt.title(
            "Payment Mode and Peak Hour by Cancellation Rate\n"
            "(Minimum 100 Orders per Group)"
        )
        plt.tight_layout()

        graph_path = (
            GRAPH_DIR / "payment_peak_cancellation_rates.png"
        )

        plt.savefig(graph_path, dpi=300, bbox_inches="tight")
        plt.show()
        plt.close()

        print("Graph saved:", graph_path)

    return grouped

# ============================================================
# 4. PEAK HOUR + DELIVERY TIME + ORDER STATUS
# ============================================================

def peak_delivery_time_analysis(df):
    """
    Compare delivery times during peak and non-peak hours,
    separately by order status.
    """

    print("\n" + "=" * 70)
    print("2. PEAK HOUR + DELIVERY TIME + ORDER STATUS")
    print("=" * 70)

    required_cols = [
        "Peak_Hour",
        "Delivery_Time_Min",
        "Order_Status"
    ]

    data = prepare_analysis_data(df, required_cols)

    if data.empty:
        return pd.DataFrame()

    data = data.dropna(subset=required_cols)

    data = data[
        data["Order_Status"].isin(
            ["Delivered", "Cancelled"]
        )
    ].copy()

    # Delivery time must be positive to be meaningful
    data = data[data["Delivery_Time_Min"] > 0]

    if data.empty:
        print("No valid delivery-time records.")
        return pd.DataFrame()

    grouped = (
        data.groupby(
            ["Peak_Hour", "Order_Status"],
            observed=True
        )
        .agg(
            Total_Orders=("Delivery_Time_Min", "size"),
            Average_Delivery_Time_Min=(
                "Delivery_Time_Min", "mean"
            ),
            Median_Delivery_Time_Min=(
                "Delivery_Time_Min", "median"
            ),
            Minimum_Delivery_Time_Min=(
                "Delivery_Time_Min", "min"
            ),
            Maximum_Delivery_Time_Min=(
                "Delivery_Time_Min", "max"
            )
        )
        .reset_index()
        .round(2)
    )

    print("\nDelivery time summary:")
    print(grouped.to_string(index=False))

    report_path = (
        REPORT_DIR / "peak_delivery_time_analysis.csv"
    )

    grouped.to_csv(report_path, index=False)
    print("\nReport saved:", report_path)

    # Plot average delivery time
    pivot_data = grouped.pivot(
        index="Peak_Hour",
        columns="Order_Status",
        values="Average_Delivery_Time_Min"
    )

    ax = pivot_data.plot(
        kind="bar",
        figsize=(10, 6)
    )

    ax.set_xlabel("Peak Hour")
    ax.set_ylabel("Average Delivery Time (minutes)")
    ax.set_title(
        "Average Delivery Time by Peak Hour and Order Status"
    )

    plt.xticks(rotation=0)
    plt.tight_layout()

    graph_path = (
        GRAPH_DIR / "peak_delivery_time_by_status.png"
    )

    plt.savefig(graph_path, dpi=300, bbox_inches="tight")
    plt.show()
    plt.close()

    print("Graph saved:", graph_path)

    return grouped

# ============================================================
# 5. PAYMENT MODE + ORDER VALUE + PEAK HOUR
# ============================================================

def payment_order_value_analysis(df):
    """
    Compare order values by payment mode and peak hour.
    """

    print("\n" + "=" * 70)
    print("3. PAYMENT MODE + ORDER VALUE + PEAK HOUR")
    print("=" * 70)

    required_cols = [
        "Payment_Mode",
        "Order_Value",
        "Peak_Hour"
    ]

    data = prepare_analysis_data(df, required_cols)

    if data.empty:
        return pd.DataFrame()

    data = data.dropna(subset=required_cols)

    if data.empty:
        print("No valid order-value records.")
        return pd.DataFrame()

    grouped = (
        data.groupby(
            ["Payment_Mode", "Peak_Hour"],
            observed=True
        )
        .agg(
            Total_Orders=("Order_Value", "size"),
            Average_Order_Value=("Order_Value", "mean"),
            Median_Order_Value=("Order_Value", "median"),
            Minimum_Order_Value=("Order_Value", "min"),
            Maximum_Order_Value=("Order_Value", "max")
        )
        .reset_index()
        .round(2)
    )

    print("\nOrder value summary:")
    print(grouped.to_string(index=False))

    report_path = (
        REPORT_DIR / "payment_order_value_peak_analysis.csv"
    )

    grouped.to_csv(report_path, index=False)
    print("\nReport saved:", report_path)

    # Plot average order value
    pivot_data = grouped.pivot(
        index="Payment_Mode",
        columns="Peak_Hour",
        values="Average_Order_Value"
    )

    ax = pivot_data.plot(
        kind="bar",
        figsize=(11, 6)
    )

    ax.set_xlabel("Payment Mode")
    ax.set_ylabel("Average Order Value")
    ax.set_title(
        "Average Order Value by Payment Mode and Peak Hour"
    )

    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    graph_path = (
        GRAPH_DIR / "payment_order_value_peak.png"
    )

    plt.savefig(graph_path, dpi=300, bbox_inches="tight")
    plt.show()
    plt.close()

    print("Graph saved:", graph_path)

    return grouped

# ============================================================
# 6. CITY + PAYMENT MODE + PEAK HOUR
# ============================================================

def city_payment_peak_analysis(df):
    """
    Compare payment preferences across cities and peak hours.
    """

    print("\n" + "=" * 70)
    print("4. CITY + PAYMENT MODE + PEAK HOUR")
    print("=" * 70)

    required_cols = [
        "City",
        "Payment_Mode",
        "Peak_Hour"
    ]

    data = prepare_analysis_data(df, required_cols)

    if data.empty:
        return pd.DataFrame()

    data = data.dropna(subset=required_cols)

    if data.empty:
        print("No valid city-payment records.")
        return pd.DataFrame()

    grouped = (
        data.groupby(
            ["City", "Payment_Mode", "Peak_Hour"],
            observed=True
        )
        .size()
        .reset_index(name="Total_Orders")
    )

    # Calculate payment preference within each city and period
    grouped["City_Period_Total"] = (
        grouped.groupby(
            ["City", "Peak_Hour"],
            observed=True
        )["Total_Orders"]
        .transform("sum")
    )

    grouped["Payment_Percentage"] = (
        grouped["Total_Orders"]
        / grouped["City_Period_Total"]
        * 100
    ).round(2)

    grouped = grouped.sort_values(
        ["City", "Peak_Hour", "Payment_Percentage"],
        ascending=[True, True, False]
    ).reset_index(drop=True)

    print("\nPayment preferences by city and peak hour:")
    print(grouped.head(30).to_string(index=False))

    report_path = (
        REPORT_DIR / "city_payment_peak_analysis.csv"
    )

    grouped.to_csv(report_path, index=False)
    print("\nComplete report saved:", report_path)

    # Visualize the 15 largest city-payment-period groups
    top_groups = (
        grouped[grouped["Total_Orders"] >= 100]
        .nlargest(15, "Total_Orders")
        .copy()
    )

    if not top_groups.empty:
        top_groups["City_Payment_Peak"] = (
            top_groups["City"].astype(str)
            + " - "
            + top_groups["Payment_Mode"].astype(str)
            + " - "
            + top_groups["Peak_Hour"].astype(str)
        )

        top_groups = top_groups.sort_values(
            "Payment_Percentage",
            ascending=True
        )

        plt.figure(figsize=(13, 8))

        bars = plt.barh(
            top_groups["City_Payment_Peak"],
            top_groups["Payment_Percentage"]
        )

        plt.bar_label(bars, fmt="%.1f%%", padding=3)
        plt.xlabel("Payment Method Share within City and Period (%)")
        plt.ylabel("City - Payment Mode - Peak Hour")
        plt.title(
            "Payment Preferences Across Cities and Peak Hours\n"
            "(Top 15 Groups by Order Count; Minimum 100 Orders)"
        )

        plt.tight_layout()

        graph_path = (
            GRAPH_DIR / "city_payment_peak_preferences.png"
        )

        plt.savefig(graph_path, dpi=300, bbox_inches="tight")
        plt.show()
        plt.close()

        print("Graph saved:", graph_path)

    return grouped

# ============================================================
# 7. PEAK HOUR + DISTANCE + DELIVERY TIME
# ============================================================
def peak_distance_delivery_analysis(df):
    """
    Analyze how delivery distance relates to delivery time
    during peak and non-peak hours.

    Includes correlation coefficients and distance bands.
    """

    print("\n" + "=" * 70)
    print("5. PEAK HOUR + DISTANCE + DELIVERY TIME")
    print("=" * 70)

    required_cols = [
        "Peak_Hour",
        "Distance_km",
        "Delivery_Time_Min"
    ]

    data = prepare_analysis_data(df, required_cols)

    if data.empty:
        return pd.DataFrame()

    data = data.dropna(subset=required_cols)

    # Exclude non-positive distances and delivery times
    data = data[
        (data["Distance_km"] > 0)
        & (data["Delivery_Time_Min"] > 0)
    ].copy()

    if data.empty:
        print("No valid distance and delivery-time records.")
        return pd.DataFrame()

    # --------------------------------------------------------
    # 7.1 Calculate correlation by peak-hour category
    # --------------------------------------------------------

    correlation_rows = []

    for peak_hour, group in data.groupby(
        "Peak_Hour",
        observed=True
    ):
        correlation = group[
            ["Distance_km", "Delivery_Time_Min"]
        ].corr().iloc[0, 1]

        correlation_rows.append({
            "Peak_Hour": peak_hour,
            "Total_Orders": len(group),
            "Average_Distance_km": group["Distance_km"].mean(),
            "Average_Delivery_Time_Min": (
                group["Delivery_Time_Min"].mean()
            ),
            "Distance_Time_Correlation": correlation
        })

    correlation_report = pd.DataFrame(correlation_rows)

    correlation_report = correlation_report.round(3)

    print("\nDistance and delivery-time correlation:")
    print(correlation_report.to_string(index=False))

    correlation_path = (
        REPORT_DIR / "peak_distance_delivery_correlation.csv"
    )

    correlation_report.to_csv(
        correlation_path,
        index=False
    )

    print("\nCorrelation report saved:", correlation_path)

    # --------------------------------------------------------
    # 7.2 Create distance bands
    # --------------------------------------------------------

    bins = [0, 2, 5, 10, float("inf")]

    labels = [
        "0-2 km",
        "2-5 km",
        "5-10 km",
        "Above 10 km"
    ]

    data["Distance_Band"] = pd.cut(
        data["Distance_km"],
        bins=bins,
        labels=labels,
        right=True,
        include_lowest=True
    )

    distance_summary = (
        data.dropna(subset=["Distance_Band"])
        .groupby(
            ["Peak_Hour", "Distance_Band"],
            observed=True
        )
        .agg(
            Total_Orders=("Delivery_Time_Min", "size"),
            Average_Delivery_Time_Min=(
                "Delivery_Time_Min", "mean"
            ),
            Median_Delivery_Time_Min=(
                "Delivery_Time_Min", "median"
            ),
            Average_Distance_km=("Distance_km", "mean")
        )
        .reset_index()
        .round(2)
    )

    print("\nDelivery time by distance band and peak hour:")
    print(distance_summary.to_string(index=False))

    summary_path = (
        REPORT_DIR / "peak_distance_delivery_summary.csv"
    )

    distance_summary.to_csv(summary_path, index=False)

    print("\nDistance summary saved:", summary_path)

    # --------------------------------------------------------
    # 7.3 Create line chart for average delivery time
    # --------------------------------------------------------

    pivot_data = distance_summary.pivot(
        index="Distance_Band",
        columns="Peak_Hour",
        values="Average_Delivery_Time_Min"
    )

    ax = pivot_data.plot(
        kind="line",
        marker="o",
        figsize=(10, 6)
    )

    ax.set_xlabel("Delivery Distance Band")
    ax.set_ylabel("Average Delivery Time (minutes)")
    ax.set_title(
        "Delivery Distance vs Delivery Time by Peak Hour"
    )

    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()

    graph_path = (
        GRAPH_DIR / "peak_distance_delivery_time.png"
    )

    plt.savefig(graph_path, dpi=300, bbox_inches="tight")
    plt.show()
    plt.close()

    print("Graph saved:", graph_path)

    # --------------------------------------------------------
    # 7.4 Create scatter plot
    # --------------------------------------------------------

    plt.figure(figsize=(10, 6))

    for peak_hour, group in data.groupby(
        "Peak_Hour",
        observed=True
    ):
        plt.scatter(
            group["Distance_km"],
            group["Delivery_Time_Min"],
            alpha=0.35,
            label=str(peak_hour)
        )

    plt.xlabel("Delivery Distance (km)")
    plt.ylabel("Delivery Time (minutes)")
    plt.title(
        "Delivery Distance vs Delivery Time "
        "During Peak and Non-Peak Hours"
    )

    plt.legend(title="Peak Hour")
    plt.tight_layout()

    scatter_path = (
        GRAPH_DIR / "peak_distance_delivery_scatter.png"
    )

    plt.savefig(
        scatter_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()
    plt.close()

    print("Scatter plot saved:", scatter_path)

    return distance_summary

# ============================================================
# 8. MASTER FUNCTION
# ============================================================

def run_payment_peak_analysis(df):
    """
    Execute all five multivariate analyses.

    Returns:
        dict: Analysis reports indexed by analysis name.
    """

    print("\n" + "=" * 70)
    print("RUNNING ALL PAYMENT AND PEAK-HOUR ANALYSES")
    print("=" * 70)

    reports = {}

    reports["payment_peak_status"] = (
        payment_peak_status_analysis(df)
    )

    reports["peak_delivery_time"] = (
        peak_delivery_time_analysis(df)
    )

    reports["payment_order_value"] = (
        payment_order_value_analysis(df)
    )

    reports["city_payment_peak"] = (
        city_payment_peak_analysis(df)
    )

    reports["peak_distance_delivery"] = (
        peak_distance_delivery_analysis(df)
    )

    print("\n" + "=" * 70)
    print("ALL MULTIVARIATE ANALYSES COMPLETED")
    print("=" * 70)

    print("\nReports folder:", REPORT_DIR.resolve())
    print("Graphs folder:", GRAPH_DIR.resolve())

    return reports