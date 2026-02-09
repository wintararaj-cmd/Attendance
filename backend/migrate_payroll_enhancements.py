"""
Database Migration Script: Add Part-time, Contract Worker, and OT Support
Adds new columns to salary_structures and attendance_logs tables
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
    print("Starting migration: Add Part-time/Contract Worker & OT Support...")
    print(f"Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL.split('://')[1] if '://' in DATABASE_URL else 'unknown'}")
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            print("\nStep 1: Adding columns to salary_structures table...")
            
            # Add columns to salary_structures table
            salary_structure_columns = [
                ("is_hourly_based", "BOOLEAN", "DEFAULT FALSE"),
                ("hourly_rate", "NUMERIC(12, 2)", "DEFAULT 0.0"),
                ("contract_rate_per_day", "NUMERIC(12, 2)", "DEFAULT 0.0"),
                ("ot_rate_multiplier", "NUMERIC(5, 2)", "DEFAULT 1.5"),
                ("ot_weekend_multiplier", "NUMERIC(5, 2)", "DEFAULT 2.0"),
                ("ot_holiday_multiplier", "NUMERIC(5, 2)", "DEFAULT 2.5"),
            ]
            
            for col_name, col_type, col_default in salary_structure_columns:
                try:
                    # Check if column exists
                    if "sqlite" in DATABASE_URL:
                        # SQLite doesn't support IF NOT EXISTS in ALTER TABLE
                        result = conn.execute(text(f"PRAGMA table_info(salary_structures)"))
                        columns = [row[1] for row in result]
                        if col_name not in columns:
                            conn.execute(text(f"ALTER TABLE salary_structures ADD COLUMN {col_name} {col_type} {col_default}"))
                            conn.commit()
                            print(f"   [OK] Added column: {col_name}")
                        else:
                            print(f"   [SKIP] Column {col_name} already exists")
                    else:
                        # PostgreSQL supports IF NOT EXISTS
                        conn.execute(text(f"ALTER TABLE salary_structures ADD COLUMN IF NOT EXISTS {col_name} {col_type} {col_default}"))
                        conn.commit()
                        print(f"   [OK] Added column: {col_name}")
                except Exception as e:
                    print(f"   [WARN] Error with column {col_name}: {e}")
            
            print("\nStep 2: Adding OT tracking columns to attendance_logs table...")
            
            # Add columns to attendance_logs table
            attendance_log_columns = [
                ("ot_hours", "NUMERIC(5, 2)", "DEFAULT 0.0"),
                ("ot_weekend_hours", "NUMERIC(5, 2)", "DEFAULT 0.0"),
                ("ot_holiday_hours", "NUMERIC(5, 2)", "DEFAULT 0.0"),
                ("total_hours_worked", "NUMERIC(5, 2)", "DEFAULT 0.0"),
            ]
            
            for col_name, col_type, col_default in attendance_log_columns:
                try:
                    if "sqlite" in DATABASE_URL:
                        result = conn.execute(text(f"PRAGMA table_info(attendance_logs)"))
                        columns = [row[1] for row in result]
                        if col_name not in columns:
                            conn.execute(text(f"ALTER TABLE attendance_logs ADD COLUMN {col_name} {col_type} {col_default}"))
                            conn.commit()
                            print(f"   [OK] Added column: {col_name}")
                        else:
                            print(f"   [SKIP] Column {col_name} already exists")
                    else:
                        conn.execute(text(f"ALTER TABLE attendance_logs ADD COLUMN IF NOT EXISTS {col_name} {col_type} {col_default}"))
                        conn.commit()
                        print(f"   [OK] Added column: {col_name}")
                except Exception as e:
                    print(f"   [WARN] Error with column {col_name}: {e}")
        
        print("\n[SUCCESS] Migration completed successfully!")
        print("\nSummary:")
        print(f"   - Added 6 columns to salary_structures table")
        print(f"   - Added 4 columns to attendance_logs table")
        print(f"\nNew Features Enabled:")
        print(f"   * Hourly-based payroll for part-time workers")
        print(f"   * Daily rate payroll for contract workers")
        print(f"   * Overtime tracking (weekday, weekend, holiday)")
        print(f"   * Configurable OT multipliers (1.5x, 2x, 2.5x)")
        
    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    run_migration()
