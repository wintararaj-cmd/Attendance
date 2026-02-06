"""
Migration Script: Update Salary Structure Table
Adds comprehensive salary components matching Indian payroll standards
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Add backend directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if 'backend' in current_dir:
    sys.path.insert(0, current_dir)
else:
    backend_dir = os.path.join(current_dir, 'backend')
    if os.path.exists(backend_dir):
        sys.path.insert(0, backend_dir)

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import ProgrammingError

# Import database URL
try:
    from app.core.database import DATABASE_URL
    print(f"✅ Using app database configuration")
except ImportError:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./attendance.db")
    print(f"⚠️ Using fallback database URL")

# Ensure SQLAlchemy compatibility
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def migrate_salary_structure():
    """Add new salary structure columns"""
    print("🔄 Starting salary structure migration...")
    
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    with engine.connect() as conn:
        # Check if salary_structures table exists
        if 'salary_structures' not in inspector.get_table_names():
            print("❌ Error: salary_structures table does not exist!")
            return False
        
        # Get existing columns
        existing_columns = [col['name'] for col in inspector.get_columns('salary_structures')]
        print(f"📋 Existing columns: {', '.join(existing_columns)}")
        
        # New columns to add
        new_columns = {
            # Rename/Add allowances
            'hra': 'NUMERIC(12, 2) DEFAULT 0.0',
            'conveyance_allowance': 'NUMERIC(12, 2) DEFAULT 0.0',
            'medical_allowance': 'NUMERIC(12, 2) DEFAULT 0.0',
            'education_allowance': 'NUMERIC(12, 2) DEFAULT 0.0',
            'other_allowance': 'NUMERIC(12, 2) DEFAULT 0.0',
            
            # Update deduction columns
            'pf_employee': 'NUMERIC(12, 2) DEFAULT 0.0',
            'pf_employer': 'NUMERIC(12, 2) DEFAULT 0.0',
            'esi_employee': 'NUMERIC(12, 2) DEFAULT 0.0',
            'esi_employer': 'NUMERIC(12, 2) DEFAULT 0.0',
            'tds': 'NUMERIC(12, 2) DEFAULT 0.0',
            
            # Benefits
            'bonus': 'NUMERIC(12, 2) DEFAULT 0.0',
            'incentive': 'NUMERIC(12, 2) DEFAULT 0.0',
            
            # Settings
            'is_pf_applicable': 'BOOLEAN DEFAULT TRUE',
            'is_esi_applicable': 'BOOLEAN DEFAULT FALSE',
            
            # Timestamps
            'created_at': 'TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP',
            'updated_at': 'TIMESTAMP WITH TIME ZONE'
        }
        
        added_count = 0
        
        # Add new columns
        for column_name, column_type in new_columns.items():
            if column_name not in existing_columns:
                try:
                    sql = f"ALTER TABLE salary_structures ADD COLUMN {column_name} {column_type}"
                    print(f"  ➕ Adding column: {column_name}")
                    conn.execute(text(sql))
                    conn.commit()
                    added_count += 1
                    print(f"  ✅ Added: {column_name}")
                except ProgrammingError as e:
                    print(f"  ⚠️ Warning: Could not add {column_name}: {str(e)}")
            else:
                print(f"  ⏭️ Skipping: {column_name} (already exists)")
        
        # Migrate old column data if exists
        if 'hra_allowance' in existing_columns and 'hra' in [col['name'] for col in inspector.get_columns('salary_structures')]:
            try:
                print("\n  🔄 Migrating hra_allowance to hra...")
                conn.execute(text("UPDATE salary_structures SET hra = hra_allowance WHERE hra_allowance IS NOT NULL"))
                conn.commit()
                print("  ✅ Data migrated")
            except Exception as e:
                print(f"  ⚠️ Migration warning: {e}")
        
        if 'pf_deduction' in existing_columns and 'pf_employee' in [col['name'] for col in inspector.get_columns('salary_structures')]:
            try:
                print("  🔄 Migrating pf_deduction to pf_employee...")
                conn.execute(text("UPDATE salary_structures SET pf_employee = pf_deduction WHERE pf_deduction IS NOT NULL"))
                conn.commit()
                print("  ✅ Data migrated")
            except Exception as e:
                print(f"  ⚠️ Migration warning: {e}")
        
        print(f"\n✨ Migration completed! Added {added_count} new columns.")
        return True

if __name__ == "__main__":
    try:
        print("=" * 60)
        print("🚀 SALARY STRUCTURE MIGRATION")
        print("=" * 60)
        success = migrate_salary_structure()
        if success:
            print("\n" + "=" * 60)
            print("✅ MIGRATION SUCCESSFUL!")
            print("=" * 60)
            sys.exit(0)
        else:
            print("\n" + "=" * 60)
            print("❌ MIGRATION FAILED!")
            print("=" * 60)
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Migration error: {str(e)}")
        import traceback
        print("\n📋 Full traceback:")
        traceback.print_exc()
        sys.exit(1)
