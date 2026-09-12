# Banking Data Dictionary

This document describes the structure, meaning and business rules of the datasets used in the Banking Data Management & BI project.

## Core Tables

- Customers
- Accounts
- Transactions
- Loans
- Branches

## 1. Customers

The `customers` table contains the master data for each bank customer.

| Column | Data Type | Description | Business Rule |
|---|---|---|---|
| customer_id | VARCHAR(10) | Unique customer identifier | Primary key, unique, not null |
| first_name | VARCHAR(50) | Customer first name | Not null |
| last_name | VARCHAR(50) | Customer last name | Not null |
| birth_date | DATE | Customer date of birth | Customer must be at least 18 years old |
| gender | VARCHAR(10) | Customer gender | Controlled values |
| city | VARCHAR(50) | City of residence | Not null |
| country | VARCHAR(50) | Country of residence | Not null |
| annual_income | DECIMAL(12,2) | Estimated annual income in EUR | Must be >= 0 |
| customer_segment | VARCHAR(20) | Commercial customer segment | Standard, Premium or Private |
| join_date | DATE | Date customer joined the bank | Cannot be in the future |
| risk_score | INTEGER | Internal customer risk score | Between 1 and 100 |

## 2. Accounts

The `accounts` table contains the bank accounts held by customers.

| Column | Data Type | Description | Business Rule |
|---|---|---|---|
| account_id | VARCHAR(10) | Unique account identifier | Primary key, unique, not null |
| customer_id | VARCHAR(10) | Customer who owns the account | Foreign key referencing customers.customer_id |
| branch_id | VARCHAR(10) | Branch managing the account | Foreign key referencing branches.branch_id |
| account_type | VARCHAR(20) | Type of bank account | Current, Savings or Business |
| open_date | DATE | Account opening date | Cannot be in the future |
| balance | DECIMAL(15,2) | Current account balance in EUR | Numeric value |
| currency | VARCHAR(3) | Account currency | EUR, USD or GBP |
| status | VARCHAR(20) | Current account status | Active, Inactive, Frozen or Closed |

## 3. Transactions

The `transactions` table contains financial transactions performed on customer accounts.

| Column | Data Type | Description | Business Rule |
|---|---|---|---|
| transaction_id | VARCHAR(15) | Unique transaction identifier | Primary key, unique, not null |
| account_id | VARCHAR(10) | Account associated with the transaction | Foreign key referencing accounts.account_id |
| transaction_date | TIMESTAMP | Date and time of the transaction | Cannot be in the future |
| transaction_type | VARCHAR(20) | Type of financial operation | Deposit, Withdrawal, Transfer, Payment or Fee |
| amount | DECIMAL(15,2) | Transaction amount in EUR | Must be greater than 0 |
| channel | VARCHAR(20) | Channel used for the transaction | Branch, ATM, Online, Mobile or Card |
| merchant_category | VARCHAR(50) | Merchant category when applicable | Can be null for non-merchant transactions |
| status | VARCHAR(20) | Processing status | Completed, Pending, Declined or Reversed |

## 4. Loans

The `loans` table contains information about loans granted to bank customers.

| Column | Data Type | Description | Business Rule |
|---|---|---|---|
| loan_id | VARCHAR(10) | Unique loan identifier | Primary key, unique, not null |
| customer_id | VARCHAR(10) | Customer associated with the loan | Foreign key referencing customers.customer_id |
| branch_id | VARCHAR(10) | Branch managing the loan | Foreign key referencing branches.branch_id |
| loan_type | VARCHAR(30) | Type of credit product | Mortgage, Personal, Auto or Business |
| loan_amount | DECIMAL(15,2) | Original loan amount in EUR | Must be greater than 0 |
| interest_rate | DECIMAL(5,2) | Annual interest rate (%) | Must be between 0 and 100 |
| start_date | DATE | Loan start date | Cannot be in the future |
| maturity_date | DATE | Contractual maturity date | Must be after start_date |
| outstanding_balance | DECIMAL(15,2) | Remaining principal balance | Must be >= 0 and normally <= loan_amount |
| loan_status | VARCHAR(20) | Current loan status | Performing, Delinquent, Defaulted or Closed |
| pd | DECIMAL(6,5) | Probability of Default | Between 0 and 1 |
| lgd | DECIMAL(6,5) | Loss Given Default | Between 0 and 1 |

## 5. Branches

The `branches` table contains information about the bank's branch network.

| Column | Data Type | Description | Business Rule |
|---|---|---|---|
| branch_id | VARCHAR(10) | Unique branch identifier | Primary key, unique, not null |
| branch_name | VARCHAR(100) | Name of the branch | Not null |
| city | VARCHAR(50) | City where the branch is located | Not null |
| region | VARCHAR(50) | Geographic region of the branch | Not null |
| opening_date | DATE | Date the branch started operations | Cannot be in the future |