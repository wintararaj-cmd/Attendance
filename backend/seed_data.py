import logging
import uuid
import datetime
import random
from decimal import Decimal
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.models import Employee, SalaryStructure, AttendanceLog, Department
# from app.services.auth import auth_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_demo_data():
    db = SessionLocal()
    try:
        logger.info("🌱 Starting Database Seeding...")

        # 1. Create Departments
        departments = ["Engineering", "HR", "Sales", "Operations"]
        for dept_name in departments:
            exists = db.query(Department).filter(Department.name == dept_name).first()
            if not exists:
                new_dept = Department(
                    id=str(uuid.uuid4()),
                    name=dept_name,
                    status="active",
                    company_id="default"
                )
                db.add(new_dept)
        db.commit()
        logger.info("✅ Departments seeded.")

        # 2. Create Employees & Salary Structures
        employees_data = [
            {
                "emp_code": "DEMO001",
                "first_name": "Alice",
                "last_name": "Fulltime",
                "department": "Engineering",
                "designation": "Senior Dev",
                "type": "full_time",
                "salary": {
                    "basic_salary": 25000,
                    "hra": 10000,
                    "special_allowance": 5000,
                    "is_hourly_based": False
                }
            },
            {
                "emp_code": "DEMO002",
                "first_name": "Bob",
                "last_name": "Parttime",
                "department": "Operations",
                "designation": "Assistant",
                "type": "part_time",
                "salary": {
                    "is_hourly_based": True,
                    "hourly_rate": 200,  # 200 per hour
                    "is_pf_applicable": False,
                    "ot_rate_multiplier": 1.5
                }
            },
            {
                "emp_code": "DEMO003",
                "first_name": "Charlie",
                "last_name": "Contractor",
                "department": "Sales",
                "designation": "Consultant",
                "type": "contract",
                "salary": {
                    "contract_rate_per_day": 1500, # 1500 per day
                    "is_hourly_based": False,
                    "is_pf_applicable": False
                }
            }
        ]

        today = datetime.date.today()
        
        for data in employees_data:
            # Check if employee exists
            emp = db.query(Employee).filter(Employee.emp_code == data["emp_code"]).first()
            if not emp:
                logger.info(f"Creating employee: {data['first_name']} ({data['type']})")
                emp = Employee(
                    id=str(uuid.uuid4()),
                    emp_code=data["emp_code"],
                    first_name=data["first_name"],
                    last_name=data["last_name"],
                    department=data["department"],
                    designation=data["designation"],
                    employee_type=data["type"],
                    mobile_no=f"99999{random.randint(10000, 99999)}",
                    status="active",
                    joining_date=today - datetime.timedelta(days=60),
                    is_face_registered=False 
                )
                db.add(emp)
                db.commit()
                db.refresh(emp)

                # Create Salary Structure
                salary_conf = data["salary"]
                new_salary = SalaryStructure(
                    id=str(uuid.uuid4()),
                    employee_id=emp.id,
                    basic_salary=salary_conf.get("basic_salary", 0),
                    hra=salary_conf.get("hra", 0),
                    special_allowance=salary_conf.get("special_allowance", 0),
                    is_hourly_based=salary_conf.get("is_hourly_based", False),
                    hourly_rate=salary_conf.get("hourly_rate", 0),
                    contract_rate_per_day=salary_conf.get("contract_rate_per_day", 0),
                    ot_rate_multiplier=salary_conf.get("ot_rate_multiplier", 1.5),
                    is_pf_applicable=salary_conf.get("is_pf_applicable", True),
                    is_esi_applicable=False
                )
                db.add(new_salary)
                db.commit()

                # 3. Create Demo Attendance Logs (Past 10 days)
                logger.info(f"   Generating attendance logs for {emp.first_name}...")
                for i in range(10):
                    log_date = today - datetime.timedelta(days=i)
                    
                    # Skip Sundays for full time
                    if log_date.weekday() == 6 and data["type"] == "full_time":
                        continue

                    # Random check-in time (9 AM +/- 30 mins)
                    start_hour = 9
                    check_in = datetime.datetime.combine(log_date, datetime.time(hour=start_hour, minute=random.randint(0, 59)))
                    
                    # Duration based on type
                    if data["type"] == "part_time":
                        hours_worked = random.uniform(3.5, 6.0) # 3.5 to 6 hours
                    else:
                        hours_worked = random.uniform(8.0, 10.0) # 8 to 10 hours (some OT)
                    
                    check_out = check_in + datetime.timedelta(hours=hours_worked)
                    
                    # Calculate OT
                    ot_hours = 0
                    if hours_worked > 9:
                        ot_hours = hours_worked - 9

                    log = AttendanceLog(
                        id=str(uuid.uuid4()),
                        employee_id=emp.id,
                        date=log_date,
                        check_in=check_in,
                        check_out=check_out,
                        status="present",
                        confidence_score=95.0,
                        total_hours_worked=round(hours_worked, 2),
                        ot_hours=round(ot_hours, 2)
                    )
                    db.add(log)
                db.commit()
            else:
                logger.info(f"Using existing employee: {data['first_name']}")

        logger.info("✅ Database seeding completed successfully!")

    except Exception as e:
        logger.error(f"❌ Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_demo_data()
