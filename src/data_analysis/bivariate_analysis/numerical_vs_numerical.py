
# ============================================================
# BIVARIATE ANALYSIS: NUMERICAL vs NUMERICAL
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from pathlib import Path
from itertools import combinations

from data_analysis.univariate_analysis.config import NUMERICAL_COLS


BASE_DIR = Path(
    r"C:\Users\Priya Jeyakishore\OneDrive\Desktop\GUVI_Data_Science_ZenClass\Online_Food_Delivery_Analysis\output"
)

GRAPH_DIR = BASE_DIR / "graphs" / "bivariate_analysis" / "numerical_vs_numerical"
REPORT_DIR = BASE_DIR / "reports" / "bivariate_analysis" / "numerical_vs_numerical"

GRAPH_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def numerical_vs_numerical(df):

    print("\n" + "=" * 70)
    print("NUMERICAL vs NUMERICAL ANALYSIS")
    print("=" * 70)

    available_cols = [
        col for col in NUMERICAL_COLS
        if col in df.columns
    ]

    if len(available_cols) < 2:
        print("At least two numerical columns are required.")
        return pd.DataFrame()

    numeric_df = df[available_cols].apply(
        pd.to_numeric,
        errors="coerce"
    )

    # Correlation matrix
    correlation = numeric_df.corr(method="pearson")

    print("\nPearson correlation matrix:")
    print(correlation.round(3))

    correlation.to_csv(
        REPORT_DIR / "numerical_correlation_matrix.csv"
    )

    # Heatmap
    plt.figure(figsize=(11, 8))

    sns.heatmap(
        correlation,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        vmin=-1,
        vmax=1
    )

    plt.title("Numerical Variables Correlation Matrix")
    plt.tight_layout()

    plt.savefig(
        GRAPH_DIR / "correlation_heatmap.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()
    plt.close()

    # Selected pairs with clear business meaning
    preferred_pairs = [
        ("Distance_km", "Delivery_Time_Min"),
        ("Order_Value", "Final_Amount"),
        ("Customer_Age", "Order_Value"),
        ("Restaurant_Rating", "Delivery_Rating"),
        ("Discount_Applied", "Final_Amount"),
    ]

    pairs = [
        pair for pair in preferred_pairs
        if pair[0] in numeric_df.columns
        and pair[1] in numeric_df.columns
    ]

    # Add other pairs only if none of the preferred pairs are available
    if not pairs:
        pairs = list(combinations(available_cols, 2))

    correlation_rows = []

    for x_col, y_col in pairs:

        pair_data = numeric_df[[x_col, y_col]].dropna()

        if len(pair_data) < 2:
            continue

        r = pair_data[x_col].corr(pair_data[y_col])

        correlation_rows.append({
            "Variable_1": x_col,
            "Variable_2": y_col,
            "Valid_Pairs": len(pair_data),
            "Pearson_Correlation": r
        })

        print(f"\n{x_col} vs {y_col}")
        print(f"Valid pairs: {len(pair_data):,}")
        print(f"Pearson correlation: {r:.3f}")

        # Scatter plot
        plt.figure(figsize=(8, 5))

        sns.scatterplot(
            data=pair_data,
            x=x_col,
            y=y_col,
            alpha=0.35
        )

        plt.title(f"{x_col} vs {y_col} (r = {r:.2f})")
        plt.tight_layout()

        graph_path = GRAPH_DIR / (
            f"{x_col.lower()}_vs_{y_col.lower()}.png"
        )

        plt.savefig(
            graph_path,
            dpi=300,
            bbox_inches="tight"
        )

        plt.show()
        plt.close()

    report = pd.DataFrame(correlation_rows)

    report.to_csv(
        REPORT_DIR / "selected_pair_correlations.csv",
        index=False
    )

    print("\nNumerical bivariate analysis completed.")

    return report

