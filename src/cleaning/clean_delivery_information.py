
import pandas as pd


def clean_delivery_information(df):
    """
    Clean and validate delivery information.

    1. Clean Delivery_Time_Min and Distance_km.
    2. Impute missing time and distance for delivered orders
       using medians from valid delivered orders.
    3. Clean Delivery_Partner_ID and fill missing IDs with Unknown.
    4. Keep Delivery_Rating numeric; invalid and missing ratings
       remain NaN.
    5. Print missing-value reports and outlier checks.
    """

    df = df.copy()

    print("\n" + "=" * 70)
    print("DELIVERY INFORMATION CLEANING AND IMPUTATION")
    print("=" * 70)

    # ============================================================
    # 1. VALIDATE REQUIRED COLUMNS
    # ============================================================

    required_columns = [
        "Delivery_Time_Min",
        "Distance_km",
        "Delivery_Partner_ID",
        "Delivery_Rating",
        "Order_Status"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Required columns missing: {missing_columns}"
        )

    # Normalize order status for consistent matching.
    status = (
        df["Order_Status"]
        .astype("string")
        .str.strip()
        .str.casefold()
    )

    delivered_mask = status.eq("delivered").fillna(False)

    print("Total records:", len(df))
    print("Delivered orders:", int(delivered_mask.sum()))

    # ============================================================
    # 2. CLEAN DELIVERY TIME
    # ============================================================

    print("\n" + "=" * 70)
    print("1. DELIVERY TIME CLEANING")
    print("=" * 70)

    df["Delivery_Time_Min"] = pd.to_numeric(
        df["Delivery_Time_Min"],
        errors="coerce"
    )

    # Delivery time must be positive.
    invalid_time_mask = df["Delivery_Time_Min"].le(0)
    invalid_time_count = int(invalid_time_mask.sum())

    df.loc[
        invalid_time_mask,
        "Delivery_Time_Min"
    ] = float("nan")

    print("Invalid non-positive values:", invalid_time_count)
    print(
        "Missing/invalid before imputation:",
        df["Delivery_Time_Min"].isna().sum()
    )

    print("\nDelivery time summary before imputation:")
    print(df["Delivery_Time_Min"].describe())

    # ============================================================
    # 3. CLEAN DELIVERY DISTANCE
    # ============================================================

    print("\n" + "=" * 70)
    print("2. DELIVERY DISTANCE CLEANING")
    print("=" * 70)

    df["Distance_km"] = pd.to_numeric(
        df["Distance_km"],
        errors="coerce"
    )

    # Distance must be positive.
    invalid_distance_mask = df["Distance_km"].le(0)
    invalid_distance_count = int(invalid_distance_mask.sum())

    df.loc[
        invalid_distance_mask,
        "Distance_km"
    ] = float("nan")

    print(
        "Invalid non-positive values:",
        invalid_distance_count
    )

    print(
        "Missing/invalid before imputation:",
        df["Distance_km"].isna().sum()
    )

    print("\nDistance summary before imputation:")
    print(df["Distance_km"].describe())

    # ============================================================
    # 4. CLEAN DELIVERY PARTNER ID
    # ============================================================

    print("\n" + "=" * 70)
    print("3. DELIVERY PARTNER ID CLEANING")
    print("=" * 70)

    df["Delivery_Partner_ID"] = (
        df["Delivery_Partner_ID"]
        .astype("string")
        .str.strip()
    )

    invalid_ids = [
        "", "nan", "none", "null", "na", "n/a"
    ]

    invalid_partner_mask = (
        df["Delivery_Partner_ID"]
        .str.casefold()
        .isin(invalid_ids)
        .fillna(False)
    )

    df.loc[
        invalid_partner_mask,
        "Delivery_Partner_ID"
    ] = pd.NA

    missing_partner_before = int(
        df["Delivery_Partner_ID"].isna().sum()
    )

    print(
        "Missing partner IDs before filling:",
        missing_partner_before
    )

    print(
        "Unique delivery partners:",
        df["Delivery_Partner_ID"].nunique()
    )

    # Do not assign an arbitrary existing partner ID.
    df["Delivery_Partner_ID"] = (
        df["Delivery_Partner_ID"].fillna("Unknown")
    )

    print(
        "Missing partner IDs after filling:",
        df["Delivery_Partner_ID"].isna().sum()
    )

    # ============================================================
    # 5. CLEAN DELIVERY RATING — KEEP NUMERIC
    # ============================================================

    print("\n" + "=" * 70)
    print("4. DELIVERY RATING CLEANING")
    print("=" * 70)

    df["Delivery_Rating"] = pd.to_numeric(
        df["Delivery_Rating"],
        errors="coerce"
    )

    missing_rating_before = int(
        df["Delivery_Rating"].isna().sum()
    )

    # Assumes the documented rating scale is 1 to 5.
    invalid_rating_mask = (
        df["Delivery_Rating"].notna()
        & ~df["Delivery_Rating"].between(1, 5)
    )

    invalid_rating_count = int(invalid_rating_mask.sum())

    # Invalid ratings become NaN; valid ratings remain numeric.
    df.loc[
        invalid_rating_mask,
        "Delivery_Rating"
    ] = float("nan")

    missing_rating_after = int(
        df["Delivery_Rating"].isna().sum()
    )

    print("Missing ratings before validation:",
          missing_rating_before)
    print("Invalid ratings replaced with NaN:",
          invalid_rating_count)
    print("Missing ratings after validation:",
          missing_rating_after)

    print(
        "Missing rating percentage:",
        round(df["Delivery_Rating"].isna().mean() * 100, 2),
        "%"
    )

    print("\nDelivery rating distribution:")
    print(
        df["Delivery_Rating"]
        .value_counts(dropna=False)
        .sort_index()
    )

    print("\nDelivery rating summary:")
    print(df["Delivery_Rating"].describe())

    # ============================================================
    # 6. IMPUTE MISSING DELIVERY TIME
    # ============================================================

    print("\n" + "=" * 70)
    print("5. DELIVERY TIME IMPUTATION")
    print("=" * 70)

    time_missing_before = int(
        df["Delivery_Time_Min"].isna().sum()
    )

    # Calculate the median from valid delivered orders only.
    valid_times = df.loc[
        delivered_mask,
        "Delivery_Time_Min"
    ].dropna()

    time_imputed_count = 0

    if not valid_times.empty:

        median_delivery_time = valid_times.median()

        missing_time_mask = (
            delivered_mask
            & df["Delivery_Time_Min"].isna()
        )

        time_imputed_count = int(missing_time_mask.sum())

        df.loc[
            missing_time_mask,
            "Delivery_Time_Min"
        ] = median_delivery_time

        print(
            "Median delivered-order time:",
            round(median_delivery_time, 2)
        )

        print(
            "Delivered-order times imputed:",
            time_imputed_count
        )

    else:
        print(
            "No valid delivered-order times available. "
            "Imputation skipped."
        )

    print("Missing time before imputation:", time_missing_before)
    print(
        "Missing time after imputation:",
        df["Delivery_Time_Min"].isna().sum()
    )

    # ============================================================
    # 7. IMPUTE MISSING DELIVERY DISTANCE
    # ============================================================

    print("\n" + "=" * 70)
    print("6. DELIVERY DISTANCE IMPUTATION")
    print("=" * 70)

    distance_missing_before = int(
        df["Distance_km"].isna().sum()
    )

    # Calculate the median from valid delivered orders only.
    valid_distances = df.loc[
        delivered_mask,
        "Distance_km"
    ].dropna()

    distance_imputed_count = 0

    if not valid_distances.empty:

        median_distance = valid_distances.median()

        missing_distance_mask = (
            delivered_mask
            & df["Distance_km"].isna()
        )

        distance_imputed_count = int(
            missing_distance_mask.sum()
        )

        df.loc[
            missing_distance_mask,
            "Distance_km"
        ] = median_distance

        print(
            "Median delivered-order distance:",
            round(median_distance, 2)
        )

        print(
            "Delivered-order distances imputed:",
            distance_imputed_count
        )

    else:
        print(
            "No valid delivered-order distances available. "
            "Imputation skipped."
        )

    print(
        "Missing distance before imputation:",
        distance_missing_before
    )

    print(
        "Missing distance after imputation:",
        df["Distance_km"].isna().sum()
    )

    # ============================================================
    # 8. MISSING VALUES BY ORDER STATUS
    # ============================================================

    print("\n" + "=" * 70)
    print("7. MISSING VALUES BY ORDER STATUS")
    print("=" * 70)

    delivery_columns = [
        "Delivery_Time_Min",
        "Distance_km",
        "Delivery_Partner_ID",
        "Delivery_Rating"
    ]

    for column in delivery_columns:

        print(f"\n{column} by Order_Status:")

        report = (
            df.groupby("Order_Status", dropna=False)[column]
            .agg(
                Total_Rows="size",
                Missing_Values=lambda x: x.isna().sum(),
                Available_Values=lambda x: x.notna().sum()
            )
        )

        report["Missing_Percentage"] = (
            report["Missing_Values"]
            / report["Total_Rows"]
            * 100
        ).round(2)

        print(report)

    # ============================================================
    # 9. DELIVERY TIME AND DISTANCE MISSINGNESS PATTERN
    # ============================================================

    print("\n" + "=" * 70)
    print("8. DELIVERY TIME AND DISTANCE MISSINGNESS")
    print("=" * 70)

    time_missing = df["Delivery_Time_Min"].isna()
    distance_missing = df["Distance_km"].isna()

    missing_pattern = pd.DataFrame({
        "Both_Missing": time_missing & distance_missing,
        "Time_Only_Missing": time_missing & ~distance_missing,
        "Distance_Only_Missing": ~time_missing & distance_missing,
        "Neither_Missing": ~time_missing & ~distance_missing
    })

    print("\nMissingness counts:")
    print(missing_pattern.sum())

    print("\nMissingness percentages:")
    print((missing_pattern.mean() * 100).round(2))

    delivered = df.loc[delivered_mask]

    print("\nDelivered orders:", len(delivered))

    for column in ["Delivery_Time_Min", "Distance_km"]:

        missing_count = int(delivered[column].isna().sum())

        missing_pct = (
            delivered[column].isna().mean() * 100
            if len(delivered) > 0
            else 0
        )

        print(
            f"{column}: {missing_count:,} missing "
            f"({missing_pct:.2f}%) among delivered orders"
        )

    # ============================================================
    # 10. OUTLIER CHECK
    # ============================================================

    print("\n" + "=" * 70)
    print("9. DELIVERY INFORMATION OUTLIER CHECK")
    print("=" * 70)

    for column in ["Delivery_Time_Min", "Distance_km"]:

        values = df[column].dropna()

        if values.empty:
            print(f"\n{column}: No valid values available.")
            continue

        q1 = values.quantile(0.25)
        q3 = values.quantile(0.75)
        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        outliers = values[
            (values < lower_bound)
            | (values > upper_bound)
        ]

        print(f"\n{column}")
        print(f"Lower IQR bound: {lower_bound:.2f}")
        print(f"Upper IQR bound: {upper_bound:.2f}")
        print(f"Potential outliers: {len(outliers):,}")

        print("\nLargest observed values:")
        print(values.nlargest(10).to_list())

    # ============================================================
    # 11. FINAL VALIDATION
    # ============================================================

    print("\n" + "=" * 70)
    print("10. FINAL DELIVERY INFORMATION VALIDATION")
    print("=" * 70)

    print("\nMissing values after cleaning:")
    print(df[delivery_columns].isna().sum())

    print("\nMissing percentage after cleaning:")
    print(
        (df[delivery_columns].isna().mean() * 100).round(2)
    )

    print("\nFinal data types:")
    print(df[delivery_columns].dtypes)

    # Confirm the rating column remains numeric.
    assert pd.api.types.is_numeric_dtype(
        df["Delivery_Rating"]
    ), "Delivery_Rating must remain numeric."

    print("\nFinal dataset shape:", df.shape)
    print("Delivery information cleaning completed.")

    return df
