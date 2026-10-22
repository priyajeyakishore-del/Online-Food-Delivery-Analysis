
import pandas as pd


# ============================================================
# FINANCIAL DATA CLEANING
# Columns: Order_Value, Discount_Applied, Profit_Margin
# ============================================================

FINANCIAL_COLUMNS = [
    "Order_Value",
    "Discount_Applied",
    "Profit_Margin"
]


def clean_financial_data(df):
    """Clean financial columns except Final_Amount."""

    df = df.copy()

    # 1. Check required columns
    missing_columns = [
        col for col in FINANCIAL_COLUMNS
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing financial columns: {missing_columns}"
        )

    # 2. Convert columns to numeric
    for col in FINANCIAL_COLUMNS:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # 3. Impute missing Order_Value using median
    order_value_median = df["Order_Value"].median()

    if pd.notna(order_value_median):
        df["Order_Value"] = df["Order_Value"].fillna(
            order_value_median
        )

    # 4. Impute missing Discount_Applied using mode
    discount_mode = df["Discount_Applied"].mode()

    if not discount_mode.empty:
        df["Discount_Applied"] = df["Discount_Applied"].fillna(
            discount_mode.iloc[0]
        )

    # 5. Keep Profit_Margin missing values unchanged
    # Negative profit margins may represent genuine losses.

    # 6. Final validation
    print("\nFinancial Cleaning Summary")
    print("=" * 50)

    print("\nMissing values:")
    print(df[FINANCIAL_COLUMNS].isna().sum())

    print("\nNegative values:")
    print((df[FINANCIAL_COLUMNS] < 0).sum())

    print("\nFinancial cleaning completed.")

    return df
