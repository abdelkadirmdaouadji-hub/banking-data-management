from pathlib import Path
import sys
import pandas as pd


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Select loans file from command line
file_name = (
    sys.argv[1]
    if len(sys.argv) > 1
    else "loans.csv"
)

LOANS_FILE = (
    PROJECT_ROOT / "data" / "raw" / file_name
)

CUSTOMERS_FILE = (
    PROJECT_ROOT / "data" / "raw" / "customers.csv"
)

BRANCHES_FILE = (
    PROJECT_ROOT / "data" / "raw" / "branches.csv"
)

PROCESSED_DATA_DIR = (
    PROJECT_ROOT / "data" / "processed"
)

PROCESSED_DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# Load datasets
loans = pd.read_csv(
    LOANS_FILE,
    parse_dates=["start_date"]
)

customers = pd.read_csv(
    CUSTOMERS_FILE,
    parse_dates=["join_date"]
)

branches = pd.read_csv(
    BRANCHES_FILE,
    parse_dates=["opening_date"]
)


# Basic verification
print("Datasets loaded successfully.")
print(f"Loans: {len(loans):,}")
print(f"Customers: {len(customers):,}")
print(f"Branches: {len(branches):,}")


# --------------------------------------------------
# Data Quality masks
# --------------------------------------------------

# Invalid customer reference
invalid_customer_ref = ~loans["customer_id"].isin(
    customers["customer_id"]
)

# Invalid branch reference
invalid_branch_ref = ~loans["branch_id"].isin(
    branches["branch_id"]
)

# Duplicate loan ID
duplicate_loan_id = loans["loan_id"].duplicated(
    keep=False
)

# Invalid loan type
valid_loan_types = [
    "Personal",
    "Mortgage",
    "Auto",
    "Business"
]

invalid_loan_type = ~loans["loan_type"].isin(
    valid_loan_types
)

# Invalid loan amount
invalid_loan_amount = (
    loans["loan_amount"] <= 0
)

# Invalid interest rate
invalid_interest_rate = (
    (loans["interest_rate"] <= 0)
    | (loans["interest_rate"] > 100)
)

# Invalid loan term
invalid_term_months = (
    loans["term_months"] <= 0
)

# Future loan start date
today = pd.Timestamp.today().normalize()

future_start_date = (
    loans["start_date"] > today
)

# Invalid loan status
valid_loan_statuses = [
    "Active",
    "Paid",
    "Defaulted"
]

invalid_loan_status = ~loans["loan_status"].isin(
    valid_loan_statuses
)


# --------------------------------------------------
# Missing values
# --------------------------------------------------

missing_loan_id = loans["loan_id"].isna()
missing_customer_id = loans["customer_id"].isna()
missing_branch_id = loans["branch_id"].isna()
missing_loan_type = loans["loan_type"].isna()
missing_loan_amount = loans["loan_amount"].isna()
missing_interest_rate = loans["interest_rate"].isna()
missing_term_months = loans["term_months"].isna()
missing_start_date = loans["start_date"].isna()
missing_loan_status = loans["loan_status"].isna()


# --------------------------------------------------
# Temporal consistency
# --------------------------------------------------

customer_join_map = customers.set_index(
    "customer_id"
)["join_date"]

branch_opening_map = branches.set_index(
    "branch_id"
)["opening_date"]

customer_join_dates = loans[
    "customer_id"
].map(customer_join_map)

branch_opening_dates = loans[
    "branch_id"
].map(branch_opening_map)


# Loan cannot start before customer joined the bank
loan_before_customer_join = (
    loans["start_date"] < customer_join_dates
)


# Loan cannot start before branch opened
loan_before_branch_opening = (
    loans["start_date"] < branch_opening_dates
)


# --------------------------------------------------
# Combine all Data Quality rules
# --------------------------------------------------

invalid_rows = (
    invalid_customer_ref
    | invalid_branch_ref
    | duplicate_loan_id
    | invalid_loan_type
    | invalid_loan_amount
    | invalid_interest_rate
    | invalid_term_months
    | future_start_date
    | invalid_loan_status
    | missing_loan_id
    | missing_customer_id
    | missing_branch_id
    | missing_loan_type
    | missing_loan_amount
    | missing_interest_rate
    | missing_term_months
    | missing_start_date
    | missing_loan_status
    | loan_before_customer_join
    | loan_before_branch_opening
)


# Split valid and rejected loans
clean_loans = loans[
    ~invalid_rows
].copy()

rejected_loans = loans[
    invalid_rows
].copy()


# Display results
print("\n--- LOAN CLEANING RESULTS ---")
print(f"Input rows: {len(loans):,}")
print(f"Clean rows: {len(clean_loans):,}")
print(f"Rejected rows: {len(rejected_loans):,}")


# --------------------------------------------------
# Add rejection reasons
# --------------------------------------------------

rejected_loans["rejection_reason"] = ""

rejection_rules = [
    (invalid_customer_ref, "Invalid customer reference"),
    (invalid_branch_ref, "Invalid branch reference"),
    (duplicate_loan_id, "Duplicate loan ID"),
    (invalid_loan_type, "Invalid loan type"),
    (invalid_loan_amount, "Invalid loan amount"),
    (invalid_interest_rate, "Invalid interest rate"),
    (invalid_term_months, "Invalid loan term"),
    (future_start_date, "Future loan start date"),
    (invalid_loan_status, "Invalid loan status"),
    (missing_loan_id, "Missing loan ID"),
    (missing_customer_id, "Missing customer ID"),
    (missing_branch_id, "Missing branch ID"),
    (missing_loan_type, "Missing loan type"),
    (missing_loan_amount, "Missing loan amount"),
    (missing_interest_rate, "Missing interest rate"),
    (missing_term_months, "Missing loan term"),
    (missing_start_date, "Missing start date"),
    (missing_loan_status, "Missing loan status"),
    (
        loan_before_customer_join,
        "Loan started before customer join date"
    ),
    (
        loan_before_branch_opening,
        "Loan started before branch opening date"
    )
]

for rule_mask, reason in rejection_rules:
    affected_indexes = loans.index[
        rule_mask
    ].intersection(
        rejected_loans.index
    )

    rejected_loans.loc[
        affected_indexes,
        "rejection_reason"
    ] += reason + "; "
    
    
    # --------------------------------------------------
# Save cleaned and rejected datasets
# --------------------------------------------------

input_stem = Path(file_name).stem

clean_output_file = (
    PROCESSED_DATA_DIR
    / f"{input_stem}_clean.csv"
)

rejected_output_file = (
    PROCESSED_DATA_DIR
    / f"{input_stem}_rejected.csv"
)


clean_loans.to_csv(
    clean_output_file,
    index=False
)

rejected_loans.to_csv(
    rejected_output_file,
    index=False
)


print(
    f"\nClean dataset saved to: "
    f"{clean_output_file}"
)

print(
    f"Rejected dataset saved to: "
    f"{rejected_output_file}"
)


# --------------------------------------------------
# Create cleaning summary
# --------------------------------------------------

cleaning_summary = pd.DataFrame({
    "metric": [
        "input_rows",
        "clean_rows",
        "rejected_rows",
        "rejection_rate_pct"
    ],
    "value": [
        len(loans),
        len(clean_loans),
        len(rejected_loans),
        round(
            len(rejected_loans)
            / len(loans)
            * 100,
            4
        )
    ]
})


summary_output_file = (
    PROCESSED_DATA_DIR
    / f"{input_stem}_cleaning_summary.csv"
)

cleaning_summary.to_csv(
    summary_output_file,
    index=False
)


print("\n--- CLEANING SUMMARY ---")
print(cleaning_summary)

print(
    f"\nCleaning summary saved to: "
    f"{summary_output_file}"
)