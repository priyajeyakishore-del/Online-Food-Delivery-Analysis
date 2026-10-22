
# ============================================================
# STEP 4: BOXPLOT ANALYSIS
# Purpose:
# 1. Visualize potential outliers
# 2. Understand data spread
# 3. Identify median location
# 4. Save boxplots and outlier reports
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from pathlib import Path

from data_analysis.univariate_analysis.config import NUMERICAL_COLS


# ============================================================
# OUTPUT DIRECTORIES
# ============================================================

GRAPH_DIR = Path(
    r"C:\Users\Priya Jeyakishore\OneDrive\Desktop\GUVI_Data_Science_ZenClass\Online_Food_Delivery_Analysis\output\graphs\univariate_analysis\numerical\box_plot"
)

REPORT_DIR = Path(
    r"C:\Users\Priya Jeyakishore\OneDrive\Desktop\GUVI_Data_Science_ZenClass\Online_Food_Delivery_Analysis\output\reports\univariate_analysis"
)

GRAPH_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# FUNCTION: BOXPLOT ANALYSIS
# ============================================================

def boxplot_analysis(df):

    print("\n" + "=" * 70)
    print("STEP 4: BOXPLOT ANALYSIS")
    print("=" * 70)

    outlier_report = []

    # Use only numerical columns that exist in the dataset
    available_cols = [
        col for col in NUMERICAL_COLS
        if col in df.columns
    ]

    if not available_cols:
        print("No configured numerical columns found.")
        return pd.DataFrame()

    for col in available_cols:

        # Convert values to numeric without modifying original data
        values = pd.to_numeric(
            df[col],
            errors="coerce"
        ).dropna()

        if values.empty:
            print(f"\nSkipping {col}: no valid numerical values.")
            continue

        # ----------------------------------------------------
        # Calculate quartiles and IQR
        # ----------------------------------------------------

        Q1 = values.quantile(0.25)
        median = values.median()
        Q3 = values.quantile(0.75)

        IQR = Q3 - Q1

        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        # Identify potential outliers using the IQR rule
        outliers = values[
            (values < lower_bound) |
            (values > upper_bound)
        ]

        outlier_count = len(outliers)
        outlier_percentage = (
            outlier_count / len(values)
        ) * 100

        # ----------------------------------------------------
        # Print summary
        # ----------------------------------------------------

        print(f"\nColumn: {col}")
        print("-" * 50)
        print(f"Valid values       : {len(values):,}")
        print(f"Minimum            : {values.min():.2f}")
        print(f"Q1                 : {Q1:.2f}")
        print(f"Median             : {median:.2f}")
        print(f"Q3                 : {Q3:.2f}")
        print(f"Maximum            : {values.max():.2f}")
        print(f"IQR                : {IQR:.2f}")
        print(f"Lower bound        : {lower_bound:.2f}")
        print(f"Upper bound        : {upper_bound:.2f}")
        print(f"Potential outliers : {outlier_count:,}")
        print(f"Outlier percentage : {outlier_percentage:.2f}%")

        # ----------------------------------------------------
        # Store outlier summary
        # ----------------------------------------------------

        outlier_report.append({
            "Column": col,
            "Valid_Count": len(values),
            "Minimum": values.min(),
            "Q1": Q1,
            "Median": median,
            "Q3": Q3,
            "Maximum": values.max(),
            "IQR": IQR,
            "Lower_Bound": lower_bound,
            "Upper_Bound": upper_bound,
            "Outlier_Count": outlier_count,
            "Outlier_Percentage": outlier_percentage
        })

        # ----------------------------------------------------
        # Plot boxplot
        # ----------------------------------------------------

        plt.figure(figsize=(8, 4))

        sns.boxplot(
            x=values,
            color="skyblue"
        )

        plt.title(f"Boxplot of {col}")
        plt.xlabel(col)
        plt.tight_layout()

        # Save graph
        graph_path = GRAPH_DIR / (
            col.lower().replace(" ", "_") + "_boxplot.png"
        )

        plt.savefig(
            graph_path,
            dpi=300,
            bbox_inches="tight"
        )

        plt.show()
        plt.close()

        print(f"Graph saved to: {graph_path}")

    # ========================================================
    # SAVE OUTLIER REPORT
    # ========================================================

    report_df = pd.DataFrame(outlier_report)

    if not report_df.empty:

        report_path = REPORT_DIR / "boxplot_outlier_report.csv"

        report_df.to_csv(
            report_path,
            index=False
        )

        print("\n" + "=" * 70)
        print("OUTLIER ANALYSIS SUMMARY")
        print("=" * 70)

        print(
            report_df[
                ["Column", "Outlier_Count", "Outlier_Percentage"]
            ].to_string(index=False)
        )

        print(f"\nReport saved to: {report_path}")

    return report_df
