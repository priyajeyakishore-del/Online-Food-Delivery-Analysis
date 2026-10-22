import pandas as pd
def dataset_overview(df):

    print("\n" + "=" * 70)
    print("1. DATASET OVERVIEW")
    print("=" * 70)

    # --------------------------------------------------------
    # 1.1 Dataset dimensions
    # --------------------------------------------------------
    print("\n1.1 DATASET SHAPE")
    print("-" * 70)

    rows, columns = df.shape

    print(f"Total rows    : {rows:,}")
    print(f"Total columns : {columns:,}")

    # --------------------------------------------------------
    # 1.2 Dataset information
    # --------------------------------------------------------
    print("\n1.2 DATASET INFORMATION")
    print("-" * 70)

    df.info()

    # --------------------------------------------------------
    # 1.3 Numerical summary
    # --------------------------------------------------------
    print("\n1.3 NUMERICAL COLUMN SUMMARY")
    print("-" * 70)

    print(df.describe())

    # --------------------------------------------------------
    # 1.4 Categorical summary
    # --------------------------------------------------------
    print("\n1.4 CATEGORICAL COLUMN SUMMARY")
    print("-" * 70)

    categorical_columns = df.select_dtypes(
        include=["object", "string", "category"]
    ).columns

    if len(categorical_columns) > 0:
        print(df[categorical_columns].describe().T)
    else:
        print("No categorical columns found.")

    # --------------------------------------------------------
    # 1.5 Key business metrics
    # --------------------------------------------------------
    print("\n1.5 KEY BUSINESS METRICS")
    print("-" * 70)

    total_orders = df["Order_ID"].nunique()

    total_customers = df["Customer_ID"].nunique()

    total_restaurants = df["Restaurant_ID"].nunique()

    total_cities = df["City"].nunique()

    total_cuisines = df["Cuisine_Type"].nunique()

    # Exclude missing dates when calculating the date range
    order_dates = pd.to_datetime(
        df["Order_Date"],
        errors="coerce"
    ).dropna()

    if not order_dates.empty:
        start_date = order_dates.min().date()
        end_date = order_dates.max().date()
    else:
        start_date = "Not available"
        end_date = "Not available"

    print(f"Total orders      : {total_orders:,}")
    print(f"Total customers   : {total_customers:,}")
    print(f"Total restaurants : {total_restaurants:,}")
    print(f"Date range        : {start_date} to {end_date}")
    print(f"Number of cities  : {total_cities:,}")
    print(f"Number of cuisines: {total_cuisines:,}")

    print("\n" + "=" * 70)
    print("DATASET OVERVIEW COMPLETED")
    print("=" * 70)



