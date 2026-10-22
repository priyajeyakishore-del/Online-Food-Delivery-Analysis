
# ============================================================
# UNIVARIATE ANALYSIS - NUMERICAL STATISTICAL SUMMARY
# Objective:
# Understand the central tendency, spread, and missing values
# of numerical variables.
# ============================================================

import pandas as pd
from pathlib import Path

from data_analysis.univariate_analysis.config import (
    NUMERICAL_COLS
)


# ============================================================
# 1. OUTPUT DIRECTORY CONFIGURATION
# ============================================================

OUTPUT_DIR = Path(
    r"C:\Users\Priya Jeyakishore\OneDrive\Desktop\GUVI_Data_Science_ZenClass\Online_Food_Delivery_Analysis\output\reports\univariate_analysis"
)

# Create output directory if it does not exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. NUMERICAL SUMMARY FUNCTION
# ============================================================

def numerical_summary(df):

    print("\n" + "=" * 80)
    print("UNIVARIATE ANALYSIS - NUMERICAL STATISTICAL SUMMARY")
    print("=" * 80)

    # --------------------------------------------------------
    # STEP 1: Validate numerical columns
    # --------------------------------------------------------

    available_cols = [
        col for col in NUMERICAL_COLS
        if col in df.columns
    ]

    missing_cols = [
        col for col in NUMERICAL_COLS
        if col not in df.columns
    ]

    if missing_cols:
        print("\nWARNING: Columns not found in dataset:")
        print(missing_cols)

    if not available_cols:
        print("No specified numerical columns found.")
        return None

    # Convert selected columns to numeric in a separate copy.
    # Invalid values become NaN for analysis only.
    numerical_df = df[available_cols].apply(
        pd.to_numeric,
        errors="coerce"
    )

    # --------------------------------------------------------
    # STEP 2: Dataset dimensions
    # --------------------------------------------------------

    print("\n1. DATASET INFORMATION")
    print("-" * 80)

    print(f"Total records: {len(df):,}")
    print(f"Numerical variables analyzed: {len(available_cols)}")

    # --------------------------------------------------------
    # STEP 3: Descriptive statistical summary
    # --------------------------------------------------------

    print("\n2. DESCRIPTIVE STATISTICAL SUMMARY")
    print("-" * 80)

    descriptive_summary = numerical_df.describe().T.round(2)

    descriptive_summary = descriptive_summary.rename(
        columns={
            "count": "Count",
            "mean": "Mean",
            "std": "Std",
            "min": "Min",
            "25%": "Q1",
            "50%": "Median",
            "75%": "Q3",
            "max": "Max"
        }
    )

    print(descriptive_summary.to_string())

    # --------------------------------------------------------
    # STEP 4: Missing-value analysis
    # --------------------------------------------------------

    print("\n3. MISSING VALUE ANALYSIS")
    print("-" * 80)

    missing_count = numerical_df.isna().sum()

    missing_percentage = (
        missing_count / len(df) * 100
    ).round(2)

    missing_summary = pd.DataFrame({
        "Missing_Count": missing_count,
        "Missing_Percentage": missing_percentage
    }).sort_values(
        by="Missing_Percentage",
        ascending=False
    )

    print(missing_summary.to_string())

    # --------------------------------------------------------
    # STEP 5: Consolidated summary for reporting
    # --------------------------------------------------------

    print("\n4. CONSOLIDATED NUMERICAL SUMMARY")
    print("-" * 80)

    summary = pd.DataFrame({
        "Count": numerical_df.count(),
        "Mean": numerical_df.mean(),
        "Median": numerical_df.median(),
        "Std": numerical_df.std(),
        "Min": numerical_df.min(),
        "Q1": numerical_df.quantile(0.25),
        "Q3": numerical_df.quantile(0.75),
        "Max": numerical_df.max(),
        "Missing_Count": missing_count,
        "Missing_Percentage": missing_percentage
    }).round(2)

    print(summary.to_string())

    # --------------------------------------------------------
    # STEP 6: Save reports to the output folder
    # --------------------------------------------------------

    summary_path = (
        OUTPUT_DIR / "numerical_statistical_summary.csv"
    )

    summary.to_csv(
        summary_path,
        index=True,
        index_label="Variable"
    )



    print("\n5. REPORTS SAVED SUCCESSFULLY")
    print("-" * 80)

    print(f"Statistical summary:\n{summary_path}")

    print("\n" + "=" * 80)
    print("NUMERICAL STATISTICAL SUMMARY COMPLETED")
    print("=" * 80)

    return summary
