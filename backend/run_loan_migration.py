"""
Migration script to add employee loan/advance tables
Run this script to create the required database tables for loan management
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base
from app.models.models import EmployeeLoan, LoanPayment
from sqlalchemy import text


def run_migration():
    """Create loan and loan_payments tables"""
    
    # Read the SQL migration file
    sql_file = os.path.join(os.path.dirname(__file__), 'migrations', 'loan_tables.sql')
    
    if os.path.exists(sql_file):
        with open(sql_file, 'r') as f:
            sql_content = f.read()
    else:
        # Inline SQL for PostgreSQL
        sql_content = """
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
"""
    
    # Execute the SQL
    with engine.connect() as conn:
        # Check if tables already exist
        result = conn.execute(text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_name IN ('employee_loans', 'loan_payments')
        """))
        existing_tables = [row[0] for row in result.fetchall()]
        
        if 'employee_loans' in existing_tables and 'loan_payments' in existing_tables:
            print("Loan tables already exist. Skipping migration.")
            return
            
        # Execute the SQL to create tables
        conn.execute(text(sql_content))
        conn.commit()
        print("Successfully created loan tables!")
    
    # Also create ORM tables
    Base.metadata.create_all(bind=engine)
    print("Migration completed successfully!")


if __name__ == "__main__":
    run_migration()
