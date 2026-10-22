# ============================================================
# OPERATIONAL INSIGHTS ANALYSIS
# Project: Online Food Delivery Analysis
# Database: online_food_delivery_db
#
# Analyses:
# 13. Peak-hour demand analysis
# 14. Payment-mode preferences
# 15. Cancellation-reason analysis
#
# Outputs:
# output/sql_analysis/reports/operational/
# output/sql_analysis/graphs/operational/
# ============================================================

from pathlib import Path
import warnings

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sqlalchemy import text
from database.connection import create_db_engine


warnings.filterwarnings("ignore", category=FutureWarning)

# ============================================================
# 1. CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

REPORT_DIR = (
    PROJECT_ROOT
    / "output"
    / "sql_analysis"
    / "reports"
    / "operational"
)

GRAPH_DIR = (
    PROJECT_ROOT
    / "output"
    / "sql_analysis"
    / "graphs"
    / "operational"
)

REPORT_DIR.mkdir(parents=True, exist_ok=True)
GRAPH_DIR.mkdir(parents=True, exist_ok=True)

TABLE_NAME = "food_delivery_data"


# ============================================================
# 2. DATABASE CONNECTION
# ============================================================

def get_engine():
    """Create the existing project's MySQL database engine."""
    return create_db_engine()


def run_query(query):
    """Execute a SQL query and return its result as a DataFrame."""
    engine = get_engine()

    try:
        with engine.connect() as connection:
            df = pd.read_sql_query(text(query), connection)

        return df

    finally:
        engine.dispose()


# ============================================================
# 3. REPORT AND GRAPH UTILITIES
# ============================================================

def save_report(df, filename):
    """Save analysis results to CSV, including empty reports."""
    output_path = REPORT_DIR / filename

    df.to_csv(output_path, index=False)

    print(f"Report saved: {output_path}")

    if df.empty:
        print("No records were returned for this analysis.")
    else:
        print(df.to_string(index=False))

    return output_path


def save_no_data_graph(title, filename, message="No data available"):
    """Save a placeholder image when an analysis has no results."""
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.text(
        0.5,
        0.5,
        message,
        horizontalalignment="center",
        verticalalignment="center",
        transform=ax.transAxes,
        fontsize=13,
    )

    ax.set_title(title)
    ax.axis("off")

    plt.tight_layout()
    plt.savefig(GRAPH_DIR / filename, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"Placeholder graph saved: {GRAPH_DIR / filename}")


def save_bar_chart(
    df,
    x_column,
    y_column,
    title,
    x_label,
    y_label,
    filename,
    horizontal=False,
    percentage=False,
):
    """Create and save a bar chart safely."""

    if df.empty or x_column not in df.columns or y_column not in df.columns:
        save_no_data_graph(title, filename)
        return

    plot_df = df[[x_column, y_column]].dropna().copy()

    if plot_df.empty:
        save_no_data_graph(title, filename)
        return

    # Keep charts readable when categories have long labels.
    fig_height = max(5, min(10, len(plot_df) * 0.4)) if horizontal else 6
    fig, ax = plt.subplots(figsize=(11, fig_height))

    if horizontal:
        plot_df = plot_df.sort_values(y_column, ascending=True)

        sns.barplot(
            data=plot_df,
            x=y_column,
            y=x_column,
            ax=ax,
        )

        ax.set_xlabel(y_label)
        ax.set_ylabel(x_label)

    else:
        sns.barplot(
            data=plot_df,
            x=x_column,
            y=y_column,
            ax=ax,
        )

        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.tick_params(axis="x", rotation=30)

    if percentage:
        ax.set_ylabel(f"{y_label} (%)")

    ax.set_title(title)
    ax.grid(axis="y", linestyle="--", alpha=0.3)

    plt.tight_layout()

    output_path = GRAPH_DIR / filename
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"Graph saved: {output_path}")


# ============================================================
# 4. PEAK-HOUR DEMAND ANALYSIS
# ============================================================

def peak_hour_demand_analysis():
    """
    Analyse order demand, delivery outcomes, cancellation rate,
    and delivered revenue by peak-hour classification.
    """

    print("\n" + "=" * 80)
    print("13. PEAK-HOUR DEMAND ANALYSIS")
    print("=" * 80)

    query = f"""
        SELECT
            CASE
                WHEN Peak_Hour = 1 THEN 'Peak Hour'
                WHEN Peak_Hour = 0 THEN 'Off-Peak'
                ELSE 'Unknown'
            END AS Peak_Hour_Category,

            COUNT(*) AS Total_Orders,

            SUM(
                CASE
                    WHEN LOWER(TRIM(Order_Status)) = 'delivered'
                    THEN 1 ELSE 0
                END
            ) AS Delivered_Orders,

            SUM(
                CASE
                    WHEN LOWER(TRIM(Order_Status)) = 'cancelled'
                    THEN 1 ELSE 0
                END
            ) AS Cancelled_Orders,

            ROUND(
                100.0 * SUM(
                    CASE
                        WHEN LOWER(TRIM(Order_Status)) = 'cancelled'
                        THEN 1 ELSE 0
                    END
                ) / NULLIF(COUNT(*), 0),
                2
            ) AS Cancellation_Rate_Percent,

            ROUND(
                SUM(
                    CASE
                        WHEN LOWER(TRIM(Order_Status)) = 'delivered'
                        THEN COALESCE(Final_Amount, 0)
                        ELSE 0
                    END
                ),
                2
            ) AS Delivered_Revenue,

            ROUND(
                AVG(
                    CASE
                        WHEN LOWER(TRIM(Order_Status)) = 'delivered'
                        THEN Delivery_Time_Min
                        ELSE NULL
                    END
                ),
                2
            ) AS Average_Delivery_Time_Min

        FROM {TABLE_NAME}

        GROUP BY
            CASE
                WHEN Peak_Hour = 1 THEN 'Peak Hour'
                WHEN Peak_Hour = 0 THEN 'Off-Peak'
                ELSE 'Unknown'
            END

        ORDER BY Total_Orders DESC
    """

    df = run_query(query)

    save_report(df, "peak_hour_demand.csv")

    save_bar_chart(
        df,
        "Peak_Hour_Category",
        "Total_Orders",
        "Order Demand: Peak Hour vs Off-Peak",
        "Demand Category",
        "Total Orders",
        "peak_hour_order_demand.png",
    )

    save_bar_chart(
        df,
        "Peak_Hour_Category",
        "Cancellation_Rate_Percent",
        "Cancellation Rate by Peak-Hour Category",
        "Demand Category",
        "Cancellation Rate (%)",
        "peak_hour_cancellation_rate.png",
    )

    save_bar_chart(
        df,
        "Peak_Hour_Category",
        "Delivered_Revenue",
        "Delivered Revenue by Peak-Hour Category",
        "Demand Category",
        "Delivered Revenue",
        "peak_hour_delivered_revenue.png",
    )

    return df


# ============================================================
# 5. PAYMENT-MODE PREFERENCES
# ============================================================

def payment_mode_preferences_analysis():
    """
    Compare payment-mode popularity, share of all orders,
    delivered revenue, average order value, and cancellations.
    """

    print("\n" + "=" * 80)
    print("14. PAYMENT-MODE PREFERENCES")
    print("=" * 80)

    query = f"""
        SELECT
            COALESCE(
                NULLIF(TRIM(Payment_Mode), ''),
                'Unknown'
            ) AS Payment_Mode_Category,

            COUNT(*) AS Total_Orders,

            ROUND(
                100.0 * COUNT(*) / NULLIF(
                    (SELECT COUNT(*) FROM {TABLE_NAME}),
                    0
                ),
                2
            ) AS Order_Share_Percent,

            SUM(
                CASE
                    WHEN LOWER(TRIM(Order_Status)) = 'delivered'
                    THEN 1 ELSE 0
                END
            ) AS Delivered_Orders,

            SUM(
                CASE
                    WHEN LOWER(TRIM(Order_Status)) = 'cancelled'
                    THEN 1 ELSE 0
                END
            ) AS Cancelled_Orders,

            ROUND(
                100.0 * SUM(
                    CASE
                        WHEN LOWER(TRIM(Order_Status)) = 'cancelled'
                        THEN 1 ELSE 0
                    END
                ) / NULLIF(COUNT(*), 0),
                2
            ) AS Cancellation_Rate_Percent,

            ROUND(
                SUM(
                    CASE
                        WHEN LOWER(TRIM(Order_Status)) = 'delivered'
                        THEN COALESCE(Final_Amount, 0)
                        ELSE 0
                    END
                ),
                2
            ) AS Delivered_Revenue,

            ROUND(
                AVG(
                    CASE
                        WHEN LOWER(TRIM(Order_Status)) = 'delivered'
                        THEN Final_Amount
                        ELSE NULL
                    END
                ),
                2
            ) AS Average_Delivered_Order_Value

        FROM {TABLE_NAME}

        GROUP BY COALESCE(
            NULLIF(TRIM(Payment_Mode), ''),
            'Unknown'
        )

        ORDER BY Total_Orders DESC
    """

    df = run_query(query)

    save_report(df, "payment_mode_preferences.csv")

    save_bar_chart(
        df,
        "Payment_Mode_Category",
        "Total_Orders",
        "Customer Payment-Mode Preferences",
        "Payment Mode",
        "Total Orders",
        "payment_mode_order_count.png",
    )

    save_bar_chart(
        df,
        "Payment_Mode_Category",
        "Order_Share_Percent",
        "Order Share by Payment Mode",
        "Payment Mode",
        "Order Share (%)",
        "payment_mode_order_share.png",
    )

    save_bar_chart(
        df,
        "Payment_Mode_Category",
        "Delivered_Revenue",
        "Delivered Revenue by Payment Mode",
        "Payment Mode",
        "Delivered Revenue",
        "payment_mode_delivered_revenue.png",
    )

    return df


# ============================================================
# 6. CANCELLATION-REASON ANALYSIS
# ============================================================

def cancellation_reason_analysis():
    """
    Analyse cancellation reasons using cancelled orders only.
    Excludes delivered orders and their 'Not Applicable' reasons.
    """

    print("\n" + "=" * 80)
    print("15. CANCELLATION-REASON ANALYSIS")
    print("=" * 80)

    # --------------------------------------------------------
    # 6A. Overall cancellation reasons
    # --------------------------------------------------------

    reason_query = f"""
        SELECT
            COALESCE(
                NULLIF(TRIM(Cancellation_Reason), ''),
                'Unknown'
            ) AS Cancellation_Reason_Category,

            COUNT(*) AS Cancellation_Count,

            ROUND(
                100.0 * COUNT(*) / NULLIF(
                    (
                        SELECT COUNT(*)
                        FROM {TABLE_NAME}
                        WHERE LOWER(TRIM(Order_Status)) = 'cancelled'
                    ),
                    0
                ),
                2
            ) AS Cancellation_Share_Percent

        FROM {TABLE_NAME}

        WHERE LOWER(TRIM(Order_Status)) = 'cancelled'

        GROUP BY COALESCE(
            NULLIF(TRIM(Cancellation_Reason), ''),
            'Unknown'
        )

        ORDER BY Cancellation_Count DESC
    """

    reason_df = run_query(reason_query)

    save_report(
        reason_df,
        "cancellation_reasons.csv",
    )

    save_bar_chart(
        reason_df,
        "Cancellation_Reason_Category",
        "Cancellation_Count",
        "Order Cancellations by Reason",
        "Cancellation Reason",
        "Number of Cancellations",
        "cancellation_count_by_reason.png",
        horizontal=True,
    )

    save_bar_chart(
        reason_df,
        "Cancellation_Reason_Category",
        "Cancellation_Share_Percent",
        "Share of Cancellations by Reason",
        "Cancellation Reason",
        "Cancellation Share (%)",
        "cancellation_share_by_reason.png",
        horizontal=True,
    )

    # --------------------------------------------------------
    # 6B. Cancellation reasons by city
    # --------------------------------------------------------

    city_query = f"""
        SELECT
            COALESCE(
                NULLIF(TRIM(City), ''),
                'Unknown'
            ) AS City_Category,

            COALESCE(
                NULLIF(TRIM(Cancellation_Reason), ''),
                'Unknown'
            ) AS Cancellation_Reason_Category,

            COUNT(*) AS Cancellation_Count

        FROM {TABLE_NAME}

        WHERE LOWER(TRIM(Order_Status)) = 'cancelled'

        GROUP BY
            COALESCE(NULLIF(TRIM(City), ''), 'Unknown'),
            COALESCE(
                NULLIF(TRIM(Cancellation_Reason), ''),
                'Unknown'
            )

        ORDER BY City_Category, Cancellation_Count DESC
    """

    city_df = run_query(city_query)

    save_report(
        city_df,
        "cancellation_reasons_by_city.csv",
    )

    # --------------------------------------------------------
    # 6C. Cancellation reasons by peak-hour category
    # --------------------------------------------------------

    peak_query = f"""
        SELECT
            CASE
                WHEN Peak_Hour = 1 THEN 'Peak Hour'
                WHEN Peak_Hour = 0 THEN 'Off-Peak'
                ELSE 'Unknown'
            END AS Peak_Hour_Category,

            COALESCE(
                NULLIF(TRIM(Cancellation_Reason), ''),
                'Unknown'
            ) AS Cancellation_Reason_Category,

            COUNT(*) AS Cancellation_Count

        FROM {TABLE_NAME}

        WHERE LOWER(TRIM(Order_Status)) = 'cancelled'

        GROUP BY
            CASE
                WHEN Peak_Hour = 1 THEN 'Peak Hour'
                WHEN Peak_Hour = 0 THEN 'Off-Peak'
                ELSE 'Unknown'
            END,
            COALESCE(
                NULLIF(TRIM(Cancellation_Reason), ''),
                'Unknown'
            )

        ORDER BY Peak_Hour_Category, Cancellation_Count DESC
    """

    peak_df = run_query(peak_query)

    save_report(
        peak_df,
        "cancellation_reasons_by_peak_hour.csv",
    )

    # Create a stacked bar chart for cancellation reasons by peak hour.
    if not peak_df.empty:
        pivot_df = peak_df.pivot_table(
            index="Peak_Hour_Category",
            columns="Cancellation_Reason_Category",
            values="Cancellation_Count",
            aggfunc="sum",
            fill_value=0,
        )

        ax = pivot_df.plot(
            kind="bar",
            stacked=True,
            figsize=(11, 6),
        )

        ax.set_title("Cancellation Reasons: Peak Hour vs Off-Peak")
        ax.set_xlabel("Demand Category")
        ax.set_ylabel("Number of Cancellations")
        ax.tick_params(axis="x", rotation=0)
        ax.legend(
            title="Cancellation Reason",
            bbox_to_anchor=(1.02, 1),
            loc="upper left",
        )

        plt.tight_layout()

        graph_path = GRAPH_DIR / "cancellation_reasons_by_peak_hour.png"
        plt.savefig(graph_path, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"Graph saved: {graph_path}")

    else:
        save_no_data_graph(
            "Cancellation Reasons: Peak Hour vs Off-Peak",
            "cancellation_reasons_by_peak_hour.png",
        )

    return reason_df, city_df, peak_df


# ============================================================
# 7. RUN ALL OPERATIONAL INSIGHTS
# ============================================================

def run_operational_insights_analysis():
    """Run all three operational analyses independently."""

    print("\n" + "#" * 80)
    print("OPERATIONAL INSIGHTS ANALYSIS STARTED")
    print("#" * 80)

    analyses = [
        ("Peak-hour demand analysis", peak_hour_demand_analysis),
        ("Payment-mode preferences", payment_mode_preferences_analysis),
        ("Cancellation-reason analysis", cancellation_reason_analysis),
    ]

    for analysis_name, analysis_function in analyses:
        try:
            analysis_function()

        except Exception as error:
            print(f"\nERROR in {analysis_name}: {error}")
            print("Continuing with the next operational analysis.")

    print("\n" + "#" * 80)
    print("OPERATIONAL INSIGHTS ANALYSIS COMPLETED")
    print("#" * 80)

    print(f"\nReports folder: {REPORT_DIR}")
    print(f"Graphs folder: {GRAPH_DIR}")


# ============================================================
# 8. SCRIPT ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_operational_insights_analysis()