import random
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker


# Reproducibility
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
Faker.seed(SEED)

fake = Faker("en_US")

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
# Number of synthetic customers
N_CUSTOMERS = 50_000
N_BRANCHES = 25
N_ACCOUNTS = 65_000
N_LOANS = 15_000
N_TRANSACTIONS = 300_000

print("Banking data generator initialized.")
print(f"Customers to generate: {N_CUSTOMERS:,}")
print(f"Raw output directory: {RAW_DATA_DIR}")
def random_birth_date(min_age=18, max_age=85):
    today = date.today()

    latest_birth_date = date(
        today.year - min_age,
        today.month,
        today.day
    )

    earliest_birth_date = date(
        today.year - max_age,
        today.month,
        today.day
    )

    days_between = (latest_birth_date - earliest_birth_date).days

    return earliest_birth_date + timedelta(
        days=random.randint(0, days_between)
    )


def generate_customers(n_customers):
    customers = []

    segments = ["Standard", "Premium", "Private"]
    segment_weights = [0.75, 0.20, 0.05]

    for i in range(1, n_customers + 1):
        customer_id = f"C{i:06d}"

        gender = random.choice(["Male", "Female"])

        if gender == "Male":
            first_name = fake.first_name_male()
        else:
            first_name = fake.first_name_female()

        last_name = fake.last_name()
        birth_date = random_birth_date()

        city = fake.city()
        country = "Belgium"

        annual_income = round(
            max(0, np.random.normal(45_000, 18_000)),
            2
        )

        customer_segment = random.choices(
            segments,
            weights=segment_weights,
            k=1
        )[0]

        join_date = fake.date_between(
            start_date="-12y",
            end_date="today"
        )

        risk_score = random.randint(1, 100)

        customers.append({
            "customer_id": customer_id,
            "first_name": first_name,
            "last_name": last_name,
            "birth_date": birth_date,
            "gender": gender,
            "city": city,
            "country": country,
            "annual_income": annual_income,
            "customer_segment": customer_segment,
            "join_date": join_date,
            "risk_score": risk_score,
        })

    return pd.DataFrame(customers)

def generate_branches(n_branches):
    branches = []
    
    locations = [
        ("Brussels", "Brussels-Capital"),
        ("Antwerp", "Flanders"),
        ("Ghent", "Flanders"),
        ("Bruges", "Flanders"),
        ("Leuven", "Flanders"),
        ("Mechelen", "Flanders"),
        ("Hasselt", "Flanders"),
        ("Liege", "Wallonia"),
        ("Namur", "Wallonia"),
        ("Mons", "Wallonia"),
        ("Charleroi", "Wallonia"),
        ("Tournai", "Wallonia")
    ]

    for i in range(1, n_branches + 1):
        branch_id = f"B{i:03d}"

        city, region = random.choice(locations)

        branch_name = f"{city} Branch {i}"
        opening_date = fake.date_between(
            start_date="-25y",
            end_date="today"
)

        manager_name = fake.name()
        
        


        branches.append({
            "branch_id": branch_id,
             "branch_name": branch_name,
            "city": city,
            "region": region,
            "country": "Belgium",
            "opening_date": opening_date,
            "manager_name": manager_name
})
    return pd.DataFrame(branches)

def generate_accounts(n_accounts, customers_df, branches_df):
    accounts = []

    customer_ids = customers_df["customer_id"].tolist()
    branch_ids = branches_df["branch_id"].tolist()
    
    customer_join_dates = customers_df.set_index(
    "customer_id"
    )["join_date"].to_dict()

    branch_opening_dates = branches_df.set_index(
    "branch_id"
    )["opening_date"].to_dict()
    
    account_types = ["Checking", "Savings", "Business"]
    account_type_weights = [0.55, 0.35, 0.10]
    for i in range(1, n_accounts + 1):
        account_id = f"A{i:07d}"

        customer_id = random.choice(customer_ids)
        branch_id = random.choice(branch_ids)
        account_type = random.choices(
            account_types,
            weights=account_type_weights,
            k=1
        )[0]
        if account_type == "Checking":
            balance = round(
                max(0, np.random.normal(3_500, 2_500)),
                2
            )

        elif account_type == "Savings":
            balance = round(
                max(0, np.random.normal(12_000, 8_000)),
                2
            )

        else:
            balance = round(
                max(0, np.random.normal(30_000, 20_000)),
                2
            )   
        earliest_opening_date = max(
            customer_join_dates[customer_id],
            branch_opening_dates[branch_id]
        )

        days_between = (
            date.today() - earliest_opening_date
        ).days

        opening_date = earliest_opening_date + timedelta(
            days=random.randint(0, days_between)
        )

        status = random.choices(
            ["Active", "Inactive", "Closed"],
            weights=[0.85, 0.10, 0.05],
            k=1
        )[0]
        accounts.append({
            "account_id": account_id,
            "customer_id": customer_id,
            "branch_id": branch_id,
            "account_type": account_type,
            "balance": balance,
            "opening_date": opening_date,
            "status": status

        })
        
    return pd.DataFrame(accounts)

def generate_loans(n_loans, customers_df, branches_df):
    loans = []

    customer_ids = customers_df["customer_id"].tolist()
    branch_ids = branches_df["branch_id"].tolist()

    customer_join_dates = customers_df.set_index(
        "customer_id"
    )["join_date"].to_dict()

    branch_opening_dates = branches_df.set_index(
        "branch_id"
    )["opening_date"].to_dict()

    loan_types = [
        "Personal",
        "Mortgage",
        "Auto",
        "Business"
    ]

    loan_type_weights = [
        0.40,
        0.30,
        0.20,
        0.10
    ]

    for i in range(1, n_loans + 1):
        loan_id = f"L{i:06d}"

        customer_id = random.choice(customer_ids)
        branch_id = random.choice(branch_ids)

        loan_type = random.choices(
            loan_types,
            weights=loan_type_weights,
            k=1
        )[0]

        # Loan amount
        if loan_type == "Personal":
            loan_amount = round(
                random.uniform(2_000, 40_000),
                2
            )

        elif loan_type == "Mortgage":
            loan_amount = round(
                random.uniform(80_000, 500_000),
                2
            )

        elif loan_type == "Auto":
            loan_amount = round(
                random.uniform(10_000, 70_000),
                2
            )

        else:
            loan_amount = round(
                random.uniform(20_000, 250_000),
                2
            )

        # Interest rate
        if loan_type == "Personal":
            interest_rate = round(
                random.uniform(4.0, 12.0),
                2
            )

        elif loan_type == "Mortgage":
            interest_rate = round(
                random.uniform(2.0, 6.0),
                2
            )

        elif loan_type == "Auto":
            interest_rate = round(
                random.uniform(3.0, 8.0),
                2
            )

        else:
            interest_rate = round(
                random.uniform(4.0, 10.0),
                2
            )

        # Loan term
        if loan_type == "Personal":
            term_months = random.choice([
                12, 24, 36, 48, 60
            ])

        elif loan_type == "Mortgage":
            term_months = random.choice([
                120, 180, 240, 300, 360
            ])

        elif loan_type == "Auto":
            term_months = random.choice([
                24, 36, 48, 60, 72
            ])

        else:
            term_months = random.choice([
                12, 24, 36, 48, 60, 84
            ])

        # Loan start date
        earliest_start_date = max(
            customer_join_dates[customer_id],
            branch_opening_dates[branch_id]
        )

        days_between = (
            date.today() - earliest_start_date
        ).days

        start_date = earliest_start_date + timedelta(
            days=random.randint(0, days_between)
        )

        # Loan status
        loan_status = random.choices(
            ["Active", "Paid", "Defaulted"],
            weights=[0.70, 0.25, 0.05],
            k=1
        )[0]

        # Add the loan to the dataset
        loans.append({
            "loan_id": loan_id,
            "customer_id": customer_id,
            "branch_id": branch_id,
            "loan_type": loan_type,
            "loan_amount": loan_amount,
            "interest_rate": interest_rate,
            "term_months": term_months,
            "start_date": start_date,
            "loan_status": loan_status
        })

    return pd.DataFrame(loans)

def generate_transactions(
    n_transactions,
    accounts_df
):
    transactions = []

    account_ids = accounts_df[
        "account_id"
    ].tolist()

    account_opening_dates = accounts_df.set_index(
        "account_id"
    )["opening_date"].to_dict()

    transaction_types = [
        "Card Payment",
        "Bank Transfer",
        "Cash Withdrawal",
        "Direct Debit",
        "Deposit"
    ]

    transaction_type_weights = [
        0.40,
        0.25,
        0.15,
        0.10,
        0.10
    ]

    channels = [
        "Mobile",
        "Web",
        "ATM",
        "Branch",
        "POS"
    ]
    
    for i in range(1, n_transactions + 1):
        transaction_id = f"T{i:09d}"

        account_id = random.choice(
            account_ids
        )

        account_opening_date = (
            account_opening_dates[account_id]
        )

        days_between = (
            date.today() - account_opening_date
        ).days

        transaction_date = (
            account_opening_date
            + timedelta(
                days=random.randint(
                    0,
                    days_between
                )
            )
        )
        
        transaction_type = random.choices(
            transaction_types,
            weights=transaction_type_weights,
            k=1
        )[0]

        if transaction_type == "Card Payment":
            channel = random.choice([
                "POS",
                "Web",
                "Mobile"
            ])

        elif transaction_type == "Cash Withdrawal":
            channel = "ATM"

        elif transaction_type == "Bank Transfer":
            channel = random.choice([
                "Mobile",
                "Web",
                "Branch"
            ])

        elif transaction_type == "Direct Debit":
            channel = random.choice([
                "Web",
                "Mobile"
            ])

        else:
            channel = random.choice([
                "ATM",
                "Branch"
            ]) 
            
        # Transaction amount
        if transaction_type == "Card Payment":
            amount = round(
                random.uniform(5, 500),
                2
            )

        elif transaction_type == "Cash Withdrawal":
            amount = round(
                random.uniform(20, 1000),
                2
            )

        elif transaction_type == "Bank Transfer":
            amount = round(
                random.uniform(50, 10_000),
                2
            )

        elif transaction_type == "Direct Debit":
            amount = round(
                random.uniform(10, 2_000),
                2
            )

        else:
            # Deposit
            amount = round(
                random.uniform(20, 5_000),
                2
            )
            
        # Transaction status
        transaction_status = random.choices(
            [
                "Completed",
                "Failed",
                "Pending"
            ],
            weights=[
                0.94,
                0.04,
                0.02
            ],
            k=1
        )[0]
        
        # Merchant category
        if transaction_type == "Card Payment":
            merchant_category = random.choice([
                "Groceries",
                "Restaurants",
                "Transport",
                "Shopping",
                "Entertainment",
                "Healthcare",
                "Travel"
            ])
        else:
            merchant_category = None
            
        transactions.append({
            "transaction_id": transaction_id,
            "account_id": account_id,
            "transaction_date": transaction_date,
            "transaction_type": transaction_type,
            "amount": amount,
            "channel": channel,
            "merchant_category": merchant_category,
            "transaction_status": transaction_status
        })
        
    return pd.DataFrame(transactions)       


customers_df = generate_customers(N_CUSTOMERS)
branches_df = generate_branches(N_BRANCHES)
accounts_df = generate_accounts(N_ACCOUNTS, customers_df, branches_df)
loans_df = generate_loans(
    N_LOANS,
    customers_df,
    branches_df
)
transactions_df = generate_transactions(
    N_TRANSACTIONS,
    accounts_df
)

print(customers_df.head())
print()
print(customers_df.shape)

print("\n--- BRANCHES ---")
print(branches_df.head())
print()
print(branches_df.shape)

print("\n--- ACCOUNTS ---")
print(accounts_df.head())
print()
print(accounts_df.shape)

print("\n--- LOANS ---")
print(loans_df.head())
print()
print(loans_df.shape)

print("\n--- TRANSACTIONS ---")
print(transactions_df.head())
print()
print(transactions_df.shape)


output_file = RAW_DATA_DIR / "customers.csv"
customers_df.to_csv(
    output_file,
    index=False
)

print(f"Customers dataset saved to: {output_file}")

branches_output_file = RAW_DATA_DIR / "branches.csv"

branches_df.to_csv(
    branches_output_file,
    index=False
)

print(f"Branches dataset saved to: {branches_output_file}")

accounts_output_file = RAW_DATA_DIR / "accounts.csv"

accounts_df.to_csv(
    accounts_output_file,
    index=False
)

print(f"Accounts dataset saved to: {accounts_output_file}")

loans_output_file = RAW_DATA_DIR / "loans.csv"

loans_df.to_csv(
    loans_output_file,
    index=False
)

print(f"Loans dataset saved to: {loans_output_file}")

transactions_output_file = (
    RAW_DATA_DIR / "transactions.csv"
)

transactions_df.to_csv(
    transactions_output_file,
    index=False
)

print(
    f"Transactions dataset saved to: "
    f"{transactions_output_file}"
)