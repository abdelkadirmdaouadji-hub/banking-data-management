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
CUSTOMERS_FILE = PROJECT_ROOT / "data" / "raw" / "customers.csv"
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

# 1. Referential integrity: customer_id
invalid_customer_refs = (
    ~accounts["customer_id"].isin(customers["customer_id"])
).sum()

print(
    f"\nInvalid customer references: "
    f"{invalid_customer_refs}"
)

# 2. Referential integrity: branch_id
invalid_branch_refs = (
    ~accounts["branch_id"].isin(branches["branch_id"])
).sum()

print(
    f"Invalid branch references: "
    f"{invalid_branch_refs}"
)

# 3. Duplicate account IDs
duplicate_account_ids = accounts["account_id"].duplicated(
    keep=False
).sum()

# 4. Invalid account types
valid_account_types = ["Checking", "Savings", "Business"]

invalid_account_types = (
    ~accounts["account_type"].isin(valid_account_types)
).sum()

# 5. Invalid account status
valid_statuses = ["Active", "Inactive", "Closed"]

invalid_statuses = (
    ~accounts["status"].isin(valid_statuses)
).sum()

# 6. Negative balances
negative_balances = (
    accounts["balance"] < 0
).sum()

# 7. Future opening dates
today = pd.Timestamp.today().normalize()

future_opening_dates = (
    accounts["opening_date"] > today
).sum()

# 8. Missing values
missing_account_id = accounts["account_id"].isna().sum()
missing_customer_id = accounts["customer_id"].isna().sum()
missing_branch_id = accounts["branch_id"].isna().sum()
missing_account_type = accounts["account_type"].isna().sum()
missing_balance = accounts["balance"].isna().sum()
missing_opening_date = accounts["opening_date"].isna().sum()
missing_status = accounts["status"].isna().sum()

# 9. Account opened before customer join date
accounts_with_customer_dates = accounts.merge(
    customers[["customer_id", "join_date"]],
    on="customer_id",
    how="left"
)

accounts_before_customer_join = (
    accounts_with_customer_dates["opening_date"]
    < accounts_with_customer_dates["join_date"]
).sum()

print(
    f"Accounts opened before customer join date: "
    f"{accounts_before_customer_join}"
)

# 10. Account opened before branch opening date
accounts_with_branch_dates = accounts.merge(
    branches[["branch_id", "opening_date"]],
    on="branch_id",
    how="left",
    suffixes=("_account", "_branch")
)

accounts_before_branch_opening = (
    accounts_with_branch_dates["opening_date_account"]
    < accounts_with_branch_dates["opening_date_branch"]
).sum()

print(
    f"Accounts opened before branch opening date: "
    f"{accounts_before_branch_opening}"
)

print(f"Duplicate account IDs: {duplicate_account_ids}")
print(f"Invalid account types: {invalid_account_types}")
print(f"Invalid statuses: {invalid_statuses}")
print(f"Negative balances: {negative_balances}")
print(f"Future opening dates: {future_opening_dates}")
print(f"Missing account ID: {missing_account_id}")
print(f"Missing customer ID: {missing_customer_id}")
print(f"Missing branch ID: {missing_branch_id}")
print(f"Missing account type: {missing_account_type}")
print(f"Missing balance: {missing_balance}")
print(f"Missing opening date: {missing_opening_date}")
print(f"Missing status: {missing_status}")

quality_checks = [
    {"check": "Invalid customer references", "errors": invalid_customer_refs},
    {"check": "Invalid branch references", "errors": invalid_branch_refs},
    {"check": "Duplicate account IDs", "errors": duplicate_account_ids},
    {"check": "Invalid account types", "errors": invalid_account_types},
    {"check": "Invalid statuses", "errors": invalid_statuses},
    {"check": "Negative balances", "errors": negative_balances},
    {"check": "Future opening dates", "errors": future_opening_dates},
    {"check": "Missing account ID", "errors": missing_account_id},
    {"check": "Missing customer ID", "errors": missing_customer_id},
    {"check": "Missing branch ID", "errors": missing_branch_id},
    {"check": "Missing account type", "errors": missing_account_type},
    {"check": "Missing balance", "errors": missing_balance},
    {"check": "Missing opening date", "errors": missing_opening_date},
    {"check": "Missing status", "errors": missing_status},
    {
        "check": "Accounts before customer join date",
        "errors": accounts_before_customer_join
    },
    {
        "check": "Accounts before branch opening date",
        "errors": accounts_before_branch_opening
    }
]

quality_report = pd.DataFrame(quality_checks)

quality_report["status"] = quality_report["errors"].apply(
    lambda x: "PASS" if x == 0 else "FAIL"
)

print("\n--- ACCOUNTS DATA QUALITY REPORT ---")
print(quality_report)

overall_status = (
    "PASS"
    if (quality_report["errors"] == 0).all()
    else "FAIL"
)

print(f"\nOverall data quality status: {overall_status}")

QUALITY_REPORT_DIR = PROJECT_ROOT / "data" / "quality_reports"

report_name = f"{Path(file_name).stem}_quality_report.csv"

report_file = QUALITY_REPORT_DIR / report_name

quality_report.to_csv(
    report_file,
    index=False
)

print(f"Quality report saved to: {report_file}")

if overall_status == "FAIL":
    sys.exit(1)

sys.exit(0)

