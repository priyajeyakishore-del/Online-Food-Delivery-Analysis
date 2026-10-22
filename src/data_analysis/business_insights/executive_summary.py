
# ============================================================
# EXECUTIVE SUMMARY
# PROJECT: ONLINE FOOD DELIVERY ANALYSIS
# FILE: executive_summary.py
# ============================================================


# ============================================================
# 1. REUSABLE HELPER FUNCTION
# ============================================================

def format_value(value, decimals=2):

    if value is None:
        return "Not available"

    try:
        if value != value:  # Handles NaN
            return "Not available"
    except (TypeError, ValueError):
        pass

    if isinstance(value, (int, float)):
        return f"{value:,.{decimals}f}"

    return str(value)


# ============================================================
# 2. EXECUTIVE SUMMARY FUNCTION
# ============================================================

def executive_summary(df, kpis):

    total_records = len(df)

    delivered_orders = kpis.get("Delivered_Orders", 0)
    cancelled_orders = kpis.get("Cancelled_Orders", 0)

    delivery_rate = kpis.get("Delivery_Rate_Percent", 0)
    cancellation_rate = kpis.get("Cancellation_Rate_Percent", 0)

    lines = []

    lines.append("=" * 75)
    lines.append("1. EXECUTIVE SUMMARY")
    lines.append("=" * 75)

    lines.append(
        f"Total dataset records: {total_records:,}"
    )

    lines.append(
        f"Delivered orders: {delivered_orders:,}"
    )

    lines.append(
        f"Cancelled orders: {cancelled_orders:,}"
    )

    lines.append(
        f"Delivery rate: {format_value(delivery_rate)}%"
    )

    lines.append(
        f"Cancellation rate: {format_value(cancellation_rate)}%"
    )

    # --------------------------------------------------------
    # Delivery performance
    # --------------------------------------------------------

    if "Average_Delivery_Time_Min" in kpis:

        lines.append(
            "Average delivery time: "
            f"{format_value(kpis['Average_Delivery_Time_Min'])} minutes"
        )

    # --------------------------------------------------------
    # Order value
    # --------------------------------------------------------

    if "Average_Order_Value" in kpis:

        lines.append(
            "Average order value: "
            f"{format_value(kpis['Average_Order_Value'])}"
        )

    # --------------------------------------------------------
    # Business overview
    # --------------------------------------------------------

    lines.append("")
    lines.append("Business Overview:")

    lines.append(
        "This report summarizes order fulfillment, cancellations, "
        "delivery performance, and order-value metrics."
    )

    lines.append(
        "The findings can help identify operational patterns, "
        "prioritize further investigation, and support data-driven "
        "business decisions."
    )

    lines.append("")
    lines.append("Data Limitation:")

    lines.append(
        "Metrics are calculated from the available dataset. "
        "Missing values, duplicate records, and status definitions "
        "may affect individual results."
    )

    return "\n".join(lines)


# ============================================================
# 3. MODULE EXECUTION NOTE
# ============================================================

# This module does not load data or execute the full report.
# Import executive_summary() into business_insights_report.py.
