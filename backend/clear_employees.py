"""
Quick script to clear all employees and attendance logs
Run this to reset the system after fixing Mock Mode
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
    # Delete all attendance logs
    result = db.execute(text("DELETE FROM attendance_logs"))
    print(f"✅ Deleted {result.rowcount} attendance logs")
    
    # Delete all employees
    result = db.execute(text("DELETE FROM employees"))
    print(f"✅ Deleted {result.rowcount} employees")
    
    db.commit()
    print("\n🎉 Database cleared successfully!")
    print("📝 You can now re-register employees with the real AI system")
    
except Exception as e:
    db.rollback()
    print(f"❌ Error: {e}")
finally:
    db.close()
