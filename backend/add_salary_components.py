import os
import sys
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./attendance.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def add_salary_components():
    print(f"Connecting to database: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    table_name = 'salary_structures'
    
    if table_name not in inspector.get_table_names():
        print(f"Error: Table {table_name} does not exist.")
        return

    existing_columns = [col['name'] for col in inspector.get_columns(table_name)]
    print(f"Existing columns: {existing_columns}")

    new_columns = {
        'washing_allowance': 'NUMERIC(12, 2) DEFAULT 0.0',
        'welfare_deduction': 'NUMERIC(12, 2) DEFAULT 0.0'
    }

    with engine.connect() as conn:
        for col_name, col_type in new_columns.items():
            if col_name not in existing_columns:
                print(f"Adding column: {col_name}")
                try:
                    sql = text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}")
                    conn.execute(sql)
                    conn.commit()
                    print(f"Successfully added {col_name}")
                except Exception as e:
                    print(f"Failed to add {col_name}: {e}")
            else:
                print(f"Column {col_name} already exists.")

if __name__ == "__main__":
    add_salary_components()
