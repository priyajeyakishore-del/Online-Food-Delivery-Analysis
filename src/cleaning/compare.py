# ============================================================
# DATASET COMPARISON BEFORE AND AFTER CLEANING
# ============================================================
import pandas as pd 
def compare_dataset_before_after(df_raw, df):
    """
    Compare raw and cleaned datasets.

    Parameters:
        df_raw : Dataset before cleaning
        df     : Dataset after cleaning

    Returns:
        Summary report as a dictionary
    """

    print("\n" + "=" * 70)
    print("DATASET COMPARISON: BEFORE VS AFTER CLEANING")
    print("=" * 70)

    # --------------------------------------------------------
    # 1. DATASET SHAPE COMPARISON
    # --------------------------------------------------------

    print("\n1. DATASET SHAPE")

    print(f"Before cleaning: {df_raw.shape}")
    print(f"After cleaning : {df.shape}")

    print(f"Rows before: {len(df_raw):,}")
    print(f"Rows after : {len(df):,}")

    print(f"Columns before: {len(df_raw.columns)}")
    print(f"Columns after : {len(df.columns)}")

    print(f"Rows removed: {len(df_raw) - len(df):,}")
    print(f"Columns removed: {len(df_raw.columns) - len(df.columns)}")

    # --------------------------------------------------------
    # 2. COLUMN COMPARISON
    # --------------------------------------------------------

    print("\n2. COLUMN CHANGES")

    removed_columns = sorted(
        set(df_raw.columns) - set(df.columns)
    )

    added_columns = sorted(
        set(df.columns) - set(df_raw.columns)
    )

    common_columns = [
        col for col in df_raw.columns
        if col in df.columns
    ]

    print("Removed columns:", removed_columns or "None")
    print("Added columns:", added_columns or "None")
    print("Common columns:", len(common_columns))

    # --------------------------------------------------------
    # 3. MISSING VALUE COMPARISON
    # --------------------------------------------------------

    print("\n3. MISSING VALUE COMPARISON")

    raw_missing = df_raw.isna().sum()
    clean_missing = df.isna().sum()

    missing_comparison = pd.DataFrame({
        "Missing_Before": raw_missing,
        "Missing_After": clean_missing.reindex(
            raw_missing.index
        ),
    })

    missing_comparison["Missing_After"] = (
        missing_comparison["Missing_After"]
        .fillna(0)
        .astype(int)
    )

    missing_comparison["Missing_Before_%"] = (
        missing_comparison["Missing_Before"]
        / len(df_raw) * 100
    ).round(2)

    missing_comparison["Missing_After_%"] = (
        missing_comparison["Missing_After"]
        / len(df) * 100
        if len(df) > 0
        else 0
    )

    missing_comparison["Missing_After_%"] = (
        missing_comparison["Missing_After_%"].round(2)
    )

    missing_comparison["Missing_Values_Change"] = (
        missing_comparison["Missing_Before"]
        - missing_comparison["Missing_After"]
    )

    print(
        missing_comparison.to_string()
    )

    # --------------------------------------------------------
    # 4. DATA TYPE COMPARISON
    # --------------------------------------------------------

    print("\n4. DATA TYPE COMPARISON")

    dtype_comparison = pd.DataFrame({
        "Data_Type_Before": df_raw.dtypes.astype(str),
        "Data_Type_After": df.dtypes.astype(str)
    })

    dtype_comparison["Type_Changed"] = (
        dtype_comparison["Data_Type_Before"]
        != dtype_comparison["Data_Type_After"]
    )

    print(dtype_comparison.to_string())

    # --------------------------------------------------------
    # 5. DUPLICATE ROW COMPARISON
    # --------------------------------------------------------

    print("\n5. DUPLICATE ROWS")

    raw_duplicates = df_raw.duplicated().sum()
    clean_duplicates = df.duplicated().sum()

    print(f"Before cleaning: {raw_duplicates:,}")
    print(f"After cleaning : {clean_duplicates:,}")
    print(
        f"Duplicate reduction: "
        f"{raw_duplicates - clean_duplicates:,}"
    )

    # --------------------------------------------------------
    # 6. MEMORY USAGE COMPARISON
    # --------------------------------------------------------

    print("\n6. MEMORY USAGE")

    raw_memory = df_raw.memory_usage(
        deep=True
    ).sum() / (1024 ** 2)

    clean_memory = df.memory_usage(
        deep=True
    ).sum() / (1024 ** 2)

    print(f"Before cleaning: {raw_memory:.2f} MB")
    print(f"After cleaning : {clean_memory:.2f} MB")
    print(f"Memory change   : {clean_memory - raw_memory:.2f} MB")

    # --------------------------------------------------------
    # 7. SUMMARY
    # --------------------------------------------------------

    print("\n7. CLEANING SUMMARY")

    print(
        f"Rows preserved: "
        f"{len(df) == len(df_raw)}"
    )

    print(
        f"Columns preserved: "
        f"{set(df.columns) == set(df_raw.columns)}"
    )

    print(
        f"Missing values before: "
        f"{df_raw.isna().sum().sum():,}"
    )

    print(
        f"Missing values after: "
        f"{df.isna().sum().sum():,}"
    )

    print("\nDataset comparison completed.")

    return {
        "missing_comparison": missing_comparison,
        "dtype_comparison": dtype_comparison,
        "removed_columns": removed_columns,
        "added_columns": added_columns
    }