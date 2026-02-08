"""
Fix Salary Structure Schema Mismatch
Removes extra columns that don't exist in the model
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
    print(f"[OK] Using app database configuration")
except ImportError:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./attendance.db")
    print(f"[WARN] Using fallback database URL")

# Ensure SQLAlchemy compatibility
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def fix_salary_schema():
    """Remove extra columns that don't exist in the model"""
    print("[INFO] Fixing salary_structures schema...")
    
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    with engine.connect() as conn:
        # Check if salary_structures table exists
        if 'salary_structures' not in inspector.get_table_names():
            print("[ERROR] salary_structures table does not exist!")
            return False
        
        # Get existing columns
        existing_columns = [col['name'] for col in inspector.get_columns('salary_structures')]
        print(f"[INFO] Existing columns: {', '.join(existing_columns)}")
        
        # Columns that should NOT exist (not in the model)
        columns_to_remove = ['name', 'hra_percentage']
        
        removed_count = 0
        for column_name in columns_to_remove:
            if column_name in existing_columns:
                try:
                    print(f"  [-] Removing column: {column_name}")
                    sql = f"ALTER TABLE salary_structures DROP COLUMN IF EXISTS {column_name}"
                    conn.execute(text(sql))
                    conn.commit()
                    removed_count += 1
                    print(f"  [OK] Removed: {column_name}")
                except Exception as e:
                    print(f"  [WARN] Could not remove {column_name}: {str(e)}")
            else:
                print(f"  [SKIP] Column {column_name} doesn't exist")
        
        print(f"\n[SUCCESS] Schema fix completed! Removed {removed_count} columns.")
        return True

if __name__ == "__main__":
    try:
        print("=" * 60)
        print("FIX SALARY STRUCTURE SCHEMA")
        print("=" * 60)
        success = fix_salary_schema()
        if success:
            print("\n" + "=" * 60)
            print("[SUCCESS] SCHEMA FIX SUCCESSFUL!")
            print("=" * 60)
            print("\nNext steps:")
            print("1. Restart your backend server")
            print("2. Try saving the salary configuration again")
            sys.exit(0)
        else:
            print("\n" + "=" * 60)
            print("[FAILED] SCHEMA FIX FAILED!")
            print("=" * 60)
            sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Schema fix error: {str(e)}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        sys.exit(1)
