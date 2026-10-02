-- ============================================================
-- Banking Data Management Project
-- SQL Analytics & BI Layer
-- ============================================================

-- 1. Executive KPI Summary

SELECT
    (SELECT COUNT(*) FROM customers) AS total_customers,
    (SELECT COUNT(*) FROM accounts) AS total_accounts,
    (SELECT COUNT(*) FROM branches) AS total_branches,
    (SELECT COUNT(*) FROM loans) AS total_loans,
    (SELECT COUNT(*) FROM transactions) AS total_transactions,
    (SELECT ROUND(SUM(balance), 2) FROM accounts) AS total_account_balance,
    (SELECT ROUND(SUM(loan_amount), 2) FROM loans) AS total_loan_amount,
    (SELECT ROUND(SUM(amount), 2) FROM transactions) AS total_transaction_amount;


    -- 2. Customer Segment Analysis

SELECT
    customer_segment,
    COUNT(*) AS total_customers,
    ROUND(AVG(annual_income), 2) AS avg_annual_income,
    ROUND(AVG(risk_score), 2) AS avg_risk_score
FROM customers
GROUP BY customer_segment
ORDER BY total_customers DESC;


-- 3. Account Portfolio Analysis

SELECT
    account_type,
    COUNT(*) AS total_accounts,
    ROUND(SUM(balance), 2) AS total_balance,
    ROUND(AVG(balance), 2) AS avg_balance
FROM accounts
GROUP BY account_type
ORDER BY total_balance DESC;


-- 4. Loan Portfolio Analysis

SELECT
    loan_type,
    COUNT(*) AS total_loans,
    ROUND(SUM(loan_amount), 2) AS total_loan_amount,
    ROUND(AVG(loan_amount), 2) AS avg_loan_amount,
    ROUND(AVG(interest_rate), 2) AS avg_interest_rate
FROM loans
GROUP BY loan_type
ORDER BY total_loan_amount DESC;


-- 5. Loan Status Analysis

SELECT
    loan_status,
    COUNT(*) AS total_loans,
    ROUND(SUM(loan_amount), 2) AS total_loan_amount,
    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
        2
    ) AS loan_share_pct
FROM loans
GROUP BY loan_status
ORDER BY total_loans DESC;


-- 6. Transaction Type Analysis

SELECT
    transaction_type,
    COUNT(*) AS total_transactions,
    ROUND(SUM(amount), 2) AS total_transaction_amount,
    ROUND(AVG(amount), 2) AS avg_transaction_amount,
    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
        2
    ) AS transaction_share_pct
FROM transactions
GROUP BY transaction_type
ORDER BY total_transaction_amount DESC;


-- 7. Monthly Transaction Trend

SELECT
    DATE_TRUNC('month', transaction_date)::DATE AS transaction_month,
    COUNT(*) AS total_transactions,
    ROUND(SUM(amount), 2) AS total_transaction_amount,
    ROUND(AVG(amount), 2) AS avg_transaction_amount
FROM transactions
GROUP BY transaction_month
ORDER BY transaction_month;


-- 8. Branch Account Performance

SELECT
    b.branch_id,
    b.branch_name,
    b.city,
    b.region,
    COUNT(a.account_id) AS total_accounts,
    ROUND(SUM(a.balance), 2) AS total_account_balance,
    ROUND(AVG(a.balance), 2) AS avg_account_balance
FROM branches b
LEFT JOIN accounts a
    ON b.branch_id = a.branch_id
GROUP BY
    b.branch_id,
    b.branch_name,
    b.city,
    b.region
ORDER BY total_account_balance DESC;


-- 9. Branch Loan Performance

SELECT
    b.branch_id,
    b.branch_name,
    b.city,
    b.region,
    COUNT(l.loan_id) AS total_loans,
    ROUND(SUM(l.loan_amount), 2) AS total_loan_amount,
    ROUND(AVG(l.loan_amount), 2) AS avg_loan_amount,
    ROUND(AVG(l.interest_rate), 2) AS avg_interest_rate
FROM branches b
LEFT JOIN loans l
    ON b.branch_id = l.branch_id
GROUP BY
    b.branch_id,
    b.branch_name,
    b.city,
    b.region
ORDER BY total_loan_amount DESC;


-- 10. Transaction Channel Analysis

SELECT
    channel,
    COUNT(*) AS total_transactions,
    ROUND(SUM(amount), 2) AS total_transaction_amount,
    ROUND(AVG(amount), 2) AS avg_transaction_amount,
    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
        2
    ) AS transaction_share_pct
FROM transactions
GROUP BY channel
ORDER BY total_transactions DESC;


-- 11. Transaction Status Analysis

SELECT
    transaction_status,
    COUNT(*) AS total_transactions,
    ROUND(SUM(amount), 2) AS total_transaction_amount,
    ROUND(AVG(amount), 2) AS avg_transaction_amount,
    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
        2
    ) AS transaction_share_pct
FROM transactions
GROUP BY transaction_status
ORDER BY total_transactions DESC;


-- 12. Customer Risk Distribution

SELECT
    CASE
        WHEN risk_score BETWEEN 1 AND 30 THEN 'Low Risk'
        WHEN risk_score BETWEEN 31 AND 70 THEN 'Medium Risk'
        WHEN risk_score BETWEEN 71 AND 100 THEN 'High Risk'
    END AS risk_category,
    COUNT(*) AS total_customers,
    ROUND(AVG(risk_score), 2) AS avg_risk_score,
    ROUND(AVG(annual_income), 2) AS avg_annual_income,
    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
        2
    ) AS customer_share_pct
FROM customers
GROUP BY risk_category
ORDER BY avg_risk_score;


-- 13. Loan Exposure by Customer Risk Category

SELECT
    CASE
        WHEN c.risk_score BETWEEN 1 AND 30 THEN 'Low Risk'
        WHEN c.risk_score BETWEEN 31 AND 70 THEN 'Medium Risk'
        WHEN c.risk_score BETWEEN 71 AND 100 THEN 'High Risk'
    END AS risk_category,
    COUNT(l.loan_id) AS total_loans,
    ROUND(SUM(l.loan_amount), 2) AS total_loan_amount,
    ROUND(AVG(l.loan_amount), 2) AS avg_loan_amount,
    ROUND(AVG(l.interest_rate), 2) AS avg_interest_rate
FROM customers c
INNER JOIN loans l
    ON c.customer_id = l.customer_id
GROUP BY risk_category
ORDER BY total_loan_amount DESC;


