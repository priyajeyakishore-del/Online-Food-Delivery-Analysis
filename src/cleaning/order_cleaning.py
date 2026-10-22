
import pandas as pd


def clean_order_information(df, drop_order_time=False):
    """
    Clean and validate order information columns.

    Steps:
    1. Validate required columns.
    2. Clean Order_ID.
    3. Convert Order_Date to datetime.
    4. Inspect Order_Time and check its reliability.
    5. Derive Order_Day from Order_Date.
    6. Clean Peak_Hour as nullable Boolean.
    7. Validate the cleaned columns.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataset.

    drop_order_time : bool, default=False
        False: retain Order_Time for investigation.
        True: drop Order_Time after inspection.

    Returns
    -------
    pandas.DataFrame
        Cleaned copy of the input dataset.
    """

    df = df.copy()

    print("\n" + "=" * 60)
    print("ORDER INFORMATION CLEANING AND VALIDATION")
    print("=" * 60)

    # ============================================================
    # 1. VALIDATE REQUIRED COLUMNS
    # ============================================================

    print("\n1. REQUIRED COLUMN VALIDATION")
    print("-" * 40)

    required_columns = [
        "Order_ID",
        "Order_Date",
        "Order_Day",
        "Peak_Hour"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Required columns missing: {missing_columns}"
        )

    print("All required columns are available.")

    # ============================================================
    # 2. CLEAN ORDER ID
    # ============================================================

    print("\n2. ORDER ID CLEANING")
    print("-" * 40)

    df["Order_ID"] = (
        df["Order_ID"]
        .astype("string")
        .str.strip()
    )

    invalid_ids = [
        "", "nan", "none", "null", "na", "n/a"
    ]

    df["Order_ID"] = df["Order_ID"].mask(
        df["Order_ID"].str.lower().isin(invalid_ids)
    )

    missing_ids = int(df["Order_ID"].isna().sum())

    duplicate_ids = int(
        df.loc[
            df["Order_ID"].notna(),
            "Order_ID"
        ].duplicated().sum()
    )

    print("Missing Order_ID:", missing_ids)
    print("Duplicate non-missing Order_ID rows:", duplicate_ids)

    # ============================================================
    # 3. CLEAN ORDER DATE
    # ============================================================

    print("\n3. ORDER DATE CLEANING")
    print("-" * 40)

    order_date = (
        df["Order_Date"]
        .astype("string")
        .str.strip()
    )

    invalid_dates = [
        "", "nan", "none", "null", "na", "n/a", "########"
    ]

    order_date = order_date.mask(
        order_date.str.lower().isin(invalid_dates)
    )

    df["Order_Date"] = pd.to_datetime(
        order_date,
        format="mixed",
        errors="coerce"
    ).dt.normalize()

    missing_dates = int(df["Order_Date"].isna().sum())

    print("Missing Order_Date:", missing_dates)

    if df["Order_Date"].notna().any():
        print("Earliest date:", df["Order_Date"].min())
        print("Latest date  :", df["Order_Date"].max())
    else:
        print("No valid order dates available.")

    # ============================================================
    # 4. INSPECT ORDER TIME
    # ============================================================

    print("\n4. ORDER TIME INSPECTION")
    print("-" * 40)

    normalized_time = None

    if "Order_Time" in df.columns:

        order_time = (
            df["Order_Time"]
            .astype("string")
            .str.strip()
        )

        invalid_time_text = [
            "", "nan", "none", "null", "na", "n/a"
        ]

        normalized_time = order_time.mask(
            order_time.str.lower().isin(invalid_time_text)
        )

        print("Original data type:", df["Order_Time"].dtype)
        print("Total rows:", len(df))
        print(
            "Missing/missing-like values:",
            int(normalized_time.isna().sum())
        )
        print(
            "Non-missing values:",
            int(normalized_time.notna().sum())
        )
        print(
            "Unique non-missing time values:",
            int(normalized_time.nunique(dropna=True))
        )

        print("\nMost common Order_Time values:")
        print(
            normalized_time.value_counts(
                dropna=False
            ).head(20)
        )

        # Parse for inspection only.
        # Do not overwrite the original time column.
        parsed_time = pd.to_datetime(
            normalized_time,
            errors="coerce"
        )

        parseable_mask = (
            normalized_time.notna()
            & parsed_time.notna()
        )

        unparseable_mask = (
            normalized_time.notna()
            & parsed_time.isna()
        )

        non_missing_count = int(normalized_time.notna().sum())

        print("\nTime parsing validation:")
        print(
            "Parseable non-missing values:",
            int(parseable_mask.sum())
        )
        print(
            "Unparseable non-missing values:",
            int(unparseable_mask.sum())
        )
        print(
            "Parseable percentage:",
            round(
                parseable_mask.sum()
                / max(non_missing_count, 1)
                * 100,
                2
            ),
            "%"
        )

        # Check whether Order_Time contains useful variation.
        valid_times = normalized_time.dropna()
        unique_time_count = int(valid_times.nunique())

        print("\nOrder_Time reliability check:")

        if len(valid_times) > 0:

            most_common_percentage = (
                valid_times.value_counts(normalize=True).iloc[0]
                * 100
            )

            print(
                "Most frequent time percentage:",
                round(most_common_percentage, 2),
                "%"
            )

        if unique_time_count == 1:
            print(
                "WARNING: All non-missing Order_Time values "
                "are identical."
            )
            print(
                "Do not derive Peak_Hour from Order_Time."
            )

        elif unique_time_count == 0:
            print("WARNING: No valid Order_Time values available.")

        else:
            print(
                "Multiple time values exist. Verify their "
                "validity before deriving Peak_Hour."
            )

        # Drop Order_Time only if explicitly requested.
        if drop_order_time:
            df.drop(columns=["Order_Time"], inplace=True)
            print("\nOrder_Time dropped by request.")
        else:
            print("\nOrder_Time retained for investigation.")

    else:
        print("Order_Time column is absent.")
        print("Peak_Hour will not be derived from order time.")

    # ============================================================
    # 5. CLEAN ORDER DAY
    # ============================================================

    print("\n5. ORDER DAY CLEANING")
    print("-" * 40)

    # Derive the weekday name from Order_Date.
    # A missing date results in a missing weekday.
    df["Order_Day"] = (
        df["Order_Date"]
        .dt.day_name()
        .astype("string")
    )

    print("\nOrder_Day distribution:")
    print(df["Order_Day"].value_counts(dropna=False))

    print(
        "\nMissing Order_Day:",
        int(df["Order_Day"].isna().sum())
    )

    # ============================================================
    # 6. CLEAN PEAK HOUR
    # ============================================================

    print("\n6. PEAK HOUR CLEANING")
    print("-" * 40)

    # Normalize common representations of Boolean values.
    # Missing or invalid values remain pd.NA.
    peak_hour_text = (
        df["Peak_Hour"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    peak_hour_mapping = {
        "true": True,
        "false": False,
        "1": True,
        "0": False
    }

    df["Peak_Hour"] = (
        peak_hour_text
        .map(peak_hour_mapping)
        .astype("boolean")
    )

    # Do not use Order_Time to fill missing labels because
    # all observed times are currently 0:00.
    peak_counts = df["Peak_Hour"].value_counts(dropna=False)

    known_count = int(df["Peak_Hour"].notna().sum())
    missing_peak_count = int(df["Peak_Hour"].isna().sum())
    total_records = len(df)

    print("\nPeak_Hour distribution:")
    print(peak_counts)

    print("\nPeak_Hour validation summary:")
    print("Total records:", total_records)
    print("Known labels:", known_count)
    print("Missing labels:", missing_peak_count)

    print(
        "Known labels percentage:",
        round(
            known_count / max(total_records, 1) * 100,
            2
        ),
        "%"
    )

    print(
        "Missing labels percentage:",
        round(
            missing_peak_count / max(total_records, 1) * 100,
            2
        ),
        "%"
    )

    print("\nCleaning decision:")
    print("- Valid True/False values preserved.")
    print("- Missing values retained as pd.NA.")
    print("- No arbitrary imputation performed.")

    # ============================================================
    # 7. FINAL VALIDATION
    # ============================================================

    print("\n7. FINAL VALIDATION")
    print("-" * 40)

    validation_columns = [
        "Order_ID",
        "Order_Date",
        "Order_Day",
        "Peak_Hour"
    ]

    print("\nMissing values:")
    print(df[validation_columns].isna().sum())

    print("\nMissing percentage:")
    print(
        (
            df[validation_columns].isna().mean() * 100
        ).round(2)
    )

    print("\nData types:")
    print(df[validation_columns].dtypes)

    # Validate Order_Day against Order_Date.
    expected_day = df["Order_Date"].dt.day_name()

    day_mismatches = (
        df["Order_Day"].notna()
        & expected_day.notna()
        & df["Order_Day"].ne(expected_day)
    ).sum()

    print("\nOrder_Day mismatches:", int(day_mismatches))

    # Validate known Peak_Hour values.
    valid_peak_values = (
        df["Peak_Hour"]
        .dropna()
        .isin([True, False])
        .all()
    )

    print(
        "Peak_Hour contains only Boolean values "
        "among known entries:",
        bool(valid_peak_values)
    )

    print(
        "Peak_Hour dtype is nullable Boolean:",
        str(df["Peak_Hour"].dtype) == "boolean"
    )

    print("\nFinal dataset shape:", df.shape)

    print(
        "Order_Time exists:",
        "Order_Time" in df.columns
    )

    print("\nOrder information cleaning completed.")

    return df
