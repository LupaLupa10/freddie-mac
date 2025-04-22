import numpy as np
import pandas as pd


def _get_last_period_before_default(group):
    return group[group['monthly_reporting_period'] < group['zero_balance_effective_date'].iloc[0]].sort_values(by='monthly_reporting_period', ascending=False)

def calculate_ead(group):
    last_period_data = _get_last_period_before_default(group)
    return last_period_data.iloc[0]['current_actual_upb'] if not last_period_data.empty else np.nan

def calculate_lgd(group, ead):
    if pd.isna(ead) or ead == 0:
        return np.nan

    last_period_data = _get_last_period_before_default(group)
    if last_period_data.empty:
        return np.nan

    last_period = last_period_data.iloc[0]

    total_recoveries = last_period['mi_recoveries'] + last_period['net_sales_proceeds'] + last_period['non_mi_recoveries']
    total_expenses = last_period[[
        'expenses', 'legal_costs', 'maintenance_costs',
        'taxes_and_insurance', 'miscellaneous_expenses'
    ]].sum()

    lgd = (ead - total_recoveries + total_expenses) / ead
    return lgd

def calculate_ead_lgd(data):
    if data is None:
        raise ValueError("Data not loaded or merged yet.")

    loss_codes = ['02', '03', '06', '09', '15']
    defaulted_loans = data[data['zero_balance_code'].isin(loss_codes)].copy()

    if defaulted_loans.empty:
        print("No defaulted loans found based on zero_balance_code.")
        defaulted_loans['ead'] = np.nan
        defaulted_loans['lgd'] = np.nan
        return defaulted_loans[['loan_sequence_number', 'monthly_reporting_period', 'ead', 'lgd']]

    defaulted_loans['zero_balance_effective_date'] = pd.to_datetime(defaulted_loans['zero_balance_effective_date'], format='%Y%m')

    grouped = defaulted_loans.groupby('loan_sequence_number')

    ead_results = grouped.apply(calculate_ead)
    defaulted_loans = defaulted_loans.merge(ead_results.rename('ead'), on='loan_sequence_number', how='left')

    lgd_results = defaulted_loans.groupby('loan_sequence_number').apply(lambda group: calculate_lgd(group, group['ead'].iloc[0]))
    defaulted_loans = defaulted_loans.merge(lgd_results.rename('lgd'), on='loan_sequence_number', how='left')

    print("EAD and LGD calculated for defaulted loans.")
    return defaulted_loans[['loan_sequence_number', 'monthly_reporting_period', 'ead', 'lgd']]


if __name__ == "__main__":
    use_csv = input("Do you want to load data from 'data/combined_dataset/data.csv'? (yes/no): ").lower()
    if use_csv == 'yes':
        try:
            df = pd.read_csv("data/combined_dataset/data.csv", low_memory=False)
            ead_lgd_df = calculate_ead_lgd(df.copy())

            if not ead_lgd_df.empty:
                print("\nEAD and LGD Results from CSV:")
                print(ead_lgd_df.head())
            else:
                print("\nNo defaulted loans found in the CSV to display EAD and LGD.")

        except FileNotFoundError:
            print("Error: data/combined_dataset/data.csv not found. Make sure the file exists in the specified path.")
        except Exception as e:
            print(f"An error occurred while loading CSV: {e}")

    else:
        data = pd.DataFrame({
            'loan_sequence_number': ['A', 'A', 'B', 'B', 'C'],
            'monthly_reporting_period': pd.to_datetime(['2024-01-01', '2024-02-01', '2024-03-01', '2024-04-01', '2024-05-01']),
            'current_actual_upb': [100000, 95000, 75000, 0, 120000],
            'zero_balance_code': [np.nan, '03', np.nan, '03', np.nan],
            'zero_balance_effective_date': pd.to_datetime(['NaT', '2024-02-15', 'NaT', '2024-04-20', 'NaT']),
            'mi_recoveries': [0, 1000, 0, 500, 0],
            'net_sales_proceeds': [0, 60000, 0, 40000, 0],
            'non_mi_recoveries': [0, 200, 0, 100, 0],
            'expenses': [0, 1500, 0, 1000, 0],
            'legal_costs': [0, 200, 0, 150, 0],
            'maintenance_costs': [0, 300, 0, 200, 0],
            'taxes_and_insurance': [0, 50, 0, 30, 0],
            'miscellaneous_expenses': [0, 50, 0, 20, 0],
        })

        ead_lgd_results = calculate_ead_lgd(data.copy())
        print("\nEAD and LGD Results from Example Data:")
        print(ead_lgd_results)