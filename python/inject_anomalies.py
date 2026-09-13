from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "customers.csv"
OUTPUT_FILE = PROJECT_ROOT / "data" / "raw" / "customers_with_anomalies.csv"


customers = pd.read_csv(
    INPUT_FILE
)

# 1. Duplicate customer ID
customers.loc[1, "customer_id"] = customers.loc[0, "customer_id"]

# 2. Negative annual income
customers.loc[10, "annual_income"] = -2500

# 3. Invalid customer segment
customers.loc[20, "customer_segment"] = "VIP"

# 4. Invalid risk score
customers.loc[30, "risk_score"] = 150

# 5. Future join date
customers.loc[40, "join_date"] = (
    pd.Timestamp.today() + pd.Timedelta(days=30)
).strftime("%Y-%m-%d")

# 6. Customer under 18
customers.loc[50, "birth_date"] = (
    pd.Timestamp.today() - pd.DateOffset(years=16)
).strftime("%Y-%m-%d")

# 7. Missing customer ID
customers.loc[60, "customer_id"] = None

# 8. Invalid birth date
customers.loc[70, "birth_date"] = "not-a-date"

# 9. Missing join date
customers.loc[80, "join_date"] = None

# 10. Missing annual income
customers.loc[90, "annual_income"] = None

customers.to_csv(
    OUTPUT_FILE,
    index=False
)

print("Anomalies injected successfully.")
print(f"Output file: {OUTPUT_FILE}")