
import pandas as pd


# ============================================================
# 1. DEFINE CUSTOMER COLUMNS
# ============================================================

CUSTOMER_COLUMNS = [
    "Customer_ID",
    "Customer_Age",
    "Customer_Gender"
]


# ============================================================
# 2. VALIDATE REQUIRED COLUMNS
# ============================================================

def validate_customer_columns(df):
    """Check whether all required customer columns exist."""

    missing_columns = [
        col for col in CUSTOMER_COLUMNS
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Required customer columns not found: {missing_columns}"
        )


# ============================================================
# 3. CUSTOMER_ID DATA QUALITY ANALYSIS
# ============================================================

def analyze_customer_id(df):
    """Analyze missing, unique, and duplicate customer IDs."""

    print("\n" + "=" * 70)
    print("CUSTOMER_ID DATA QUALITY ANALYSIS")
    print("=" * 70)

    print("\nMissing customer IDs:")
    print(df["Customer_ID"].isna().sum())

    print("\nUnique non-missing customer IDs:")
    print(df["Customer_ID"].nunique())

    print("\nDuplicate customer ID rows (including missing values):")
    print(df["Customer_ID"].duplicated().sum())

    print("\nDuplicate non-missing customer IDs:")
    print(
        df.loc[df["Customer_ID"].notna(), "Customer_ID"]
        .duplicated()
        .sum()
    )


# ============================================================
# 4. CLEAN CUSTOMER AGE
# ============================================================

def clean_customer_age(df):
    """
    Convert age to numeric, mark ages outside 18-100 as missing,
    and impute missing ages using the median.
    """

    df = df.copy()

    print("\n" + "=" * 70)
    print("CUSTOMER_AGE CLEANING")
    print("=" * 70)

    # Convert age to numeric
    df["Customer_Age"] = pd.to_numeric(
        df["Customer_Age"],
        errors="coerce"
    )

    print("\nMissing ages before cleaning:")
    print(df["Customer_Age"].isna().sum())

    print("\nAge statistics before cleaning:")
    print(df["Customer_Age"].describe())

    # Identify ages outside the selected range
    invalid_age = (
        df["Customer_Age"].notna()
        & (
            (df["Customer_Age"] < 18)
            | (df["Customer_Age"] > 100)
        )
    )

    print("\nInvalid ages (below 18 or above 100):")
    print(invalid_age.sum())

    # Replace invalid ages with missing values
    df.loc[invalid_age, "Customer_Age"] = float("nan")

    # Calculate median from valid ages
    age_median = df["Customer_Age"].median()

    print("\nMedian age used for imputation:", age_median)

    # Impute only if a valid median exists
    if pd.notna(age_median):
        df["Customer_Age"] = df["Customer_Age"].fillna(
            age_median
        )
    else:
        print(
            "Warning: No valid ages available. "
            "Missing ages remain unchanged."
        )

    print("\nMissing ages after cleaning:")
    print(df["Customer_Age"].isna().sum())

    return df


# ============================================================
# 5. CLEAN CUSTOMER GENDER
# ============================================================

def clean_customer_gender(df):
    """ Standardize gender categories without guessing missing values."""

    df = df.copy()

    if "Customer_Gender" not in df.columns:
        return df

    # Standardize text and convert blanks to missing values
    gender = (
        df["Customer_Gender"]
        .astype("string")
        .str.strip()
        .str.title()
    )

    gender = gender.replace("", pd.NA)

    # Standardize common abbreviations
    gender = gender.replace({
        "M": "Male",
        "F": "Female",
        "Man": "Male",
        "Woman": "Female"
    })

    # Keep Other distinct from missing information
    df["Customer_Gender"] = gender.fillna("Unknown")

    print("\nCustomer Gender Cleaning Summary")
    print("=" * 40)
    print(df["Customer_Gender"].value_counts(dropna=False))
    print("\nMissing values:",
          df["Customer_Gender"].isna().sum())

    return df

# ============================================================
# 6. CUSTOMER CLEANING SUMMARY
# ============================================================

def validate_customer_data(df):
    """Display final customer data quality summary."""

    print("\n" + "=" * 70)
    print("CUSTOMER INFORMATION CLEANING SUMMARY")
    print("=" * 70)

    print("\nMissing values:")
    print(df[CUSTOMER_COLUMNS].isna().sum())

    print("\nData types:")
    print(df[CUSTOMER_COLUMNS].dtypes)


# ============================================================
# 7. MAIN REUSABLE CUSTOMER CLEANING FUNCTION
# ============================================================

def clean_customer_data(df, analyze_before=True):
    """
    Run the complete customer information cleaning workflow.

    Returns
    -------
    pandas.DataFrame
        Dataset with cleaned customer age and gender.
        Customer IDs are checked but not modified.
    """

    df = df.copy()

    validate_customer_columns(df)

    if analyze_before:
        analyze_customer_id(df)

    df = clean_customer_age(df)

    df = clean_customer_gender(df)

    validate_customer_data(df)

    print("\nCustomer information cleaning completed successfully.")

    return df
