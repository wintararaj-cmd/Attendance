"""
Quick script to check database contents
"""
import os
import sys
from sqlalchemy import create_engine, text

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.core.database import DATABASE_URL
except:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./attendance.db")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def check_data():
    print("=" * 60)
    print("DATABASE CONTENT CHECK")
    print("=" * 60)
    
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Check employees
        result = conn.execute(text("SELECT COUNT(*) FROM employees"))
        emp_count = result.scalar()
        print(f"\n📊 Employees: {emp_count} records")
        
        if emp_count > 0:
            result = conn.execute(text("SELECT id, emp_code, first_name, last_name, employee_type FROM employees LIMIT 5"))
            print("\nSample employees:")
            for row in result:
                print(f"  - {row[1]}: {row[2]} {row[3] or ''} ({row[4]})")
        
        # Check attendance
        result = conn.execute(text("SELECT COUNT(*) FROM attendance_logs"))
        att_count = result.scalar()
        print(f"\n📊 Attendance Logs: {att_count} records")
        
        # Check salary structures
        result = conn.execute(text("SELECT COUNT(*) FROM salary_structures"))
        sal_count = result.scalar()
        print(f"\n📊 Salary Structures: {sal_count} records")
        
        # Check departments
        result = conn.execute(text("SELECT COUNT(*) FROM departments"))
        dept_count = result.scalar()
        print(f"\n📊 Departments: {dept_count} records")
        
        # Check admin users
        result = conn.execute(text("SELECT COUNT(*) FROM admin_users"))
        admin_count = result.scalar()
        print(f"\n📊 Admin Users: {admin_count} records")
        
        print("\n" + "=" * 60)
        
        if emp_count == 0:
            print("⚠️  WARNING: No employees found!")
            print("This means the data was lost during deployment.")
            print("\nPossible reasons:")
            print("1. init_database.py dropped tables (before the fix)")
            print("2. Database was reset")
            print("3. Fresh deployment to new database")
        else:
            print("✅ Data exists! Employees are in the database.")
            print("If frontend shows 'No employees', check:")
            print("1. API endpoint is correct")
            print("2. Frontend is connecting to right backend")
            print("3. Authentication/authorization issues")

if __name__ == "__main__":
    check_data()
