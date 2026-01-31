"""
Remove all inactive employees to allow re-registration
Run this once to clean up soft-deleted employees
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./attendance.db")

# Ensure SQLAlchemy compatibility
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print(f"Connecting to: {DATABASE_URL}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Delete attendance logs for inactive employees first
    result = db.execute(text("""
        DELETE FROM attendance_logs 
        WHERE employee_id IN (
            SELECT id FROM employees WHERE status = 'inactive'
        )
    """))
    print(f"✅ Deleted {result.rowcount} attendance logs for inactive employees")
    
    # Delete inactive employees
    result = db.execute(text("DELETE FROM employees WHERE status = 'inactive'"))
    print(f"✅ Deleted {result.rowcount} inactive employees")
    
    db.commit()
    print("\n🎉 Cleanup successful!")
    print("📝 You can now re-register employees")
    
except Exception as e:
    db.rollback()
    print(f"❌ Error: {e}")
finally:
    db.close()
