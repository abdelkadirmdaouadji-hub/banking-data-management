-- ============================================================
-- Banking Data Management Project
-- PostgreSQL Views for Power BI
-- ============================================================

-- 1. Customer BI View

CREATE OR REPLACE VIEW vw_customer_profile AS
SELECT
    customer_id,
    first_name,
    last_name,
    birth_date,
    gender,
    city,
    country,
    annual_income,
    customer_segment,
    join_date,
    risk_score,
    CASE
        WHEN risk_score BETWEEN 1 AND 30 THEN 'Low Risk'
        WHEN risk_score BETWEEN 31 AND 70 THEN 'Medium Risk'
        WHEN risk_score BETWEEN 71 AND 100 THEN 'High Risk'
    END AS risk_category
FROM customers;


-- 2. Account BI View

CREATE OR REPLACE VIEW vw_account_portfolio AS
SELECT
    a.account_id,
    a.customer_id,
    a.branch_id,
    a.account_type,
    a.balance,
    a.opening_date,
    a.status AS account_status,
    c.customer_segment,
    c.risk_score,
    c.risk_category,
    b.branch_name,
    b.city AS branch_city,
    b.region AS branch_region
FROM accounts a
INNER JOIN vw_customer_profile c
    ON a.customer_id = c.customer_id
INNER JOIN branches b
    ON a.branch_id = b.branch_id;


-- 3. Loan BI View

CREATE OR REPLACE VIEW vw_loan_portfolio AS
SELECT
    l.loan_id,
    l.customer_id,
    l.branch_id,
    l.loan_type,
    l.loan_amount,
    l.interest_rate,
    l.term_months,
    l.start_date,
    l.loan_status,
    c.customer_segment,
    c.risk_score,
    c.risk_category,
    b.branch_name,
    b.city AS branch_city,
    b.region AS branch_region
FROM loans l
INNER JOIN vw_customer_profile c
    ON l.customer_id = c.customer_id
INNER JOIN branches b
    ON l.branch_id = b.branch_id;


-- 4. Transaction BI View

CREATE OR REPLACE VIEW vw_transaction_details AS
SELECT
    t.transaction_id,
    t.account_id,
    t.transaction_date,
    t.transaction_type,
    t.amount,
    t.channel,
    t.merchant_category,
    t.transaction_status,
    a.customer_id,
    a.branch_id,
    a.account_type,
    a.account_status,
    c.customer_segment,
    c.risk_score,
    c.risk_category,
    b.branch_name,
    b.city AS branch_city,
    b.region AS branch_region
FROM transactions t
INNER JOIN vw_account_portfolio a
    ON t.account_id = a.account_id
INNER JOIN vw_customer_profile c
    ON a.customer_id = c.customer_id
INNER JOIN branches b
    ON a.branch_id = b.branch_id;


-- 5. Branch Performance BI View

CREATE OR REPLACE VIEW vw_branch_performance AS
WITH account_metrics AS (
    SELECT
        branch_id,
        COUNT(*) AS total_accounts,
        ROUND(SUM(balance), 2) AS total_account_balance,
        ROUND(AVG(balance), 2) AS avg_account_balance
    FROM accounts
    GROUP BY branch_id
),
loan_metrics AS (
    SELECT
        branch_id,
        COUNT(*) AS total_loans,
        ROUND(SUM(loan_amount), 2) AS total_loan_amount,
        ROUND(AVG(loan_amount), 2) AS avg_loan_amount
    FROM loans
    GROUP BY branch_id
)
SELECT
    b.branch_id,
    b.branch_name,
    b.city,
    b.region,
    b.country,
    COALESCE(a.total_accounts, 0) AS total_accounts,
    COALESCE(a.total_account_balance, 0) AS total_account_balance,
    COALESCE(a.avg_account_balance, 0) AS avg_account_balance,
    COALESCE(l.total_loans, 0) AS total_loans,
    COALESCE(l.total_loan_amount, 0) AS total_loan_amount,
    COALESCE(l.avg_loan_amount, 0) AS avg_loan_amount
FROM branches b
LEFT JOIN account_metrics a
    ON b.branch_id = a.branch_id
LEFT JOIN loan_metrics l
    ON b.branch_id = l.branch_id;

    
     