
import pandas as pd


def clean_restaurant_data(df, rating_max=None):
    """
    Clean and validate restaurant-related columns.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataset.
    rating_max : float or None, default None
        Maximum permitted rating.
        None: preserve numeric ratings outside 0-5.
        5: treat ratings outside 0-5 as invalid and impute them
           using the median of valid ratings.

    Returns
    -------
    pandas.DataFrame
        Cleaned copy of the input dataset.

    Notes
    -----
    - Preserves row count and column structure.
    - Does not add imputation flag columns.
    - Does not invent restaurant ID/name mappings.
    - Uses Unknown for missing restaurant names and cuisines.
    - Reports source-data consistency issues.
    """

    # ============================================================
    # 1. COPY DATA AND VALIDATE INPUT
    # ============================================================

    df = df.copy()

    original_rows = len(df)
    original_columns = df.columns.tolist()

    required_columns = [
        "Restaurant_ID",
        "Restaurant_Name",
        "Cuisine_Type",
        "Restaurant_Rating"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    if rating_max is not None and rating_max <= 0:
        raise ValueError("rating_max must be positive or None.")

    print("\n" + "=" * 70)
    print("RESTAURANT DATA CLEANING AND VALIDATION")
    print("=" * 70)

    print(f"Original shape: {df.shape}")

    # Use positional assignment for missing ID placeholders.
    # This also works if the DataFrame index has duplicate labels.

    invalid_tokens = {
        "", "nan", "none", "null", "na", "n/a", "<na>"
    }

    # ============================================================
    # 2. CLEAN RESTAURANT IDs
    # ============================================================

    print("\n2. RESTAURANT ID CLEANING")
    print("-" * 50)

    ids = df["Restaurant_ID"].astype("string").str.strip()

    ids = ids.mask(ids.str.lower().isin(invalid_tokens))

    missing_ids_before = int(ids.isna().sum())

    existing_ids = set(ids.dropna().tolist())

    for pos in range(len(ids)):
        if pd.isna(ids.iloc[pos]):
            candidate = f"MISSING_RESTAURANT_ID_{pos + 1:06d}"
            suffix = 1

            while candidate in existing_ids:
                candidate = (
                    f"MISSING_RESTAURANT_ID_{pos + 1:06d}_{suffix}"
                )
                suffix += 1

            ids.iloc[pos] = candidate
            existing_ids.add(candidate)

    df["Restaurant_ID"] = ids.astype("string")

    print("Missing IDs before cleaning:", missing_ids_before)
    print("Missing IDs after cleaning:", int(ids.isna().sum()))
    print("Unique restaurant IDs:", df["Restaurant_ID"].nunique())

    # ============================================================
    # 3. CLEAN RESTAURANT NAMES
    # ============================================================

    print("\n3. RESTAURANT NAME CLEANING")
    print("-" * 50)

    names = df["Restaurant_Name"].astype("string").str.strip()

    names = names.mask(names.str.lower().isin(invalid_tokens))

    # Standardize placeholder capitalization.
    names = names.mask(
        names.str.lower().eq("unknown").fillna(False),
        "Unknown"
    )

    missing_names_before = int(names.isna().sum())

    df["Restaurant_Name"] = names.fillna("Unknown")

    print("Missing names before cleaning:", missing_names_before)
    print(
        "Unknown names after cleaning:",
        int(df["Restaurant_Name"].eq("Unknown").sum())
    )

    # ============================================================
    # 4. CLEAN CUISINE TYPES
    # ============================================================

    print("\n4. CUISINE CLEANING")
    print("-" * 50)

    cuisines = (
        df["Cuisine_Type"]
        .astype("string")
        .str.strip()
    )

    cuisines = cuisines.mask(
        cuisines.str.lower().isin(invalid_tokens)
    )

    cuisines = cuisines.mask(
        cuisines.str.lower().eq("unknown").fillna(False),
        "Unknown"
    )

    missing_cuisines_before = int(cuisines.isna().sum())

    df["Cuisine_Type"] = (
        cuisines.str.title().fillna("Unknown")
    )

    print("Missing cuisines before cleaning:", missing_cuisines_before)
    print(
        "Unknown cuisines after cleaning:",
        int(df["Cuisine_Type"].eq("Unknown").sum())
    )

    # ============================================================
    # 5. CLEAN RESTAURANT RATINGS
    # ============================================================

    print("\n5. RESTAURANT RATING CLEANING")
    print("-" * 50)

    original_ratings = df["Restaurant_Rating"]

    rating_text = (
        original_ratings.astype("string").str.strip()
    )

    rating_text = rating_text.mask(
        rating_text.str.lower().isin(invalid_tokens)
    )

    ratings = pd.to_numeric(rating_text, errors="coerce")

    invalid_text_count = int(
        (original_ratings.notna() & ratings.isna()).sum()
    )

    missing_ratings_before = int(ratings.isna().sum())

    # Use only valid numeric ratings to calculate the median.
    valid_for_median = ratings.dropna()

    if rating_max is not None:
        valid_for_median = valid_for_median[
            valid_for_median.between(0, rating_max)
        ]
    else:
        valid_for_median = valid_for_median[
            valid_for_median.ge(0)
        ]

    if valid_for_median.empty and missing_ratings_before > 0:
        raise ValueError(
            "Cannot impute ratings: no valid numeric ratings "
            "are available for calculating a median."
        )

    # If no imputation is needed, an empty valid set is acceptable.
    rating_median = (
        valid_for_median.median()
        if not valid_for_median.empty
        else None
    )

    # Optionally enforce the chosen rating range.
    if rating_max is not None:
        invalid_range = ~ratings.between(0, rating_max)
        invalid_range_count = int(
            (ratings.notna() & invalid_range).sum()
        )
        ratings = ratings.mask(invalid_range)
    else:
        invalid_range_count = int(
            (ratings.notna() & ratings.lt(0)).sum()
        )
        ratings = ratings.mask(ratings.lt(0))

    missing_after_range_check = int(ratings.isna().sum())

    if missing_after_range_check > 0:
        valid_after_range_check = ratings.dropna()

        if valid_after_range_check.empty:
            raise ValueError(
                "All ratings are missing or outside the permitted "
                "range. Cannot calculate a defensible median."
            )

        rating_median = valid_after_range_check.median()
        ratings = ratings.fillna(rating_median)

    df["Restaurant_Rating"] = ratings

    print("Invalid text ratings:", invalid_text_count)
    print("Missing ratings before cleaning:", missing_ratings_before)
    print("Out-of-range ratings treated as invalid:", invalid_range_count)
    print("Median used for imputation:", rating_median)
    print(
        "Missing ratings after cleaning:",
        int(df["Restaurant_Rating"].isna().sum())
    )

    if rating_max is None:
        print(
            "Rating policy: numeric ratings above 5 were preserved; "
            "negative ratings were treated as invalid."
        )
    else:
        print(f"Rating policy: enforce range 0 to {rating_max}.")

    # ============================================================
    # 6. CHECK RESTAURANT ID / NAME / CUISINE CONSISTENCY
    # ============================================================

    print("\n6. RESTAURANT MAPPING CONSISTENCY")
    print("-" * 50)

    known_names = df.loc[
        df["Restaurant_Name"].ne("Unknown"),
        ["Restaurant_ID", "Restaurant_Name"]
    ]

    known_cuisines = df.loc[
        df["Cuisine_Type"].ne("Unknown"),
        ["Restaurant_ID", "Cuisine_Type"]
    ]

    # Check ID-to-name consistency.
    id_name_counts = (
        known_names.groupby("Restaurant_ID")["Restaurant_Name"]
        .nunique()
    )

    conflicting_ids = id_name_counts[id_name_counts > 1]

    # Check ID-to-cuisine consistency independently.
    id_cuisine_counts = (
        known_cuisines.groupby("Restaurant_ID")["Cuisine_Type"]
        .nunique()
    )

    conflicting_cuisine_ids = id_cuisine_counts[
        id_cuisine_counts > 1
    ]

    # Check name-to-ID consistency.
    name_id_counts = (
        known_names.groupby("Restaurant_Name")["Restaurant_ID"]
        .nunique()
    )

    conflicting_names = name_id_counts[name_id_counts > 1]

    print("Unique IDs:", df["Restaurant_ID"].nunique())
    print("IDs associated with multiple known names:",
          len(conflicting_ids))
    print("IDs associated with multiple known cuisines:",
          len(conflicting_cuisine_ids))
    print("Names associated with multiple IDs:",
          len(conflicting_names))

    if not conflicting_ids.empty:
        print("\nTop conflicting IDs and name counts:")
        print(
            conflicting_ids.sort_values(
                ascending=False
            ).head(10).to_string()
        )

    if not conflicting_cuisine_ids.empty:
        print("\nTop conflicting IDs and cuisine counts:")
        print(
            conflicting_cuisine_ids.sort_values(
                ascending=False
            ).head(10).to_string()
        )

    if not conflicting_names.empty:
        print("\nTop names linked to multiple IDs:")
        print(
            conflicting_names.sort_values(
                ascending=False
            ).head(10).to_string()
        )

    print(
        "\nMapping conflicts are reported, not automatically changed: "
        "the correct mappings cannot be inferred safely."
    )

    # ============================================================
    # 7. MISSING VALUE VALIDATION
    # ============================================================

    print("\n7. MISSING VALUE VALIDATION")
    print("-" * 50)

    print("\nMissing values:")
    print(df[required_columns].isna().sum())

    print("\nMissing percentage:")
    print(
        (df[required_columns].isna().mean() * 100).round(2)
    )

    # ============================================================
    # 8. RESTAURANT SUMMARY
    # ============================================================

    print("\n8. RESTAURANT SUMMARY")
    print("-" * 50)

    print("Total records:", len(df))
    print("Unique restaurant IDs:", df["Restaurant_ID"].nunique())
    print("Unique restaurant names:", df["Restaurant_Name"].nunique())
    print("Unique cuisine types:", df["Cuisine_Type"].nunique())

    print("\nCuisine distribution:")
    print(df["Cuisine_Type"].value_counts(dropna=False))

    # ============================================================
    # 9. RATING SUMMARY
    # ============================================================

    print("\n9. RESTAURANT RATING SUMMARY")
    print("-" * 50)

    print(df["Restaurant_Rating"].describe())

    print("\nRating frequency:")
    print(
        df["Restaurant_Rating"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    above_5 = df["Restaurant_Rating"].gt(5)

    print("\nRatings above 5:", int(above_5.sum()))
    print(
        "Percentage above 5:",
        round(above_5.mean() * 100, 2),
        "%"
    )

    if above_5.any():
        print("\nSample records with ratings above 5:")
        print(
            df.loc[
                above_5,
                [
                    "Restaurant_ID",
                    "Restaurant_Name",
                    "Cuisine_Type",
                    "Restaurant_Rating"
                ]
            ].head(10).to_string(index=False)
        )

    # ============================================================
    # 10. FINAL VALIDATION
    # ============================================================

    print("\n10. FINAL VALIDATION")
    print("-" * 50)

    assert len(df) == original_rows, "Row count changed."
    assert df.columns.tolist() == original_columns, (
        "Column structure changed."
    )
    assert df[required_columns].isna().sum().sum() == 0, (
        "Missing values remain in required restaurant columns."
    )
    assert df["Restaurant_ID"].nunique() <= len(df), (
        "Unique ID count cannot exceed the number of records."
    )
    assert pd.api.types.is_numeric_dtype(
        df["Restaurant_Rating"]
    ), "Restaurant_Rating must be numeric."

    print("Row count preserved:", len(df) == original_rows)
    print("Column structure preserved:",
          df.columns.tolist() == original_columns)
    print("No missing values in required columns:",
          df[required_columns].isna().sum().sum() == 0)
    print("Ratings are numeric:",
          pd.api.types.is_numeric_dtype(df["Restaurant_Rating"]))
    print("Final shape:", df.shape)

    if len(conflicting_ids) or len(conflicting_cuisine_ids):
        print(
            "\nWARNING: Restaurant ID mappings remain inconsistent. "
            "Verify them against a trusted source."
        )

    if above_5.any() and rating_max is None:
        print(
            "WARNING: Ratings above 5 remain. Confirm the source scale."
        )

    print("\nRestaurant data cleaning completed.")

    return df
