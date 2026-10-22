
# ============================================================
# STEP 3: DISTRIBUTION ANALYSIS - NUMERICAL VARIABLES
# Project: Online Food Delivery Analysis
#
# Objectives:
# 1. Visualize numerical variable distributions.
# 2. Identify normality, skewness, multiple peaks, and extremes.
# 3. Save histograms with KDE curves in the output folder.
# ============================================================

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from pathlib import Path

from data_analysis.univariate_analysis.config import (
    NUMERICAL_COLS
)


# ============================================================
# 1. OUTPUT DIRECTORY
# ============================================================

GRAPH_DIR = Path(
    r"C:\Users\Priya Jeyakishore\OneDrive\Desktop\GUVI_Data_Science_ZenClass\Online_Food_Delivery_Analysis\output\graphs\univariate_analysis\numerical\data_distribution"
)

GRAPH_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. DISTRIBUTION ANALYSIS FUNCTION
# ============================================================

def distribution_analysis(df):

    print("\n" + "=" * 80)
    print("DISTRIBUTION ANALYSIS - NUMERICAL VARIABLES")
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
        print("\nWARNING: Columns not found:")
        print(missing_cols)

    if not available_cols:
        print("No specified numerical columns found.")
        return None

    # --------------------------------------------------------
    # STEP 2: Analyze each variable
    # --------------------------------------------------------

    for col in available_cols:

        # Convert values to numeric for analysis
        values = pd.to_numeric(
            df[col],
            errors="coerce"
        ).dropna()

        if values.empty:
            print(f"\nSkipping {col}: no valid numeric values.")
            continue

        print("\n" + "-" * 60)
        print(f"Variable: {col}")
        print("-" * 60)

        # Basic distribution statistics
        print(f"Valid observations : {len(values):,}")
        print(f"Mean               : {values.mean():.2f}")
        print(f"Median             : {values.median():.2f}")
        print(f"Standard deviation : {values.std():.2f}")
        print(f"Skewness           : {values.skew():.2f}")
        print(f"Minimum            : {values.min():.2f}")
        print(f"Maximum            : {values.max():.2f}")

        # ----------------------------------------------------
        # STEP 3: Plot histogram and KDE curve
        # ----------------------------------------------------

        plt.figure(figsize=(8, 5))

        sns.histplot(
            values,
            bins="auto",
            kde=values.nunique() > 1,
            color="steelblue",
            edgecolor="white"
        )

        plt.title(
            f"Distribution of {col}",
            fontsize=14,
            fontweight="bold"
        )

        plt.xlabel(col)
        plt.ylabel("Frequency")
        plt.tight_layout()

        # ----------------------------------------------------
        # STEP 4: Save graph
        # ----------------------------------------------------

        filename = (
            col.lower().replace(" ", "_")
            + "_distribution.png"
        )

        graph_path = GRAPH_DIR / filename

        plt.savefig(
            graph_path,
            dpi=300,
            bbox_inches="tight"
        )

        print(f"Graph saved: {graph_path}")

        # Display graph
        plt.show()
        plt.close()

    print("\n" + "=" * 80)
    print("DISTRIBUTION ANALYSIS COMPLETED")
    print("=" * 80)




if __name__ == "__main__":

    DATA_PATH = Path(
        r"C:\Users\Priya Jeyakishore\OneDrive\Desktop\GUVI_Data_Science_ZenClass\Online_Food_Delivery_Analysis\cleaned_data\cleaned_online_food_delivery.csv"
    )

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}\n"
            "Update DATA_PATH to your actual cleaned CSV location."
        )

    df_clean = pd.read_csv(DATA_PATH)

    
