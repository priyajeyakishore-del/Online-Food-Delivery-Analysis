# ============================================================
# BUSINESS INSIGHTS REPORT
# PROJECT: ONLINE FOOD DELIVERY ANALYSIS
# FILE: business_insights_report.py
# PURPOSE: Generate one consolidated business insights report
# ============================================================

from pathlib import Path

# ============================================================
# IMPORT BUSINESS INSIGHTS MODULES
# ============================================================

from data_analysis.business_insights.executive_summary import (
    executive_summary
)

from data_analysis.business_insights.data_overview import (
    data_overview
)

from data_analysis.business_insights.key_findings import (
    key_findings
)

from data_analysis.business_insights.kpi_analysis import (
    kpi_analysis
)

from data_analysis.business_insights.trend_analysis import (
    trend_analysis
)

from data_analysis.business_insights.root_cause_analysis import (
    root_cause_analysis
)

from data_analysis.business_insights.recommendations import (
    recommendations
)

from data_analysis.business_insights.business_impact import (
    business_impact
)


# ============================================================
# 1. PATH CONFIGURATION
# ============================================================

# This script is saved inside the project's src directory.
# parents[0] = src
# parents[1] = Online_Food_Delivery_Analysis

PROJECT_DIR = Path(__file__).resolve().parents[1]

OUTPUT_DIR = PROJECT_DIR / "output"

REPORT_DIR = (
    OUTPUT_DIR
    / "reports"
    / "business_insights"
)

REPORT_FILE = REPORT_DIR / "business_insights_report.txt"

KPI_FILE = REPORT_DIR / "business_kpi_summary.csv"

# Create the report directory if it does not exist.
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. MAIN BUSINESS INSIGHTS FUNCTION
# ============================================================

def run_business_insights(df):
    """
    Generate, save, and display the complete business insights report.

    Parameters
    ----------
    df : pandas.DataFrame
        Already-loaded and cleaned food delivery dataset.

    Returns
    -------
    str
        Complete consolidated business insights report.
    """

    # --------------------------------------------------------
    # Validate the input dataset
    # --------------------------------------------------------

    if df is None:
        raise ValueError(
            "Dataset is None. Please provide a valid DataFrame."
        )

    if df.empty:
        raise ValueError(
            "Dataset is empty. Please provide a non-empty DataFrame."
        )

    print("=" * 75)
    print("GENERATING BUSINESS INSIGHTS REPORT")
    print("=" * 75)

    # --------------------------------------------------------
    # Calculate KPIs once.
    # kpi_analysis(df) must return:
    #     report_text, kpis
    # --------------------------------------------------------

    kpi_section, kpis = kpi_analysis(df)

    # --------------------------------------------------------
    # 1. EXECUTIVE SUMMARY
    # --------------------------------------------------------

    executive_summary_report = executive_summary(
        df,
        kpis
    )

    # --------------------------------------------------------
    # 2. DATA OVERVIEW
    # --------------------------------------------------------

    data_overview_report = data_overview(df)

    # --------------------------------------------------------
    # 3. KEY FINDINGS
    # --------------------------------------------------------

    key_findings_report = key_findings(df)

    # --------------------------------------------------------
    # 4. KPI ANALYSIS
    # --------------------------------------------------------

    # Already calculated above to avoid duplicate calculations.
    kpi_analysis_report = kpi_section

    # --------------------------------------------------------
    # 5. TREND ANALYSIS
    # --------------------------------------------------------

    trend_analysis_report = trend_analysis(df)

    # --------------------------------------------------------
    # 6. ROOT CAUSE ANALYSIS
    # --------------------------------------------------------

    root_cause_report = root_cause_analysis(df)

    # --------------------------------------------------------
    # 7. RECOMMENDATIONS
    # --------------------------------------------------------

    recommendations_report = recommendations(df)

    # --------------------------------------------------------
    # 8. BUSINESS IMPACT
    # --------------------------------------------------------

    business_impact_report = business_impact(
        df,
        kpis
    )

    # --------------------------------------------------------
    # COMBINE ALL EIGHT SECTIONS IN THE REQUIRED ORDER
    # --------------------------------------------------------

    report_sections = [
        executive_summary_report,
        data_overview_report,
        key_findings_report,
        kpi_analysis_report,
        trend_analysis_report,
        root_cause_report,
        recommendations_report,
        business_impact_report
    ]

    complete_report = "\n\n".join(
        section.strip()
        for section in report_sections
        if isinstance(section, str) and section.strip()
    )

    # --------------------------------------------------------
    # SAVE THE COMPLETE REPORT
    # --------------------------------------------------------

    REPORT_FILE.write_text(
        complete_report,
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # DISPLAY THE REPORT ONLY ONCE
    # --------------------------------------------------------

    print("\n")
    print(complete_report)

    # --------------------------------------------------------
    # DISPLAY OUTPUT FILE LOCATIONS
    # --------------------------------------------------------

    print("\n" + "=" * 75)
    print("BUSINESS INSIGHTS REPORT GENERATED SUCCESSFULLY")
    print("=" * 75)

    print(f"\nProject directory : {PROJECT_DIR}")
    print(f"Report directory  : {REPORT_DIR}")
    print(f"Report file       : {REPORT_FILE}")

    if KPI_FILE.exists():
        print(f"KPI summary file  : {KPI_FILE}")
    else:
        print(
            "KPI summary file  : Not found at the expected path. "
            "Check the save path in kpi_analysis.py."
        )

    print("\nSections included:")

    section_names = [
        "1. Executive Summary",
        "2. Data Overview",
        "3. Key Findings",
        "4. KPI Analysis",
        "5. Trend Analysis",
        "6. Root Cause Analysis",
        "7. Recommendations",
        "8. Business Impact"
    ]

    for section_name in section_names:
        print(f"   {section_name}")

    return complete_report


# ============================================================
# 3. SCRIPT EXECUTION
# ============================================================

if __name__ == "__main__":

    import pandas as pd

    # --------------------------------------------------------
    # Dataset path
    # --------------------------------------------------------

    DATA_FILE = (
        PROJECT_DIR
        / "output"
        / "cleaned_online_food_delivery_dataset.csv"
    )

    # --------------------------------------------------------
    # Check whether the cleaned dataset exists
    # --------------------------------------------------------

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            "\nCleaned dataset not found.\n"
            f"Expected location:\n{DATA_FILE}\n\n"
            "Please check the file name and output directory."
        )

    # --------------------------------------------------------
    # Load the cleaned dataset only when this script is run
    # directly. Imported use of run_business_insights(df)
    # does not reload the dataset.
    # --------------------------------------------------------

    df = pd.read_csv(DATA_FILE)

    print(f"Dataset loaded successfully: {DATA_FILE}")
    print(f"Dataset shape: {df.shape}")

    # --------------------------------------------------------
    # Generate the complete report
    # --------------------------------------------------------

    run_business_insights(df)