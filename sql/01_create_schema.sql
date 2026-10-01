-- ============================================================
-- Banking Data Management Project
-- PostgreSQL relational schema
-- ============================================================

CREATE TABLE customers (
    customer_id VARCHAR(7) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    birth_date DATE NOT NULL,
    gender VARCHAR(10) NOT NULL,
    city VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    annual_income NUMERIC(12, 2) NOT NULL,
    customer_segment VARCHAR(20) NOT NULL,
    join_date DATE NOT NULL,
    risk_score SMALLINT NOT NULL,

    CONSTRAINT chk_customer_income
        CHECK (annual_income >= 0),

    CONSTRAINT chk_customer_segment
        CHECK (
            customer_segment IN ('Standard', 'Premium', 'Private')
        ),

    CONSTRAINT chk_customer_risk_score
        CHECK (risk_score BETWEEN 1 AND 100),

    CONSTRAINT chk_customer_gender
        CHECK (gender IN ('Male', 'Female'))
);

CREATE TABLE branches (
    branch_id VARCHAR(4) PRIMARY KEY,
    branch_name VARCHAR(150) NOT NULL,
    city VARCHAR(100) NOT NULL,
    region VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    opening_date DATE NOT NULL,
    manager_name VARCHAR(150) NOT NULL
);

CREATE TABLE accounts (
    account_id VARCHAR(8) PRIMARY KEY,
    customer_id VARCHAR(7) NOT NULL,
    branch_id VARCHAR(4) NOT NULL,
    account_type VARCHAR(20) NOT NULL,
    balance NUMERIC(14, 2) NOT NULL,
    opening_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL,

    CONSTRAINT fk_accounts_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),

    CONSTRAINT fk_accounts_branch
        FOREIGN KEY (branch_id)
        REFERENCES branches(branch_id),

    CONSTRAINT chk_account_type
        CHECK (
            account_type IN ('Checking', 'Savings', 'Business')
        ),

    CONSTRAINT chk_account_balance
        CHECK (balance >= 0),

    CONSTRAINT chk_account_status
        CHECK (
            status IN ('Active', 'Inactive', 'Closed')
        )
);

CREATE TABLE loans (
    loan_id VARCHAR(7) PRIMARY KEY,
    customer_id VARCHAR(7) NOT NULL,
    branch_id VARCHAR(4) NOT NULL,
    loan_type VARCHAR(20) NOT NULL,
    loan_amount NUMERIC(14, 2) NOT NULL,
    interest_rate NUMERIC(5, 2) NOT NULL,
    term_months INTEGER NOT NULL,
    start_date DATE NOT NULL,
    loan_status VARCHAR(20) NOT NULL,

    CONSTRAINT fk_loans_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),

    CONSTRAINT fk_loans_branch
        FOREIGN KEY (branch_id)
        REFERENCES branches(branch_id),

    CONSTRAINT chk_loan_type
        CHECK (
            loan_type IN ('Personal', 'Mortgage', 'Auto', 'Business')
        ),

    CONSTRAINT chk_loan_amount
        CHECK (loan_amount > 0),

    CONSTRAINT chk_loan_interest_rate
        CHECK (interest_rate > 0 AND interest_rate <= 100),

    CONSTRAINT chk_loan_term
        CHECK (term_months > 0),

    CONSTRAINT chk_loan_status
        CHECK (
            loan_status IN ('Active', 'Paid', 'Defaulted')
        )
);

CREATE TABLE transactions (
    transaction_id VARCHAR(10) PRIMARY KEY,
    account_id VARCHAR(8) NOT NULL,
    transaction_date DATE NOT NULL,
    transaction_type VARCHAR(30) NOT NULL,
    amount NUMERIC(14, 2) NOT NULL,
    channel VARCHAR(20) NOT NULL,
    merchant_category VARCHAR(50),
    transaction_status VARCHAR(20) NOT NULL,

    CONSTRAINT fk_transactions_account
        FOREIGN KEY (account_id)
        REFERENCES accounts(account_id),

    CONSTRAINT chk_transaction_type
        CHECK (
            transaction_type IN (
                'Card Payment',
                'Bank Transfer',
                'Cash Withdrawal',
                'Direct Debit',
                'Deposit'
            )
        ),

    CONSTRAINT chk_transaction_amount
        CHECK (amount > 0),

    CONSTRAINT chk_transaction_channel
        CHECK (
            channel IN ('Mobile', 'Web', 'ATM', 'Branch', 'POS')
        ),

    CONSTRAINT chk_transaction_status
        CHECK (
            transaction_status IN ('Completed', 'Failed', 'Pending')
        ),

    CONSTRAINT chk_transaction_type_channel
        CHECK (
            (transaction_type = 'Card Payment'
                AND channel IN ('POS', 'Web', 'Mobile'))
            OR
            (transaction_type = 'Cash Withdrawal'
                AND channel = 'ATM')
            OR
            (transaction_type = 'Bank Transfer'
                AND channel IN ('Mobile', 'Web', 'Branch'))
            OR
            (transaction_type = 'Direct Debit'
                AND channel IN ('Web', 'Mobile'))
            OR
            (transaction_type = 'Deposit'
                AND channel IN ('ATM', 'Branch'))
        )
);