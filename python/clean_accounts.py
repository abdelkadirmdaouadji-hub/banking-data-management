from pathlib import Path
import sys
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if len(sys.argv) > 1:
    file_name = sys.argv[1]
else:
    file_name = "accounts.csv"

ACCOUNTS_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / file_name
)
CUSTOMERS_FILE = PROJECT_ROOT / "data" / "processed" / "customers.csv"
BRANCHES_FILE = PROJECT_ROOT / "data" / "raw" / "branches.csv"

accounts = pd.read_csv(
    ACCOUNTS_FILE,
    parse_dates=["opening_date"]
)

customers = pd.read_csv(
    CUSTOMERS_FILE,
    parse_dates=["join_date"]
)

branches = pd.read_csv(
    BRANCHES_FILE,
    parse_dates=["opening_date"]
)

print("Datasets loaded successfully.")
print(f"Accounts: {len(accounts):,}")
print(f"Customers: {len(customers):,}")
print(f"Branches: {len(branches):,}")

# 1. Invalid customer references
invalid_customer_ref = (
    ~accounts["customer_id"].isin(customers["customer_id"])
)

print(
    f"Invalid customer references: "
    f"{invalid_customer_ref.sum()}"
)

# 2. Invalid branch references
invalid_branch_ref = (
    ~accounts["branch_id"].isin(branches["branch_id"])
)

print(
    f"Invalid branch references: "
    f"{invalid_branch_ref.sum()}"
)

# 3. Duplicate account IDs
duplicate_account_id = accounts["account_id"].duplicated(
    keep=False
)

print(
    f"Duplicate account IDs: "
    f"{duplicate_account_id.sum()}"
)

# 4. Invalid account types
valid_account_types = [
    "Checking",
    "Savings",
    "Business"
]

invalid_account_type = (
    ~accounts["account_type"].isin(valid_account_types)
)

print(
    f"Invalid account types: "
    f"{invalid_account_type.sum()}"
)

# 5. Invalid account statuses
valid_statuses = [
    "Active",
    "Inactive",
    "Closed"
]

invalid_status = (
    ~accounts["status"].isin(valid_statuses)
)

print(
    f"Invalid account statuses: "
    f"{invalid_status.sum()}"
)

# 6. Negative balances
negative_balance = (
    accounts["balance"] < 0
)

print(
    f"Negative balances: "
    f"{negative_balance.sum()}"
)

# 7. Future opening dates
today = pd.Timestamp.today().normalize()

future_opening_date = (
    accounts["opening_date"] > today
)

print(
    f"Future opening dates: "
    f"{future_opening_date.sum()}"
)

# 8. Missing values
missing_account_id = accounts["account_id"].isna()
missing_customer_id = accounts["customer_id"].isna()
missing_branch_id = accounts["branch_id"].isna()
missing_account_type = accounts["account_type"].isna()
missing_balance = accounts["balance"].isna()
missing_opening_date = accounts["opening_date"].isna()
missing_status = accounts["status"].isna()

print(f"Missing account IDs: {missing_account_id.sum()}")
print(f"Missing customer IDs: {missing_customer_id.sum()}")
print(f"Missing branch IDs: {missing_branch_id.sum()}")
print(f"Missing account types: {missing_account_type.sum()}")
print(f"Missing balances: {missing_balance.sum()}")
print(f"Missing opening dates: {missing_opening_date.sum()}")
print(f"Missing statuses: {missing_status.sum()}")

# 9. Combine all validation rules
invalid_rows = (
    invalid_customer_ref
    | invalid_branch_ref
    | duplicate_account_id
    | invalid_account_type
    | invalid_status
    | negative_balance
    | future_opening_date
    | missing_account_id
    | missing_customer_id
    | missing_branch_id
    | missing_account_type
    | missing_balance
    | missing_opening_date
    | missing_status
)

print(
    f"\nTotal invalid rows: "
    f"{invalid_rows.sum()}"
)

# 10. Split clean and rejected records
clean_accounts = accounts[~invalid_rows].copy()
rejected_accounts = accounts[invalid_rows].copy()

print(f"\nInput rows: {len(accounts):,}")
print(f"Clean rows: {len(clean_accounts):,}")
print(f"Rejected rows: {len(rejected_accounts):,}")

# 11. Add rejection reasons
rejected_accounts["rejection_reason"] = ""

rejected_accounts.loc[
    invalid_customer_ref[invalid_rows],
    "rejection_reason"
] += "Invalid customer reference; "

rejected_accounts.loc[
    invalid_branch_ref[invalid_rows],
    "rejection_reason"
] += "Invalid branch reference; "

rejected_accounts.loc[
    duplicate_account_id[invalid_rows],
    "rejection_reason"
] += "Duplicate account ID; "

rejected_accounts.loc[
    invalid_account_type[invalid_rows],
    "rejection_reason"
] += "Invalid account type; "

rejected_accounts.loc[
    invalid_status[invalid_rows],
    "rejection_reason"
] += "Invalid account status; "

rejected_accounts.loc[
    negative_balance[invalid_rows],
    "rejection_reason"
] += "Negative balance; "

rejected_accounts.loc[
    future_opening_date[invalid_rows],
    "rejection_reason"
] += "Future opening date; "

rejected_accounts.loc[
    missing_account_id[invalid_rows],
    "rejection_reason"
] += "Missing account ID; "

rejected_accounts.loc[
    missing_customer_id[invalid_rows],
    "rejection_reason"
] += "Missing customer ID; "

rejected_accounts.loc[
    missing_branch_id[invalid_rows],
    "rejection_reason"
] += "Missing branch ID; "

rejected_accounts.loc[
    missing_account_type[invalid_rows],
    "rejection_reason"
] += "Missing account type; "

rejected_accounts.loc[
    missing_balance[invalid_rows],
    "rejection_reason"
] += "Missing balance; "

rejected_accounts.loc[
    missing_opening_date[invalid_rows],
    "rejection_reason"
] += "Missing opening date; "

rejected_accounts.loc[
    missing_status[invalid_rows],
    "rejection_reason"
] += "Missing status; "

# 12. Save clean and rejected datasets
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

input_stem = Path(file_name).stem

clean_output_file = (
    PROCESSED_DATA_DIR / f"{input_stem}_clean.csv"
)

rejected_output_file = (
    PROCESSED_DATA_DIR / f"{input_stem}_rejected.csv"
)

clean_accounts.to_csv(
    clean_output_file,
    index=False
)

rejected_accounts.to_csv(
    rejected_output_file,
    index=False
)

print(f"\nClean accounts saved to: {clean_output_file}")
print(f"Rejected accounts saved to: {rejected_output_file}")

# 13. Create cleaning summary
cleaning_summary = pd.DataFrame({
    "metric": [
        "input_rows",
        "clean_rows",
        "rejected_rows",
        "rejection_rate_pct"
    ],
    "value": [
        len(accounts),
        len(clean_accounts),
        len(rejected_accounts),
        round(
            len(rejected_accounts) / len(accounts) * 100,
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

print(f"Cleaning summary saved to: {summary_output_file}")


