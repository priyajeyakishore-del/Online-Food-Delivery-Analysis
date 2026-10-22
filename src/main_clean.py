import pandas as pd
from pathlib import Path
from contextlib import redirect_stdout

from cleaning.order_outcome_cleaning import clean_order_outcome
from cleaning.payment_info_clean import clean_payment_mode
from cleaning.customer_info_clean import clean_customer_data
from cleaning.location_cleaning import clean_location_data
from cleaning.financial_cleaning import clean_financial_data
from cleaning.final_amount_clean import clean_final_amount
from cleaning.restaurant_cleaning import clean_restaurant_data
from cleaning.order_cleaning import clean_order_information
from cleaning.clean_delivery_information import clean_delivery_information
from cleaning.profit_margin import verify_profit_margin_formula
from cleaning.compare import compare_dataset_before_after


# File paths
PROJECT_DIR = Path(__file__).resolve().parents[1]

file_path = PROJECT_DIR / "raw_data" / "online_food_delivery_dataset.csv"
output_path = PROJECT_DIR / "output" / "Data_Cleaning" / "cleaned_online_food_delivery_dataset.csv"
report_path = PROJECT_DIR / "output" / "Data_Cleaning" / "data_cleaning_report.txt"

# Create output folders
output_path.parent.mkdir(parents=True, exist_ok=True)
report_path.parent.mkdir(parents=True, exist_ok=True)


# Load raw dataset
df = pd.read_csv(file_path)
df_raw = df.copy()

# Save all cleaning output to the report
with open(report_path, "w", encoding="utf-8") as report, redirect_stdout(report):

    print("DATA CLEANING REPORT")
    print("=" * 60)

    df = clean_order_outcome(df, analyze_before=True)
    df = clean_payment_mode(df)
    df = clean_customer_data(df, analyze_before=True)
    df = clean_location_data(df)
    df = clean_financial_data(df)
    df = clean_final_amount(df)
    df = clean_restaurant_data(df)
    df = clean_order_information(df)
    df = clean_delivery_information(df)

    # Verify Profit_Margin without changing its original values
    decision = verify_profit_margin_formula(df)

    # Compare before and after cleaning
    comparison_report = compare_dataset_before_after(
        df_raw=df_raw,
        df=df
    )

    # Save cleaned dataset
    df.to_csv(output_path, index=False)

    print("\nDATA CLEANING COMPLETED")
    print(f"Final dataset shape: {df.shape}")
    print(f"Remaining missing values: {df.isna().sum().sum()}")
    print(f"Cleaned dataset saved to: {output_path}")
    print(f"Report saved to: {report_path}")

print(f"Cleaning report saved to: {report_path}")
print(f"Cleaned dataset saved to: {output_path}")