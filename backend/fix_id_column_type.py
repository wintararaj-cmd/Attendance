"""
Fix Salary Structure ID Column Type
Changes id column from INTEGER to VARCHAR to support UUIDs
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

def fix_id_column_type():
    """Change id column from INTEGER to VARCHAR"""
    print("[INFO] Fixing salary_structures id column type...")
    
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    with engine.connect() as conn:
        # Check if salary_structures table exists
        if 'salary_structures' not in inspector.get_table_names():
            print("[ERROR] salary_structures table does not exist!")
            return False
        
        # Get current id column type
        columns = inspector.get_columns('salary_structures')
        id_column = next((col for col in columns if col['name'] == 'id'), None)
        
        if id_column:
            print(f"[INFO] Current id column type: {id_column['type']}")
        
        try:
            # Step 1: Drop existing data (if any) or backup
            print("[WARN] This will delete existing salary structures data!")
            print("[INFO] Truncating salary_structures table...")
            conn.execute(text("TRUNCATE TABLE salary_structures CASCADE"))
            conn.commit()
            print("[OK] Table truncated")
            
            # Step 2: Drop and recreate id column with correct type
            print("[INFO] Dropping id column...")
            conn.execute(text("ALTER TABLE salary_structures DROP COLUMN IF EXISTS id CASCADE"))
            conn.commit()
            print("[OK] Dropped id column")
            
            print("[INFO] Adding id column as VARCHAR...")
            conn.execute(text("ALTER TABLE salary_structures ADD COLUMN id VARCHAR PRIMARY KEY"))
            conn.commit()
            print("[OK] Added id column as VARCHAR")
            
            print(f"\n[SUCCESS] ID column type fixed!")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error fixing id column: {str(e)}")
            return False

if __name__ == "__main__":
    try:
        print("=" * 60)
        print("FIX SALARY STRUCTURE ID COLUMN TYPE")
        print("=" * 60)
        
        success = fix_id_column_type()
        if success:
            print("\n" + "=" * 60)
            print("[SUCCESS] ID COLUMN FIX SUCCESSFUL!")
            print("=" * 60)
            print("\nNext steps:")
            print("1. Restart your backend server")
            print("2. Try saving the salary configuration again")
            sys.exit(0)
        else:
            print("\n" + "=" * 60)
            print("[FAILED] ID COLUMN FIX FAILED!")
            print("=" * 60)
            sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Fix error: {str(e)}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        sys.exit(1)
