import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns  

pd.set_option('display.max_columns', None)


class DataProcessor:
    def __init__(self, origination_file, servicing_file, dataset_path="data/combined_dataset", output_path="data/plots"):
        self.origination_file = origination_file
        self.servicing_file = servicing_file
        self.dataset_path = dataset_path
        self.output_path = output_path  
        self.origination = None
        self.servicing = None
        self.data = None  

    def load_data(self):
        try:
            self.origination = pd.read_csv(self.origination_file, low_memory=False)
            self.servicing = pd.read_csv(self.servicing_file, low_memory=False)
            print("Data loaded successfully.")
        except FileNotFoundError as e:
            print(f"Error: {e}")
            raise 

    def preprocess_data(self):
        self.origination["loan_sequence_number"] = self.origination["loan_sequence_number"].astype(str)
        self.servicing["loan_sequence_number"] = self.servicing["loan_sequence_number"].astype(str)
        self.origination.dropna(subset=["loan_sequence_number"], inplace=True)
        self.servicing.dropna(subset=["loan_sequence_number"], inplace=True)
        self.servicing['monthly_reporting_period'] = pd.to_datetime(
            self.servicing['monthly_reporting_period'].astype(str), format='%Y%m'
        )
        self.servicing.sort_values(by=["loan_sequence_number", "monthly_reporting_period"], inplace=True)
        print(self.origination.shape)
        print(self.servicing.shape)
        
    def merge_data(self):
        if self.servicing is not None and self.origination is not None:
            self.data = self.servicing.merge(
                self.origination,
                on='loan_sequence_number',
                how='left'
            )
        else:
            raise ValueError("Servicing or origination data not loaded.")

    def create_target_variable(self):
        self.data['is_default'] = self.data['current_loan_delinquency_status'].apply(
            lambda x: 1 if (x == 'RA' or (x.isdigit() and int(x) >= 3)) else 0
        )

    def create_lag_features(self):
        self.data["prior_dq_status"] = self.data.groupby("loan_sequence_number")["current_loan_delinquency_status"].shift(1)
        self.data["prior_upb"] = self.data.groupby("loan_sequence_number")["current_actual_upb"].shift(1)
        
    def plot_summary_statistics(self, features):
        if features is None:
            features = self.data.select_dtypes(include="number").columns.tolist()

        data = self.data[features].copy()
        summary = data.describe().T
        summary = summary[['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']]
        num_rows = len(summary.index)
        num_cols = len(summary.columns)
        fig_width = min(1 + 0.9 * num_cols, 12)
        fig_height = min(1 + 0.5 * num_rows, 10)
        plt.figure(figsize=(fig_width, fig_height))
        table = plt.table(
            cellText=np.round(summary.values, 2),
            rowLabels=summary.index,
            colLabels=summary.columns,
            cellLoc='center',
            loc='center',
            fontsize=8  
        )
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1.2, 1.2) 

        plt.axis('off')
        plt.tight_layout()
        filename = f"{self.output_path}/summary_stats.png"
        plt.savefig(filename, dpi=300)
        plt.show()
        plt.close()
        
    def remove_missing_rows(self, features):
        for col in features:
            if col not in self.data.columns:
                print(f"Warning: {col} not found in data. Skipping.")
                continue

            if col == 'credit_score':
                self.data = self.data[self.data[col] != 9999]
            else:
                self.data = self.data[self.data[col] != 999]

    def remove_outliers_by_percentile(self, features, lower_percentile=0.01, upper_percentile=0.99):
        for col in features:
            if col not in self.data.columns:
                print(f"Warning: {col} not in dataframe.")
                continue
            if self.data[col].dtype not in [np.float64, np.int64, np.float32, np.int32]:
                print(f"Warning: {col} is not numeric.")
                continue

            lower = self.data[col].quantile(lower_percentile)
            upper = self.data[col].quantile(upper_percentile)
            self.data = self.data[(self.data[col] >= lower) & (self.data[col] <= upper)]

    def save_data_to_csv(self):
        self.data.to_csv(f"{self.dataset_path}/data.csv", index=False)
        print(f"Final dataset saved to {self.dataset_path}/data.csv")
        print(f"Final combined dataset contains: {self.data.shape}")
        print("This shows the first few rows:")
        print(self.data.head())
            
    # VISUALIZATION 
    def plot_correlation_map(self, features):
        corr = self.data[features].corr()
        plt.figure(figsize=(8, 6))
        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".4f")
        plt.title("Correlation Matrix (Including Binary Default)")
        plt.savefig(f"{self.output_path}/correlation.png")
        plt.show()
        plt.close()

    def plot_number_of_defaults_over_time(self):
        defaults_by_month = (
                self.data[self.data['is_default'] == 1]
                .groupby('monthly_reporting_period')
                .size()
                .sort_index()
            )

        fig, ax = plt.subplots(figsize=(8, 6))
        defaults_by_month.plot(kind='line', marker='o', ax=ax)
        ax.set_title('Count of Defaults per Month')
        ax.set_xlabel('Month')
        ax.set_ylabel('Default Count')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"{self.output_path}/defaults_per_month.png")
        plt.show()
        plt.close()

    def plot_current_status_over_time(self):
        filtered = self.data[self.data['current_loan_delinquency_status'] == '0']
        status_by_month = (
            filtered
            .groupby('monthly_reporting_period')
            .size()
            .sort_index()
        )
        fig, ax = plt.subplots(figsize=(8, 6))
        status_by_month.plot(kind='line', marker='o', ax=ax)
        ax.set_title("Loans in Current Status Over Time")
        ax.set_xlabel('Month')
        ax.set_ylabel('Number of Loans')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"{self.output_path}/current_status_trend_linechart.png")
        plt.show()
        plt.close()

    def plot_delinquency_status_over_time(self):
        target_statuses = ['1', '2', '3', '6', '7', 'RA']
        filtered = self.data[self.data['current_loan_delinquency_status'].isin(target_statuses)]
        delinquency_status_by_month = (
                filtered
                .groupby(['monthly_reporting_period', 'current_loan_delinquency_status'])
                .size()
                .unstack(fill_value=0)
                .sort_index()
            )
        ordered_cols = ['1', '2', '3', '6', '7', 'RA']
        delinquency_status_by_month = delinquency_status_by_month[ordered_cols]
        status_labels = {
            '1': '30 Days Delinquent',
            '2': '60 Days Delinquent',
            '3': '90 Days Delinquent',
            '6': '180+ Days Delinquent',
            '7': 'Foreclosure',
            'RA': 'REO Acquired'
        }   
        delinquency_status_by_month.rename(columns=status_labels, inplace=True)
        ax = delinquency_status_by_month.plot(
                kind='line',
                figsize=(8, 6),
                colormap='tab10',
                marker='o'  
            )
        ax.set_title('Delinquency Status Trends Over Time')
        ax.set_xlabel('Month')
        ax.set_ylabel('Number of Loans')
        ax.legend(title='Delinquency Status', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"{self.output_path}/delinquency_status_trends_linechart.png")
        plt.show()
        plt.close()

    def plot_loan_age_distribution(self):
        plt.figure(figsize=(8, 6))
        sns.histplot(data=self.data, x='loan_age', hue='is_default', bins=50, kde=True, element="step", stat="density", common_norm=False)
        plt.title('Loan Age Distribution by Default Status')
        plt.xlabel('Loan Age (months)')
        plt.ylabel('Density')
        plt.savefig(f"{self.output_path}/loan_age_by_default.png")
        plt.show()
        plt.close()
        
    def plot_credit_score_distribution(self):
        plt.figure(figsize=(8, 6))
        sns.histplot(data=self.data, x='credit_score', hue='is_default', bins=50, kde=True, element="step", stat="density", common_norm=False)
        plt.title('Credit Score Distribution by Default Status')
        plt.xlabel('Credit Score at Origination')
        plt.ylabel('Density')
        plt.savefig(f"{self.output_path}/credit_score_by_default.png")
        plt.show()
        plt.close()
  
    def plot_original_debt_to_income_ratio(self):
        plt.figure(figsize=(8, 6))
        sns.histplot(data=self.data, x='original_debt_to_income_ratio', hue='is_default', bins=50, kde=True, element="step", stat="density", common_norm=False)
        plt.title('Original DTI Distribution by Default Status')
        plt.xlabel('Original DTI')
        plt.ylabel('Density')
        plt.savefig(f"{self.output_path}/original_dti_by_default.png")
        plt.show()
        plt.close()

    def plot_original_combined_loan_to_value(self):
        plt.figure(figsize=(8, 6))
        sns.histplot(data=self.data, x='original_combined_loan_to_value', hue='is_default', bins=50, kde=True, element="step", stat="density", common_norm=False)
        plt.title('Original CLTV Distribution by Default Status')
        plt.xlabel('Original CLTV')
        plt.ylabel('Density')
        plt.savefig(f"{self.output_path}/original_cltv_by_default.png")
        plt.show()
        plt.close()

    def plot_interest_rate_over_time(self):
        plt.figure(figsize=(8, 6))
        sns.lineplot(data=self.data, x='monthly_reporting_period', y='current_interest_rate', hue='is_default', estimator='mean')
        plt.title('Average Interest Rate Over Time by Default Status')
        plt.xlabel('Month')
        plt.ylabel('Interest Rate')
        plt.savefig(f"{self.output_path}/interest_rate_by_default.png")
        plt.show()
        plt.close()

    # MAIN
    def run_data_processing(self):
        self.load_data()
        self.preprocess_data()
        self.merge_data()
        self.create_target_variable()
        self.create_lag_features()
        self.remove_missing_rows(features=['credit_score', 'original_combined_loan_to_value', 'original_debt_to_income_ratio'])
        self.plot_summary_statistics(features=['credit_score', 'loan_age', 'original_combined_loan_to_value', 'original_debt_to_income_ratio', 'current_interest_rate'])
        # self.remove_outliers_by_percentile(
        #     features=['credit_score', 'loan_age', 'original_combined_loan_to_value', 
        #             'original_debt_to_income_ratio', 'current_interest_rate'],
        #     lower_percentile=0.00,
        #     upper_percentile=0.99
        # )
        self.save_data_to_csv()
        self.plot_correlation_map(features=['credit_score', 'loan_age', 'original_combined_loan_to_value', 'original_debt_to_income_ratio', 'current_interest_rate', 'is_default'])
        self.plot_delinquency_status_over_time()
        self.plot_number_of_defaults_over_time()
        self.plot_current_status_over_time()
        self.plot_loan_age_distribution()
        self.plot_credit_score_distribution()
        self.plot_original_debt_to_income_ratio()
        self.plot_original_combined_loan_to_value()
        self.plot_interest_rate_over_time()


if __name__ == "__main__":
    data_processor = DataProcessor(
        "data/combined_dataset/consolidated_orig.csv",
        "data/combined_dataset/consolidated_svcg.csv"
    )
    data_processor.run_data_processing()
