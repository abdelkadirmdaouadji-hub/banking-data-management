from pathlib import Path
import sys
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = (
    PROJECT_ROOT / "data" / "raw"
)

PROCESSED_DATA_DIR = (
    PROJECT_ROOT / "data" / "processed"
)

PROCESSED_DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)


file_name = (
    sys.argv[1]
    if len(sys.argv) > 1
    else "transactions.csv"
)

INPUT_FILE = RAW_DATA_DIR / file_name


transactions = pd.read_csv(
    INPUT_FILE,
    parse_dates=["transaction_date"]
)

accounts = pd.read_csv(
    RAW_DATA_DIR / "accounts.csv",
    parse_dates=["opening_date"]
)


print(
    "Transactions loaded:",
    len(transactions)
)

print(
    "Accounts loaded:",
    len(accounts)
)

# Check invalid account references
invalid_account_ref = (
    ~transactions["account_id"].isin(
        accounts["account_id"]
    )
)

# Check duplicate transaction IDs
duplicate_transaction_id = (
    transactions["transaction_id"]
    .duplicated(keep=False)
)

# Check invalid transaction types
valid_transaction_types = [
    "Card Payment",
    "Bank Transfer",
    "Cash Withdrawal",
    "Direct Debit",
    "Deposit"
]

invalid_transaction_type = (
    ~transactions["transaction_type"].isin(
        valid_transaction_types
    )
)

# Check invalid transaction amounts
invalid_amount = (
    transactions["amount"] <= 0
)

# Check future transaction dates
today = pd.Timestamp.today().normalize()

future_transaction_date = (
    transactions["transaction_date"] > today
)


# Check invalid transaction statuses
valid_transaction_statuses = [
    "Completed",
    "Failed",
    "Pending"
]

invalid_transaction_status = (
    ~transactions["transaction_status"].isin(
        valid_transaction_statuses
    )
)


# Check invalid transaction channels
valid_channels = [
    "Mobile",
    "Web",
    "ATM",
    "Branch",
    "POS"
]

invalid_channel = (
    ~transactions["channel"].isin(
        valid_channels
    )
)


# Check transaction type / channel consistency
valid_type_channel = (
    (
        (transactions["transaction_type"] == "Card Payment")
        & transactions["channel"].isin(
            ["POS", "Web", "Mobile"]
        )
    )
    | (
        (transactions["transaction_type"] == "Cash Withdrawal")
        & (transactions["channel"] == "ATM")
    )
    | (
        (transactions["transaction_type"] == "Bank Transfer")
        & transactions["channel"].isin(
            ["Mobile", "Web", "Branch"]
        )
    )
    | (
        (transactions["transaction_type"] == "Direct Debit")
        & transactions["channel"].isin(
            ["Web", "Mobile"]
        )
    )
    | (
        (transactions["transaction_type"] == "Deposit")
        & transactions["channel"].isin(
            ["ATM", "Branch"]
        )
    )
)

invalid_type_channel = ~valid_type_channel

# Check missing required values
missing_transaction_id = (
    transactions["transaction_id"].isna()
)

missing_account_id = (
    transactions["account_id"].isna()
)

missing_transaction_date = (
    transactions["transaction_date"].isna()
)

missing_transaction_type = (
    transactions["transaction_type"].isna()
)

missing_amount = (
    transactions["amount"].isna()
)

missing_channel = (
    transactions["channel"].isna()
)

missing_transaction_status = (
    transactions["transaction_status"].isna()
)


# Check merchant category consistency
invalid_merchant_category = (
    (
        (transactions["transaction_type"] == "Card Payment")
        & transactions["merchant_category"].isna()
    )
    | (
        (transactions["transaction_type"] != "Card Payment")
        & transactions["merchant_category"].notna()
    )
)


# Check transactions before account opening date
account_opening_map = accounts.set_index(
    "account_id"
)["opening_date"]

account_opening_dates = transactions[
    "account_id"
].map(account_opening_map)

transaction_before_account_opening = (
    transactions["transaction_date"]
    < account_opening_dates
)

# Combine all data quality rules
invalid_rows = (
    invalid_account_ref
    | duplicate_transaction_id
    | invalid_transaction_type
    | invalid_amount
    | future_transaction_date
    | invalid_transaction_status
    | invalid_channel
    | invalid_type_channel
    | missing_transaction_id
    | missing_account_id
    | missing_transaction_date
    | missing_transaction_type
    | missing_amount
    | missing_channel
    | missing_transaction_status
    | invalid_merchant_category
    | transaction_before_account_opening
)


# Split clean and rejected transactions
clean_transactions = transactions[
    ~invalid_rows
].copy()

rejected_transactions = transactions[
    invalid_rows
].copy()

# Add rejection reason
rejected_transactions[
    "rejection_reason"
] = ""

rejection_rules = [
    (
        invalid_account_ref,
        "Invalid account reference"
    ),
    (
        duplicate_transaction_id,
        "Duplicate transaction ID"
    ),
    (
        invalid_transaction_type,
        "Invalid transaction type"
    ),
    (
        invalid_amount,
        "Invalid transaction amount"
    ),
    (
        future_transaction_date,
        "Future transaction date"
    ),
    (
        invalid_transaction_status,
        "Invalid transaction status"
    ),
    (
        invalid_channel,
        "Invalid transaction channel"
    ),
    (
        invalid_type_channel,
        "Invalid type/channel combination"
    ),
    (
        missing_transaction_id,
        "Missing transaction ID"
    ),
    (
        missing_account_id,
        "Missing account ID"
    ),
    (
        missing_transaction_date,
        "Missing transaction date"
    ),
    (
        missing_transaction_type,
        "Missing transaction type"
    ),
    (
        missing_amount,
        "Missing transaction amount"
    ),
    (
        missing_channel,
        "Missing transaction channel"
    ),
    (
        missing_transaction_status,
        "Missing transaction status"
    ),
    (
        invalid_merchant_category,
        "Invalid merchant category"
    ),
    (
        transaction_before_account_opening,
        "Transaction before account opening"
    )
]

for rule_mask, reason in rejection_rules:
    affected_indexes = transactions.index[
        rule_mask
    ].intersection(
        rejected_transactions.index
    )

    rejected_transactions.loc[
        affected_indexes,
        "rejection_reason"
    ] += reason + "; "
    
# Define output file names
input_stem = Path(file_name).stem

clean_output_file = (
    PROCESSED_DATA_DIR
    / f"{input_stem}_clean.csv"
)

rejected_output_file = (
    PROCESSED_DATA_DIR
    / f"{input_stem}_rejected.csv"
)


# Save clean and rejected transactions
clean_transactions.to_csv(
    clean_output_file,
    index=False
)

rejected_transactions.to_csv(
    rejected_output_file,
    index=False
)

print(
    f"Clean transactions saved to: "
    f"{clean_output_file}"
)

print(
    f"Rejected transactions saved to: "
    f"{rejected_output_file}"
)


print(
    "Clean transactions:",
    len(clean_transactions)
)

print(
    "Rejected transactions:",
    len(rejected_transactions)
)

# Build cleaning summary
cleaning_summary = pd.DataFrame({
    "metric": [
        "input_rows",
        "clean_rows",
        "rejected_rows",
        "rejection_rate_pct"
    ],
    "value": [
        len(transactions),
        len(clean_transactions),
        len(rejected_transactions),
        round(
            len(rejected_transactions)
            / len(transactions)
            * 100,
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

print("\n--- CLEANING SUMMARY ---")
print(cleaning_summary)

print(
    f"\nCleaning summary saved to: "
    f"{summary_output_file}"
)