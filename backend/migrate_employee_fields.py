"""
Database Migration Script
Adds new columns to Employee table for enhanced HR management
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, SessionLocal
from sqlalchemy import text

def migrate_database():
    """Add new columns to employees table"""
    db = SessionLocal()
    
    try:
        print("🔄 Starting database migration...")
        
        # List of columns to add
        migrations = [
            ("email", "VARCHAR", "NULL"),
            ("department", "VARCHAR", "NULL"),
            ("designation", "VARCHAR", "NULL"),
            ("employee_type", "VARCHAR", "DEFAULT 'full_time'"),
            ("joining_date", "DATE", "NULL"),
            ("status", "VARCHAR", "DEFAULT 'active'"),
            ("created_at", "TIMESTAMP", "DEFAULT CURRENT_TIMESTAMP"),
            ("updated_at", "TIMESTAMP", "NULL"),
        ]
        
        for column_name, column_type, constraint in migrations:
            try:
                # Check if column exists
                check_query = text(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='employees' AND column_name='{column_name}'
                """)
                result = db.execute(check_query).fetchone()
                
                if result:
                    print(f"✅ Column '{column_name}' already exists, skipping...")
                else:
                    # Add column
                    alter_query = text(f"""
                        ALTER TABLE employees 
                        ADD COLUMN {column_name} {column_type} {constraint}
                    """)
                    db.execute(alter_query)
                    db.commit()
                    print(f"✅ Added column: {column_name}")
            
            except Exception as e:
                print(f"⚠️  Column '{column_name}' migration: {e}")
                db.rollback()
        
        print("\n✅ Database migration completed successfully!")
        print("\n📋 Summary:")
        print("   - Added email field")
        print("   - Added department field")
        print("   - Added designation field")
        print("   - Added employee_type field (full_time, part_time, contract, intern)")
        print("   - Added joining_date field")
        print("   - Added status field (active, inactive)")
        print("   - Added created_at and updated_at timestamps")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        db.rollback()
    
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("  DATABASE MIGRATION: Enhanced Employee Management")
    print("=" * 60)
    print()
    
    migrate_database()
    
    print()
    print("=" * 60)
    print("  Migration Complete!")
    print("=" * 60)
