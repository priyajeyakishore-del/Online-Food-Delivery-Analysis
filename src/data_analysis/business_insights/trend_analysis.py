
# ============================================================
# TREND ANALYSIS
# PROJECT: ONLINE FOOD DELIVERY ANALYSIS
# File: data_analysis/business_insights/trend_analysis.py
# ============================================================

import pandas as pd


# ============================================================
# 1. REUSABLE HELPER FUNCTIONS
# ============================================================

def get_numeric_series(df, column):
    """Convert a column to numeric and return valid values."""
    if column not in df.columns:
        return pd.Series(dtype="float64")

    return pd.to_numeric(
        df[column], errors="coerce"
    ).dropna()


def format_number(value, decimals=2):
    """Format numeric values consistently."""
    if value is None or pd.isna(value):
        return "N/A"

    return f"{value:,.{decimals}f}"


def percentage(part, total):
    """Calculate percentage safely."""
    if total == 0:
        return 0.0

    return part / total * 100


# ============================================================
# 2. TREND ANALYSIS FUNCTION
# ============================================================

def trend_analysis(df):
    """
    Generate time-based business trends.

    Parameters
    ----------
    df : pandas.DataFrame
        Already-loaded food delivery dataset.

    Returns
    -------
    str
        Formatted trend analysis report.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame.")

    if df.empty:
        return (
            "=" * 65
            + "\n5. TREND ANALYSIS\n"
            + "=" * 65
            + "\nNo trends available because the dataset is empty."
        )

    lines = [
        "=" * 65,
        "5. TREND ANALYSIS",
        "=" * 65,
        "",
    ]

    # --------------------------------------------------------
    # 1. Prepare order dates
    # --------------------------------------------------------

    if "Order_Date" not in df.columns:
        lines.append(
            "Order_Date column is unavailable. "
            "Time-based trend analysis cannot be performed."
        )
        return "\n".join(lines)

    work_df = df.copy()

    work_df["_Order_Date"] = pd.to_datetime(
        work_df["Order_Date"], errors="coerce"
    )

    valid_dates = work_df["_Order_Date"].notna().sum()

    lines.append("1. DATE COVERAGE")
    lines.append(f"   Total records: {len(work_df):,}")
    lines.append(f"   Valid order dates: {valid_dates:,}")
    lines.append(
        f"   Invalid or missing dates: {len(work_df) - valid_dates:,}"
    )

    work_df = work_df.dropna(subset=["_Order_Date"]).copy()

    if work_df.empty:
        lines.extend([
            "",
            "No valid order dates are available for trend analysis.",
        ])
        return "\n".join(lines)

    # --------------------------------------------------------
    # 2. Monthly order volume
    # --------------------------------------------------------

    lines.append("\n2. MONTHLY ORDER VOLUME")

    work_df["_Month"] = (
        work_df["_Order_Date"].dt.to_period("M")
    )

    monthly_orders = work_df.groupby("_Month").size()

    if not monthly_orders.empty:
        busiest_month = monthly_orders.idxmax()
        quietest_month = monthly_orders.idxmin()

        lines.append(
            f"   Busiest month: {busiest_month} "
            f"({monthly_orders.max():,} records)."
        )

        lines.append(
            f"   Lowest-volume month: {quietest_month} "
            f"({monthly_orders.min():,} records)."
        )

        lines.append(
            f"   Average monthly order volume: "
            f"{monthly_orders.mean():,.2f} records."
        )

        lines.append("\n   Monthly order counts:")

        for month, count in monthly_orders.items():
            lines.append(f"   - {month}: {count:,}")

    # --------------------------------------------------------
    # 3. Monthly delivery and cancellation trends
    # --------------------------------------------------------

    lines.append("\n3. MONTHLY DELIVERY AND CANCELLATION TRENDS")

    if "Order_Status" in work_df.columns:
        work_df["_Status"] = (
            work_df["Order_Status"]
            .astype("string")
            .str.strip()
            .str.title()
        )

        monthly_status = pd.crosstab(
            work_df["_Month"],
            work_df["_Status"]
        )

        monthly_delivered = (
            monthly_status["Delivered"]
            if "Delivered" in monthly_status.columns
            else pd.Series(0, index=monthly_status.index)
        )

        monthly_cancelled = (
            monthly_status["Cancelled"]
            if "Cancelled" in monthly_status.columns
            else pd.Series(0, index=monthly_status.index)
        )

        monthly_classified = monthly_delivered + monthly_cancelled

        monthly_cancellation_rate = (
            monthly_cancelled
            .div(monthly_classified.where(monthly_classified != 0))
            * 100
        )

        if not monthly_cancellation_rate.dropna().empty:
            highest_cancel_month = (
                monthly_cancellation_rate.dropna().idxmax()
            )

            highest_cancel_rate = (
                monthly_cancellation_rate.loc[highest_cancel_month]
            )

            lines.append(
                f"   Highest monthly cancellation rate: "
                f"{highest_cancel_month} "
                f"({highest_cancel_rate:.2f}%)."
            )

        lines.append(
            "   Monthly cancellation rate uses only records classified "
            "as Delivered or Cancelled."
        )

        lines.append("\n   Monthly status summary:")

        for month in monthly_status.index:
            delivered = int(monthly_delivered.loc[month])
            cancelled = int(monthly_cancelled.loc[month])

            lines.append(
                f"   - {month}: Delivered={delivered:,}, "
                f"Cancelled={cancelled:,}"
            )
    else:
        lines.append("   Order_Status column is unavailable.")

    # --------------------------------------------------------
    # 4. Monthly order value trend
    # --------------------------------------------------------

    lines.append("\n4. MONTHLY ORDER VALUE TREND")

    if "Order_Value" in work_df.columns:
        work_df["_Order_Value"] = pd.to_numeric(
            work_df["Order_Value"], errors="coerce"
        )

        monthly_value = (
            work_df.dropna(subset=["_Order_Value"])
            .groupby("_Month")["_Order_Value"]
            .mean()
        )

        if not monthly_value.empty:
            highest_value_month = monthly_value.idxmax()
            lowest_value_month = monthly_value.idxmin()

            lines.append(
                f"   Highest average order value month: "
                f"{highest_value_month} "
                f"({format_number(monthly_value.max())})."
            )

            lines.append(
                f"   Lowest average order value month: "
                f"{lowest_value_month} "
                f"({format_number(monthly_value.min())})."
            )

            lines.append("\n   Monthly average order value:")

            for month, value in monthly_value.items():
                lines.append(
                    f"   - {month}: {format_number(value)}"
                )
        else:
            lines.append("   No valid order values are available.")
    else:
        lines.append("   Order_Value column is unavailable.")

    # --------------------------------------------------------
    # 5. Monthly delivery time trend
    # --------------------------------------------------------

    lines.append("\n5. MONTHLY DELIVERY TIME TREND")

    if "Delivery_Time" in work_df.columns:
        work_df["_Delivery_Time"] = pd.to_numeric(
            work_df["Delivery_Time"], errors="coerce"
        )

        valid_delivery = work_df[
            work_df["_Delivery_Time"].ge(0)
        ].copy()

        monthly_delivery_time = (
            valid_delivery
            .groupby("_Month")["_Delivery_Time"]
            .mean()
        )

        if not monthly_delivery_time.empty:
            slowest_month = monthly_delivery_time.idxmax()
            fastest_month = monthly_delivery_time.idxmin()

            lines.append(
                f"   Highest average delivery time month: "
                f"{slowest_month} "
                f"({format_number(monthly_delivery_time.max())} minutes)."
            )

            lines.append(
                f"   Lowest average delivery time month: "
                f"{fastest_month} "
                f"({format_number(monthly_delivery_time.min())} minutes)."
            )

            lines.append("\n   Monthly average delivery time:")

            for month, value in monthly_delivery_time.items():
                lines.append(
                    f"   - {month}: {format_number(value)} minutes"
                )
        else:
            lines.append(
                "   No valid non-negative delivery times are available."
            )
    else:
        lines.append("   Delivery_Time column is unavailable.")

    # --------------------------------------------------------
    # 6. Trend interpretation
    # --------------------------------------------------------

    lines.extend([
        "",
        "6. INTERPRETATION",
        "   - Monthly comparisons describe records in the supplied dataset.",
        "   - Partial first or last months can have fewer orders because",
        "     they may not cover a complete calendar month.",
        "   - A trend indicates a pattern, not necessarily its cause.",
        "   - Check seasonal effects and data completeness before",
        "     making operational decisions.",
    ])

    return "\n".join(lines)
