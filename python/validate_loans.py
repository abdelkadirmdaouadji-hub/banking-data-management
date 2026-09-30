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
# Check 1: Invalid customer references
# --------------------------------------------------

invalid_customer_ref = ~loans["customer_id"].isin(
    customers["customer_id"]
)

invalid_customer_count = invalid_customer_ref.sum()


# --------------------------------------------------
# Check 2: Invalid branch references
# --------------------------------------------------

invalid_branch_ref = ~loans["branch_id"].isin(
    branches["branch_id"]
)

invalid_branch_count = invalid_branch_ref.sum()


# --------------------------------------------------
# Check 3: Duplicate loan IDs
# --------------------------------------------------

duplicate_loan_id = loans["loan_id"].duplicated(
    keep=False
)

duplicate_loan_count = duplicate_loan_id.sum()


# --------------------------------------------------
# Check 4: Invalid loan types
# --------------------------------------------------

valid_loan_types = [
    "Personal",
    "Mortgage",
    "Auto",
    "Business"
]

invalid_loan_type = ~loans["loan_type"].isin(
    valid_loan_types
)

invalid_loan_type_count = invalid_loan_type.sum()


# --------------------------------------------------
# Check 5: Invalid loan amounts
# --------------------------------------------------

invalid_loan_amount = (
    loans["loan_amount"] <= 0
)

invalid_loan_amount_count = invalid_loan_amount.sum()


# --------------------------------------------------
# Check 6: Invalid interest rates
# --------------------------------------------------

invalid_interest_rate = (
    (loans["interest_rate"] <= 0)
    | (loans["interest_rate"] > 100)
)

invalid_interest_rate_count = (
    invalid_interest_rate.sum()
)


# --------------------------------------------------
# Check 7: Invalid loan terms
# --------------------------------------------------

invalid_term_months = (
    loans["term_months"] <= 0
)

invalid_term_months_count = (
    invalid_term_months.sum()
)


# --------------------------------------------------
# Check 8: Future loan start dates
# --------------------------------------------------

today = pd.Timestamp.today().normalize()

future_start_date = (
    loans["start_date"] > today
)

future_start_date_count = (
    future_start_date.sum()
)


# --------------------------------------------------
# Check 9: Invalid loan statuses
# --------------------------------------------------

valid_loan_statuses = [
    "Active",
    "Paid",
    "Defaulted"
]

invalid_loan_status = ~loans["loan_status"].isin(
    valid_loan_statuses
)

invalid_loan_status_count = (
    invalid_loan_status.sum()
)


# --------------------------------------------------
# Check 10: Missing values
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

missing_values_count = (
    missing_loan_id.sum()
    + missing_customer_id.sum()
    + missing_branch_id.sum()
    + missing_loan_type.sum()
    + missing_loan_amount.sum()
    + missing_interest_rate.sum()
    + missing_term_months.sum()
    + missing_start_date.sum()
    + missing_loan_status.sum()
)


# --------------------------------------------------
# Check 11: Loan started before customer joined
# --------------------------------------------------

loans_with_customers = loans.merge(
    customers[["customer_id", "join_date"]],
    on="customer_id",
    how="left"
)

loan_before_customer_join = (
    loans_with_customers["start_date"]
    < loans_with_customers["join_date"]
)

loan_before_customer_join_count = (
    loan_before_customer_join.sum()
)


# --------------------------------------------------
# Check 12: Loan started before branch opening
# --------------------------------------------------

loans_with_branches = loans.merge(
    branches[["branch_id", "opening_date"]],
    on="branch_id",
    how="left"
)

loan_before_branch_opening = (
    loans_with_branches["start_date"]
    < loans_with_branches["opening_date"]
)

loan_before_branch_opening_count = (
    loan_before_branch_opening.sum()
)


# --------------------------------------------------
# Build Data Quality checks
# --------------------------------------------------

quality_checks = [
    (
        "Invalid customer references",
        invalid_customer_count
    ),
    (
        "Invalid branch references",
        invalid_branch_count
    ),
    (
        "Duplicate loan IDs",
        duplicate_loan_count
    ),
    (
        "Invalid loan types",
        invalid_loan_type_count
    ),
    (
        "Invalid loan amounts",
        invalid_loan_amount_count
    ),
    (
        "Invalid interest rates",
        invalid_interest_rate_count
    ),
    (
        "Invalid loan terms",
        invalid_term_months_count
    ),
    (
        "Future loan start dates",
        future_start_date_count
    ),
    (
        "Invalid loan statuses",
        invalid_loan_status_count
    ),
    (
        "Missing values",
        missing_values_count
    ),
    (
        "Loans started before customer join date",
        loan_before_customer_join_count
    ),
    (
        "Loans started before branch opening date",
        loan_before_branch_opening_count
    )
]


# --------------------------------------------------
# Print Data Quality summary
# --------------------------------------------------

print("\n--- LOAN DATA QUALITY CHECKS ---")

for check_name, error_count in quality_checks:
    print(
        f"{check_name}: {error_count}"
    )


# --------------------------------------------------
# Create structured Data Quality report
# --------------------------------------------------

quality_report = pd.DataFrame(
    quality_checks,
    columns=[
        "check_name",
        "error_count"
    ]
)

quality_report["status"] = quality_report[
    "error_count"
].apply(
    lambda x: "PASS" if x == 0 else "FAIL"
)


print("\n--- DATA QUALITY REPORT ---")
print(quality_report)


# --------------------------------------------------
# Overall Data Quality status
# --------------------------------------------------

overall_status = (
    "PASS"
    if (quality_report["status"] == "PASS").all()
    else "FAIL"
)

print("\n--- OVERALL DATA QUALITY STATUS ---")
print(f"Overall status: {overall_status}")


# --------------------------------------------------
# Save Data Quality report
# --------------------------------------------------

QUALITY_REPORT_DIR = (
    PROJECT_ROOT
    / "data"
    / "quality_reports"
)

QUALITY_REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

input_stem = Path(file_name).stem

report_output_file = (
    QUALITY_REPORT_DIR
    / f"{input_stem}_quality_report.csv"
)

quality_report.to_csv(
    report_output_file,
    index=False
)

print(
    f"\nQuality report saved to: "
    f"{report_output_file}"
)

# Return an exit code for automation / CI pipelines
sys.exit(
    0 if overall_status == "PASS" else 1
)