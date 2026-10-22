# ============================================================
# FEATURE ENGINEERING
# PROJECT: ONLINE FOOD DELIVERY ANALYSIS
# ============================================================
#
# Purpose:
# 1. Create date-based features.
# 2. Create distance categories.
# 3. Create delivery-time categories.
# 4. Create order-value categories.
# 5. Calculate discount percentage.
# 6. Create rating categories.
# 7. Generate a feature summary report.
# 8. Save the feature-engineered dataset.
#
# IMPORTANT:
# Order_Time is excluded from feature engineering because
# the raw dataset contains only 0:00 and missing values.
#
# ============================================================

from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# 1. PROJECT PATHS AND CONFIGURATION
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_DIR
    / "output"
    / "cleaned_online_food_delivery_dataset.csv"
)

OUTPUT_DIR = (
    PROJECT_DIR
    / "output"
    / "feature_engineering"
)

REPORT_DIR = OUTPUT_DIR / "reports"

OUTPUT_FILE = (
    OUTPUT_DIR
    / "feature_engineered_dataset.csv"
)

SUMMARY_FILE = (
    REPORT_DIR
    / "feature_engineering_summary.csv"
)


# ============================================================
# 2. LOAD DATASET
# ============================================================

def load_dataset(file_path=INPUT_FILE):
    """
    Load the cleaned dataset.

    Parameters
    ----------
    file_path : Path
        Location of the cleaned CSV file.

    Returns
    -------
    pandas.DataFrame
        Loaded dataset.
    """

    if not file_path.exists():
        raise FileNotFoundError(
            f"Input dataset not found: {file_path}"
        )

    df = pd.read_csv(file_path)

    print("\nDataset loaded successfully")
    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")

    return df


# ============================================================
# 3. DATE FEATURE ENGINEERING
# ============================================================

def create_date_features(df):
    """
    Extract useful calendar features from Order_Date.

    Features created:
    - Order_Year
    - Order_Month
    - Order_Month_Name
    - Order_Weekday
    - Is_Weekend
    """

    df = df.copy()

    if "Order_Date" not in df.columns:
        print("Warning: Order_Date column not found.")
        return df

    order_date = pd.to_datetime(
        df["Order_Date"],
        errors="coerce"
    )

    # Year of the order
    df["Order_Year"] = order_date.dt.year.astype("Int64")

    # Month number: 1 to 12
    df["Order_Month"] = order_date.dt.month.astype("Int64")

    # Month name
    df["Order_Month_Name"] = (
        order_date.dt.month_name()
        .astype("string")
    )

    # Weekday name
    df["Order_Weekday"] = (
        order_date.dt.day_name()
        .astype("string")
    )

    # Saturday and Sunday = weekend
    is_weekend = order_date.dt.dayofweek.ge(5)

    df["Is_Weekend"] = (
        is_weekend
        .where(order_date.notna(), pd.NA)
        .astype("boolean")
    )

    print("Date features created")

    return df


# ============================================================
# 4. REMOVE UNRELIABLE TIME FEATURES
# ============================================================

def remove_unreliable_time_features(df):
    """
    Remove derived time-of-day features because Order_Time
    contains only 0:00 and missing values in the source data.

    The original Order_Time column is preserved.
    """

    df = df.copy()

    unreliable_features = [
        "Order_Hour",
        "Order_Time_Category"
    ]

    existing_features = [
        column
        for column in unreliable_features
        if column in df.columns
    ]

    if existing_features:
        df.drop(
            columns=existing_features,
            inplace=True
        )

    print(
        "Order-time features skipped: "
        "source time values have no variation"
    )

    return df


# ============================================================
# 5. DISTANCE CATEGORY
# ============================================================

def create_distance_category(df):
    """
    Categorize delivery distance.

    Categories:
    - Short: distance <= 2 km
    - Medium: 2 to 5 km
    - Long: 5 to 10 km
    - Very Long: more than 10 km

    Zero and negative distances are treated as invalid.
    Missing values remain missing.
    """

    df = df.copy()

    column = "Distance_km"

    if column not in df.columns:
        print("Warning: Distance_km column not found.")
        return df

    distance = pd.to_numeric(
        df[column],
        errors="coerce"
    )

    # Exclude invalid distances
    distance = distance.where(distance > 0)

    df["Distance_Category"] = pd.cut(
        distance,
        bins=[
            0,
            2,
            5,
            10,
            np.inf
        ],
        labels=[
            "Short (0-2 km)",
            "Medium (2-5 km)",
            "Long (5-10 km)",
            "Very Long (>10 km)"
        ],
        include_lowest=True,
        right=True,
        ordered=True
    ).astype("string")

    print("Distance category created")

    return df


# ============================================================
# 6. DELIVERY TIME CATEGORY
# ============================================================

def create_delivery_time_category(df):
    """
    Categorize delivery duration in minutes.

    Categories:
    - Fast: 30 minutes or less
    - Moderate: 31 to 45 minutes
    - Slow: 46 to 60 minutes
    - Very Slow: more than 60 minutes

    Zero and negative durations are treated as invalid.
    """

    df = df.copy()

    column = "Delivery_Time_Min"

    if column not in df.columns:
        print(
            "Warning: Delivery_Time_Min column not found."
        )
        return df

    delivery_time = pd.to_numeric(
        df[column],
        errors="coerce"
    )

    delivery_time = delivery_time.where(
        delivery_time > 0
    )

    df["Delivery_Time_Category"] = pd.cut(
        delivery_time,
        bins=[
            0,
            30,
            45,
            60,
            np.inf
        ],
        labels=[
            "Fast (<=30 min)",
            "Moderate (31-45 min)",
            "Slow (46-60 min)",
            "Very Slow (>60 min)"
        ],
        include_lowest=True,
        right=True,
        ordered=True
    ).astype("string")

    print("Delivery-time category created")

    return df


# ============================================================
# 7. ORDER VALUE CATEGORY
# ============================================================

def create_order_value_category(df):
    """
    Categorize orders by Order_Value.

    Categories:
    - Low: <= 200
    - Medium: 201 to 500
    - High: 501 to 1000
    - Premium: > 1000

    Invalid negative order values are treated as missing.
    """

    df = df.copy()

    column = "Order_Value"

    if column not in df.columns:
        print("Warning: Order_Value column not found.")
        return df

    order_value = pd.to_numeric(
        df[column],
        errors="coerce"
    )

    order_value = order_value.where(
        order_value >= 0
    )

    df["Order_Value_Category"] = pd.cut(
        order_value,
        bins=[
            -np.inf,
            200,
            500,
            1000,
            np.inf
        ],
        labels=[
            "Low (<=200)",
            "Medium (201-500)",
            "High (501-1000)",
            "Premium (>1000)"
        ],
        right=True,
        ordered=True
    ).astype("string")

    print("Order-value category created")

    return df


# ============================================================
# 8. DISCOUNT PERCENTAGE
# ============================================================

def create_discount_percentage(df):
    """
    Calculate discount percentage.

    Formula:
        Discount_Percentage =
            (Discount_Applied / Order_Value) * 100

    Rules:
    - Order_Value must be greater than zero.
    - Discount_Applied must be non-negative.
    - Missing input values remain missing.
    - Values are not artificially capped at 100%.
    """

    df = df.copy()

    required_columns = [
        "Order_Value",
        "Discount_Applied"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        print(
            "Warning: Cannot calculate discount percentage. "
            f"Missing columns: {missing_columns}"
        )
        return df

    order_value = pd.to_numeric(
        df["Order_Value"],
        errors="coerce"
    )

    discount = pd.to_numeric(
        df["Discount_Applied"],
        errors="coerce"
    )

    valid_rows = (
        order_value.gt(0)
        & discount.ge(0)
    )

    discount_percentage = (
        discount.div(order_value) * 100
    )

    df["Discount_Percentage"] = (
        discount_percentage.where(valid_rows)
    )

    print("Discount percentage created")

    return df


# ============================================================
# 9. RATING CATEGORY
# ============================================================

def create_rating_category(df):
    """
    Categorize Delivery_Rating.

    Categories:
    - Poor: rating <= 2
    - Average: rating > 2 and <= 3
    - Good: rating > 3 and <= 4
    - Excellent: rating > 4 and <= 5

    Missing and invalid ratings remain missing.
    """

    df = df.copy()

    column = "Delivery_Rating"

    if column not in df.columns:
        print(
            "Warning: Delivery_Rating column not found. "
            "Rating_Category was not created."
        )
        return df

    rating = pd.to_numeric(
        df[column],
        errors="coerce"
    )

    # Only accept ratings from 1 to 5
    rating = rating.where(
        rating.between(1, 5)
    )

    df["Rating_Category"] = pd.cut(
        rating,
        bins=[
            0,
            2,
            3,
            4,
            5
        ],
        labels=[
            "Poor",
            "Average",
            "Good",
            "Excellent"
        ],
        right=True,
        ordered=True
    ).astype("string")

    print("Rating category created")

    return df


# ============================================================
# 10. FEATURE ENGINEERING PIPELINE
# ============================================================

def run_feature_engineering(df):
    """
    Execute all feature-engineering functions in sequence.

    The original rows are preserved. This function does not
    impute missing values or remove dataset rows.
    """

    original_row_count = len(df)

    result = df.copy()

    # Date features
    result = create_date_features(result)

    # Do not derive time features from unreliable source data
    result = remove_unreliable_time_features(result)

    # Distance features
    result = create_distance_category(result)

    # Delivery duration features
    result = create_delivery_time_category(result)

    # Order value features
    result = create_order_value_category(result)

    # Discount features
    result = create_discount_percentage(result)

    # Rating features
    result = create_rating_category(result)

    # Validate row count
    if len(result) != original_row_count:
        raise ValueError(
            "Row count changed during feature engineering. "
            f"Original: {original_row_count}, "
            f"Output: {len(result)}"
        )

    print("\nAll feature-engineering functions completed.")

    return result


# ============================================================
# 11. FEATURE SUMMARY REPORT
# ============================================================

def generate_feature_summary(df):
    """
    Create a summary for generated features.

    Reports:
    - Feature name
    - Data type
    - Non-missing count
    - Missing count
    - Unique non-missing values
    """

    feature_columns = [
        "Order_Year",
        "Order_Month",
        "Order_Month_Name",
        "Order_Weekday",
        "Is_Weekend",
        "Distance_Category",
        "Delivery_Time_Category",
        "Order_Value_Category",
        "Discount_Percentage",
        "Rating_Category"
    ]

    available_features = [
        column
        for column in feature_columns
        if column in df.columns
    ]

    summary = []

    for column in available_features:
        series = df[column]

        summary.append({
            "Feature_Name": column,
            "Data_Type": str(series.dtype),
            "Non_Missing_Count": int(
                series.notna().sum()
            ),
            "Missing_Count": int(
                series.isna().sum()
            ),
            "Unique_Values": int(
                series.nunique(dropna=True)
            )
        })

    summary_df = pd.DataFrame(summary)

    print("\nFeature engineering summary:")

    if not summary_df.empty:
        print(
            summary_df.to_string(index=False)
        )

    return summary_df


# ============================================================
# 12. SAVE OUTPUTS
# ============================================================

def save_outputs(df, summary_df):
    """
    Save the feature-engineered dataset and summary report.
    """

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save engineered dataset
    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nFeature-engineered dataset saved:")
    print(OUTPUT_FILE)

    # Save feature summary
    summary_df.to_csv(
        SUMMARY_FILE,
        index=False
    )

    print("\nFeature summary report saved:")
    print(SUMMARY_FILE)


# ============================================================
# 13. MAIN FUNCTION
# ============================================================

def main():
    """
    Main entry point for feature engineering.
    """

    # Load cleaned data
    df = load_dataset()

    original_rows = len(df)

    # Run feature engineering
    engineered_df = run_feature_engineering(df)

    # Generate summary
    summary_df = generate_feature_summary(
        engineered_df
    )

    # Save results
    save_outputs(
        engineered_df,
        summary_df
    )

    # Final validation
    print("\n" + "=" * 60)
    print("FEATURE ENGINEERING COMPLETED")
    print("=" * 60)

    print(f"Original rows: {original_rows}")
    print(f"Output rows: {len(engineered_df)}")
    print(
        f"Original columns: {df.shape[1]}"
    )
    print(
        f"Output columns: {engineered_df.shape[1]}"
    )

    if original_rows == len(engineered_df):
        print("Row-count validation: PASSED")
    else:
        print("Row-count validation: FAILED")

    return engineered_df


# ============================================================
# 14. SCRIPT ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()