from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "accounts.csv"
OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "accounts_with_anomalies.csv"
)

accounts = pd.read_csv(INPUT_FILE)

# 1. Duplicate account ID
accounts.loc[1, "account_id"] = accounts.loc[0, "account_id"]

# 2. Unknown customer ID
accounts.loc[2, "customer_id"] = "C999999"

# 3. Unknown branch ID
accounts.loc[3, "branch_id"] = "B999"

# 4. Invalid account type
accounts.loc[4, "account_type"] = "Crypto"

# 5. Negative balance
accounts.loc[5, "balance"] = -5000

# 6. Future opening date
accounts.loc[6, "opening_date"] = (
    pd.Timestamp.today() + pd.Timedelta(days=60)
).strftime("%Y-%m-%d")

# 7. Invalid status
accounts.loc[7, "status"] = "Unknown"

# 8. Missing customer ID
accounts.loc[8, "customer_id"] = None

accounts.to_csv(
    OUTPUT_FILE,
    index=False
)

print("Account anomalies injected successfully.")
print(f"Output file: {OUTPUT_FILE}")