# -*- coding: utf-8 -*-
"""
Check salary_structures table schema
"""
import os
import sys
import io

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from sqlalchemy import create_engine, inspect, text

# Add backend directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from app.core.database import DATABASE_URL
    print(f"✅ Using app database configuration")
except ImportError:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./attendance.db")
    print(f"⚠️ Using fallback database URL")

# Ensure SQLAlchemy compatibility
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print(f"\n📊 Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL.split('://')[1]}")

engine = create_engine(DATABASE_URL)
inspector = inspect(engine)

print("\n" + "="*60)
print("SALARY_STRUCTURES TABLE SCHEMA")
print("="*60)

if 'salary_structures' in inspector.get_table_names():
    columns = inspector.get_columns('salary_structures')
    print(f"\n✅ Table exists with {len(columns)} columns:\n")
    
    for col in columns:
        print(f"  - {col['name']:<30} {str(col['type']):<20} {'NULL' if col['nullable'] else 'NOT NULL'}")
    
    # Check for specific required columns
    column_names = [col['name'] for col in columns]
    required_columns = [
        'basic_salary', 'hra', 'conveyance_allowance', 'medical_allowance',
        'special_allowance', 'education_allowance', 'other_allowance',
        'pf_employee', 'pf_employer', 'esi_employee', 'esi_employer',
        'professional_tax', 'tds', 'bonus', 'incentive',
        'is_pf_applicable', 'is_esi_applicable'
    ]
    
    print("\n" + "="*60)
    print("COLUMN CHECK")
    print("="*60 + "\n")
    
    missing = []
    for col in required_columns:
        if col in column_names:
            print(f"  ✅ {col}")
        else:
            print(f"  ❌ {col} - MISSING!")
            missing.append(col)
    
    if missing:
        print(f"\n⚠️  WARNING: {len(missing)} columns are missing!")
        print("Run the migration script to add them:")
        print("  python migrate_db.py")
    else:
        print("\n✅ All required columns are present!")
    
    # Check row count
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM salary_structures"))
        count = result.scalar()
        print(f"\n📊 Total salary records: {count}")
        
else:
    print("\n❌ Table 'salary_structures' does not exist!")
    print("Run the migration script to create it:")
    print("  python migrate_db.py")

print("\n" + "="*60)
