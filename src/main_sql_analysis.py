# ============================================================
# MAIN SQL ANALYSIS RUNNER
# File: src/main_sql_analysis.py
# Project: Online Food Delivery Analysis
# ============================================================

from pathlib import Path
import sys

# ============================================================
# 1. PROJECT PATH CONFIGURATION
# ============================================================

SRC_DIR = Path(__file__).resolve().parent

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


# ============================================================
# 2. IMPORT SQL ANALYSIS MODULES
# ============================================================

from sql_analysis.customer_analysis import run_customer_analysis
from sql_analysis.revenue_profit_analysis import run_revenue_profit_analysis
from sql_analysis.delivery_analysis import run_delivery_performance_analysis
from sql_analysis.restaurant_analysis import run_restaurant_performance_analysis
from sql_analysis.operational_analysis import run_operational_insights_analysis


# ============================================================
# 3. MAIN FUNCTION
# ============================================================

def main():
    """Run all SQL-based analyses."""

    print("\n" + "=" * 70)
    print("ONLINE FOOD DELIVERY ANALYSIS")
    print("SQL ANALYSIS PIPELINE")
    print("=" * 70)

    # --------------------------------------------------------
    # 3.1 Customer and Order Analysis
    # --------------------------------------------------------

    print("\n[1/5] CUSTOMER & ORDER ANALYSIS")

    run_customer_analysis()

    # --------------------------------------------------------
    # 3.2 Revenue and Profit Analysis
    # --------------------------------------------------------

    print("\n[2/5] REVENUE & PROFIT ANALYSIS")
    run_revenue_profit_analysis()

    # --------------------------------------------------------
    # 3.3 Delivery Analysis
    # --------------------------------------------------------

    print("\n[3/5] DELIVERY ANALYSIS")
    run_delivery_performance_analysis()

    # --------------------------------------------------------
    # 3.4 Restaurant Analysis
    # --------------------------------------------------------

    print("\n[4/5] RESTAURANT ANALYSIS")
    run_restaurant_performance_analysis()

    # --------------------------------------------------------
    # 3.5 Operational Analysis
    # --------------------------------------------------------

    print("\n[5/5] OPERATIONAL ANALYSIS")
    run_operational_insights_analysis()

    print("\n" + "=" * 70)
    print("SQL ANALYSIS PIPELINE COMPLETED")
    print("=" * 70)


# ============================================================
# 4. ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()