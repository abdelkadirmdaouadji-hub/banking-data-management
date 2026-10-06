# Banking Data Dictionary

This document describes the structure, meaning, and principal business rules of the PostgreSQL tables used in the Banking Data Management & BI project.

All data in this project is synthetic and is used only to demonstrate data management, data quality, SQL, and BI practices.

## Core Tables

- Customers
- Branches
- Accounts
- Loans
- Transactions

## 1. Customers

The `customers` table contains the master data for each synthetic bank customer.

| Column | Data Type | Description | Business Rule |
|---|---|---|---|
| customer_id | VARCHAR(7) | Unique customer identifier | Primary key, unique, not null |
| first_name | VARCHAR(100) | Customer first name | Not null |
| last_name | VARCHAR(100) | Customer last name | Not null |
| birth_date | DATE | Customer date of birth | Not null |
| gender | VARCHAR(10) | Customer gender | Male or Female |
| city | VARCHAR(100) | City of residence | Not null |
| country | VARCHAR(100) | Country of residence | Not null |
| annual_income | NUMERIC(12,2) | Synthetic annual income | Must be >= 0 |
| customer_segment | VARCHAR(20) | Customer segment | Standard, Premium or Private |
| join_date | DATE | Date the customer joined the bank | Not null |
| risk_score | SMALLINT | Synthetic internal risk score | Between 1 and 100 |

## 2. Branches

The `branches` table contains information about the synthetic branch network.

| Column | Data Type | Description | Business Rule |
|---|---|---|---|
| branch_id | VARCHAR(4) | Unique branch identifier | Primary key, unique, not null |
| branch_name | VARCHAR(150) | Branch name | Not null |
| city | VARCHAR(100) | Branch city | Not null |
| region | VARCHAR(100) | Branch region | Not null |
| country | VARCHAR(100) | Branch country | Not null |
| opening_date | DATE | Branch opening date | Not null |
| manager_name | VARCHAR(150) | Synthetic branch manager name | Not null |

## 3. Accounts

The `accounts` table contains accounts linked to customers and branches.

| Column | Data Type | Description | Business Rule |
|---|---|---|---|
| account_id | VARCHAR(8) | Unique account identifier | Primary key, unique, not null |
| customer_id | VARCHAR(7) | Account owner | Foreign key referencing customers.customer_id |
| branch_id | VARCHAR(4) | Managing branch | Foreign key referencing branches.branch_id |
| account_type | VARCHAR(20) | Account type | Checking, Savings or Business |
| balance | NUMERIC(14,2) | Synthetic account balance | Must be >= 0 |
| opening_date | DATE | Account opening date | Not null |
| status | VARCHAR(20) | Account status | Active, Inactive or Closed |

## 4. Loans

The `loans` table contains synthetic loan records linked to customers and branches.

| Column | Data Type | Description | Business Rule |
|---|---|---|---|
| loan_id | VARCHAR(7) | Unique loan identifier | Primary key, unique, not null |
| customer_id | VARCHAR(7) | Customer associated with the loan | Foreign key referencing customers.customer_id |
| branch_id | VARCHAR(4) | Branch associated with the loan | Foreign key referencing branches.branch_id |
| loan_type | VARCHAR(20) | Loan type | Personal, Mortgage, Auto or Business |
| loan_amount | NUMERIC(14,2) | Original synthetic loan amount | Must be > 0 |
| interest_rate | NUMERIC(5,2) | Synthetic annual interest rate | > 0 and <= 100 |
| term_months | INTEGER | Loan term in months | Must be > 0 |
| start_date | DATE | Loan start date | Not null |
| loan_status | VARCHAR(20) | Loan status | Active, Paid or Defaulted |

## 5. Transactions

The `transactions` table contains synthetic transactions associated with accounts.

| Column | Data Type | Description | Business Rule |
|---|---|---|---|
| transaction_id | VARCHAR(10) | Unique transaction identifier | Primary key, unique, not null |
| account_id | VARCHAR(8) | Associated account | Foreign key referencing accounts.account_id |
| transaction_date | DATE | Transaction date | Not null |
| transaction_type | VARCHAR(30) | Transaction type | Card Payment, Bank Transfer, Cash Withdrawal, Direct Debit or Deposit |
| amount | NUMERIC(14,2) | Synthetic transaction amount | Must be > 0 |
| channel | VARCHAR(20) | Transaction channel | Mobile, Web, ATM, Branch or POS |
| merchant_category | VARCHAR(50) | Merchant category when applicable | Nullable |
| transaction_status | VARCHAR(20) | Processing status | Completed, Failed or Pending |

The PostgreSQL schema also enforces permitted transaction type/channel combinations. The Python data quality pipeline performs additional validation before certified datasets are loaded into PostgreSQL.
