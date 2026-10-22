# ============================================================
# BUSINESS IMPACT ANALYSIS
# File: business_impact.py
# Purpose: Evaluate the business impact of food delivery
#          performance, cancellations, delays, and revenue.
# ============================================================

import pandas as pd


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_numeric_column(df, column):
    """Return a numeric version of a column, or an empty Series."""
    if column not in df.columns:
        return pd.Series(dtype="float64")

    return pd.to_numeric(df[column], errors="coerce")


def format_number(value, decimals=2):
    """Format numeric values with commas."""
    if pd.isna(value):
        return "N/A"

    return f"{value:,.{decimals}f}"


def get_column_mean(df, column):
    """Calculate the mean of a numeric column."""
    values = get_numeric_column(df, column).dropna()

    if values.empty:
        return None

    return values.mean()


def get_column_sum(df, column):
    """Calculate the sum of a numeric column."""
    values = get_numeric_column(df, column).dropna()

    if values.empty:
        return None

    return values.sum()

# ============================================================
# MAIN BUSINESS IMPACT FUNCTION
# ============================================================

def business_impact(df, kpis):
    """
    Generate a business impact report.

    Parameters
    ----------
    df : pandas.DataFrame
        Already loaded and cleaned food delivery dataset.

    kpis : dict
        KPI dictionary returned by kpi_analysis(df).

    Returns
    -------
    str
        Formatted business impact report.
    """

    report = []

    report.append("=" * 75)
    report.append("8. BUSINESS IMPACT")
    report.append("=" * 75)

    # --------------------------------------------------------
    # 1. Order Fulfilment Impact
    # --------------------------------------------------------

    total_orders = kpis.get("Total_Records", len(df))
    delivered = kpis.get("Delivered_Orders", 0)
    cancelled = kpis.get("Cancelled_Orders", 0)

    delivery_rate = kpis.get("Delivery_Rate_Percent", 0)
    cancellation_rate = kpis.get("Cancellation_Rate_Percent", 0)

    report.append("\n1. ORDER FULFILMENT IMPACT")
    report.append("-" * 50)

    report.append(f"Total order records: {total_orders:,}")
    report.append(f"Successfully delivered orders: {delivered:,}")
    report.append(f"Cancelled orders: {cancelled:,}")
    report.append(f"Delivery rate: {delivery_rate:.2f}%")
    report.append(f"Cancellation rate: {cancellation_rate:.2f}%")

    if cancellation_rate >= 15:
        report.append(
            "Business impact: The cancellation rate is high enough "
            "to warrant a focused investigation into lost orders, "
            "customer dissatisfaction, and operational inefficiencies."
        )
    else:
        report.append(
            "Business impact: Continue monitoring cancellations and "
            "investigate recurring cancellation patterns."
        )

    # --------------------------------------------------------
    # 2. Order Value and Revenue Exposure
    # --------------------------------------------------------

    report.append("\n2. ORDER VALUE AND REVENUE EXPOSURE")
    report.append("-" * 50)

    average_order_value = kpis.get("Average_Order_Value")
    average_final_amount = kpis.get("Average_Final_Amount")
    observed_order_value_total = kpis.get("Observed_Order_Value_Total")
    observed_final_amount_total = kpis.get("Observed_Final_Amount_Total")

    report.append(
        "Average order value: "
        f"{format_number(average_order_value)}"
    )
    report.append(
        "Average final amount: "
        f"{format_number(average_final_amount)}"
    )
    report.append(
        "Observed order value total: "
        f"{format_number(observed_order_value_total)}"
    )
    report.append(
        "Observed final amount total: "
        f"{format_number(observed_final_amount_total)}"
    )

    report.append(
        "Business impact: Order value and final amount help assess "
        "transaction size and the value recorded after discounts. "
        "These totals should not automatically be treated as actual "
        "profit or collected revenue."
    )

    # --------------------------------------------------------
    # 3. Delivery Delay Impact
    # --------------------------------------------------------


    report.append("\n3. DELIVERY DELAY IMPACT")
    report.append("-" * 50)

    average_delivery_time = kpis.get("Average_Delivery_Time_Min")
    median_delivery_time = kpis.get("Median_Delivery_Time_Min")

    report.append(
        "Average delivery time: "
        f"{format_number(average_delivery_time)} minutes"
    )
    report.append(
        "Median delivery time: "
        f"{format_number(median_delivery_time)} minutes"
    )

    if average_delivery_time is not None:
        if average_delivery_time >= 120:
            report.append(
                "Business impact: The average delivery time is at "
                "least two hours. Review dispatching, preparation "
                "time, delivery distance, and partner allocation."
            )
        else:
            report.append(
                "Business impact: Monitor delivery times against "
                "the company's promised delivery window and service "
                "targets."
            )
    else:
        report.append(
            "Business impact: Delivery-time data is unavailable, "
            "so delay impact cannot be assessed."
        )

    if (
        average_delivery_time is not None
        and median_delivery_time is not None
        and average_delivery_time > median_delivery_time
    ):
        report.append(
            "Additional observation: The average exceeds the median, "
            "which may indicate some unusually long deliveries. "
            "Investigate the distribution and extreme values."
        )

    # --------------------------------------------------------
    # 4. Discount and Transaction Impact
    # --------------------------------------------------------

    report.append("\n4. DISCOUNT AND TRANSACTION IMPACT")
    report.append("-" * 50)

    order_value = get_numeric_column(df, "Order_Value")
    discount = get_numeric_column(df, "Discount_Applied")
    final_amount = get_numeric_column(df, "Final_Amount")

    if not discount.dropna().empty:
        average_discount = discount.mean()
        total_discount_recorded = discount.sum()

        report.append(
            f"Average recorded discount: "
            f"{format_number(average_discount)}"
        )
        report.append(
            f"Total recorded discounts: "
            f"{format_number(total_discount_recorded)}"
        )
    else:
        report.append("Discount information is unavailable.")

    if (
        not order_value.dropna().empty
        and not discount.dropna().empty
        and not final_amount.dropna().empty
    ):
        comparable = pd.DataFrame({
            "Order_Value": order_value,
            "Discount_Applied": discount,
            "Final_Amount": final_amount
        }).dropna()

        if not comparable.empty:
            expected_amount = (
                comparable["Order_Value"]
                - comparable["Discount_Applied"]
            )

            mismatches = (
                comparable["Final_Amount"] - expected_amount
            ).abs() > 0.01

            mismatch_count = int(mismatches.sum())

            report.append(
                "Rows with a final amount inconsistent with "
                "Order_Value - Discount_Applied: "
                f"{mismatch_count:,} out of {len(comparable):,}"
            )

            if mismatch_count:
                report.append(
                    "Business impact: Review inconsistent transactions "
                    "to prevent inaccurate revenue reporting and "
                    "incorrect discount calculations."
                )
            else:
                report.append(
                    "Business impact: The checked transactions follow "
                    "the expected final amount formula."
                )
    else:
        report.append(
            "Final amount consistency could not be fully checked "
            "because one or more required columns are unavailable."
        )

    # --------------------------------------------------------
    # 5. Customer Experience Impact
    # --------------------------------------------------------

    report.append("\n5. CUSTOMER EXPERIENCE IMPACT")
    report.append("-" * 50)

    if "Customer_Rating" in df.columns:
        ratings = get_numeric_column(df, "Customer_Rating").dropna()

        if not ratings.empty:
            report.append(
                f"Average customer rating: {ratings.mean():.2f}"
            )
            report.append(
                f"Orders with recorded ratings: {len(ratings):,}"
            )

            low_rating_count = int((ratings <= 2).sum())
            low_rating_percentage = (
                low_rating_count / len(ratings) * 100
            )

            report.append(
                f"Ratings of 2 or below: {low_rating_count:,} "
                f"({low_rating_percentage:.2f}% of rated orders)"
            )

            report.append(
                "Business impact: Review low-rated orders alongside "
                "delivery time, order status, cancellation reasons, "
                "and delivery distance where those fields are available."
            )
        else:
            report.append("No valid customer ratings are available.")
    else:
        report.append(
            "Customer rating analysis skipped: Customer_Rating "
            "column not found."
        )

    # --------------------------------------------------------
    # 6. Operational Improvement Opportunities
    # --------------------------------------------------------

    report.append("\n6. OPERATIONAL IMPROVEMENT OPPORTUNITIES")
    report.append("-" * 50)

    opportunities = []

    if cancellation_rate >= 15:
        opportunities.append(
            "Investigate cancellation patterns by city, cuisine, "
            "payment mode, and cancellation reason."
        )

    if (
        average_delivery_time is not None
        and average_delivery_time >= 120
    ):
        opportunities.append(
            "Review long delivery times and evaluate dispatching, "
            "restaurant preparation, and delivery distance."
        )

    if (
        "Cancellation_Reason" in df.columns
        and "Order_Status" in df.columns
    ):
        cancelled_mask = (
            df["Order_Status"].astype(str).str.strip().str.lower()
            == "cancelled"
        )
        cancelled_rows = df.loc[cancelled_mask]

        if not cancelled_rows.empty:
            reasons = (
                cancelled_rows["Cancellation_Reason"]
                .fillna("")
                .astype(str)
                .str.strip()
            )

            missing_reason_count = int(
                reasons.isin(["", "nan", "none", "unknown"]).sum()
            )

            if missing_reason_count:
                opportunities.append(
                    f"Improve cancellation reason recording; "
                    f"{missing_reason_count:,} cancelled orders have "
                    "a missing or generic reason."
                )

    if not opportunities:
        opportunities.append(
            "Continue monitoring operational KPIs and investigate "
            "the largest adverse patterns identified in the report."
        )

    for number, opportunity in enumerate(opportunities, start=1):
        report.append(f"{number}. {opportunity}")

    # --------------------------------------------------------
    # 7. Business Impact Summary
    # --------------------------------------------------------

    report.append("\n7. BUSINESS IMPACT SUMMARY")
    report.append("-" * 50)

    report.append(
        "Priority areas for management:"
    )
    report.append(
        "- Reduce avoidable cancellations to improve order fulfilment."
    )
    report.append(
        "- Improve delivery speed and reliability to support customer "
        "satisfaction."
    )
    report.append(
        "- Validate order value, discounts, and final amount calculations."
    )
    report.append(
        "- Use city-, cuisine-, and payment-level analysis to target "
        "improvements instead of applying the same solution everywhere."
    )
    report.append(
        "- Measure the results after changes using comparable KPIs."
    )

    report.append(
        "\nNote: This analysis identifies potential business impacts. "
        "It does not calculate actual profit, customer lifetime value, "
        "or confirmed revenue lost from cancellations because the dataset "
        "does not establish all required financial inputs."
    )

    report.append("\n" + "=" * 75)

    return "\n".join(report)