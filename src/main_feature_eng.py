# ============================================================
# MAIN FEATURE ENGINEERING SCRIPT
# PROJECT: ONLINE FOOD DELIVERY ANALYSIS
# ============================================================

from feature_engineering.feature_engineering import main


def main_feature_engineering():
    """Run the complete feature engineering pipeline."""
    print("\n" + "=" * 60)
    print("ONLINE FOOD DELIVERY - FEATURE ENGINEERING")
    print("=" * 60)

    main()

    print("\nFeature engineering completed successfully!")


if __name__ == "__main__":
    main_feature_engineering()