
# ============================================================
# KPI ANALYSIS
# PROJECT: ONLINE FOOD DELIVERY ANALYSIS
# File: data_analysis/business_insights/kpi_analysis.py
# ============================================================

import pandas as pd
from pathlib import Path


# ============================================================
# 1. PATH CONFIGURATION
# ============================================================

# Assumes this file is inside:
# src/data_analysis/business_insights/

PROJECT_DIR = Path(__file__).resolve().parents[2]

REPORT_DIR = (
    PROJECT_DIR
    / "output"
    / "reports"
    / "business_insights"
)

REPORT_DIR.mkdir(parents=True, exist_ok=True)

KPI_FILE = REPORT_DIR / "business_kpi_summary.csv"


# ============================================================
# 2. REUSABLE HELPER FUNCTIONS
# ============================================================

def get_numeric_series(df, column):
    """
    Convert a column to numeric and return valid values.
    Missing columns return an empty Series.
    """
    if column not in df.columns:
        return pd.Series(dtype="float64")

    return pd.to_numeric(
        df[column], errors="coerce"
    ).dropna()


def format_count(value):
    """Format counts as integers with thousands separators."""
    if value is None or pd.isna(value):
        return "N/A"

    return f"{int(value):,}"


def format_decimal(value):
    """Format numeric metrics to two decimal places."""
    if value is None or pd.isna(value):
        return "N/A"

    return f"{value:,.2f}"


def format_percentage(value):
    """Format percentage metrics with a percent symbol."""
    if value is None or pd.isna(value):
        return "N/A"

    return f"{value:.2f}%"


def calculate_percentage(numerator, denominator):
    """Calculate a percentage without division-by-zero errors."""
    if denominator == 0:
        return 0.0

    return (numerator / denominator) * 100


def get_status_counts(df):
    """Normalize status text and calculate order counts."""
    if "Order_Status" not in df.columns:
        return pd.Series(dtype="int64")

    status = (
        df["Order_Status"]
        .astype("string")
        .str.strip()
        .str.title()
    )

    return status.value_counts(dropna=True)


# ============================================================
# 3. MAIN KPI FUNCTION
# ============================================================

def kpi_analysis(df):
    """
    Calculate key business KPIs.

    Parameters
    ----------
    df : pandas.DataFrame
        Already-loaded, cleaned food delivery dataset.

    Returns
    -------
    report_text : str
        Formatted KPI report.
    kpis : dict
        KPI values for use in other report sections.

    Notes
    -----
    This function does not load the dataset and does not print
    the report. The main report function handles final printing.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame.")

    total_records = len(df)

    # --------------------------------------------------------
    # Order status KPIs
    # --------------------------------------------------------

    status_counts = get_status_counts(df)

    delivered_orders = int(status_counts.get("Delivered", 0))
    cancelled_orders = int(status_counts.get("Cancelled", 0))

    other_or_missing_status = (
        total_records - delivered_orders - cancelled_orders
    )

    delivery_rate = calculate_percentage(
        delivered_orders, total_records
    )

    cancellation_rate = calculate_percentage(
        cancelled_orders, total_records
    )

    # --------------------------------------------------------
    # Order ID quality KPIs
    # --------------------------------------------------------

    if "Order_ID" in df.columns:
        unique_order_ids = int(df["Order_ID"].nunique())
        duplicate_order_id_rows = int(
            df["Order_ID"].duplicated().sum()
        )
    else:
        unique_order_ids = None
        duplicate_order_id_rows = None

    # --------------------------------------------------------
    # Order value KPIs
    # --------------------------------------------------------

    order_values = get_numeric_series(df, "Order_Value")

    average_order_value = (
        order_values.mean() if not order_values.empty else None
    )

    median_order_value = (
        order_values.median() if not order_values.empty else None
    )

    observed_order_value_total = (
        order_values.sum() if not order_values.empty else None
    )

    # --------------------------------------------------------
    # Final amount KPIs
    # --------------------------------------------------------

    final_amounts = get_numeric_series(df, "Final_Amount")

    average_final_amount = (
        final_amounts.mean() if not final_amounts.empty else None
    )

    observed_final_amount_total = (
        final_amounts.sum() if not final_amounts.empty else None
    )

    # --------------------------------------------------------
    # Delivery time KPIs
    # --------------------------------------------------------

    delivery_times = get_numeric_series(df, "Delivery_Time")

    # Exclude negative delivery times from these metrics.
    delivery_times = delivery_times[delivery_times >= 0]

    average_delivery_time = (
        delivery_times.mean()
        if not delivery_times.empty else None
    )

    median_delivery_time = (
        delivery_times.median()
        if not delivery_times.empty else None
    )

    # --------------------------------------------------------
    # Distance KPIs
    # --------------------------------------------------------

    distances = get_numeric_series(df, "Distance")

    # Exclude negative distances from these metrics.
    distances = distances[distances >= 0]

    average_distance = (
        distances.mean() if not distances.empty else None
    )

    # --------------------------------------------------------
    # Category counts
    # --------------------------------------------------------

    def unique_count(column):
        if column not in df.columns:
            return None

        return int(df[column].nunique(dropna=True))

    # --------------------------------------------------------
    # Consolidated KPI dictionary
    # --------------------------------------------------------

    kpis = {
        "Total_Records": total_records,
        "Unique_Order_IDs": unique_order_ids,
        "Duplicate_Order_ID_Rows": duplicate_order_id_rows,

        "Delivered_Orders": delivered_orders,
        "Cancelled_Orders": cancelled_orders,
        "Other_or_Missing_Status_Orders": other_or_missing_status,

        "Delivery_Rate_Percent": delivery_rate,
        "Cancellation_Rate_Percent": cancellation_rate,

        "Available_Order_Value_Records": len(order_values),
        "Missing_Order_Value_Records": (
            total_records - len(order_values)
        ),
        "Average_Order_Value": average_order_value,
        "Median_Order_Value": median_order_value,
        "Observed_Order_Value_Total": observed_order_value_total,

        "Available_Final_Amount_Records": len(final_amounts),
        "Missing_Final_Amount_Records": (
            total_records - len(final_amounts)
        ),
        "Average_Final_Amount": average_final_amount,
        "Observed_Final_Amount_Total": observed_final_amount_total,

        "Valid_Delivery_Time_Records": len(delivery_times),
        "Average_Delivery_Time_Min": average_delivery_time,
        "Median_Delivery_Time_Min": median_delivery_time,

        "Valid_Distance_Records": len(distances),
        "Average_Distance_km": average_distance,

        "Unique_City_Count": unique_count("City"),
        "Unique_Cuisine_Type_Count": unique_count("Cuisine_Type"),
        "Unique_Payment_Mode_Count": unique_count("Payment_Mode"),
    }

    # --------------------------------------------------------
    # Format the KPI report
    # --------------------------------------------------------

    count_keys = {
        "Total_Records",
        "Unique_Order_IDs",
        "Duplicate_Order_ID_Rows",
        "Delivered_Orders",
        "Cancelled_Orders",
        "Other_or_Missing_Status_Orders",
        "Available_Order_Value_Records",
        "Missing_Order_Value_Records",
        "Available_Final_Amount_Records",
        "Missing_Final_Amount_Records",
        "Valid_Delivery_Time_Records",
        "Valid_Distance_Records",
        "Unique_City_Count",
        "Unique_Cuisine_Type_Count",
        "Unique_Payment_Mode_Count",
    }

    percentage_keys = {
        "Delivery_Rate_Percent",
        "Cancellation_Rate_Percent",
    }

    report_lines = [
        "=" * 65,
        "4. KPI ANALYSIS",
        "=" * 65,
        "",
    ]

    for key, value in kpis.items():

        # Convert key names into readable labels.
        label = key.replace("_", " ")

        if key in count_keys:
            formatted_value = format_count(value)

        elif key in percentage_keys:
            formatted_value = format_percentage(value)

        else:
            formatted_value = format_decimal(value)

        report_lines.append(
            f"{label}: {formatted_value}"
        )

    report_text = "\n".join(report_lines)

    # --------------------------------------------------------
    # Save KPI values as a CSV file
    # --------------------------------------------------------

    kpi_df = pd.DataFrame(
        list(kpis.items()),
        columns=["KPI", "Value"]
    )

    kpi_df.to_csv(KPI_FILE, index=False)

    # IMPORTANT:
    # Do not print(report_text) here.
    # The main report function should print the full report once.

    return report_text, kpis
