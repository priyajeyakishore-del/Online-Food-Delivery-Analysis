
# ============================================================
# BUSINESS RECOMMENDATIONS
# PROJECT: ONLINE FOOD DELIVERY ANALYSIS
# File: data_analysis/business_insights/recommendations.py
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


def get_status_counts(df):
    """Return normalized order-status counts."""
    if "Order_Status" not in df.columns:
        return pd.Series(dtype="int64")

    status = (
        df["Order_Status"]
        .astype("string")
        .str.strip()
        .str.title()
    )

    return status.value_counts(dropna=True)


def calculate_percentage(part, total):
    """Calculate percentage safely."""
    if total == 0:
        return 0.0

    return (part / total) * 100


def format_number(value, decimals=2):
    """Format numeric values consistently."""
    if value is None or pd.isna(value):
        return "N/A"

    return f"{value:,.{decimals}f}"


# ============================================================
# 2. RECOMMENDATIONS FUNCTION
# ============================================================

def recommendations(df):
    """
    Generate data-informed business recommendations.

    Parameters
    ----------
    df : pandas.DataFrame
        Already-loaded cleaned food delivery dataset.

    Returns
    -------
    str
        Formatted business recommendations report.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame.")

    if df.empty:
        return (
            "=" * 65
            + "\n7. RECOMMENDATIONS\n"
            + "=" * 65
            + "\nRecommendations cannot be generated from an empty dataset."
        )

    total_records = len(df)
    status_counts = get_status_counts(df)

    delivered = int(status_counts.get("Delivered", 0))
    cancelled = int(status_counts.get("Cancelled", 0))

    classified_orders = delivered + cancelled

    cancellation_rate = calculate_percentage(
        cancelled, classified_orders
    )

    lines = [
        "=" * 65,
        "7. BUSINESS RECOMMENDATIONS",
        "=" * 65,
        "",
        "Recommendations are based on observed dataset patterns.",
        "Validate proposed changes with operational data before implementation.",
    ]

    recommendation_number = 1

    # --------------------------------------------------------
    # 1. Order cancellation management
    # --------------------------------------------------------

    lines.extend([
        "",
        f"{recommendation_number}. REDUCE ORDER CANCELLATIONS",
    ])

    if classified_orders > 0:
        lines.append(
            f"   Observation: {cancelled:,} orders were cancelled "
            f"({cancellation_rate:.2f}% of orders classified as "
            "Delivered or Cancelled)."
        )

        if cancellation_rate >= 15:
            lines.extend([
                "   Recommendation:",
                "   - Investigate the most frequently reported cancellation reasons.",
                "   - Improve order confirmation and restaurant acceptance workflows.",
                "   - Notify customers promptly about delays or unavailable items.",
                "   - Monitor cancellation rates weekly by city, cuisine, and time.",
            ])
        else:
            lines.extend([
                "   Recommendation:",
                "   - Continue monitoring cancellation rates.",
                "   - Investigate categories with higher-than-average cancellation rates.",
                "   - Maintain a process for recording cancellation reasons.",
            ])
    else:
        lines.append(
            "   Observation: No valid Delivered or Cancelled status records "
            "are available for calculating the cancellation rate."
        )
        lines.append(
            "   Recommendation: Validate order status data before setting "
            "cancellation reduction targets."
        )

    recommendation_number += 1

    # --------------------------------------------------------
    # 2. Delivery performance
    # --------------------------------------------------------

    lines.extend([
        "",
        f"{recommendation_number}. IMPROVE DELIVERY PERFORMANCE",
    ])

    delivery_times = get_numeric_series(df, "Delivery_Time")
    delivery_times = delivery_times[delivery_times >= 0]

    if not delivery_times.empty:
        average_delivery = delivery_times.mean()
        median_delivery = delivery_times.median()

        lines.append(
            f"   Observation: Average delivery time is "
            f"{format_number(average_delivery)} minutes; median is "
            f"{format_number(median_delivery)} minutes."
        )

        lines.extend([
            "   Recommendation:",
            "   - Investigate the cities and delivery partners with the longest",
            "     average delivery times.",
            "   - Review restaurant preparation time, travel distance, and peak-hour",
            "     workload before changing delivery targets.",
            "   - Track median and 90th-percentile delivery times over time.",
        ])
    else:
        lines.append(
            "   Observation: No valid non-negative delivery-time values are available."
        )
        lines.append(
            "   Recommendation: Improve delivery-time recording and validation."
        )

    recommendation_number += 1

    # --------------------------------------------------------
    # 3. Cancellation reason tracking
    # --------------------------------------------------------

    lines.extend([
        "",
        f"{recommendation_number}. IMPROVE CANCELLATION REASON TRACKING",
    ])

    if "Cancellation_Reason" in df.columns:
        missing_reasons = int(
            df["Cancellation_Reason"].isna().sum()
        )

        lines.append(
            f"   Observation: {missing_reasons:,} records have missing "
            "Cancellation_Reason values."
        )

        lines.extend([
            "   Recommendation:",
            "   - Require a reason when an order is cancelled, where practical.",
            "   - Use standardized cancellation categories.",
            "   - Keep unknown reasons distinct from 'Not Applicable'.",
            "   - Review reason completeness by restaurant and delivery partner.",
        ])
    else:
        lines.append(
            "   Observation: Cancellation_Reason is not available."
        )
        lines.append(
            "   Recommendation: Add a standardized cancellation-reason field "
            "to future operational data."
        )

    recommendation_number += 1

    # --------------------------------------------------------
    # 4. Order value and revenue monitoring
    # --------------------------------------------------------

    lines.extend([
        "",
        f"{recommendation_number}. MONITOR ORDER VALUE AND REVENUE",
    ])

    order_values = get_numeric_series(df, "Order_Value")
    final_amounts = get_numeric_series(df, "Final_Amount")

    if not order_values.empty:
        lines.append(
            f"   Observation: Average order value is "
            f"{format_number(order_values.mean())}."
        )

        lines.extend([
            "   Recommendation:",
            "   - Monitor average order value by city, cuisine, and customer segment.",
            "   - Test bundles or minimum-order promotions where profitable.",
            "   - Compare changes against contribution margin, not order value alone.",
        ])
    else:
        lines.append(
            "   Observation: No valid Order_Value values are available."
        )
        lines.append(
            "   Recommendation: Validate order-value collection before "
            "evaluating sales performance."
        )

    if not final_amounts.empty:
        negative_amounts = int((final_amounts < 0).sum())

        if negative_amounts > 0:
            lines.append(
                f"   Data quality alert: {negative_amounts:,} negative "
                "Final_Amount values require investigation."
            )

    recommendation_number += 1

    # --------------------------------------------------------
    # 5. Discount management
    # --------------------------------------------------------

    lines.extend([
        "",
        f"{recommendation_number}. OPTIMIZE DISCOUNT STRATEGY",
    ])

    if (
        "Order_Value" in df.columns
        and "Discount_Applied" in df.columns
        and "Final_Amount" in df.columns
    ):
        amounts = pd.DataFrame({
            "Order_Value": pd.to_numeric(
                df["Order_Value"], errors="coerce"
            ),
            "Discount_Applied": pd.to_numeric(
                df["Discount_Applied"], errors="coerce"
            ),
            "Final_Amount": pd.to_numeric(
                df["Final_Amount"], errors="coerce"
            ),
        }).dropna()

        if not amounts.empty:
            formula_amount = (
                amounts["Order_Value"]
                - amounts["Discount_Applied"]
            )

            mismatches = int(
                (
                    (formula_amount - amounts["Final_Amount"])
                    .abs() > 0.01
                ).sum()
            )

            lines.append(
                f"   Observation: {mismatches:,} complete records differ "
                "from the simple Order_Value - Discount_Applied formula."
            )

            lines.extend([
                "   Recommendation:",
                "   - Confirm whether the formula reflects the actual pricing rules.",
                "   - Review discounts that exceed the order value.",
                "   - Measure promotion effectiveness using incremental orders",
                "     and profit, not discount usage alone.",
            ])
        else:
            lines.append(
                "   Observation: Insufficient complete amount records "
                "for discount validation."
            )
    else:
        lines.append(
            "   Observation: One or more amount or discount columns are unavailable."
        )
        lines.append(
            "   Recommendation: Ensure order value, discount, and final amount "
            "are consistently recorded."
        )

    recommendation_number += 1

    # --------------------------------------------------------
    # 6. Customer and category analysis
    # --------------------------------------------------------

    lines.extend([
        "",
        f"{recommendation_number}. USE CATEGORY-LEVEL PERFORMANCE ANALYSIS",
        "   Recommendation:",
        "   - Compare cancellation rates and delivery times by city and cuisine.",
        "   - Investigate consistently underperforming groups before intervening.",
        "   - Segment performance by peak hours if reliable time data is available.",
        "   - Avoid decisions based only on total order counts; account for group size.",
    ])

    recommendation_number += 1

    # --------------------------------------------------------
    # 7. Data quality and reporting
    # --------------------------------------------------------

    lines.extend([
        "",
        f"{recommendation_number}. STRENGTHEN DATA QUALITY",
    ])

    missing_cells = int(df.isna().sum().sum())
    total_cells = int(df.shape[0] * df.shape[1])

    missing_rate = calculate_percentage(
        missing_cells, total_cells
    )

    duplicate_rows = int(df.duplicated().sum())

    lines.append(
        f"   Observation: {missing_cells:,} missing cells "
        f"({missing_rate:.2f}% of all cells) and "
        f"{duplicate_rows:,} duplicate complete rows."
    )

    lines.extend([
        "   Recommendation:",
        "   - Validate dates, delivery times, distances, and financial amounts.",
        "   - Check duplicate Order_ID values separately from duplicate rows.",
        "   - Retain the raw dataset and document cleaning decisions.",
        "   - Monitor missingness before and after each cleaning step.",
    ])

    # --------------------------------------------------------
    # 8. Implementation priorities
    # --------------------------------------------------------

    lines.extend([
        "",
        "8. SUGGESTED IMPLEMENTATION PRIORITIES",
        "",
        "   Immediate:",
        "   - Validate cancellation reasons and financial calculations.",
        "   - Establish a baseline for cancellation and delivery-time metrics.",
        "",
        "   Short term:",
        "   - Investigate high-cancellation cities and long-delivery categories.",
        "   - Review peak-hour capacity and customer notifications.",
        "",
        "   Ongoing:",
        "   - Track KPIs weekly and compare them with a consistent baseline.",
        "   - Evaluate interventions using measurable outcomes.",
        "",
        "   Note: Recommendations are hypotheses to test, not proof that a",
        "   particular operational factor caused the observed outcome.",
    ])

    return "\n".join(lines)
