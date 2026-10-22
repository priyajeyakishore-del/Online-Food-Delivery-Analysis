
# ============================================================
# CATEGORICAL UNIVARIATE ANALYSIS
# Purpose:
# 1. Frequency counts
# 2. Category percentages
# 3. Unique category counts
# 4. Missing value analysis
# 5. Bar charts
# 6. Save reports and graphs
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from pathlib import Path

from data_analysis.univariate_analysis.config import CATEGORICAL_COLS


# ============================================================
# OUTPUT DIRECTORIES
# ============================================================

BASE_DIR = Path(
    r"C:\Users\Priya Jeyakishore\OneDrive\Desktop\GUVI_Data_Science_ZenClass\Online_Food_Delivery_Analysis\output"
)

GRAPH_DIR = BASE_DIR / "graphs" / "univariate_analysis" / "categorical"
REPORT_DIR = BASE_DIR / "reports" / "univariate_analysis"

GRAPH_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# FUNCTION: CATEGORICAL ANALYSIS
# ============================================================

def categorical_analysis(df):

    print("\n" + "=" * 70)
    print("CATEGORICAL UNIVARIATE ANALYSIS")
    print("=" * 70)

    summary_rows = []

    for col in CATEGORICAL_COLS:

        if col not in df.columns:
            print(f"\nSkipping {col}: column not found.")
            continue

        print(f"\n{'=' * 60}")
        print(f"Column: {col}")
        print("=" * 60)

        # ----------------------------------------------------
        # Frequency counts
        # ----------------------------------------------------

        # Keep missing values visible in the frequency report
        counts = (
            df[col]
            .astype("string")
            .fillna("Missing")
            .value_counts(dropna=False)
        )

        percentages = counts / len(df) * 100

        frequency_df = pd.DataFrame({
            "Category": counts.index.astype(str),
            "Frequency": counts.values,
            "Percentage": percentages.values
        })

        print(f"Unique categories: {df[col].nunique(dropna=True)}")
        print(f"Missing values: {df[col].isna().sum():,}")
        print("\nFrequency distribution:")
        print(frequency_df.to_string(index=False))

        # ----------------------------------------------------
        # Save frequency report
        # ----------------------------------------------------

        report_path = REPORT_DIR / f"{col.lower()}_frequency.csv"

        frequency_df.to_csv(report_path, index=False)

        # ----------------------------------------------------
        # Summary statistics
        # ----------------------------------------------------

        summary_rows.append({
            "Column": col,
            "Unique_Categories": df[col].nunique(dropna=True),
            "Missing_Count": df[col].isna().sum(),
            "Missing_Percentage": df[col].isna().mean() * 100,
            "Most_Frequent_Category": (
                str(df[col].mode(dropna=True).iloc[0])
                if not df[col].mode(dropna=True).empty
                else "No valid category"
            ),
            "Most_Frequent_Count": (
                int(df[col].value_counts().iloc[0])
                if not df[col].value_counts().empty
                else 0
            )
        })

        # ----------------------------------------------------
        # Bar chart
        # ----------------------------------------------------

        # Limit long categories to the top 20 for readability
        plot_data = counts.head(20).sort_values(ascending=False)

        plt.figure(figsize=(10, 5))

        sns.barplot(
            x=plot_data.values,
            y=plot_data.index.astype(str),
            color="steelblue"
        )

        plt.title(f"Category Frequency: {col}")
        plt.xlabel("Number of Records")
        plt.ylabel(col)
        plt.tight_layout()

        graph_path = GRAPH_DIR / f"{col.lower()}_frequency.png"

        plt.savefig(
            graph_path,
            dpi=300,
            bbox_inches="tight"
        )

        plt.show()
        plt.close()

        print(f"\nFrequency report saved: {report_path}")
        print(f"Graph saved: {graph_path}")

    # ========================================================
    # SAVE OVERALL SUMMARY
    # ========================================================

    summary_df = pd.DataFrame(summary_rows)

    summary_path = REPORT_DIR / "categorical_analysis_summary.csv"

    summary_df.to_csv(summary_path, index=False)

    print("\n" + "=" * 70)
    print("CATEGORICAL ANALYSIS SUMMARY")
    print("=" * 70)

    print(summary_df.to_string(index=False))
    print(f"\nSummary saved: {summary_path}")

    return summary_df
