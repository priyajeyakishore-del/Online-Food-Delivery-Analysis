
import pandas as pd


# ============================================================
# 1. DEFINE ORDER OUTCOME COLUMNS
# ============================================================

ORDER_OUTCOME_COLUMNS = [
    "Order_Status",
    "Cancellation_Reason"
]


# ============================================================
# 2. DATA QUALITY ANALYSIS
# ============================================================

def analyze_order_outcome(df):
    """
    Analyze missing values, unique categories,
    and category frequencies for order outcome columns.
    """

    missing_columns = [
        col for col in ORDER_OUTCOME_COLUMNS
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Required columns not found: {missing_columns}"
        )

    print("\n" + "=" * 70)
    print("ORDER OUTCOME DATA QUALITY ANALYSIS")
    print("=" * 70)

    for col in ORDER_OUTCOME_COLUMNS:

        print(f"\n{'=' * 70}")
        print(f"Column: {col}")
        print("=" * 70)

        missing_count = df[col].isna().sum()
        missing_percentage = df[col].isna().mean() * 100

        print("\nMissing count:", missing_count)
        print("Missing percentage:", round(missing_percentage, 2), "%")

        print("\nUnique categories:", df[col].nunique())

        print("\nCategory frequencies:")
        print(df[col].value_counts(dropna=False))

        if df[col].dtype == "object":
            print("\nDistinct raw text values:")
            print(df[col].dropna().unique())


# ============================================================
# 3. STANDARDIZE CATEGORICAL TEXT
# ============================================================

def standardize_order_outcome(df):
    """
    Remove extra spaces and standardize text case
    in order outcome categorical columns.
    """

    df = df.copy()

    for col in ORDER_OUTCOME_COLUMNS:

        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

        df[col] = df[col].map(
            lambda value: (
                " ".join(value.split()).title()
                if isinstance(value, str)
                else value
            )
        )

    return df


# ============================================================
# 4. HANDLE MISSING CANCELLATION REASONS
# ============================================================

def handle_cancellation_reason(df):
    """
    Fill missing cancellation reasons according to order status.

    Delivered + missing reason  -> Not Applicable
    Cancelled + missing reason  -> Unknown
    Other statuses              -> Keep missing
    """

    df = df.copy()

    required_columns = [
        "Order_Status",
        "Cancellation_Reason"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Required columns not found: {missing_columns}"
        )

    status = df["Order_Status"].str.strip().str.casefold()
    reason_missing = df["Cancellation_Reason"].isna()

    delivered_missing = (
        status.eq("delivered")
        & reason_missing
    )

    cancelled_missing = (
        status.eq("cancelled")
        & reason_missing
    )

    df.loc[
        delivered_missing,
        "Cancellation_Reason"
    ] = "Not Applicable"

    df.loc[
        cancelled_missing,
        "Cancellation_Reason"
    ] = "Unknown"

    print("\nCancellation reason imputation:")
    print(
        "Delivered orders filled:",
        delivered_missing.sum()
    )
    print(
        "Cancelled orders filled:",
        cancelled_missing.sum()
    )

    return df


# ============================================================
# 5. VALIDATE CLEANED ORDER OUTCOME DATA
# ============================================================

def validate_order_outcome(df):
    """
    Verify cleaned categories, remaining missing values,
    and logical consistency between status and reason.
    """

    print("\n" + "=" * 70)
    print("ORDER OUTCOME VALIDATION")
    print("=" * 70)

    for col in ORDER_OUTCOME_COLUMNS:
        print(f"\nCleaned categories: {col}")
        print(df[col].value_counts(dropna=False))

    print("\nOrder Status vs Cancellation Reason:")

    print(
        pd.crosstab(
            df["Order_Status"],
            df["Cancellation_Reason"].fillna("Missing"),
            margins=True
        )
    )

    status = df["Order_Status"].str.strip().str.casefold()
    reason = df["Cancellation_Reason"].str.strip().str.casefold()

    cancelled_without_reason = (
        status.eq("cancelled")
        & df["Cancellation_Reason"].isna()
    )

    delivered_with_reason = (
        status.eq("delivered")
        & df["Cancellation_Reason"].notna()
        & reason.ne("not applicable")
    )

    print(
        "\nCancelled orders still missing a reason:",
        cancelled_without_reason.sum()
    )

    print(
        "Delivered orders with an actual cancellation reason:",
        delivered_with_reason.sum()
    )

    print(
        "\nRemaining missing values:",
        df[ORDER_OUTCOME_COLUMNS].isna().sum()
    )


# ============================================================
# 6. MAIN REUSABLE CLEANING FUNCTION
# ============================================================

def clean_order_outcome(df, analyze_before=True):
    """
    Run the complete order outcome cleaning workflow.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataset.
    analyze_before : bool
        Whether to print data quality analysis before cleaning.

    Returns
    -------
    pandas.DataFrame
        Dataset with cleaned order outcome columns.
    """

    df = df.copy()

    if analyze_before:
        analyze_order_outcome(df)

    df = standardize_order_outcome(df)

    df = handle_cancellation_reason(df)

    validate_order_outcome(df)

    print("\nOrder outcome cleaning completed successfully.")

    return df
