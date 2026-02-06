import sys
import os
from sqlalchemy import text, inspect

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Force correct DB path
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "attendance.db")
os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

from app.core.database import engine, SessionLocal

def fix_schema():
    print("Starting schema fix...")
    session = SessionLocal()
    try:
        # Use inspector to get existing columns safely for SQLite
        inspector = inspect(engine)
        columns = [c['name'] for c in inspector.get_columns('employees')]
        print(f"Existing columns: {columns}")

        # Columns to check and add
        target_columns = {
            "email": "VARCHAR NULL",
            "department": "VARCHAR NULL",
            "designation": "VARCHAR NULL",
            "employee_type": "VARCHAR DEFAULT 'full_time'",
            "joining_date": "DATE NULL",
            "status": "VARCHAR DEFAULT 'active'",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "TIMESTAMP NULL"
        }

        for col_name, col_def in target_columns.items():
            if col_name not in columns:
                print(f"Adding missing column: {col_name}...")
                try:
                    session.execute(text(f"ALTER TABLE employees ADD COLUMN {col_name} {col_def}"))
                    session.commit()
                    print(f" - Successfully added {col_name}")
                except Exception as e:
                    print(f" - Failed to add {col_name}: {e}")
                    session.rollback()
            else:
                print(f"Column {col_name} already exists.")

        print("Schema fix completed.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Critical error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    fix_schema()
