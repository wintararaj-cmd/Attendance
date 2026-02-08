"""
Migration Script: Add employee_id column to salary_structures table
This fixes the "column salary_structures.employee_id does not exist" error
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

def add_employee_id_column():
    """Add employee_id column to salary_structures table"""
    print("[INFO] Starting migration to add employee_id column...")
    
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
        
        # Check if employee_id already exists
        if 'employee_id' in existing_columns:
            print("[OK] employee_id column already exists!")
            return True
        
        try:
            # Add employee_id column
            print("  [+] Adding employee_id column...")
            sql = """
            ALTER TABLE salary_structures 
            ADD COLUMN employee_id VARCHAR
            """
            conn.execute(text(sql))
            conn.commit()
            print("  [OK] Added employee_id column")
            
            # Add foreign key constraint
            print("  [+] Adding foreign key constraint...")
            try:
                sql_fk = """
                ALTER TABLE salary_structures 
                ADD CONSTRAINT fk_salary_employee 
                FOREIGN KEY (employee_id) REFERENCES employees(id)
                """
                conn.execute(text(sql_fk))
                conn.commit()
                print("  [OK] Added foreign key constraint")
            except Exception as e:
                print(f"  [WARN] Could not add foreign key constraint: {str(e)}")
            
            # Add unique constraint
            print("  [+] Adding unique constraint...")
            try:
                sql_unique = """
                ALTER TABLE salary_structures 
                ADD CONSTRAINT unique_employee_salary 
                UNIQUE (employee_id)
                """
                conn.execute(text(sql_unique))
                conn.commit()
                print("  [OK] Added unique constraint")
            except Exception as e:
                print(f"  [WARN] Could not add unique constraint: {str(e)}")
            
            print(f"\n[SUCCESS] Migration completed successfully!")
            return True
            
        except ProgrammingError as e:
            print(f"  [ERROR] Error adding employee_id column: {str(e)}")
            return False

if __name__ == "__main__":
    try:
        print("=" * 60)
        print("MIGRATION: ADD EMPLOYEE_ID COLUMN")
        print("=" * 60)
        success = add_employee_id_column()
        if success:
            print("\n" + "=" * 60)
            print("[SUCCESS] MIGRATION SUCCESSFUL!")
            print("=" * 60)
            print("\nNext steps:")
            print("1. Restart your backend server")
            print("2. Try saving the salary configuration again")
            sys.exit(0)
        else:
            print("\n" + "=" * 60)
            print("[FAILED] MIGRATION FAILED!")
            print("=" * 60)
            sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Migration error: {str(e)}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        sys.exit(1)

