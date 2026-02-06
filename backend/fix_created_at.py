import sys
import os
from sqlalchemy import text

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "attendance.db")
os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

from app.core.database import SessionLocal

def fix_created_at():
    session = SessionLocal()
    try:
        print("Adding created_at column...")
        # Add as nullable first to avoid default value issues in SQLite
        session.execute(text("ALTER TABLE employees ADD COLUMN created_at TIMESTAMP"))
        session.commit()
        print("Success!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    fix_created_at()
