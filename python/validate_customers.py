from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
QUALITY_REPORT_DIR = PROJECT_ROOT / "data" / "quality_reports"
if len(sys.argv) > 1:
    file_name = sys.argv[1]
else:
    file_name = "customers.csv"

CUSTOMERS_FILE = PROJECT_ROOT / "data" / "raw" / file_name
customers = pd.read_csv(
    CUSTOMERS_FILE,
    parse_dates=["birth_date", "join_date"]
)

customers["birth_date"] = pd.to_datetime(
    customers["birth_date"],
    errors="coerce",
    format="mixed"
)

customers["join_date"] = pd.to_datetime(
    customers["join_date"],
    errors="coerce",
    format="mixed"
)

print("Customers dataset loaded successfully.")
print(f"Rows: {len(customers):,}")
print(f"Columns: {len(customers.columns)}")

print("\n--- DATA QUALITY CHECKS ---")

# 1. Missing values
missing_values = customers.isnull().sum()
print("\n1. Missing values:")
print(missing_values)


# 2. Duplicate customer IDs
duplicate_ids = customers["customer_id"].duplicated(
    keep=False
).sum()
print(f"\n2. Duplicate customer IDs: {duplicate_ids}")


# 3. Invalid annual income
invalid_income = (customers["annual_income"] < 0).sum()
print(f"\n3. Negative annual income: {invalid_income}")


# 4. Invalid customer segments
valid_segments = ["Standard", "Premium", "Private"]

invalid_segments = (
    ~customers["customer_segment"].isin(valid_segments)
).sum()

print(f"\n4. Invalid customer segments: {invalid_segments}")


# 5. Invalid risk scores
invalid_risk_scores = (
    (customers["risk_score"] < 1)
    | (customers["risk_score"] > 100)
).sum()

print(f"\n5. Invalid risk scores: {invalid_risk_scores}")


# 6. Future join dates
today = pd.Timestamp.today().normalize()

future_join_dates = (
    customers["join_date"] > today
).sum()

print(f"\n6. Future join dates: {future_join_dates}")

# 7. Customers under 18
today = pd.Timestamp.today().normalize()

age = (
    today.year
    - customers["birth_date"].dt.year
    - (
        (today.month < customers["birth_date"].dt.month)
        | (
            (today.month == customers["birth_date"].dt.month)
            & (today.day < customers["birth_date"].dt.day)
        )
    ).astype(int)
)

underage_customers = (age < 18).sum()

print(f"\n7. Customers under 18: {underage_customers}")

# 8. Missing values
missing_customer_id = customers["customer_id"].isna().sum()
missing_birth_date = customers["birth_date"].isna().sum()
missing_join_date = customers["join_date"].isna().sum()
missing_annual_income = customers["annual_income"].isna().sum()


quality_checks = [
    {
        "check": "Duplicate customer IDs",
        "errors": duplicate_ids
    },
    {
        "check": "Negative annual income",
        "errors": invalid_income
    },
    {
        "check": "Invalid customer segments",
        "errors": invalid_segments
    },
    {
        "check": "Invalid risk scores",
        "errors": invalid_risk_scores
    },
    {
        "check": "Future join dates",
        "errors": future_join_dates
    },
    {
        "check": "Customers under 18",
        "errors": underage_customers
    },
        {
        "check": "Missing customer ID",
        "errors": missing_customer_id
    },
    {
        "check": "Missing or invalid birth date",
        "errors": missing_birth_date
    },
    {
        "check": "Missing or invalid join date",
        "errors": missing_join_date
    },
    {
        "check": "Missing annual income",
        "errors": missing_annual_income
    }
]

quality_report = pd.DataFrame(quality_checks)

quality_report["status"] = quality_report["errors"].apply(
    lambda x: "PASS" if x == 0 else "FAIL"
)

overall_status = (
    "PASS"
    if (quality_report["errors"] == 0).all()
    else "FAIL"
)

print(f"\nOverall data quality status: {overall_status}")

print("\n--- DATA QUALITY REPORT ---")
print(quality_report)

report_name = f"{Path(file_name).stem}_quality_report.csv"

report_file = QUALITY_REPORT_DIR / report_name

quality_report.to_csv(
    report_file,
    index=False
)

print(f"\nQuality report saved to: {report_file}")

if overall_status == "FAIL":
    sys.exit(1)

sys.exit(0)
