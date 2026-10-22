
# ============================================================
# BIVARIATE ANALYSIS: NUMERICAL vs CATEGORICAL
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from pathlib import Path

from data_analysis.univariate_analysis.config import (
    NUMERICAL_COLS,
    CATEGORICAL_COLS
)


BASE_DIR = Path(
    r"C:\Users\Priya Jeyakishore\OneDrive\Desktop\GUVI_Data_Science_ZenClass\Online_Food_Delivery_Analysis\output"
)

GRAPH_DIR = BASE_DIR / "graphs" / "bivariate_analysis" / "numerical_vs_categorical"
REPORT_DIR = BASE_DIR / "reports" / "bivariate_analysis" / "numerical_vs_categorical"

GRAPH_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def numerical_vs_categorical(df):

    print("\n" + "=" * 70)
    print("NUMERICAL vs CATEGORICAL ANALYSIS")
    print("=" * 70)

    # Selected business-relevant pairs
    pairs = [
        ("Delivery_Time_Min", "Order_Status"),
        ("Order_Value", "Payment_Mode"),
        ("Customer_Age", "Order_Status"),
        ("Profit_Margin", "Cuisine_Type"),
        ("Final_Amount", "Order_Status"),
        ("Distance_km", "Order_Status"),
        ("Restaurant_Rating", "Cuisine_Type"),
        ("Delivery_Rating", "Order_Status"),
    ]

    pairs = [
        (num_col, cat_col)
        for num_col, cat_col in pairs
        if num_col in NUMERICAL_COLS
        and cat_col in CATEGORICAL_COLS
        and num_col in df.columns
        and cat_col in df.columns
    ]

    all_summaries = []

    for num_col, cat_col in pairs:

        print(f"\n{'=' * 60}")
        print(f"{num_col} by {cat_col}")
        print("=" * 60)

        data = df[[num_col, cat_col]].copy()

        data[num_col] = pd.to_numeric(
            data[num_col],
            errors="coerce"
        )

        data = data.dropna(subset=[num_col, cat_col])

        if data.empty:
            print("No valid observations available.")
            continue

        # Limit high-cardinality categories to the top 15
        top_categories = (
            data[cat_col]
            .value_counts()
            .head(15)
            .index
        )

        plot_data = data[
            data[cat_col].isin(top_categories)
        ].copy()

        # ----------------------------------------------------
        # Grouped statistical summary
        # ----------------------------------------------------

        summary = (
            data.groupby(cat_col)[num_col]
            .agg(
                Count="count",
                Mean="mean",
                Median="median",
                Std="std",
                Minimum="min",
                Maximum="max"
            )
            .reset_index()
        )

        summary.insert(0, "Numerical_Column", num_col)
        summary.insert(1, "Categorical_Column", cat_col)

        all_summaries.append(summary)

        print(summary.to_string(index=False))

        # Save individual report
        report_path = REPORT_DIR / (
            f"{num_col.lower()}_by_{cat_col.lower()}.csv"
        )

        summary.to_csv(report_path, index=False)

        # ----------------------------------------------------
        # Boxplot
        # ----------------------------------------------------

        plt.figure(figsize=(11, 6))

        sns.boxplot(
            data=plot_data,
            x=cat_col,
            y=num_col,
            color="skyblue"
        )

        plt.title(f"{num_col} by {cat_col}")
        plt.xlabel(cat_col)
        plt.ylabel(num_col)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        graph_path = GRAPH_DIR / (
            f"{num_col.lower()}_by_{cat_col.lower()}.png"
        )

        plt.savefig(
            graph_path,
            dpi=300,
            bbox_inches="tight"
        )

        plt.show()
        plt.close()

        print(f"Report saved: {report_path}")
        print(f"Graph saved: {graph_path}")

    # --------------------------------------------------------
    # Combined summary report
    # --------------------------------------------------------

    if all_summaries:

        combined_summary = pd.concat(
            all_summaries,
            ignore_index=True
        )

        combined_path = REPORT_DIR / (
            "numerical_by_categorical_summary.csv"
        )

        combined_summary.to_csv(
            combined_path,
            index=False
        )

        print(f"\nCombined report saved: {combined_path}")

        return combined_summary

    print("No valid numerical-categorical pairs found.")
    return pd.DataFrame()

