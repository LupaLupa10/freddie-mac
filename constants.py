LOGIN_URL = "https://freddiemac.embs.com/FLoan/secure/auth.php"
DOWNLOAD_URL = "https://freddiemac.embs.com/FLoan/Data/download.php"

ORIG_HEADERS = [
    "credit_score", "first_payment_date", "first_time_homebuyer_flag", "maturity_date",
    "msa", "mortgage_insurance_percent", "number_of_units", "occupancy_status",
    "original_combined_loan_to_value", "original_debt_to_income_ratio", "original_upb",
    "original_interest_rate", "channel", "prepayment_penalty_mortgage_flag",
    "product_type", "property_state", "property_type", "postal_code",
    "loan_sequence_number", "loan_purpose", "original_loan_term", "number_of_borrowers",
    "seller_name", "servicer_name", "super_conforming_flag"
]

SVCG_HEADERS = [
    "loan_sequence_number", "monthly_reporting_period", "current_actual_upb",
    "current_loan_delinquency_status", "loan_age", "remaining_months_to_legal_maturity",
    "repurchase_flag", "modification_flag", "zero_balance_code",
    "zero_balance_effective_date", "current_interest_rate", "current_deferred_upb",
    "due_date_of_last_paid_installment", "mi_recoveries", "net_sales_proceeds",
    "non_mi_recoveries", "expenses", "legal_costs", "maintenance_costs",
    "taxes_and_insurance", "miscellaneous_expenses", "actual_loss", "modification_cost"
]
