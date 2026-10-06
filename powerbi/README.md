# Power BI Dashboard

## Objective

This Power BI dashboard provides an analytical view of the synthetic banking dataset prepared through the Python data quality pipeline and stored in PostgreSQL.

The dashboard will focus on four analytical areas:

1. Executive Overview
2. Customers & Accounts
3. Loans & Risk
4. Transactions

## Data Source

The analytical data is stored in PostgreSQL in the `banking_db` database.

The Power BI model will be built from the certified banking datasets and SQL reporting layer created in this project.

> All banking data used in this project is synthetic and does not represent real customers, transactions, or actual Belgian banking statistics.


## Data Model

The Power BI model is designed around the certified banking entities stored in PostgreSQL.

### Core Tables

- `customers` — customer attributes, segmentation, income and risk information
- `branches` — branch and regional information
- `accounts` — customer bank accounts and balances
- `loans` — loan portfolio, interest rates and loan status
- `transactions` — banking transaction activity

### Supporting SQL Views

The PostgreSQL reporting layer also provides the following reusable views:

- `vw_customer_profile`
- `vw_account_portfolio`
- `vw_loan_portfolio`
- `vw_transaction_details`
- `vw_branch_performance`

These views provide enriched and pre-aggregated datasets for reporting and validation. The core Power BI model will preserve clear table granularity and relationships to reduce the risk of duplicate aggregation.


### Relationships

#### Customers → Accounts

`customers[customer_id]` (1) → (*) `accounts[customer_id]`

One customer can own multiple accounts, while each account belongs to one customer.

Recommended Power BI configuration:

- Cardinality: One-to-many (1:*)
- Cross-filter direction: Single
- Filter direction: Customers → Accounts


#### Accounts → Transactions

`accounts[account_id]` (1) → (*) `transactions[account_id]`

One account can have multiple transactions, while each transaction belongs to one account.

Recommended Power BI configuration:

- Cardinality: One-to-many (1:*)
- Cross-filter direction: Single
- Filter direction: Accounts → Transactions


#### Customers → Loans

`customers[customer_id]` (1) → (*) `loans[customer_id]`

One customer can have multiple loans, while each loan belongs to one customer.

Recommended Power BI configuration:

- Cardinality: One-to-many (1:*)
- Cross-filter direction: Single
- Filter direction: Customers → Loans


#### Branches → Accounts

`branches[branch_id]` (1) → (*) `accounts[branch_id]`

One branch can manage multiple accounts, while each account belongs to one branch.

Recommended Power BI configuration:

- Cardinality: One-to-many (1:*)
- Cross-filter direction: Single
- Filter direction: Branches → Accounts


#### Branches → Loans

`branches[branch_id]` (1) → (*) `loans[branch_id]`

One branch can manage multiple loans, while each loan belongs to one branch.

Recommended Power BI configuration:

- Cardinality: One-to-many (1:*)
- Cross-filter direction: Single
- Filter direction: Branches → Loans


### Date Dimension

A dedicated Date dimension will be added in Power BI to support consistent time-based analysis.

The Date table will include:

- Date
- Year
- Quarter
- Month Number
- Month Name
- Year-Month

The primary active relationship for transaction analysis will be:

`Date[Date]` (1) → (*) `transactions[transaction_date]`

Recommended Power BI configuration:

- Cardinality: One-to-many (1:*)
- Cross-filter direction: Single
- Filter direction: Date → Transactions


## DAX Measures

The dashboard will use explicit DAX measures instead of relying on implicit Power BI aggregations.

### Executive KPIs

```DAX
Total Customers =
DISTINCTCOUNT(customers[customer_id])

Total Accounts =
DISTINCTCOUNT(accounts[account_id])

Total Account Balance =
SUM(accounts[balance])

Total Loans =
DISTINCTCOUNT(loans[loan_id])

Total Loan Amount =
SUM(loans[loan_amount])

Total Transactions =
DISTINCTCOUNT(transactions[transaction_id])

Transaction Volume =
SUM(transactions[amount])
```

These measures provide the principal indicators used in the Executive Overview.

### Loan KPIs

```DAX
Active Loans =
CALCULATE(
    [Total Loans],
    loans[loan_status] = "Active"
)

Defaulted Loans =
CALCULATE(
    [Total Loans],
    loans[loan_status] = "Defaulted"
)

Defaulted Loan Share % =
DIVIDE(
    [Defaulted Loans],
    [Total Loans],
    0
)

Average Loan Amount =
AVERAGE(loans[loan_amount])

Average Interest Rate =
AVERAGE(loans[interest_rate])
```


### Transaction KPIs

```DAX
Completed Transactions =
CALCULATE(
    [Total Transactions],
    transactions[transaction_status] = "Completed"
)

Failed Transactions =
CALCULATE(
    [Total Transactions],
    transactions[transaction_status] = "Failed"
)

Failed Transaction Share % =
DIVIDE(
    [Failed Transactions],
    [Total Transactions],
    0
)

Average Transaction Amount =
AVERAGE(transactions[amount])
```


### Account KPIs

```DAX
Average Account Balance =
AVERAGE(accounts[balance])

Active Accounts =
CALCULATE(
    [Total Accounts],
    accounts[status] = "Active"
)

Active Account Share % =
DIVIDE(
    [Active Accounts],
    [Total Accounts],
    0
)

Accounts per Customer =
DIVIDE(
    [Total Accounts],
    [Total Customers],
    0
)
```


## Dashboard Pages

### 1. Executive Overview

Purpose: provide a high-level view of the synthetic banking portfolio and operational activity.

#### KPI Cards

- Total Customers
- Total Accounts
- Total Account Balance
- Total Loans
- Total Loan Amount
- Total Transactions
- Transaction Volume

#### Visuals

- Monthly Transaction Volume — Line chart
- Account Balance by Account Type — Bar chart
- Loan Amount by Loan Type — Bar chart
- Customers by Segment — Donut chart
- Transaction Volume by Channel — Bar chart

#### Slicers

- Date
- Customer Segment
- Region


### 2. Customers & Accounts

Purpose: analyze the customer base and account portfolio across segments, account types, and geographic areas.

#### KPI Cards

- Total Customers
- Total Accounts
- Total Account Balance
- Average Account Balance
- Active Accounts
- Accounts per Customer

#### Visuals

- Customers by Segment — Bar chart
- Account Balance by Account Type — Bar chart
- Accounts by Status — Donut chart
- Account Balance by Region — Bar chart
- Average Account Balance by Customer Segment — Column chart

#### Slicers

- Customer Segment
- Account Type
- Account Status
- Region


### 3. Loans & Risk

Purpose: analyze the synthetic loan portfolio by loan type, status, customer risk category, and geographic area.

#### KPI Cards

- Total Loans
- Total Loan Amount
- Average Loan Amount
- Average Interest Rate
- Active Loans
- Defaulted Loan Share %

#### Visuals

- Loan Amount by Loan Type — Bar chart
- Loans by Status — Donut chart
- Loan Amount by Risk Category — Column chart
- Loan Amount by Region — Bar chart
- Average Interest Rate by Loan Type — Column chart

#### Slicers

- Loan Type
- Loan Status
- Risk Category
- Customer Segment
- Region


### 4. Transactions

Purpose: analyze transaction activity over time and across transaction types, channels, and statuses.

#### KPI Cards

- Total Transactions
- Transaction Volume
- Average Transaction Amount
- Completed Transactions
- Failed Transactions
- Failed Transaction Share %

#### Visuals

- Monthly Transaction Volume — Line chart
- Transactions by Type — Bar chart
- Transaction Volume by Channel — Bar chart
- Transactions by Status — Donut chart
- Average Transaction Amount by Type — Column chart

#### Slicers

- Date
- Transaction Type
- Channel
- Transaction Status
- Region
- Customer Segment