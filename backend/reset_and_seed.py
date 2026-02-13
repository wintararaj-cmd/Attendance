import logging
import uuid
import datetime
import random
from decimal import Decimal
import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine, Base
from app.models.models import Employee, SalaryStructure, AttendanceLog, Department, Company, Payroll, AdminUser
from sqlalchemy import text
from app.services.auth import auth_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_and_seed():
    db = SessionLocal()
    try:
        logger.info("⚠️ STARTING DATABASE RESET...")
        
        # 1. DELETE ALL DATA (Order matters for foreign keys)
        logger.info("🗑️ Deleting existing data...")
        try:
            db.query(Payroll).delete()
            db.query(AttendanceLog).delete()
            db.query(SalaryStructure).delete()
            db.query(Employee).delete()
            db.query(Department).delete()
            db.query(Company).delete()
            db.query(AdminUser).delete()
            db.commit()
            logger.info("✅ Data cleared.")
        except Exception as e:
            logger.warning(f"⚠️ Error clearing data (tables might be empty): {e}")
            db.rollback()

        # 2. SEED COMPANY
        logger.info("🌱 Seeding Company...")
        company = Company(id="default", name="Acme Corp", domain="acme.com")
        db.add(company)
        
        # 3. SEED ADMIN USER
        logger.info("🌱 Seeding Admin User...")
        
        # Use proper hashing service
        password_hash = auth_service.get_password_hash("admin123")
        
        admin = AdminUser(
            username="admin", 
            password_hash=password_hash,
            role="superadmin"
        )
        db.add(admin)

        # 4. SEED DEPARTMENTS
        logger.info("🌱 Seeding Departments...")
        depts = ["Engineering", "HR", "Sales", "Operations"]
        dept_map = {}
        for d_name in depts:
            dept = Department(
                id=str(uuid.uuid4()),
                company_id="default",
                name=d_name,
                description=f"{d_name} Department",
                status="active"
            )
            db.add(dept)
            dept_map[d_name] = dept
        db.commit()

        # 5. SEED EMPLOYEES & SALARY STRUCTURES
        logger.info("🌱 Seeding Employees...")
        
        employees_data = [
            {
                "emp_code": "DEMO001",
                "first_name": "Alice",
                "last_name": "Fulltime",
                "department": "Engineering",
                "designation": "Senior Dev",
                "type": "full_time",
                "mobile": "9876543210",
                "salary": {
                    "basic_salary": 25000,
                    "hra": 10000,
                    "special_allowance": 5000,
                    "is_hourly_based": False,
                    "is_pf_applicable": True,
                    "ot_rate_multiplier": 1.5,
                    "conveyance_allowance": 2000,
                    "medical_allowance": 1500
                }
            },
            {
                "emp_code": "DEMO002",
                "first_name": "Bob",
                "last_name": "Parttime",
                "department": "Operations",
                "designation": "Assistant",
                "type": "part_time",
                "mobile": "9876543211",
                "salary": {
                    "is_hourly_based": True,
                    "hourly_rate": 200, 
                    "is_pf_applicable": False,
                    "ot_rate_multiplier": 1.5,
                    "basic_salary": 0
                }
            },
            {
                "emp_code": "DEMO003",
                "first_name": "Charlie",
                "last_name": "Contractor",
                "department": "Sales",
                "designation": "Consultant",
                "type": "contract",
                "mobile": "9876543212",
                "salary": {
                    "contract_rate_per_day": 1500,
                    "is_hourly_based": False,
                    "is_pf_applicable": False,
                    "basic_salary": 0
                }
            },
            {
                "emp_code": "WRK001",
                "first_name": "Suresh",
                "last_name": "Worker",
                "department": "Operations",
                "designation": "Machine Operator",
                "type": "worker",
                "mobile": "9876543213",
                "salary": {
                    "basic_salary": 500, 
                     "hra": 100,
                     "is_hourly_based": False,
                     "ot_rate_multiplier": 2.0,
                     "is_pf_applicable": True,
                     "washing_allowance": 20
                }
            }
        ]

        created_employees = []

        for data in employees_data:
            emp = Employee(
                id=str(uuid.uuid4()),
                company_id="default",
                emp_code=data["emp_code"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                mobile_no=data["mobile"],
                email=f"{data['first_name'].lower()}@acme.com",
                department=data["department"],
                designation=data["designation"],
                employee_type=data["type"],
                joining_date=datetime.date(2025, 1, 15),
                status="active"
            )
            db.add(emp)
            created_employees.append((emp, data))
            
            # Salary
            s_conf = data["salary"]
            salary = SalaryStructure(
                id=str(uuid.uuid4()),
                employee_id=emp.id,
                basic_salary=s_conf.get("basic_salary", 0),
                hra=s_conf.get("hra", 0),
                special_allowance=s_conf.get("special_allowance", 0),
                is_hourly_based=s_conf.get("is_hourly_based", False),
                hourly_rate=s_conf.get("hourly_rate", 0),
                contract_rate_per_day=s_conf.get("contract_rate_per_day", 0),
                is_pf_applicable=s_conf.get("is_pf_applicable", False),
                conveyance_allowance=s_conf.get("conveyance_allowance", 0),
                washing_allowance=s_conf.get("washing_allowance", 0),
                medical_allowance=s_conf.get("medical_allowance", 0),
                professional_tax=200 if s_conf.get("is_pf_applicable") else 0,
                ot_rate_multiplier=s_conf.get("ot_rate_multiplier", 1.0)
            )
            db.add(salary)
        
        db.commit()

        # 6. SEED ATTENDANCE LOGS
        logger.info("🌱 Seeding Attendance Logs...")
        today = datetime.date.today()
        # Seed for last 15 days
        
        for i in range(15):
            curr_date = today - datetime.timedelta(days=14-i) # 14 days ago to today
            
            if curr_date.weekday() == 6: # Skip Sunday
                continue

            for emp, data in created_employees:
                 # Logic for hours
                hours_worked = 0
                if data["type"] == "part_time":
                    hours_worked = random.uniform(3, 6)
                elif data["type"] == "contract":
                    hours_worked = 8 # Flat day usually
                else: # full_time, worker
                     hours_worked = random.uniform(8, 10.5)

                in_time = datetime.datetime.combine(curr_date, datetime.time(9, 0)) + datetime.timedelta(minutes=random.randint(-15, 30))
                out_time = in_time + datetime.timedelta(hours=hours_worked)
                
                # OT Calculation
                ot_hours = 0
                net_hours = hours_worked
                if data["type"] in ["full_time", "worker"]:
                     net_hours = hours_worked - 0.5 # Break deduction
                     if net_hours > 8:
                         ot_hours = net_hours - 8
                
                log = AttendanceLog(
                    id=str(uuid.uuid4()),
                    employee_id=emp.id,
                    date=curr_date,
                    check_in=in_time,
                    check_out=out_time,
                    status="present",
                    confidence_score=Decimal("0.99"),
                    total_hours_worked=Decimal(f"{net_hours:.2f}"),
                    ot_hours=Decimal(f"{ot_hours:.2f}")
                )
                db.add(log)
        
        db.commit()
        logger.info("✅ Database Reset and Seeded Successfully!")

    except Exception as e:
        logger.error(f"❌ Error seeding data: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_and_seed()
