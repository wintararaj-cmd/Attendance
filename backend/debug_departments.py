import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.models import Department, Employee, Company

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./attendance.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def debug_departments():
    print(f"Connecting to database: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("Querying Departments...")
        departments = db.query(Department).all()
        print(f"Found {len(departments)} departments.")
        
        for dept in departments:
            print(f"Dept: {dept.name} (ID: {dept.id})")
            print(f"  - Created At: {dept.created_at} (Type: {type(dept.created_at)})")
            print(f"  - ISO: {dept.created_at.isoformat()}")
            
            # Simulate the logic in endpoint
            employee_count = db.query(Employee).filter(
                Employee.department == dept.name,
                Employee.status == 'active'
            ).count()
            print(f"  - Employee Count: {employee_count}")
            
        # Test Insertion
        import uuid
        test_name = f"Test Dept {uuid.uuid4().hex[:8]}"
        print(f"Attempting to insert department: {test_name}")
        new_dept = Department(
            id=str(uuid.uuid4()),
            company_id='default',
            name=test_name,
            description="Test description",
            status="active"
        )
        db.add(new_dept)
        db.commit()
        print("Insertion successful.")
        db.delete(new_dept)
        db.commit()
        print("Cleanup successful.")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def check_default_company():
    print("\nChecking Default Company...")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        company = db.query(Company).filter(Company.id == 'default').first()
        if company:
            print(f"Default Company found: {company.name}")
        else:
            print("Default Company NOT found!")
            # Create it
            print("Creating default company...")
            new_company = Company(id='default', name='Default Company')
            db.add(new_company)
            db.commit()
            print("Created.")
    except Exception as e:
        print(f"Error checking company: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_default_company()
    debug_departments()
