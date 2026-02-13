import os
import sys
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./attendance.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def check_tables():
    print(f"Connecting to database: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("Tables found:", tables)
    
    if 'departments' in tables:
        print("Table 'departments' exists.")
        columns = [c['name'] for c in inspector.get_columns('departments')]
        print("Columns in 'departments':", columns)
    else:
        print("Table 'departments' DOES NOT exist.")

if __name__ == "__main__":
    check_tables()
