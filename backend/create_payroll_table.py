import os
import sys
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, Numeric, DateTime, ForeignKey, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./attendance.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def create_payroll_table():
    print(f"Connecting to database: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("Creating payrolls table if not exists...")
        sql = """
        CREATE TABLE IF NOT EXISTS payrolls (
            id VARCHAR PRIMARY KEY,
            employee_id VARCHAR REFERENCES employees(id),
            month INTEGER NOT NULL,
            year INTEGER NOT NULL,
            total_days NUMERIC(5, 2) DEFAULT 0.0,
            working_days NUMERIC(5, 2) DEFAULT 0.0,
            present_days NUMERIC(5, 2) DEFAULT 0.0,
            ot_hours NUMERIC(5, 2) DEFAULT 0.0,
            basic_earned NUMERIC(12, 2) DEFAULT 0.0,
            hra_earned NUMERIC(12, 2) DEFAULT 0.0,
            conveyance_earned NUMERIC(12, 2) DEFAULT 0.0,
            washing_allowance NUMERIC(12, 2) DEFAULT 0.0,
            other_allowances NUMERIC(12, 2) DEFAULT 0.0,
            gross_salary NUMERIC(12, 2) DEFAULT 0.0,
            pf_amount NUMERIC(12, 2) DEFAULT 0.0,
            esi_amount NUMERIC(12, 2) DEFAULT 0.0,
            pt_amount NUMERIC(12, 2) DEFAULT 0.0,
            welfare_fund NUMERIC(12, 2) DEFAULT 0.0,
            loan_deduction NUMERIC(12, 2) DEFAULT 0.0,
            total_deductions NUMERIC(12, 2) DEFAULT 0.0,
            net_salary NUMERIC(12, 2) DEFAULT 0.0,
            status VARCHAR DEFAULT 'draft',
            generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        conn.execute(text(sql))
        conn.commit()
        print("Successfully created payrolls table.")

if __name__ == "__main__":
    create_payroll_table()
