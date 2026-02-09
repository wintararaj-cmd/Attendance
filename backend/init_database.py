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
    """Initialize database by creating all tables"""
    print("=" * 60)
    print("DATABASE INITIALIZATION")
    print("=" * 60)
    print(f"\nDatabase: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL.split('://')[1] if '://' in DATABASE_URL else 'unknown'}")
    
    try:
        engine = create_engine(DATABASE_URL)
        
        print("\n[1/3] Dropping existing tables (if any)...")
        # Drop all tables in reverse order of dependencies
        try:
            Base.metadata.drop_all(engine)
            print("   [OK] Existing tables dropped")
        except Exception as e:
            print(f"   [INFO] No existing tables to drop: {e}")
        
        print("\n[2/3] Creating all tables from models...")
        Base.metadata.create_all(engine)
        print("   [OK] All tables created successfully")
        
        print("\n[3/3] Verifying table creation...")
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = [
            'admin_users', 'companies', 'departments', 
            'employees', 'attendance_logs', 'salary_structures'
        ]
        
        for table in expected_tables:
            if table in tables:
                columns = [col['name'] for col in inspector.get_columns(table)]
                print(f"   [OK] {table}: {len(columns)} columns")
            else:
                print(f"   [ERROR] {table}: NOT FOUND")
                return False
        
        print("\n" + "=" * 60)
        print("[SUCCESS] Database initialized successfully!")
        print("=" * 60)
        print("\nCreated tables:")
        for table in expected_tables:
            print(f"  - {table}")
        
        print("\nNext steps:")
        print("  1. Create an admin user (if needed)")
        print("  2. Run: python migrate_payroll_enhancements.py")
        print("  3. Start the application")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
