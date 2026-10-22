import numpy as np
import pandas as pd


def verify_profit_margin_formula(
    df,
    tolerance=0.01,
    minimum_match_pct=95.0
):
    """
    Verify whether the existing Profit_Margin matches candidate
    formulas based on Order_Value, Final_Amount and Discount_Applied.

    The function does not modify the input dataframe or recalculate
    the original Profit_Margin column.

    Returns
    -------
    dict
        Formula comparison, arithmetic validation and cleaning decision.
    """

    # ============================================================
    # 1. REQUIRED COLUMN VALIDATION
    # ============================================================
    required_columns = [
        "Profit_Margin",
        "Final_Amount",
        "Order_Value",
        "Discount_Applied"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Create a separate numeric copy; preserve the original dataframe
    data = df[required_columns].copy()

    for col in required_columns:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    data = data.replace([np.inf, -np.inf], np.nan)

    profit_margin = data["Profit_Margin"]
    final_amount = data["Final_Amount"]
    order_value = data["Order_Value"]
    discount = data["Discount_Applied"]

    # ============================================================
    # 2. DATA QUALITY ANALYSIS
    # ============================================================
    print("\n" + "=" * 75)
    print("PROFIT MARGIN DATA QUALITY ANALYSIS")
    print("=" * 75)

    print(f"Total rows: {len(data):,}")
    print(
        f"Missing Profit_Margin values: "
        f"{profit_margin.isna().sum():,}"
    )
    print(
        f"Negative Profit_Margin values: "
        f"{profit_margin.lt(0).sum():,}"
    )
    print(
        f"Zero Profit_Margin values: "
        f"{profit_margin.eq(0).sum():,}"
    )
    print(
        f"Positive Profit_Margin values: "
        f"{profit_margin.gt(0).sum():,}"
    )

    print("\nProfit_Margin descriptive statistics:")
    print(profit_margin.describe().to_string())

    # ============================================================
    # 3. CANDIDATE FORMULA GENERATION
    # ============================================================
    valid_order = order_value.notna() & order_value.ne(0)
    valid_final = final_amount.notna() & final_amount.ne(0)

    candidate_formulas = {
        "Discount as % of Order Value": (
            discount.div(order_value).mul(100)
        ).where(valid_order & discount.notna()),

        "Final Amount as % of Order Value": (
            final_amount.div(order_value).mul(100)
        ).where(valid_order & final_amount.notna()),

        "Retained Amount % using Order Value and Discount": (
            (order_value - discount).div(order_value).mul(100)
        ).where(valid_order & discount.notna()),

        "Discount as % of Final Amount": (
            discount.div(final_amount).mul(100)
        ).where(valid_final & discount.notna())
    }

    # ============================================================
    # 4. FORMULA MATCH ANALYSIS
    # ============================================================
    comparison_results = []

    for formula_name, calculated in candidate_formulas.items():

        comparison = pd.DataFrame({
            "actual": profit_margin,
            "calculated": calculated
        }).dropna()

        if comparison.empty:
            comparison_results.append({
                "Formula": formula_name,
                "Comparable_Rows": 0,
                "Matching_Rows": 0,
                "Match_Percentage": np.nan,
                "Mean_Absolute_Error": np.nan
            })
            continue

        differences = (
            comparison["actual"] - comparison["calculated"]
        ).abs()

        matches = np.isclose(
            comparison["actual"],
            comparison["calculated"],
            rtol=0,
            atol=tolerance
        )

        comparison_results.append({
            "Formula": formula_name,
            "Comparable_Rows": len(comparison),
            "Matching_Rows": int(matches.sum()),
            "Match_Percentage": round(
                matches.mean() * 100, 2
            ),
            "Mean_Absolute_Error": round(
                differences.mean(), 4
            )
        })

    results_df = pd.DataFrame(comparison_results)

    print("\n" + "=" * 75)
    print("CANDIDATE FORMULA COMPARISON")
    print("=" * 75)
    print(results_df.to_string(index=False, na_rep="N/A"))

    # ============================================================
    # 5. FINAL AMOUNT ARITHMETIC VALIDATION
    # ============================================================
    arithmetic_data = pd.DataFrame({
        "Final_Amount": final_amount,
        "Order_Value": order_value,
        "Discount_Applied": discount
    }).dropna()

    # This arithmetic check does not require Order_Value to be nonzero.
    if not arithmetic_data.empty:

        expected_final = (
            arithmetic_data["Order_Value"]
            - arithmetic_data["Discount_Applied"]
        )

        arithmetic_matches = np.isclose(
            arithmetic_data["Final_Amount"],
            expected_final,
            rtol=0,
            atol=tolerance
        )

        arithmetic_match_rows = int(arithmetic_matches.sum())

        arithmetic_match_pct = round(
            arithmetic_matches.mean() * 100, 2
        )

        arithmetic_mismatch_rows = int(
            (~arithmetic_matches).sum()
        )

    else:
        arithmetic_match_rows = 0
        arithmetic_mismatch_rows = 0
        arithmetic_match_pct = np.nan

    print("\n" + "=" * 75)
    print("FINAL_AMOUNT ARITHMETIC VALIDATION")
    print("=" * 75)

    print(f"Comparable rows: {len(arithmetic_data):,}")
    print(
        "Rows matching Order_Value - Discount_Applied:",
        f"{arithmetic_match_rows:,}"
    )
    print(
        "Rows not matching the formula:",
        f"{arithmetic_mismatch_rows:,}"
    )
    print(
        f"Arithmetic match percentage: {arithmetic_match_pct}%"
    )

    # ============================================================
    # 6. DETERMINE WHETHER A CANDIDATE FORMULA IS SUPPORTED
    # ============================================================
    usable_results = results_df.dropna(
        subset=["Match_Percentage"]
    )

    decision = {
        "status": None,
        "likely_formula": None,
        "match_percentage": None,
        "formula_results": results_df,
        "final_amount_match_percentage": arithmetic_match_pct,
        "profit_margin_action": "RETAIN ORIGINAL VALUES",
        "recalculated": False
    }

    print("\n" + "=" * 75)
    print("FORMULA VERIFICATION DECISION")
    print("=" * 75)

    if usable_results.empty:
        decision["status"] = "INSUFFICIENT DATA"

        print(
            "Insufficient comparable data to identify a formula."
        )

    else:
        best_match = usable_results["Match_Percentage"].max()

        best_rows = usable_results.loc[
            usable_results["Match_Percentage"].eq(best_match)
        ]

        best_formulas = best_rows["Formula"].tolist()
        best_comparable_rows = int(
            best_rows["Comparable_Rows"].max()
        )

        decision["likely_formula"] = best_formulas
        decision["match_percentage"] = float(best_match)

        if best_comparable_rows < 10:
            decision["status"] = "INSUFFICIENT DATA"

            print(
                "Too few comparable rows for a reliable conclusion."
            )

        elif best_match >= minimum_match_pct:
            decision["status"] = "LIKELY MATCH"

            print(f"Best candidate match: {best_match:.2f}%")
            print("Candidate formula(s):")

            for formula in best_formulas:
                print(f"- {formula}")

            print(
                "This supports a candidate formula, but does not "
                "prove it was the original source formula."
            )

        else:
            decision["status"] = "NO CLEAR MATCH"

            print(f"Best candidate match: {best_match:.2f}%")
            print(
                "None of the tested formulas sufficiently explains "
                "the existing Profit_Margin column."
            )

    # ============================================================
    # 7. FINAL CLEANING DECISION AND ANALYSIS
    # ============================================================
    print("\n" + "=" * 75)
    print("PROFIT_MARGIN CLEANING DECISION")
    print("=" * 75)

    print(
        "Decision: Retain the original Profit_Margin values, "
        "including negative values."
    )

    print(
        "Reason: The actual order cost and the original business "
        "formula are not available for verification."
    )

    print(
        "Do not calculate true profit margin from Order_Value and "
        "Final_Amount alone."
    )

    print(
        "Do not automatically remove negative values or replace "
        "them with zero."
    )

    print(
        "Treat Profit_Margin as an unverified source field until "
        "its definition and units can be confirmed."
    )

    print(
        "Note: Retaining the source values does not establish that "
        "they are correct."
    )

    print("\nNo changes were made to the input dataframe.")
    print("=" * 75)

    return decision