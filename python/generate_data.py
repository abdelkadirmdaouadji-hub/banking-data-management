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
# Number of synthetic customers
N_CUSTOMERS = 50_000

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

customers_df = generate_customers(N_CUSTOMERS)

print(customers_df.head())
print()
print(customers_df.shape)

output_file = RAW_DATA_DIR / "customers.csv"
customers_df.to_csv(
    output_file,
    index=False
)

print(f"Customers dataset saved to: {output_file}")

