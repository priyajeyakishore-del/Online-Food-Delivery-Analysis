
# ============================================================
# BIVARIATE ANALYSIS: CATEGORICAL vs CATEGORICAL
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from pathlib import Path
from data_analysis.univariate_analysis.config import CATEGORICAL_COLS


BASE_DIR = Path(
    r"C:\Users\Priya Jeyakishore\OneDrive\Desktop\GUVI_Data_Science_ZenClass\Online_Food_Delivery_Analysis\output"
)

GRAPH_DIR = BASE_DIR / "graphs" / "bivariate_analysis" / "categorical_vs_categorical"
REPORT_DIR = BASE_DIR / "reports" / "bivariate_analysis" / "categorical_vs_categorical"

GRAPH_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def categorical_vs_categorical(df):

    print("\n" + "=" * 70)
    print("CATEGORICAL vs CATEGORICAL ANALYSIS")
    print("=" * 70)

    # Business-relevant categorical pairs
    pairs = [
        ("City", "Order_Status"),
        ("Payment_Mode", "Order_Status"),
        ("Cuisine_Type", "Order_Status"),
        ("Customer_Gender", "Order_Status"),
        ("Peak_Hour", "Order_Status"),
    ]

    # Keep only pairs whose columns exist
    pairs = [
        (x, y) for x, y in pairs
        if x in CATEGORICAL_COLS
        and y in CATEGORICAL_COLS
        and x in df.columns
        and y in df.columns
    ]

    for x_col, y_col in pairs:

        print(f"\n{'=' * 60}")
        print(f"{x_col} vs {y_col}")
        print("=" * 60)

        # Exclude missing categories from the relationship calculation
        data = df[[x_col, y_col]].dropna().copy()

        if data.empty:
            print("No complete rows available.")
            continue

        # Frequency table
        frequency = pd.crosstab(
            data[x_col],
            data[y_col]
        )

        # Percentage within each row/category
        row_percentage = pd.crosstab(
            data[x_col],
            data[y_col],
            normalize="index"
        ).mul(100).round(2)

        print("\nFrequency table:")
        print(frequency)

        print("\nRow percentages (%):")
        print(row_percentage)

        # Save reports
        frequency.to_csv(
            REPORT_DIR / f"{x_col.lower()}_vs_{y_col.lower()}_frequency.csv"
        )

        row_percentage.to_csv(
            REPORT_DIR / f"{x_col.lower()}_vs_{y_col.lower()}_percentages.csv"
        )

        # Plot top 15 categories to keep charts readable
        top_categories = data[x_col].value_counts().head(15).index
        plot_data = frequency.loc[
            frequency.index.isin(top_categories)
        ]

        plot_data.plot(
            kind="bar",
            stacked=True,
            figsize=(11, 6)
        )

        plt.title(f"{x_col} vs {y_col}")
        plt.xlabel(x_col)
        plt.ylabel("Number of Orders")
        plt.xticks(rotation=45, ha="right")
        plt.legend(title=y_col)
        plt.tight_layout()

        graph_path = GRAPH_DIR / (
            f"{x_col.lower()}_vs_{y_col.lower()}.png"
        )

        plt.savefig(graph_path, dpi=300, bbox_inches="tight")
        plt.show()
        plt.close()

        print(f"\nGraph saved: {graph_path}")

    # --------------------------------------------------------
    # Cancellation rate by city
    # --------------------------------------------------------

    if {"City", "Order_Status"}.issubset(df.columns):

        valid = df[["City", "Order_Status"]].dropna().copy()

        valid = valid[
            valid["Order_Status"].isin(["Delivered", "Cancelled"])
        ]

        if not valid.empty:

            city_summary = (
                valid.assign(
                    Is_Cancelled=(
                        valid["Order_Status"] == "Cancelled"
                    ).astype(int)
                )
                .groupby("City")
                .agg(
                    Total_Orders=("Is_Cancelled", "size"),
                    Cancelled_Orders=("Is_Cancelled", "sum"),
                    Cancellation_Rate=("Is_Cancelled", "mean")
                )
                .reset_index()
            )

            city_summary["Cancellation_Rate"] *= 100

            city_summary = city_summary.sort_values(
                "Cancellation_Rate",
                ascending=False
            )

            city_summary.to_csv(
                REPORT_DIR / "cancellation_rate_by_city.csv",
                index=False
            )

            print("\nCancellation rate by city:")
            print(city_summary.to_string(index=False))

    print("\nCategorical bivariate analysis completed.")

