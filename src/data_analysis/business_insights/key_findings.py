
# ============================================================
# KEY FINDINGS
# PROJECT: ONLINE FOOD DELIVERY ANALYSIS
# File: data_analysis/business_insights/key_findings.py
# ============================================================

import pandas as pd


# ============================================================
# 1. REUSABLE HELPER FUNCTIONS
# ============================================================

def get_numeric_series(df, column):
    """Return valid numeric values from a column."""
    if column not in df.columns:
        return pd.Series(dtype="float64")

    return pd.to_numeric(
        df[column], errors="coerce"
    ).dropna()


def get_status_counts(df):
    """Return normalized order status counts."""
    if "Order_Status" not in df.columns:
        return pd.Series(dtype="int64")

    status = (
        df["Order_Status"]
        .astype("string")
        .str.strip()
        .str.title()
    )

    return status.value_counts(dropna=True)


def get_top_category(df, column, min_records=1):
    """
    Return the most frequent category and its count.
    Categories with missing values are excluded.
    """
    if column not in df.columns:
        return None, 0

    counts = (
        df[column]
        .dropna()
        .astype(str)
        .str.strip()
    )

    counts = counts[counts.ne("")].value_counts()

    if counts.empty:
        return None, 0

    eligible = counts[counts >= min_records]

    if eligible.empty:
        return None, 0

    return str(eligible.index[0]), int(eligible.iloc[0])


def percentage(part, total):
    """Calculate percentage safely."""
    if total == 0:
        return 0.0

    return (part / total) * 100


def format_number(value):
    """Format numbers to two decimal places."""
    if value is None or pd.isna(value):
        return "N/A"

    return f"{value:,.2f}"


# ============================================================
# 2. KEY FINDINGS FUNCTION
# ============================================================

def key_findings(df):
    """
    Identify important business findings from the dataset.

    Parameters
    ----------
    df : pandas.DataFrame
        Already-loaded and cleaned food delivery dataset.

    Returns
    -------
    str
        Formatted key findings report.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame.")

    if df.empty:
        return "3. KEY FINDINGS\n\nNo findings available: dataset is empty."

    findings = []

    total_orders = len(df)
    status_counts = get_status_counts(df)

    delivered = int(status_counts.get("Delivered", 0))
    cancelled = int(status_counts.get("Cancelled", 0))
    status_total = delivered + cancelled

    # --------------------------------------------------------
    # Finding 1: Order fulfilment and cancellations
    # --------------------------------------------------------

    findings.append("1. ORDER FULFILMENT")

    if "Order_Status" in df.columns:
        findings.append(
            f"   - Delivered orders: {delivered:,} "
            f"({percentage(delivered, total_orders):.2f}%)."
        )

        findings.append(
            f"   - Cancelled orders: {cancelled:,} "
            f"({percentage(cancelled, total_orders):.2f}%)."
        )

        if status_total > 0:
            findings.append(
                "   - Cancellation rate among orders classified "
                f"as Delivered or Cancelled: "
                f"{percentage(cancelled, status_total):.2f}%."
            )
    else:
        findings.append(
            "   - Order status information is unavailable."
        )

    # --------------------------------------------------------
    # Finding 2: Delivery time
    # --------------------------------------------------------

    findings.append("\n2. DELIVERY PERFORMANCE")

    delivery_time = get_numeric_series(df, "Delivery_Time")
    delivery_time = delivery_time[delivery_time >= 0]

    if not delivery_time.empty:
        findings.append(
            f"   - Average delivery time: "
            f"{format_number(delivery_time.mean())} minutes."
        )

        findings.append(
            f"   - Median delivery time: "
            f"{format_number(delivery_time.median())} minutes."
        )

        findings.append(
            f"   - Valid delivery-time records: "
            f"{len(delivery_time):,}."
        )

        if len(delivery_time) < total_orders:
            findings.append(
                "   - Delivery-time metrics are based only on "
                "valid, non-negative numeric values."
            )
    else:
        findings.append(
            "   - No valid delivery-time records are available."
        )

    # --------------------------------------------------------
    # Finding 3: Order value
    # --------------------------------------------------------

    findings.append("\n3. ORDER VALUE")

    order_value = get_numeric_series(df, "Order_Value")

    if not order_value.empty:
        findings.append(
            f"   - Average order value: "
            f"{format_number(order_value.mean())}."
        )

        findings.append(
            f"   - Median order value: "
            f"{format_number(order_value.median())}."
        )

        findings.append(
            f"   - Valid order-value records: "
            f"{len(order_value):,}."
        )
    else:
        findings.append(
            "   - No valid order-value records are available."
        )

    # --------------------------------------------------------
    # Finding 4: Final amount
    # --------------------------------------------------------

    findings.append("\n4. CUSTOMER PAYMENT VALUE")

    final_amount = get_numeric_series(df, "Final_Amount")

    if not final_amount.empty:
        findings.append(
            f"   - Average final amount: "
            f"{format_number(final_amount.mean())}."
        )

        findings.append(
            f"   - Valid final-amount records: "
            f"{len(final_amount):,}."
        )

        if (final_amount < 0).any():
            findings.append(
                f"   - Warning: {(final_amount < 0).sum():,} "
                "negative final amounts require validation."
            )
    else:
        findings.append(
            "   - No valid final-amount records are available."
        )

    # --------------------------------------------------------
    # Finding 5: City distribution
    # --------------------------------------------------------

    findings.append("\n5. CITY DISTRIBUTION")

    top_city, top_city_count = get_top_category(df, "City")

    if top_city is not None:
        findings.append(
            f"   - City with the most records: {top_city} "
            f"({top_city_count:,} records; "
            f"{percentage(top_city_count, total_orders):.2f}% "
            "of all dataset records)."
        )
    else:
        findings.append(
            "   - City information is unavailable."
        )

    # --------------------------------------------------------
    # Finding 6: Cuisine distribution
    # --------------------------------------------------------

    findings.append("\n6. CUISINE DISTRIBUTION")

    top_cuisine, top_cuisine_count = get_top_category(
        df, "Cuisine_Type"
    )

    if top_cuisine is not None:
        findings.append(
            f"   - Most frequently recorded cuisine: "
            f"{top_cuisine} ({top_cuisine_count:,} records; "
            f"{percentage(top_cuisine_count, total_orders):.2f}% "
            "of all dataset records)."
        )
    else:
        findings.append(
            "   - Cuisine information is unavailable."
        )

    # --------------------------------------------------------
    # Finding 7: Payment method
    # --------------------------------------------------------

    findings.append("\n7. PAYMENT METHOD")

    top_payment, top_payment_count = get_top_category(
        df, "Payment_Mode"
    )

    if top_payment is not None:
        findings.append(
            f"   - Most frequently recorded payment mode: "
            f"{top_payment} ({top_payment_count:,} records; "
            f"{percentage(top_payment_count, total_orders):.2f}% "
            "of all dataset records)."
        )
    else:
        findings.append(
            "   - Payment mode information is unavailable."
        )

    # --------------------------------------------------------
    # Finding 8: Data completeness
    # --------------------------------------------------------

    findings.append("\n8. DATA COMPLETENESS")

    missing_cells = int(df.isna().sum().sum())
    total_cells = int(df.shape[0] * df.shape[1])

    missing_percentage = percentage(
        missing_cells, total_cells
    )

    findings.append(
        f"   - Missing cells: {missing_cells:,} "
        f"out of {total_cells:,} ({missing_percentage:.2f}%)."
    )

    findings.append(
        "   - Completeness is measured on the DataFrame provided "
        "to this function; previously imputed values may no longer "
        "appear as missing."
    )

    # --------------------------------------------------------
    # Build and return report
    # --------------------------------------------------------

    report_lines = [
        "=" * 65,
        "3. KEY FINDINGS",
        "=" * 65,
        "",
        f"Dataset records analysed: {total_orders:,}",
        "",
        *findings,
    ]

    return "\n".join(report_lines)
