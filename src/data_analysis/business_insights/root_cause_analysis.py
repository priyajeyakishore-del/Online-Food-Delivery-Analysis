
# ============================================================
# ROOT CAUSE ANALYSIS
# PROJECT: ONLINE FOOD DELIVERY ANALYSIS
# File: data_analysis/business_insights/root_cause_analysis.py
# ============================================================

import pandas as pd


# ============================================================
# 1. REUSABLE HELPER FUNCTIONS
# ============================================================

def get_numeric_series(df, column):
    """Convert a column to numeric and return valid values."""
    if column not in df.columns:
        return pd.Series(dtype="float64")

    return pd.to_numeric(
        df[column], errors="coerce"
    ).dropna()


def format_number(value, decimals=2):
    """Format numeric values consistently."""
    if value is None or pd.isna(value):
        return "N/A"

    return f"{value:,.{decimals}f}"


def normalize_status(series):
    """Standardize order-status labels."""
    return (
        series.astype("string")
        .str.strip()
        .str.title()
    )


def categorical_rate_analysis(
    df,
    category_column,
    min_group_size=100
):
    """
    Compare cancellation rates across category groups.

    Returns a DataFrame with group sizes and cancellation rates.
    Only Delivered and Cancelled orders are used in the denominator.
    """

    required_columns = {
        category_column,
        "Order_Status",
    }

    if not required_columns.issubset(df.columns):
        return pd.DataFrame()

    temp = df[[category_column, "Order_Status"]].copy()

    temp["_Status"] = normalize_status(temp["Order_Status"])

    # Exclude other statuses from this comparison.
    temp = temp[
        temp["_Status"].isin(["Delivered", "Cancelled"])
    ].copy()

    temp = temp.dropna(subset=[category_column])

    temp[category_column] = (
        temp[category_column].astype(str).str.strip()
    )

    temp = temp[temp[category_column].ne("")]

    if temp.empty:
        return pd.DataFrame()

    grouped = temp.groupby(category_column).agg(
        Total_Orders=("_Status", "size"),
        Cancelled_Orders=(
            "_Status",
            lambda values: (values == "Cancelled").sum()
        ),
        Delivered_Orders=(
            "_Status",
            lambda values: (values == "Delivered").sum()
        ),
    )

    grouped = grouped[
        grouped["Total_Orders"] >= min_group_size
    ].copy()

    if grouped.empty:
        return pd.DataFrame()

    grouped["Cancellation_Rate_Percent"] = (
        grouped["Cancelled_Orders"]
        / grouped["Total_Orders"]
        * 100
    )

    return grouped.sort_values(
        "Cancellation_Rate_Percent",
        ascending=False
    )


def relationship_analysis(
    df,
    feature_column,
    target_column,
    min_group_size=100
):
    """Summarize a numeric target across categorical groups."""

    if feature_column not in df.columns:
        return pd.DataFrame()

    if target_column not in df.columns:
        return pd.DataFrame()

    temp = df[[feature_column, target_column]].copy()

    temp[target_column] = pd.to_numeric(
        temp[target_column], errors="coerce"
    )

    temp = temp.dropna(
        subset=[feature_column, target_column]
    )

    # Exclude negative delivery time and distance values.
    if target_column in {"Delivery_Time", "Distance"}:
        temp = temp[temp[target_column] >= 0]

    if temp.empty:
        return pd.DataFrame()

    result = temp.groupby(feature_column).agg(
        Record_Count=(target_column, "size"),
        Average_Value=(target_column, "mean"),
        Median_Value=(target_column, "median"),
    )

    result = result[
        result["Record_Count"] >= min_group_size
    ].copy()

    if result.empty:
        return pd.DataFrame()

    return result.sort_values(
        "Average_Value", ascending=False
    )


# ============================================================
# 2. ROOT CAUSE ANALYSIS FUNCTION
# ============================================================

def root_cause_analysis(df):
    """
    Investigate potential factors associated with:
    - Order cancellations
    - Delivery delays
    - Order value variation
    - Cancellation reasons

    Parameters
    ----------
    df : pandas.DataFrame
        Already-loaded, cleaned food delivery dataset.

    Returns
    -------
    str
        Formatted root cause analysis report.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame.")

    if df.empty:
        return (
            "=" * 65
            + "\n6. ROOT CAUSE ANALYSIS\n"
            + "=" * 65
            + "\nNo analysis is available because the dataset is empty."
        )

    lines = [
        "=" * 65,
        "6. ROOT CAUSE ANALYSIS",
        "=" * 65,
        "",
        "Purpose: Identify patterns associated with business problems.",
        "Note: Associations alone do not establish causation.",
    ]

    # --------------------------------------------------------
    # 1. Cancellation analysis by category
    # --------------------------------------------------------

    lines.extend([
        "",
        "1. CANCELLATION PATTERNS BY CATEGORY",
    ])

    category_columns = [
        "City",
        "Cuisine_Type",
        "Payment_Mode",
        "Customer_Gender",
    ]

    cancellation_findings = 0

    for column in category_columns:
        result = categorical_rate_analysis(
            df,
            category_column=column,
            min_group_size=100,
        )

        if result.empty:
            continue

        cancellation_findings += 1

        highest_group = result.iloc[0]
        highest_category = result.index[0]

        lowest_group = result.iloc[-1]
        lowest_category = result.index[-1]

        lines.append(f"\n   {column}:")

        lines.append(
            f"   - Highest observed cancellation rate: "
            f"{highest_category} "
            f"({highest_group['Cancellation_Rate_Percent']:.2f}%; "
            f"{int(highest_group['Total_Orders']):,} orders)."
        )

        lines.append(
            f"   - Lowest observed cancellation rate: "
            f"{lowest_category} "
            f"({lowest_group['Cancellation_Rate_Percent']:.2f}%; "
            f"{int(lowest_group['Total_Orders']):,} orders)."
        )

    if cancellation_findings == 0:
        lines.append(
            "   No suitable category-level cancellation comparisons "
            "could be calculated."
        )

    lines.append(
        "\n   Interpretation: These comparisons identify groups for "
        "further investigation; they do not prove why orders were cancelled."
    )

    # --------------------------------------------------------
    # 2. Cancellation reasons
    # --------------------------------------------------------

    lines.extend([
        "",
        "2. REPORTED CANCELLATION REASONS",
    ])

    if (
        "Cancellation_Reason" in df.columns
        and "Order_Status" in df.columns
    ):
        status = normalize_status(df["Order_Status"])

        cancelled_mask = status.eq("Cancelled").fillna(False)

        cancelled = df.loc[
            cancelled_mask, "Cancellation_Reason"
        ]

        reasons = (
            cancelled.dropna()
            .astype(str)
            .str.strip()
        )

        # Exclude blank and generic placeholder values.
        placeholders = {
            "",
            "unknown",
            "not applicable",
            "n/a",
            "na",
            "none",
            "nan",
        }

        reasons = reasons[
            ~reasons.str.lower().isin(placeholders)
        ]

        if not reasons.empty:
            reason_counts = reasons.value_counts()

            reported_reason_count = len(reasons)

            lines.append(
                f"   Orders with a usable reported reason: "
                f"{reported_reason_count:,}."
            )

            for reason, count in reason_counts.head(5).items():
                lines.append(
                    f"   - {reason}: {count:,} "
                    f"({count / reported_reason_count * 100:.2f}% "
                    "of orders with a usable reported reason)."
                )

            lines.append(
                "   Percentages describe only cancelled orders with "
                "a usable recorded reason, not all cancelled orders."
            )
        else:
            lines.append(
                "   No usable cancellation reasons are available."
            )
    else:
        lines.append(
            "   Cancellation_Reason or Order_Status column is unavailable."
        )

    # --------------------------------------------------------
    # 3. Delivery time and distance relationship
    # --------------------------------------------------------

    lines.extend([
        "",
        "3. DELIVERY TIME AND DISTANCE",
    ])

    if (
        "Delivery_Time" in df.columns
        and "Distance" in df.columns
    ):
        temp = df[["Delivery_Time", "Distance"]].copy()

        temp["Delivery_Time"] = pd.to_numeric(
            temp["Delivery_Time"], errors="coerce"
        )

        temp["Distance"] = pd.to_numeric(
            temp["Distance"], errors="coerce"
        )

        temp = temp.dropna()

        temp = temp[
            (temp["Delivery_Time"] >= 0)
            & (temp["Distance"] >= 0)
        ]

        if len(temp) >= 3:
            correlation = temp["Delivery_Time"].corr(
                temp["Distance"]
            )

            lines.append(
                f"   Valid paired records: {len(temp):,}."
            )

            if pd.notna(correlation):
                lines.append(
                    f"   Pearson correlation between distance and "
                    f"delivery time: {correlation:.3f}."
                )

                if correlation >= 0.5:
                    lines.append(
                        "   - The variables show a relatively strong "
                        "positive linear association."
                    )
                elif correlation >= 0.3:
                    lines.append(
                        "   - The variables show a moderate positive "
                        "linear association."
                    )
                elif correlation > 0:
                    lines.append(
                        "   - The variables show a weak positive "
                        "linear association."
                    )
                elif correlation <= -0.3:
                    lines.append(
                        "   - The variables show a negative linear "
                        "association."
                    )
                else:
                    lines.append(
                        "   - The linear association is weak or limited."
                    )

                lines.append(
                    "   - Correlation does not establish that distance "
                    "causes delivery delays."
                )
            else:
                lines.append(
                    "   Correlation could not be calculated because "
                    "one of the variables has no variation."
                )
        else:
            lines.append(
                "   Insufficient valid paired records for correlation."
            )
    else:
        lines.append(
            "   Delivery_Time or Distance column is unavailable."
        )

    # --------------------------------------------------------
    # 4. Delivery time by category
    # --------------------------------------------------------

    lines.extend([
        "",
        "4. DELIVERY TIME BY CATEGORY",
    ])

    delivery_categories = [
        "City",
        "Cuisine_Type",
        "Delivery_Partner_ID",
    ]

    delivery_findings = 0

    for column in delivery_categories:
        result = relationship_analysis(
            df,
            feature_column=column,
            target_column="Delivery_Time",
            min_group_size=100,
        )

        if result.empty:
            continue

        delivery_findings += 1

        slowest_category = result.index[0]
        slowest = result.iloc[0]

        fastest_category = result.index[-1]
        fastest = result.iloc[-1]

        lines.append(f"\n   {column}:")

        lines.append(
            f"   - Highest average delivery time: "
            f"{slowest_category} "
            f"({format_number(slowest['Average_Value'])} minutes; "
            f"{int(slowest['Record_Count']):,} records)."
        )

        lines.append(
            f"   - Lowest average delivery time: "
            f"{fastest_category} "
            f"({format_number(fastest['Average_Value'])} minutes; "
            f"{int(fastest['Record_Count']):,} records)."
        )

    if delivery_findings == 0:
        lines.append(
            "   No suitable category-level delivery-time comparisons "
            "could be calculated."
        )

    # --------------------------------------------------------
    # 5. Order value and discounts
    # --------------------------------------------------------

    lines.extend([
        "",
        "5. ORDER VALUE AND DISCOUNTS",
    ])

    if "Order_Value" in df.columns:
        order_values = get_numeric_series(df, "Order_Value")

        if not order_values.empty:
            lines.append(
                f"   Average order value: "
                f"{format_number(order_values.mean())}."
            )

            lines.append(
                f"   Median order value: "
                f"{format_number(order_values.median())}."
            )

            lines.append(
                f"   Valid order-value records: "
                f"{len(order_values):,}."
            )

        if (
            "Discount_Applied" in df.columns
            and "Final_Amount" in df.columns
        ):
            amounts = pd.DataFrame({
                "Order_Value": pd.to_numeric(
                    df["Order_Value"], errors="coerce"
                ),
                "Discount_Applied": pd.to_numeric(
                    df["Discount_Applied"], errors="coerce"
                ),
                "Final_Amount": pd.to_numeric(
                    df["Final_Amount"], errors="coerce"
                ),
            }).dropna()

            if not amounts.empty:
                negative_final = amounts["Final_Amount"] < 0
                negative_count = int(negative_final.sum())

                lines.append(
                    f"   Records with complete amount fields: "
                    f"{len(amounts):,}."
                )

                lines.append(
                    f"   Negative final amounts: {negative_count:,}."
                )

                if negative_count:
                    lines.append(
                        "   - Review whether discounts exceed order values "
                        "and whether the final amount calculation is valid."
                    )

                formula_matches = (
                    amounts["Order_Value"]
                    - amounts["Discount_Applied"]
                )

                formula_mismatch = ~(
                    (formula_matches - amounts["Final_Amount"])
                    .abs()
                    .le(0.01)
                )

                lines.append(
                    f"   Final amounts differing from "
                    f"Order_Value - Discount_Applied by more than 0.01: "
                    f"{int(formula_mismatch.sum()):,}."
                )

                lines.append(
                    "   - Validate the business rules before treating "
                    "all differences as data errors."
                )
    else:
        lines.append("   Order_Value column is unavailable.")

    # --------------------------------------------------------
    # 6. Potential root causes to investigate
    # --------------------------------------------------------

    lines.extend([
        "",
        "6. AREAS FOR FURTHER INVESTIGATION",
        "   - Compare cancellation rates across cities and cuisines.",
        "   - Check whether delivery distance is associated with longer",
        "     delivery times.",
        "   - Review reported cancellation reasons and missing reason data.",
        "   - Investigate delivery partner workloads and performance.",
        "   - Validate discount rules and final amount calculations.",
        "   - Check whether peak periods affect delivery time or cancellations.",
        "",
        "IMPORTANT:",
        "   The findings above describe observed relationships in the data.",
        "   They do not establish causal effects. Confirm root causes using",
        "   operational records, additional variables, and suitable tests.",
    ])

    return "\n".join(lines)
