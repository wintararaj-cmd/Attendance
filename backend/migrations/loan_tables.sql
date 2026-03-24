-- Migration: Add Employee Loan/Advance Tables
-- This migration creates tables for managing employee loans and advances
-- with EMI deduction from salary

-- Table: Employee Loan/Advance Records
CREATE TABLE IF NOT EXISTS employee_loans (
    id VARCHAR(255) PRIMARY KEY,
    employee_id VARCHAR(255) NOT NULL,
    loan_type VARCHAR(50) NOT NULL,
    loan_amount NUMERIC(12, 2) NOT NULL,
    emi_amount NUMERIC(12, 2) NOT NULL,
    total_emis INTEGER NOT NULL DEFAULT 1,
    remaining_emis INTEGER NOT NULL DEFAULT 1,
    start_date DATE NOT NULL,
    end_date DATE,
    reason TEXT,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);

-- Table: Loan EMI Payment Records
CREATE TABLE IF NOT EXISTS loan_payments (
    id VARCHAR(255) PRIMARY KEY,
    loan_id VARCHAR(255) NOT NULL,
    employee_id VARCHAR(255) NOT NULL,
    payment_date DATE NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    month INTEGER NOT NULL,
    year INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'paid',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (loan_id) REFERENCES employee_loans(id) ON DELETE CASCADE,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);

-- Add index for faster queries
CREATE INDEX IF NOT EXISTS idx_employee_loans_employee_id ON employee_loans(employee_id);
CREATE INDEX IF NOT EXISTS idx_employee_loans_status ON employee_loans(status);
CREATE INDEX IF NOT EXISTS idx_loan_payments_loan_id ON loan_payments(loan_id);
CREATE INDEX IF NOT EXISTS idx_loan_payments_employee_id ON loan_payments(employee_id);
CREATE INDEX IF NOT EXISTS idx_loan_payments_month_year ON loan_payments(month, year);
