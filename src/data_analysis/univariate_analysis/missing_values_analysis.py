
# ============================================================
# STEP 2: MISSING VALUE ANALYSIS - NUMERICAL VARIABLES
# Objective:
# Identify and visualize missing values in numerical columns.
# ============================================================

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
from data_analysis.univariate_analysis.config import (
    NUMERICAL_COLS
)


GRAPH_DIR = Path(
    r"C:\Users\Priya Jeyakishore\OneDrive\Desktop\GUVI_Data_Science_ZenClass\Online_Food_Delivery_Analysis\output\graphs\univariate_analysis\numerical"
)

# Folder for CSV reports
REPORT_DIR = Path(
    r"C:\Users\Priya Jeyakishore\OneDrive\Desktop\GUVI_Data_Science_ZenClass\Online_Food_Delivery_Analysis\output\reports\univariate_analysis"
)

# Create folders automatically if they do not exist
GRAPH_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. MISSING VALUE ANALYSIS FUNCTION
# ============================================================

def missing_values_analysis(df):

    print("\n" + "=" * 80)
    print("MISSING VALUE ANALYSIS - NUMERICAL VARIABLES")
    print("=" * 80)

    # --------------------------------------------------------
    # STEP 1: Validate columns
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
        print("\nNo specified numerical columns found.")
        return None

    # Work on a separate copy; do not modify the original df
    numerical_df = df[available_cols].apply(
        pd.to_numeric,
        errors="coerce"
    )

    # --------------------------------------------------------
    # STEP 2: Calculate missing counts
    # --------------------------------------------------------

    missing_count = numerical_df.isnull().sum()

    print("\n1. MISSING VALUE COUNTS")
    print("-" * 80)

    print(
        missing_count.sort_values(
            ascending=False
        ).to_string()
    )

    # --------------------------------------------------------
    # STEP 3: Calculate missing percentages
    # --------------------------------------------------------

    missing_percentage = (
        numerical_df.isnull().sum() / len(df) * 100
    ).round(2)

    print("\n2. MISSING VALUE PERCENTAGES")
    print("-" * 80)

    print(
        missing_percentage.sort_values(
            ascending=False
        ).to_string()
    )

    # --------------------------------------------------------
    # STEP 4: Create combined missing value report
    # --------------------------------------------------------

    missing_report = pd.DataFrame({
        "Missing_Count": missing_count,
        "Missing_Percentage": missing_percentage
    })

    missing_report = missing_report.sort_values(
        by="Missing_Percentage",
        ascending=False
    )

    print("\n3. COMBINED MISSING VALUE REPORT")
    print("-" * 80)

    print(missing_report.to_string())

    # Save CSV report
    report_path = (
        REPORT_DIR / "numerical_missing_values_report.csv"
    )

    missing_report.to_csv(
        report_path,
        index_label="Variable"
    )

    print(f"\nMissing value report saved to:\n{report_path}")

    # --------------------------------------------------------
    # STEP 5: Identify columns with missing values
    # --------------------------------------------------------

    columns_with_missing = missing_count[
        missing_count > 0
    ].index.tolist()

    if not columns_with_missing:
        print("\nNo missing values found in these numerical columns.")
        return missing_report

    # --------------------------------------------------------
    # STEP 6: Visualize missing values using heatmap
    # --------------------------------------------------------

    plt.figure(figsize=(12, 6))

    sns.heatmap(
        numerical_df[columns_with_missing].isnull(),
        cbar=False,
        yticklabels=False,
        xticklabels=True,
        cmap=["#2E8B57", "#D9534F"]
    )

    plt.title(
        "Missing Values in Numerical Variables",
        fontsize=14,
        fontweight="bold"
    )

    plt.xlabel("Numerical Variables")
    plt.ylabel("Dataset Records")
    plt.xticks(rotation=45, ha="right")

    plt.tight_layout()

    # --------------------------------------------------------
    # STEP 7: Save graph to your specified folder
    # --------------------------------------------------------

    graph_path = (
        GRAPH_DIR / "missing_values_heatmap.png"
    )

    plt.savefig(
        graph_path,
        dpi=300,
        bbox_inches="tight"
    )

    print(f"\nHeatmap saved to:\n{graph_path}")

    # Display graph
    plt.show()

    # Release memory after displaying graph
    plt.close()

    # --------------------------------------------------------
    # STEP 8: Final summary
    # --------------------------------------------------------

    print("\n4. FINAL SUMMARY")
    print("-" * 80)

    print(f"Total records analyzed: {len(df):,}")
    print(f"Numerical columns analyzed: {len(available_cols)}")
    print(f"Columns with missing values: {len(columns_with_missing)}")
    print(f"Total missing cells in selected columns: {missing_count.sum():,}")

    print("\n" + "=" * 80)
    print("MISSING VALUE ANALYSIS COMPLETED")
    print("=" * 80)

    return missing_report


# ============================================================
# 3. EXECUTION
# ============================================================

if __name__ == "__main__":

    DATA_PATH = Path(
        r"C:\Users\Priya Jeyakishore\OneDrive\Desktop\GUVI_Data_Science_ZenClass\Online_Food_Delivery_Analysis\cleaned_data\cleaned_online_food_delivery.csv"
    )

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}\n"
            "Update DATA_PATH to the location of your cleaned CSV."
        )

    df_clean = pd.read_csv(DATA_PATH)

    missing_values_analysis(df_clean)