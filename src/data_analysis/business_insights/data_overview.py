
# ============================================================
# DATA OVERVIEW
# PROJECT: ONLINE FOOD DELIVERY ANALYSIS
# File: data_analysis/business_insights/data_overview.py
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


def format_number(value, decimals=2):
    """Format numeric values consistently."""
    if value is None or pd.isna(value):
        return "N/A"

    return f"{value:,.{decimals}f}"


def format_percentage(value):
    """Format percentages to two decimal places."""
    if value is None or pd.isna(value):
        return "N/A"

    return f"{value:.2f}%"


# ============================================================
# 2. DATA OVERVIEW FUNCTION
# ============================================================

def data_overview(df):
    """
    Generate a descriptive overview of the supplied dataset.

    Parameters
    ----------
    df : pandas.DataFrame
        Already-loaded cleaned food delivery dataset.

    Returns
    -------
    str
        Formatted data overview report.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame.")

    if df.empty:
        return (
            "=" * 65
            + "\n2. DATA OVERVIEW\n"
            + "=" * 65
            + "\nThe dataset is empty."
        )

    rows, columns = df.shape

    # --------------------------------------------------------
    # Basic dataset information
    # --------------------------------------------------------

    total_cells = rows * columns
    missing_cells = int(df.isna().sum().sum())
    duplicate_rows = int(df.duplicated().sum())

    missing_percentage = (
        missing_cells / total_cells * 100
        if total_cells else 0.0
    )

    # --------------------------------------------------------
    # Column data types
    # --------------------------------------------------------

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()

    datetime_columns = df.select_dtypes(
        include=["datetime", "datetimetz"]
    ).columns.tolist()

    categorical_columns = df.select_dtypes(
        include=["object", "category", "string", "bool"]
    ).columns.tolist()

    # --------------------------------------------------------
    # Unique values and identifier columns
    # --------------------------------------------------------

    unique_order_ids = (
        int(df["Order_ID"].nunique())
        if "Order_ID" in df.columns else None
    )

    unique_customers = (
        int(df["Customer_ID"].nunique())
        if "Customer_ID" in df.columns else None
    )

    unique_restaurants = (
        int(df["Restaurant_ID"].nunique())
        if "Restaurant_ID" in df.columns else None
    )

    unique_delivery_partners = (
        int(df["Delivery_Partner_ID"].nunique())
        if "Delivery_Partner_ID" in df.columns else None
    )

    # --------------------------------------------------------
    # Order status distribution
    # --------------------------------------------------------

    if "Order_Status" in df.columns:
        status_counts = (
            df["Order_Status"]
            .astype("string")
            .str.strip()
            .str.title()
            .value_counts(dropna=True)
        )
    else:
        status_counts = pd.Series(dtype="int64")

    # --------------------------------------------------------
    # Date coverage
    # --------------------------------------------------------

    date_start = None
    date_end = None
    valid_date_count = 0

    if "Order_Date" in df.columns:
        order_dates = pd.to_datetime(
            df["Order_Date"], errors="coerce"
        ).dropna()

        valid_date_count = len(order_dates)

        if not order_dates.empty:
            date_start = order_dates.min()
            date_end = order_dates.max()

    # --------------------------------------------------------
    # Numeric column summaries
    # --------------------------------------------------------

    numeric_summary = {}

    for column in numeric_columns:
        values = get_numeric_series(df, column)

        if values.empty:
            continue

        numeric_summary[column] = {
            "mean": values.mean(),
            "median": values.median(),
            "minimum": values.min(),
            "maximum": values.max(),
        }

    # --------------------------------------------------------
    # Build report
    # --------------------------------------------------------

    lines = [
        "=" * 65,
        "2. DATA OVERVIEW",
        "=" * 65,
        "",
        "A. DATASET DIMENSIONS",
        f"   Total records: {rows:,}",
        f"   Total columns: {columns:,}",
        f"   Total cells: {total_cells:,}",
        "",
        "B. DATA TYPES",
        f"   Numeric columns: {len(numeric_columns)}",
        f"   Categorical/text columns: {len(categorical_columns)}",
        f"   Datetime columns: {len(datetime_columns)}",
        "",
        "C. DATA QUALITY",
        f"   Duplicate complete rows: {duplicate_rows:,}",
        f"   Missing cells: {missing_cells:,}",
        f"   Missing cell percentage: {format_percentage(missing_percentage)}",
        "",
        "D. UNIQUE IDENTIFIERS",
        f"   Unique order IDs: {unique_order_ids if unique_order_ids is not None else 'Column unavailable'}",
        f"   Unique customers: {unique_customers if unique_customers is not None else 'Column unavailable'}",
        f"   Unique restaurants: {unique_restaurants if unique_restaurants is not None else 'Column unavailable'}",
        f"   Unique delivery partners: {unique_delivery_partners if unique_delivery_partners is not None else 'Column unavailable'}",
        "",
        "E. ORDER STATUS DISTRIBUTION",
    ]

    if status_counts.empty:
        lines.append("   Order status column unavailable or contains no valid values.")
    else:
        for status, count in status_counts.items():
            lines.append(f"   {status}: {count:,}")

        missing_status = int(df["Order_Status"].isna().sum())

        if missing_status:
            lines.append(f"   Missing status values: {missing_status:,}")

    # --------------------------------------------------------
    # Date coverage section
    # --------------------------------------------------------

    lines.extend([
        "",
        "F. ORDER DATE COVERAGE",
    ])

    if date_start is not None and date_end is not None:
        lines.append(f"   Earliest order date: {date_start}")
        lines.append(f"   Latest order date: {date_end}")
        lines.append(f"   Valid order-date records: {valid_date_count:,}")
    else:
        lines.append("   No valid Order_Date values are available.")

    # --------------------------------------------------------
    # Numeric summary section
    # --------------------------------------------------------

    lines.extend([
        "",
        "G. NUMERIC COLUMN SUMMARY",
    ])

    if numeric_summary:
        for column, stats in numeric_summary.items():
            lines.append(
                f"   {column}: "
                f"Mean={format_number(stats['mean'])}, "
                f"Median={format_number(stats['median'])}, "
                f"Min={format_number(stats['minimum'])}, "
                f"Max={format_number(stats['maximum'])}"
            )
    else:
        lines.append("   No usable numeric columns were found.")

    # --------------------------------------------------------
    # Important interpretation note
    # --------------------------------------------------------

    lines.extend([
        "",
        "H. INTERPRETATION",
        "   - This overview describes the DataFrame supplied.",
        "   - Missing-value statistics reflect the current dataset;",
        "     previously imputed values will not appear as missing.",
        "   - Duplicate complete rows are not the same as duplicate",
        "     Order_ID values; review both when validating the data.",
    ])

    return "\n".join(lines)
