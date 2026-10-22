
from data_analysis.data_overview import dataset_overview
from data_analysis.univariate_analysis.numeric_summary import (
    numerical_summary
)
from data_analysis.univariate_analysis.missing_values_analysis import (
    missing_values_analysis
)
from data_analysis.univariate_analysis.distribution_analysis import (
    distribution_analysis
)
from data_analysis.univariate_analysis.box_plot_analysis import (
    boxplot_analysis
)
from data_analysis.univariate_analysis.categorical_analysis import (
    categorical_analysis
)
from data_analysis.bivariate_analysis.categorical_vs_categorical import (
    categorical_vs_categorical
)

from data_analysis.bivariate_analysis.numerical_vs_numerical import (
    numerical_vs_numerical
)

from data_analysis.bivariate_analysis.numerical_vs_categorical import (
    numerical_vs_categorical
)
from data_analysis.multivariate_analysis.grouped_business_analysis import (
    grouped_business_analysis
)
from data_analysis.multivariate_analysis.payment_peak_analysis import (
    run_payment_peak_analysis
)

def run_EDA_analysis(df):
    dataset_overview(df)
    numerical_summary(df)
    missing_values_analysis(df)
    distribution_analysis(df)
    boxplot_analysis(df)
    categorical_analysis(df)
    categorical_vs_categorical(df)
    numerical_correlation_report = numerical_vs_numerical(df)
    numerical_category_report = numerical_vs_categorical(df)
    grouped_business_report = grouped_business_analysis(df)
    reports = run_payment_peak_analysis(df)
if __name__ == "__main__":
    import pandas as pd

    file_path = r"C:\Users\Priya Jeyakishore\OneDrive\Desktop\GUVI_Data_Science_ZenClass\Online_Food_Delivery_Analysis\output\cleaned_online_food_delivery_dataset.csv"
# Load raw dataset
    df = pd.read_csv(file_path)

    run_EDA_analysis(df)

