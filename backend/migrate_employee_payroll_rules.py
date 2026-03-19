"""
Database Migration Script: Add Employee Payroll Rules Table
Creates a new table for storing customizable payroll rules per employee
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

try:
    from app.core.database import DATABASE_URL
except:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./attendance.db")

# Fix postgres:// to postgresql://
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def run_migration():
    print("Starting migration: Add Employee Payroll Rules Table...")
    print(f"Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL.split('://')[1] if '://' in DATABASE_URL else 'unknown'}")
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Check if table already exists
            if "sqlite" in DATABASE_URL:
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='employee_payroll_rules'"))
                table_exists = result.fetchone() is not None
            else:
                result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'employee_payroll_rules')"))
                table_exists = result.fetchone()[0]
            
            if table_exists:
                print("\n[SKIP] Table 'employee_payroll_rules' already exists.")
                return
            
            print("\nStep 1: Creating employee_payroll_rules table...")
            
            # Create the table
            if "sqlite" in DATABASE_URL:
                create_table_sql = """
                CREATE TABLE employee_payroll_rules (
                    id TEXT PRIMARY KEY,
                    employee_id TEXT UNIQUE NOT NULL,
                    
                    -- Attendance-based Allowance Rules
                    allowance_full_days INTEGER DEFAULT 21,
                    allowance_half_days INTEGER DEFAULT 15,
                    allowance_full_multiplier NUMERIC(5, 2) DEFAULT 100.0,
                    allowance_half_multiplier NUMERIC(5, 2) DEFAULT 50.0,
                    allowance_none_multiplier NUMERIC(5, 2) DEFAULT 0.0,
                    
                    -- Overtime Rules
                    standard_working_hours NUMERIC(5, 2) DEFAULT 8.0,
                    ot_rate_multiplier NUMERIC(5, 2) DEFAULT 1.5,
                    ot_weekend_multiplier NUMERIC(5, 2) DEFAULT 2.0,
                    ot_holiday_multiplier NUMERIC(5, 2) DEFAULT 2.5,
                    
                    -- PF (Provident Fund) Rules
                    pf_employee_rate NUMERIC(5, 2) DEFAULT 12.0,
                    pf_employer_rate NUMERIC(5, 2) DEFAULT 12.0,
                    pf_wage_ceiling NUMERIC(12, 2) DEFAULT 15000.0,
                    
                    -- ESI (Employee State Insurance) Rules
                    esi_employee_rate NUMERIC(5, 2) DEFAULT 0.75,
                    esi_employer_rate NUMERIC(5, 2) DEFAULT 3.25,
                    esi_wage_ceiling NUMERIC(12, 2) DEFAULT 21000.0,
                    
                    -- Professional Tax Rules
                    pt_threshold NUMERIC(12, 2) DEFAULT 10000.0,
                    pt_amount NUMERIC(12, 2) DEFAULT 200.0,
                    
                    -- Welfare Fund Rules
                    welfare_deduction NUMERIC(12, 2) DEFAULT 3.0,
                    
                    -- Staff-specific: Days in month for calculation
                    staff_month_days INTEGER DEFAULT 30,
                    
                    -- Timestamps
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP,
                    
                    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
                )
                """
            else:
                # PostgreSQL version
                create_table_sql = """
                CREATE TABLE employee_payroll_rules (
                    id VARCHAR(36) PRIMARY KEY,
                    employee_id VARCHAR(36) UNIQUE NOT NULL,
                    
                    -- Attendance-based Allowance Rules
                    allowance_full_days INTEGER DEFAULT 21,
                    allowance_half_days INTEGER DEFAULT 15,
                    allowance_full_multiplier NUMERIC(5, 2) DEFAULT 100.0,
                    allowance_half_multiplier NUMERIC(5, 2) DEFAULT 50.0,
                    allowance_none_multiplier NUMERIC(5, 2) DEFAULT 0.0,
                    
                    -- Overtime Rules
                    standard_working_hours NUMERIC(5, 2) DEFAULT 8.0,
                    ot_rate_multiplier NUMERIC(5, 2) DEFAULT 1.5,
                    ot_weekend_multiplier NUMERIC(5, 2) DEFAULT 2.0,
                    ot_holiday_multiplier NUMERIC(5, 2) DEFAULT 2.5,
                    
                    -- PF (Provident Fund) Rules
                    pf_employee_rate NUMERIC(5, 2) DEFAULT 12.0,
                    pf_employer_rate NUMERIC(5, 2) DEFAULT 12.0,
                    pf_wage_ceiling NUMERIC(12, 2) DEFAULT 15000.0,
                    
                    -- ESI (Employee State Insurance) Rules
                    esi_employee_rate NUMERIC(5, 2) DEFAULT 0.75,
                    esi_employer_rate NUMERIC(5, 2) DEFAULT 3.25,
                    esi_wage_ceiling NUMERIC(12, 2) DEFAULT 21000.0,
                    
                    -- Professional Tax Rules
                    pt_threshold NUMERIC(12, 2) DEFAULT 10000.0,
                    pt_amount NUMERIC(12, 2) DEFAULT 200.0,
                    
                    -- Welfare Fund Rules
                    welfare_deduction NUMERIC(12, 2) DEFAULT 3.0,
                    
                    -- Staff-specific: Days in month for calculation
                    staff_month_days INTEGER DEFAULT 30,
                    
                    -- Timestamps
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE,
                    
                    CONSTRAINT fk_employee FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
                )
                """
            
            conn.execute(text(create_table_sql))
            conn.commit()
            print("   [OK] Created employee_payroll_rules table")
            
            # Create index on employee_id for faster lookups
            print("\nStep 2: Creating index on employee_id...")
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_payroll_rules_employee_id ON employee_payroll_rules(employee_id)"))
            conn.commit()
            print("   [OK] Created index on employee_id")
        
        print("\n[SUCCESS] Migration completed successfully!")
        print("\nSummary:")
        print(f"   - Created 'employee_payroll_rules' table with 20 configurable fields")
        print(f"   - Added index on employee_id for faster lookups")
        print(f"\nNew Features Enabled:")
        print(f"   * Customizable attendance allowance thresholds per employee")
        print(f"   * Customizable PF rates and wage ceiling per employee")
        print(f"   * Customizable ESI rates and wage ceiling per employee")
        print(f"   * Customizable overtime multipliers per employee")
        print(f"   * Customizable professional tax rules per employee")
        print(f"   * Customizable welfare fund deduction per employee")
        
    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    run_migration()
