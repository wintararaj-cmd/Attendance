"""
Migration script to add new allowance columns to salary_structures and payrolls tables.
This adds: casting_allowance, ttb_allowance, plating_allowance

Run this script to add the new allowance columns to your existing database.
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text, inspect
from app.core.database import engine, SessionLocal
from app.models.models import Base, SalaryStructure, Payroll

def check_column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column already exists in a table."""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def add_allowance_columns():
    """Add new allowance columns to salary_structures and payrolls tables."""
    
    print("=" * 60)
    print("Migration: Adding New Allowance Columns")
    print("=" * 60)
    
    # Columns to add to salary_structures table
    salary_structure_columns = [
        ("casting_allowance", "NUMERIC(12, 2) DEFAULT 0.0"),
        ("ttb_allowance", "NUMERIC(12, 2) DEFAULT 0.0"),
        ("plating_allowance", "NUMERIC(12, 2) DEFAULT 0.0"),
    ]
    
    # Columns to add to payrolls table
    payroll_columns = [
        ("casting_allowance", "NUMERIC(12, 2) DEFAULT 0.0"),
        ("ttb_allowance", "NUMERIC(12, 2) DEFAULT 0.0"),
        ("plating_allowance", "NUMERIC(12, 2) DEFAULT 0.0"),
    ]
    
    with engine.connect() as conn:
        # Add columns to salary_structures table
        print("\n[1] Checking salary_structures table...")
        for col_name, col_type in salary_structure_columns:
            if check_column_exists("salary_structures", col_name):
                print(f"  - Column '{col_name}' already exists in salary_structures")
            else:
                try:
                    sql = f"ALTER TABLE salary_structures ADD COLUMN {col_name} {col_type}"
                    conn.execute(text(sql))
                    conn.commit()
                    print(f"  + Added column '{col_name}' to salary_structures")
                except Exception as e:
                    print(f"  ! Error adding column '{col_name}' to salary_structures: {e}")
        
        # Add columns to payrolls table
        print("\n[2] Checking payrolls table...")
        for col_name, col_type in payroll_columns:
            if check_column_exists("payrolls", col_name):
                print(f"  - Column '{col_name}' already exists in payrolls")
            else:
                try:
                    sql = f"ALTER TABLE payrolls ADD COLUMN {col_name} {col_type}"
                    conn.execute(text(sql))
                    conn.commit()
                    print(f"  + Added column '{col_name}' to payrolls")
                except Exception as e:
                    print(f"  ! Error adding column '{col_name}' to payrolls: {e}")
    
    print("\n" + "=" * 60)
    print("Migration completed!")
    print("=" * 60)
    
    # Verify the columns were added
    print("\n[3] Verifying columns...")
    print("\n  salary_structures columns:")
    inspector = inspect(engine)
    for col in inspector.get_columns("salary_structures"):
        if col['name'] in ['casting_allowance', 'ttb_allowance', 'plating_allowance', 'washing_allowance', 'other_allowances']:
            print(f"    - {col['name']}: {col['type']}")
    
    print("\n  payrolls columns:")
    for col in inspector.get_columns("payrolls"):
        if col['name'] in ['casting_allowance', 'ttb_allowance', 'plating_allowance', 'washing_allowance', 'other_allowances']:
            print(f"    - {col['name']}: {col['type']}")

if __name__ == "__main__":
    add_allowance_columns()
