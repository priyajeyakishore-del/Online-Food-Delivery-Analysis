
import pandas as pd


def clean_final_amount(df):
    """Clean and validate the Final_Amount column."""

    df = df.copy()

    required_columns = [
        "Final_Amount",
        "Order_Value",
        "Discount_Applied"
    ]

    # 1. Check required columns
    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # 2. Convert required columns to numeric
    for col in required_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # 3. Identify missing final amounts
    missing_mask = df["Final_Amount"].isna()

    # 4. Calculate missing values where both inputs are available
    calculated_amount = (
        df["Order_Value"] - df["Discount_Applied"]
    )

    can_calculate = (
        missing_mask
        & df["Order_Value"].notna()
        & df["Discount_Applied"].notna()
    )

    df.loc[can_calculate, "Final_Amount"] = (
        calculated_amount[can_calculate]
    )

    # 5. Identify negative final amounts
    negative_count = (df["Final_Amount"] < 0).sum()

    # 6. Replace negative amounts with zero
    # Apply this only if zero is the agreed business rule.
    df.loc[df["Final_Amount"] < 0, "Final_Amount"] = 0

    # 7. Final validation
    print("\n" + "=" * 60)
    print("FINAL AMOUNT CLEANING SUMMARY")
    print("=" * 60)

    print("Missing values before cleaning:", missing_mask.sum())
    print("Values calculated:", can_calculate.sum())
    print("Negative values corrected:", negative_count)
    print(
        "Remaining missing values:",
        df["Final_Amount"].isna().sum()
    )
    print(
        "Remaining negative values:",
        (df["Final_Amount"] < 0).sum()
    )

    print("\nFinal_Amount data type:", df["Final_Amount"].dtype)

    return df
