# -*- coding: utf-8 -*-
"""
Database Initialization Script
Creates all tables from scratch based on the models
"""
import os
import sys
import io

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add backend directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

# Import database configuration
try:
    from app.core.database import DATABASE_URL, Base
    from app.models.models import (
        AdminUser, Company, Department, Employee, 
        AttendanceLog, SalaryStructure
    )
    print("[OK] Using app database configuration")
except ImportError as e:
    print(f"[ERROR] Could not import models: {e}")
    sys.exit(1)

# Ensure SQLAlchemy compatibility
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def init_database():
    """Initialize database by creating missing tables (SAFE - does not drop existing data)"""
    print("=" * 60)
    print("DATABASE INITIALIZATION (SAFE MODE)")
    print("=" * 60)
    print(f"\nDatabase: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL.split('://')[1] if '://' in DATABASE_URL else 'unknown'}")
    
    try:
        engine = create_engine(DATABASE_URL)
        
        print("\n[1/2] Checking existing tables...")
        from sqlalchemy import inspect
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        print(f"   [INFO] Found {len(existing_tables)} existing tables: {', '.join(existing_tables) if existing_tables else 'none'}")
        
        print("\n[2/2] Creating missing tables (preserving existing data)...")
        # This only creates tables that don't exist - SAFE!
        Base.metadata.create_all(engine, checkfirst=True)
        print("   [OK] All required tables exist")
        
        print("\n[3/3] Verifying table structure...")
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = [
            'admin_users', 'companies', 'departments', 
            'employees', 'attendance_logs', 'salary_structures'
        ]
        
        all_exist = True
        for table in expected_tables:
            if table in tables:
                columns = [col['name'] for col in inspector.get_columns(table)]
                print(f"   [OK] {table}: {len(columns)} columns")
            else:
                print(f"   [ERROR] {table}: NOT FOUND")
                all_exist = False
        
        if not all_exist:
            print("\n[WARNING] Some tables are missing!")
            return False
        
        print("\n" + "=" * 60)
        print("[SUCCESS] Database initialization complete!")
        print("=" * 60)
        print("\n[SAFE MODE] Existing data preserved")
        print("Only missing tables were created")
        
        print("\nNext steps:")
        print("  1. Run: python migrate_payroll_enhancements.py")
        print("  2. Start the application")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
