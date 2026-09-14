from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "branches.csv"
OUTPUT_FILE = PROJECT_ROOT / "data" / "raw" / "branches_with_anomalies.csv"

branches = pd.read_csv(INPUT_FILE)

# 1. Duplicate branch ID
branches.loc[1, "branch_id"] = branches.loc[0, "branch_id"]

# 2. Future opening date
branches.loc[2, "opening_date"] = (
    pd.Timestamp.today() + pd.Timedelta(days=60)
).strftime("%Y-%m-%d")

# 3. Missing branch name
branches.loc[3, "branch_name"] = None

# 4. Invalid city/region combination
branches.loc[4, "region"] = "Wallonia"

# 5. Missing manager name
branches.loc[5, "manager_name"] = None

branches.to_csv(
    OUTPUT_FILE,
    index=False
)

print("Branch anomalies injected successfully.")
print(f"Output file: {OUTPUT_FILE}")