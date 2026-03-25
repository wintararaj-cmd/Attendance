
import os
import sys
from sqlalchemy import create_engine, text, inspect
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
    print("Starting migration: Add PF Slab Columns to Employee Payroll Rules...")
    print(f"Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL.split('://')[1] if '://' in DATABASE_URL else 'unknown'}")
    
    try:
        engine = create_engine(DATABASE_URL)
        inspector = inspect(engine)
        
        with engine.connect() as conn:
            # Check if table exists
            if "employee_payroll_rules" not in inspector.get_table_names():
                print("[ERROR] Table 'employee_payroll_rules' does not exist. Run the main migration first.")
                return
            
            # Get existing columns
            columns = [col['name'] for col in inspector.get_columns('employee_payroll_rules')]
            
            # Add pf_use_slabs if not exists
            if "pf_use_slabs" not in columns:
                print("[ADD] Adding column: pf_use_slabs")
                conn.execute(text("ALTER TABLE employee_payroll_rules ADD COLUMN pf_use_slabs BOOLEAN DEFAULT FALSE"))
                conn.commit()
            
            # Add pf_slabs if not exists
            if "pf_slabs" not in columns:
                print("[ADD] Adding column: pf_slabs")
                conn.execute(text("ALTER TABLE employee_payroll_rules ADD COLUMN pf_slabs TEXT"))
                conn.commit()
            
            print("[SUCCESS] Migration successful!")
            
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_migration()
