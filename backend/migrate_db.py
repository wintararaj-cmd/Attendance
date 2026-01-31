"""
Database Migration Script
Adds missing columns to employees table and creates all missing tables
Works from root directory or backend directory (Coolify compatible)
"""
import os
import sys

# Add backend directory to path if running from root
current_dir = os.path.dirname(os.path.abspath(__file__))
if 'backend' in current_dir:
    # Running from backend directory
    sys.path.insert(0, current_dir)
else:
    # Running from root directory
    backend_dir = os.path.join(current_dir, 'backend')
    if os.path.exists(backend_dir):
        sys.path.insert(0, backend_dir)

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import ProgrammingError

# Import database URL from app configuration
try:
    from app.core.database import DATABASE_URL
    print(f"✅ Using app database configuration")
except ImportError:
    # Fallback to environment variable
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./attendance.db")
    print(f"⚠️ Using fallback database URL")

def run_migration():
    """Run database migration to add missing columns and tables"""
    print("🔄 Starting database migration...")
    db_display = DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL.split('://')[1] if '://' in DATABASE_URL else 'unknown'
    print(f"📊 Database: {db_display}")
    
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
        
        # Create companies table if it doesn't exist
        if 'companies' not in inspector.get_table_names():
            print("\n📦 Creating companies table...")
            create_companies_sql = """
            CREATE TABLE companies (
                id VARCHAR PRIMARY KEY,
                name VARCHAR NOT NULL,
                domain VARCHAR UNIQUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
            """
            try:
                conn.execute(text(create_companies_sql))
                conn.commit()
                print("  ✅ Companies table created successfully")
                
                # Insert default company
                conn.execute(text("INSERT INTO companies (id, name) VALUES ('default', 'Default Company')"))
                conn.commit()
                print("  ✅ Default company inserted")
            except Exception as e:
                print(f"  ⚠️  Warning: Could not create companies table: {str(e)}")
        else:
            print("\n⏭️  Companies table already exists")
        
        # Create admin_users table if it doesn't exist
        if 'admin_users' not in inspector.get_table_names():
            print("\n📦 Creating admin_users table...")
            create_admin_users_sql = """
            CREATE TABLE admin_users (
                id VARCHAR PRIMARY KEY,
                username VARCHAR UNIQUE NOT NULL,
                password_hash VARCHAR NOT NULL,
                role VARCHAR DEFAULT 'admin',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
            """
            try:
                conn.execute(text(create_admin_users_sql))
                conn.commit()
                print("  ✅ Admin users table created successfully")
            except Exception as e:
                print(f"  ⚠️  Warning: Could not create admin_users table: {str(e)}")
        else:
            print("\n⏭️  Admin users table already exists")
        
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
        
        # Create salary_structures table if it doesn't exist
        if 'salary_structures' not in inspector.get_table_names():
            print("\n📦 Creating salary_structures table...")
            create_salary_structures_sql = """
            CREATE TABLE salary_structures (
                id VARCHAR PRIMARY KEY,
                employee_id VARCHAR UNIQUE,
                basic_salary NUMERIC(12, 2) DEFAULT 0.0,
                hra_allowance NUMERIC(12, 2) DEFAULT 0.0,
                special_allowance NUMERIC(12, 2) DEFAULT 0.0,
                pf_deduction NUMERIC(12, 2) DEFAULT 0.0,
                professional_tax NUMERIC(12, 2) DEFAULT 0.0,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
            """
            try:
                conn.execute(text(create_salary_structures_sql))
                conn.commit()
                print("  ✅ Salary structures table created successfully")
            except Exception as e:
                print(f"  ⚠️  Warning: Could not create salary_structures table: {str(e)}")
        else:
            print("\n⏭️  Salary structures table already exists")
        
        print(f"\n✨ Migration completed! Added {added_count} columns.")
        return True

if __name__ == "__main__":
    try:
        print("=" * 60)
        print("🚀 ATTENDANCE SYSTEM - DATABASE MIGRATION")
        print("=" * 60)
        success = run_migration()
        if success:
            print("\n" + "=" * 60)
            print("✅ DATABASE MIGRATION SUCCESSFUL!")
            print("=" * 60)
            sys.exit(0)
        else:
            print("\n" + "=" * 60)
            print("❌ DATABASE MIGRATION FAILED!")
            print("=" * 60)
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Migration error: {str(e)}")
        import traceback
        print("\n📋 Full traceback:")
        traceback.print_exc()
        print("\n" + "=" * 60)
        print("⚠️  MIGRATION FAILED - Server will start anyway")
        print("=" * 60)
        sys.exit(1)
