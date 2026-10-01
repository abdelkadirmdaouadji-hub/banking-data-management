from pathlib import Path
import sys
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = (
    PROJECT_ROOT / "data" / "raw"
)

QUALITY_REPORTS_DIR = (
    PROJECT_ROOT / "data" / "quality_reports"
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

print("Transactions loaded:", len(transactions))
print("Accounts loaded:", len(accounts))

# Check invalid account references
invalid_account_ref = (
    ~transactions["account_id"].isin(
        accounts["account_id"]
    )
)

invalid_account_ref_count = (
    invalid_account_ref.sum()
)

print(
    "Invalid account references:",
    invalid_account_ref_count
)

# Check duplicate transaction IDs
duplicate_transaction_id = (
    transactions["transaction_id"]
    .duplicated(keep=False)
)

duplicate_transaction_id_count = (
    duplicate_transaction_id.sum()
)

print(
    "Duplicate transaction IDs:",
    duplicate_transaction_id_count
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

invalid_transaction_type_count = (
    invalid_transaction_type.sum()
)

print(
    "Invalid transaction types:",
    invalid_transaction_type_count
)

# Check invalid transaction amounts
invalid_amount = (
    transactions["amount"] <= 0
)

invalid_amount_count = (
    invalid_amount.sum()
)

print(
    "Invalid transaction amounts:",
    invalid_amount_count
)

# Check future transaction dates
today = pd.Timestamp.today().normalize()

future_transaction_date = (
    transactions["transaction_date"] > today
)

future_transaction_date_count = (
    future_transaction_date.sum()
)

print(
    "Future transaction dates:",
    future_transaction_date_count
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

invalid_transaction_status_count = (
    invalid_transaction_status.sum()
)

print(
    "Invalid transaction statuses:",
    invalid_transaction_status_count
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

invalid_channel_count = (
    invalid_channel.sum()
)

print(
    "Invalid transaction channels:",
    invalid_channel_count
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

invalid_type_channel_count = (
    invalid_type_channel.sum()
)

print(
    "Invalid type/channel combinations:",
    invalid_type_channel_count
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

transaction_before_account_opening_count = (
    transaction_before_account_opening.sum()
)

print(
    "Transactions before account opening:",
    transaction_before_account_opening_count
)

# Check missing required values
required_columns = [
    "transaction_id",
    "account_id",
    "transaction_date",
    "transaction_type",
    "amount",
    "channel",
    "transaction_status"
]

missing_required_values = (
    transactions[required_columns]
    .isna()
    .sum()
    .sum()
)

print(
    "Missing required values:",
    missing_required_values
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

invalid_merchant_category_count = (
    invalid_merchant_category.sum()
)

print(
    "Invalid merchant categories:",
    invalid_merchant_category_count
)

# Build data quality report
quality_checks = [
    ("Invalid account references", invalid_account_ref_count),
    ("Duplicate transaction IDs", duplicate_transaction_id_count),
    ("Invalid transaction types", invalid_transaction_type_count),
    ("Invalid transaction amounts", invalid_amount_count),
    ("Future transaction dates", future_transaction_date_count),
    ("Invalid transaction statuses", invalid_transaction_status_count),
    ("Invalid transaction channels", invalid_channel_count),
    ("Invalid type/channel combinations", invalid_type_channel_count),
    (
        "Transactions before account opening",
        transaction_before_account_opening_count
    ),
    ("Missing required values", missing_required_values),
    ("Invalid merchant categories", invalid_merchant_category_count)
]

quality_report = pd.DataFrame(
    quality_checks,
    columns=[
        "check",
        "error_count"
    ]
)

quality_report["status"] = quality_report[
    "error_count"
].apply(
    lambda x: "PASS" if x == 0 else "FAIL"
)

# Overall data quality status
overall_status = (
    "PASS"
    if (quality_report["error_count"] == 0).all()
    else "FAIL"
)

print("\n--- TRANSACTIONS DATA QUALITY REPORT ---")
print(quality_report.to_string(index=False))

print(
    f"\nOverall Data Quality Status: "
    f"{overall_status}"
)


# Save quality report
QUALITY_REPORTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)

input_stem = Path(file_name).stem

report_file = (
    QUALITY_REPORTS_DIR
    / f"{input_stem}_quality_report.csv"
)

quality_report.to_csv(
    report_file,
    index=False
)

print(
    f"Quality report saved to: "
    f"{report_file}"
)


# Exit code for automation / pipelines
sys.exit(
    0 if overall_status == "PASS" else 1
)