
import pandas as pd


def clean_payment_mode(df):
    """
    Clean Payment_Mode without introducing mode-imputation bias.

    Steps:
    1. Standardize text values.
    2. Convert blank and invalid missing-value labels to NA.
    3. Replace missing values with 'Unknown'.
    4. Report the distribution before and after cleaning.
    """

    df = df.copy()

    print("\n" + "=" * 70)
    print("PAYMENT MODE CLEANING")
    print("=" * 70)

    # ============================================================
    # 1. VALIDATE REQUIRED COLUMN
    # ============================================================

    if "Payment_Mode" not in df.columns:
        raise ValueError("Required column missing: Payment_Mode")

    # ============================================================
    # 2. STANDARDIZE PAYMENT MODE
    # ============================================================

    df["Payment_Mode"] = (
        df["Payment_Mode"]
        .astype("string")
        .str.strip()
    )

    # Convert blank strings and missing-value labels to NA
    invalid_values = [
        "", "nan", "none", "null", "na", "n/a"
    ]

    invalid_mask = (
        df["Payment_Mode"]
        .str.casefold()
        .isin(invalid_values)
        .fillna(False)
    )

    df.loc[invalid_mask, "Payment_Mode"] = pd.NA

    # ============================================================
    # 3. REPORT BEFORE IMPUTATION
    # ============================================================

    missing_before = int(
        df["Payment_Mode"].isna().sum()
    )

    print("\nMissing values before cleaning:")
    print(f"{missing_before:,}")

    print(
        "Missing percentage before cleaning:",
        f"{df['Payment_Mode'].isna().mean() * 100:.2f}%"
    )

    print("\nPayment distribution before filling:")
    print(df["Payment_Mode"].value_counts(dropna=False))

    # ============================================================
    # 4. FILL MISSING VALUES WITH UNKNOWN
    # ============================================================

    df["Payment_Mode"] = (
        df["Payment_Mode"].fillna("Unknown")
    )

    # ============================================================
    # 5. FINAL VALIDATION
    # ============================================================

    missing_after = int(
        df["Payment_Mode"].isna().sum()
    )

    print("\nMissing values filled with Unknown:")
    print(missing_before - missing_after)

    print("\nMissing values after cleaning:")
    print(missing_after)

    print("\nPayment distribution after cleaning:")
    print(df["Payment_Mode"].value_counts(dropna=False))

    print("\nPayment distribution percentage:")
    print(
        (
            df["Payment_Mode"]
            .value_counts(normalize=True, dropna=False)
            * 100
        ).round(2)
    )

    assert missing_after == 0, (
        "Payment_Mode still contains missing values."
    )

    print("\nPayment mode cleaning completed successfully.")

    return df
