"""
Database Migration Script
Adds missing columns to employees table and creates departments table
"""
import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import ProgrammingError

# Get database URL from environment or use default
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/attendance_db")

def run_migration():
    """Run database migration to add missing columns"""
    print("🔄 Starting database migration...")
    print(f"📊 Database URL: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'localhost'}")
    
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    with engine.connect() as conn:
        # Check if employees table exists
        if 'employees' not in inspector.get_table_names():
            print("❌ Error: employees table does not exist!")
            return False
        
        # Get existing columns
        existing_columns = [col['name'] for col in inspector.get_columns('employees')]
        print(f"📋 Existing columns in employees table: {', '.join(existing_columns)}")
        
        # Columns to add
        columns_to_add = {
            'email': 'VARCHAR',
            'department': 'VARCHAR',
            'designation': 'VARCHAR',
            'employee_type': "VARCHAR DEFAULT 'full_time'",
            'joining_date': 'DATE',
            'updated_at': 'TIMESTAMP WITH TIME ZONE'
        }
        
        # Add missing columns
        added_count = 0
        for column_name, column_type in columns_to_add.items():
            if column_name not in existing_columns:
                try:
                    sql = f"ALTER TABLE employees ADD COLUMN {column_name} {column_type}"
                    print(f"  ➕ Adding column: {column_name} ({column_type})")
                    conn.execute(text(sql))
                    conn.commit()
                    added_count += 1
                    print(f"  ✅ Added: {column_name}")
                except ProgrammingError as e:
                    print(f"  ⚠️  Warning: Could not add {column_name}: {str(e)}")
            else:
                print(f"  ⏭️  Skipping: {column_name} (already exists)")
        
        # Create departments table if it doesn't exist
        if 'departments' not in inspector.get_table_names():
            print("\n📦 Creating departments table...")
            create_departments_sql = """
            CREATE TABLE departments (
                id VARCHAR PRIMARY KEY,
                company_id VARCHAR,
                name VARCHAR NOT NULL,
                description TEXT,
                department_head VARCHAR,
                status VARCHAR DEFAULT 'active',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
            """
            try:
                conn.execute(text(create_departments_sql))
                conn.commit()
                print("  ✅ Departments table created successfully")
            except Exception as e:
                print(f"  ⚠️  Warning: Could not create departments table: {str(e)}")
        else:
            print("\n⏭️  Departments table already exists")
        
        print(f"\n✨ Migration completed! Added {added_count} columns.")
        return True

if __name__ == "__main__":
    try:
        success = run_migration()
        if success:
            print("\n✅ Database migration successful!")
            sys.exit(0)
        else:
            print("\n❌ Database migration failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Migration error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
