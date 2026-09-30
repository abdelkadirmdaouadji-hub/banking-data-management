from pathlib import Path
import pandas as pd


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT / "data" / "raw" / "loans.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "loans_with_anomalies.csv"
)


# Load clean loans dataset
loans = pd.read_csv(INPUT_FILE)


# Inject anomaly 1: Duplicate loan ID
loans.loc[1, "loan_id"] = loans.loc[0, "loan_id"]


# Inject anomaly 2: Invalid customer reference
loans.loc[2, "customer_id"] = "C999999"


# Inject anomaly 3: Invalid branch reference
loans.loc[3, "branch_id"] = "B999"


# Inject anomaly 4: Invalid loan type
loans.loc[4, "loan_type"] = "Crypto"


# Inject anomaly 5: Negative loan amount
loans.loc[5, "loan_amount"] = -5000


# Inject anomaly 6: Invalid interest rate
loans.loc[6, "interest_rate"] = -2.0


# Inject anomaly 7: Invalid loan term
loans.loc[7, "term_months"] = -12


# Inject anomaly 8: Future loan start date
loans.loc[8, "start_date"] = (
    pd.Timestamp.today() + pd.Timedelta(days=60)
).strftime("%Y-%m-%d")


# Inject anomaly 9: Invalid loan status
loans.loc[9, "loan_status"] = "Unknown"


# Inject anomaly 10: Missing customer ID
loans.loc[10, "customer_id"] = None



# Save corrupted dataset
loans.to_csv(
    OUTPUT_FILE,
    index=False
)

print("Loan anomalies injected successfully.")
print(f"Output file: {OUTPUT_FILE}")