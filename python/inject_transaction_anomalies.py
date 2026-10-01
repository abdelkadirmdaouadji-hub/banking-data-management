from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "transactions.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "transactions_with_anomalies.csv"
)

transactions = pd.read_csv(
    INPUT_FILE
)

print(
    "Transactions loaded:",
    len(transactions)
)

# Inject anomaly 1: Duplicate transaction ID
transactions.loc[
    1,
    "transaction_id"
] = transactions.loc[
    0,
    "transaction_id"
]

# Inject anomaly 2: Invalid account reference
transactions.loc[
    2,
    "account_id"
] = "A9999999"

# Inject anomaly 3: Invalid transaction type
transactions.loc[
    3,
    "transaction_type"
] = "Crypto Payment"

# Inject anomaly 4: Invalid transaction amount
transactions.loc[
    4,
    "amount"
] = -500.00

# Inject anomaly 5: Future transaction date
transactions.loc[
    5,
    "transaction_date"
] = (
    pd.Timestamp.today()
    + pd.Timedelta(days=60)
).strftime("%Y-%m-%d")

# Inject anomaly 6: Invalid transaction status
transactions.loc[
    6,
    "transaction_status"
] = "Unknown"

# Inject anomaly 7: Invalid channel
transactions.loc[
    7,
    "channel"
] = "Telephone"

# Inject anomaly 8: Invalid type/channel combination
transactions.loc[
    8,
    "transaction_type"
] = "Cash Withdrawal"

transactions.loc[
    8,
    "channel"
] = "Mobile"

# Inject anomaly 9: Missing required value
transactions.loc[
    9,
    "account_id"
] = None

# Inject anomaly 10: Invalid merchant category
transactions.loc[
    10,
    "transaction_type"
] = "Card Payment"

transactions.loc[
    10,
    "merchant_category"
] = None

# Inject anomaly 11: Transaction before account opening
accounts = pd.read_csv(
    PROJECT_ROOT
    / "data"
    / "raw"
    / "accounts.csv"
)

account_id = transactions.loc[
    11,
    "account_id"
]

account_opening_date = pd.to_datetime(
    accounts.loc[
        accounts["account_id"] == account_id,
        "opening_date"
    ].iloc[0]
)

transactions.loc[
    11,
    "transaction_date"
] = (
    account_opening_date
    - pd.Timedelta(days=30)
).strftime("%Y-%m-%d")

transactions.to_csv(
    OUTPUT_FILE,
    index=False
)

print(
    "Transaction anomalies injected successfully."
)

print(
    f"Output file: {OUTPUT_FILE}"
)