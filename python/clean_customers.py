from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "customers_with_anomalies.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "customers.csv"
)


customers = pd.read_csv(INPUT_FILE)

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

print(f"Input rows: {len(customers):,}")

today = pd.Timestamp.today().normalize()

valid_segments = ["Standard", "Premium", "Private"]

# Calculate customer age
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

# Critical data quality rules
duplicate_id = customers["customer_id"].duplicated(keep=False)
negative_income = customers["annual_income"] < 0
invalid_segment = ~customers["customer_segment"].isin(valid_segments)

invalid_risk_score = (
    (customers["risk_score"] < 1)
    | (customers["risk_score"] > 100)
)

future_join_date = customers["join_date"] > today
underage_customer = age < 18

missing_customer_id = customers["customer_id"].isna()
missing_birth_date = customers["birth_date"].isna()
missing_join_date = customers["join_date"].isna()
missing_annual_income = customers["annual_income"].isna()

invalid_mask = (
    duplicate_id
    | negative_income
    | invalid_segment
    | invalid_risk_score
    | future_join_date
    | underage_customer
    | missing_customer_id
    | missing_birth_date
    | missing_join_date
    | missing_annual_income
)

print(f"Invalid rows detected: {invalid_mask.sum():,}")

customers["rejection_reason"] = ""

customers.loc[duplicate_id, "rejection_reason"] += "Duplicate customer_id; "
customers.loc[negative_income, "rejection_reason"] += "Negative annual_income; "
customers.loc[invalid_segment, "rejection_reason"] += "Invalid customer_segment; "
customers.loc[invalid_risk_score, "rejection_reason"] += "Invalid risk_score; "
customers.loc[future_join_date, "rejection_reason"] += "Future join_date; "
customers.loc[underage_customer, "rejection_reason"] += "Customer under 18; "
customers.loc[missing_customer_id, "rejection_reason"] += "Missing customer_id; "
customers.loc[missing_birth_date, "rejection_reason"] += "Missing or invalid birth_date; "
customers.loc[missing_join_date, "rejection_reason"] += "Missing or invalid join_date; "
customers.loc[missing_annual_income, "rejection_reason"] += "Missing annual_income; "


rejected_customers = customers[invalid_mask].copy()

clean_customers = customers[~invalid_mask].copy()

clean_customers = clean_customers.drop(
    columns=["rejection_reason"]
)

REJECTED_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "customers_rejected.csv"
)

clean_customers.to_csv(
    OUTPUT_FILE,
    index=False
)

rejected_customers.to_csv(
    REJECTED_FILE,
    index=False
)

print(f"Clean rows: {len(clean_customers):,}")
print(f"Rejected rows: {len(rejected_customers):,}")

rejection_summary = pd.DataFrame({
    "rule": [
        "Duplicate customer_id",
        "Negative annual_income",
        "Invalid customer_segment",
        "Invalid risk_score",
        "Future join_date",
        "Customer under 18",
        "Missing customer_id",
        "Missing or invalid birth_date",
        "Missing or invalid join_date",
        "Missing annual_income"
    ],
    "rejected_rows": [
        duplicate_id.sum(),
        negative_income.sum(),
        invalid_segment.sum(),
        invalid_risk_score.sum(),
        future_join_date.sum(),
        underage_customer.sum(),
        missing_customer_id.sum(),
        missing_birth_date.sum(),
        missing_join_date.sum(),
        missing_annual_income.sum()
    ]
})

print("\n--- CLEANING SUMMARY ---")
print(rejection_summary)

SUMMARY_FILE = (
    PROJECT_ROOT
    / "data"
    / "quality_reports"
    / "customers_cleaning_summary.csv"
)

rejection_summary.to_csv(
    SUMMARY_FILE,
    index=False
)

print(f"Cleaning summary saved to: {SUMMARY_FILE}")

print(f"Clean dataset saved to: {OUTPUT_FILE}")
print(f"Rejected dataset saved to: {REJECTED_FILE}")



