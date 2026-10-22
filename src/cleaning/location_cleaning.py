
import pandas as pd


def clean_location_data(df):
    """
    Clean City and Area without guessing missing locations.

    Rules:
    1. Standardize text and whitespace.
    2. Convert blank strings to missing values.
    3. Fill missing locations with 'Unknown'.
    4. Preserve all existing non-missing values.
    """

    df = df.copy()

    print("\n" + "=" * 60)
    print("LOCATION DATA CLEANING")
    print("=" * 60)

    location_columns = ["City", "Area"]

    required_columns = [
        col for col in location_columns
        if col not in df.columns
    ]

    if required_columns:
        raise ValueError(
            f"Missing required columns: {required_columns}"
        )

    # ============================================================
    # 1. STANDARDIZE LOCATION TEXT
    # ============================================================

    for col in location_columns:
        df[col] = (
            df[col]
            .astype("string")
            .str.strip()
            .replace("", pd.NA)
        )

    print("\nMissing values before cleaning:")
    print(df[location_columns].isna().sum())

    # ============================================================
    # 2. HANDLE MISSING LOCATIONS
    # ============================================================

    for col in location_columns:
        df[col] = df[col].fillna("Unknown")

    # ============================================================
    # 3. FINAL VALIDATION
    # ============================================================

    print("\nMissing values after cleaning:")
    print(df[location_columns].isna().sum())

    print("\nCity distribution:")
    print(df["City"].value_counts(dropna=False))

    print("\nArea distribution:")
    print(df["Area"].value_counts(dropna=False))

    assert df[location_columns].notna().all().all(), (
        "Location columns still contain missing values."
    )

    print("\nLocation cleaning completed successfully.")

    return df
