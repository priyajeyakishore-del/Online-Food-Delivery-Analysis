
# ============================================================
# ONLINE FOOD DELIVERY ANALYSIS
# Data Collection and Understanding of Data
# Tools: Python, Pandas, NumPy, Matplotlib, Seaborn
# Dataset: Online Food Delivery Dataset
# ============================================================

import sys

# Save the original console output
original_stdout = sys.stdout

# Redirect output to a text file
output_file = open(
    "data_understanding_output.txt",
    "w",
    encoding="utf-8"
)

sys.stdout = output_file


try:

    # ============================================================
    # SECTION 1: IMPORT LIBRARIES AND LOAD DATASET
    # ============================================================

    import pandas as pd

    # File path
    file_path = r"C:\Users\Priya Jeyakishore\OneDrive\Desktop\GUVI_Data_Science_ZenClass\Online_Food_Delivery_Analysis\raw_data\online_food_delivery_dataset.csv"

    # Load the raw dataset
    df = pd.read_csv(file_path)


    # ============================================================
    # SECTION 2: DATASET OVERVIEW
    # ============================================================

    print("\n" + "=" * 60)
    print("SECTION 2: DATASET OVERVIEW")
    print("=" * 60)

    # Display the total number of records and features
    print("Total Records:", df.shape[0])
    print("Total Features:", df.shape[1])

    print("\nDataset Preview:")
    print(df.head().to_string())

    print("\nDataset Information:")
    print(df.info())

    print("\nColumn Names:")
    print(df.columns.tolist())


    # ============================================================
    # SECTION 3: FEATURE CATEGORIZATION
    # ============================================================

    print("\n" + "=" * 80)
    print("SECTION 3: FEATURE CATEGORIZATION")
    print("=" * 80)

    feature_categories = {

        "Customer Information": [
            "Customer_ID",
            "Customer_Age",
            "Customer_Gender"
        ],

        "Location Information": [
            "City",
            "Area"
        ],

        "Restaurant Information": [
            "Restaurant_ID",
            "Restaurant_Name",
            "Cuisine_Type",
            "Restaurant_Rating"
        ],

        "Order Information": [
            "Order_ID",
            "Order_Date",
            "Order_Time",
            "Order_Day",
            "Peak_Hour"
        ],

        "Delivery Information": [
            "Delivery_Time_Min",
            "Distance_km",
            "Delivery_Partner_ID",
            "Delivery_Rating"
        ],

        "Financial Information": [
            "Order_Value",
            "Discount_Applied",
            "Final_Amount",
            "Profit_Margin"
        ],

        "Payment Information": [
            "Payment_Mode"
        ],

        "Outcome Variables": [
            "Order_Status",
            "Cancellation_Reason"
        ]
    }

    # Create a summary of feature categories
    feature_summary = pd.DataFrame([
        {
            "Category": category,
            "Variables": ", ".join(variables),
            "Number of Variables": len(variables)
        }
        for category, variables in feature_categories.items()
    ])

    print("\n" + "=" * 100)
    print("KEY FEATURE CATEGORIES")
    print("=" * 100)

    print(feature_summary.to_string(index=False))

    # Count the variables listed in the categories
    total_variables = sum(
        len(variables)
        for variables in feature_categories.values()
    )

    print("\n" + "=" * 100)
    print("TOTAL CATEGORIES:", len(feature_categories))
    print("TOTAL VARIABLE ENTRIES:", total_variables)
    print("TOTAL DATASET FEATURES:", df.shape[1])
    print("=" * 100)

    # Check whether any dataset columns are not categorized
    categorized_columns = [
        column
        for variables in feature_categories.values()
        for column in variables
    ]

    uncategorized_columns = [
        column
        for column in df.columns
        if column not in categorized_columns
    ]

    print("\nUncategorized Dataset Columns:")
    print(uncategorized_columns)


    # ============================================================
    # SECTION 4: DATA ISSUES IDENTIFICATION
    # ============================================================

    print("\n" + "=" * 80)
    print("SECTION 4: DATA ISSUES IDENTIFICATION")
    print("=" * 80)


    # ------------------------------------------------------------
    # 1. INCOMPLETE ROWS
    # ------------------------------------------------------------

    print("\n1. INCOMPLETE ROWS")
    print("-" * 80)

    incomplete_rows = df.isnull().any(axis=1).sum()

    print("Rows containing missing values:", incomplete_rows)

    print(
        "Percentage of incomplete rows:",
        round(incomplete_rows / len(df) * 100, 2),
        "%"
    )

    print("\nMissing Values by Column:")

    missing_values = df.isnull().sum()

    missing_report = pd.DataFrame({
        "Missing Count": missing_values,
        "Missing Percentage": (
            missing_values / len(df) * 100
        ).round(2)
    })

    print(
        missing_report[
            missing_report["Missing Count"] > 0
        ].sort_values(
            by="Missing Percentage",
            ascending=False
        ).to_string()
    )


    # ------------------------------------------------------------
    # 2. NEGATIVE PROFIT MARGINS
    # ------------------------------------------------------------

    print("\n2. NEGATIVE PROFIT MARGINS")
    print("-" * 80)

    if "Profit_Margin" in df.columns:

        profit_margin = pd.to_numeric(
            df["Profit_Margin"],
            errors="coerce"
        )

        negative_profit = (profit_margin < 0).sum()

        print(
            "Negative profit margin records:",
            negative_profit
        )

        print(
            "Negative profit margin percentage:",
            round(
                negative_profit / len(df) * 100,
                2
            ),
            "%"
        )

    else:
        print("Profit_Margin column not found.")


    # ------------------------------------------------------------
    # 3. ZERO OR NEGATIVE FINAL AMOUNTS
    # ------------------------------------------------------------

    print("\n3. ZERO OR NEGATIVE FINAL AMOUNTS")
    print("-" * 80)

    if "Final_Amount" in df.columns:

        final_amount = pd.to_numeric(
            df["Final_Amount"],
            errors="coerce"
        )

        zero_amount = (final_amount == 0).sum()
        negative_amount = (final_amount < 0).sum()

        print("Zero final amounts:", zero_amount)
        print("Negative final amounts:", negative_amount)

    else:
        print("Final_Amount column not found.")


    # ------------------------------------------------------------
    # 4. DATA TYPE INSPECTION
    # ------------------------------------------------------------

    print("\n4. DATA TYPES ACROSS COLUMNS")
    print("-" * 80)

    print(df.dtypes.to_string())

    print("\nData Type Counts:")
    print(
        df.dtypes.astype(str)
        .value_counts()
        .to_string()
    )


    # ------------------------------------------------------------
    # 5. POTENTIAL MALFORMED RECORDS
    # ------------------------------------------------------------

    print("\n5. POTENTIAL MALFORMED RECORDS")
    print("-" * 80)

    duplicate_rows = df.duplicated().sum()

    print("Duplicate rows:", duplicate_rows)

    if "Order_ID" in df.columns:

        missing_order_ids = df["Order_ID"].isnull().sum()

        duplicate_order_ids = df["Order_ID"].duplicated(
            keep=False
        ).sum()

        print("Missing Order_ID values:", missing_order_ids)

        print(
            "Rows with repeated Order_ID values:",
            duplicate_order_ids
        )


    # ============================================================
    # SECTION 5: BASIC EXPLORATORY ANALYSIS
    # ============================================================

    print("\n" + "=" * 80)
    print("SECTION 5: BASIC EXPLORATORY ANALYSIS")
    print("=" * 80)


    # ------------------------------------------------------------
    # 1. NUMERICAL VARIABLES
    # ------------------------------------------------------------

    print("\n1. NUMERICAL VARIABLES")
    print("-" * 80)

    numerical_columns = [
        "Customer_Age",
        "Delivery_Time_Min",
        "Distance_km",
        "Order_Value",
        "Discount_Applied",
        "Final_Amount",
        "Profit_Margin",
        "Delivery_Rating",
        "Restaurant_Rating"
    ]

    # Select numerical columns available in the dataset
    numerical_columns = [
        column
        for column in numerical_columns
        if column in df.columns
    ]

    # Create a separate numeric view for analysis
    # This does not change the original column values
    numerical_data = df[numerical_columns].apply(
        pd.to_numeric,
        errors="coerce"
    )

    print("\nSummary Statistics:")

    print(
        numerical_data.describe()
        .round(2)
        .to_string()
    )

    print("\nMedian Values:")

    print(
        numerical_data.median()
        .round(2)
        .to_string()
    )

    print("\nMissing Values in Numerical Variables:")

    print(
        numerical_data.isnull()
        .sum()
        .to_string()
    )


    # ------------------------------------------------------------
    # 2. CATEGORICAL VARIABLES
    # ------------------------------------------------------------

    print("\n2. CATEGORICAL VARIABLES")
    print("-" * 80)

    categorical_columns = [
        "City",
        "Area",
        "Customer_Gender",
        "Restaurant_Name",
        "Cuisine_Type",
        "Payment_Mode",
        "Order_Status",
        "Cancellation_Reason",
        "Order_Day",
        "Peak_Hour"
    ]

    for column in categorical_columns:

        if column not in df.columns:

            print(f"\n{column}: Column not found.")
            continue

        print(f"\n{column} - Value Counts:")

        print(
            df[column]
            .value_counts(dropna=False)
            .to_string()
        )

        print(f"\n{column} - Percentage Distribution:")

        percentage_distribution = (
            df[column]
            .value_counts(
                normalize=True,
                dropna=False
            ) * 100
        ).round(2)

        print(
            percentage_distribution
            .astype(str)
            .add("%")
            .to_string()
        )


    # ============================================================
    # SECTION 6: DATE AND TIME INSPECTION
    # ============================================================

    print("\n" + "=" * 80)
    print("SECTION 6: DATE AND TIME INSPECTION")
    print("=" * 80)


    # ------------------------------------------------------------
    # 1. ORDER DATE
    # ------------------------------------------------------------

    if "Order_Date" in df.columns:

        print("\n1. ORDER DATE")
        print("-" * 80)

        order_date = pd.to_datetime(
            df["Order_Date"],
            errors="coerce"
        )

        print("Missing or invalid dates:", order_date.isna().sum())

        print("Earliest Order Date:", order_date.min())

        print("Latest Order Date:", order_date.max())


    # ------------------------------------------------------------
    # 2. ORDER TIME
    # ------------------------------------------------------------

    if "Order_Time" in df.columns:

        print("\n2. ORDER TIME")
        print("-" * 80)

        print("Missing Order_Time values:", df["Order_Time"].isna().sum())

        print("\nSample Order_Time values:")

        print(
            df["Order_Time"]
            .value_counts(dropna=False)
            .head(10)
            .to_string()
        )


    # ============================================================
    # SECTION 7: FINAL DATA UNDERSTANDING SUMMARY
    # ============================================================

    print("\n" + "=" * 80)
    print("SECTION 7: FINAL DATA UNDERSTANDING SUMMARY")
    print("=" * 80)

    print("Total Records:", df.shape[0])
    print("Total Features:", df.shape[1])

    print("Total Missing Cells:", df.isnull().sum().sum())

    print("Total Duplicate Rows:", df.duplicated().sum())

    print(
        "Total Columns Containing Missing Values:",
        (df.isnull().sum() > 0).sum()
    )

    print("\nData Understanding Completed Successfully.")

finally:

    # Restore the original console output
    sys.stdout = original_stdout

    # Close the output file
    output_file.close()

print("Data understanding output saved to data_understanding_output.txt")

