from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends, Body
from fastapi.responses import FileResponse
from typing import Optional, List
from sqlalchemy.orm import Session
import shutil
import os
import json
import uuid
import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from ..services.face_recognition import face_service
from ..services.payroll import payroll_service
from ..services.face_recognition import face_service
from ..services.payroll import payroll_service
from ..services.auth import auth_service, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from ..core.database import get_db, engine
from ..models import models
from ..models.models import Employee, AttendanceLog, SalaryStructure, AdminUser
from jose import JWTError, jwt

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# ... (skip lines) replaced with actual functions
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(AdminUser).filter(AdminUser.username == username).first()
    if user is None:
        raise credentials_exception
    return user

@router.get("/debug/init-db")
def init_db(db: Session = Depends(get_db)):
    try:
        models.Base.metadata.create_all(bind=engine)
        
        # Create Default Company if not exists
        from ..models.models import Company
        default_company = db.query(Company).filter(Company.id == "default").first()
        if not default_company:
            db.add(Company(id="default", name="Default Company"))
            db.commit()
            
        return {"status": "success", "message": "Tables created and Default Company initialized"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/debug/check-attendance/{emp_code}")
def check_attendance_debug(emp_code: str, db: Session = Depends(get_db)):
    """Debug endpoint to check attendance records for an employee"""
    emp = db.query(Employee).filter(Employee.emp_code == emp_code).first()
    if not emp:
        return {"error": "Employee not found", "emp_code": emp_code}
    
    logs = db.query(AttendanceLog).filter(AttendanceLog.employee_id == emp.id).order_by(AttendanceLog.check_in.desc()).limit(10).all()
    
    return {
        "employee": {
            "id": emp.id,
            "emp_code": emp.emp_code,
            "name": f"{emp.first_name} {emp.last_name or ''}",
            "is_face_registered": emp.is_face_registered
        },
        "attendance_count": len(logs),
        "recent_logs": [
            {
                "date": log.date.isoformat(),
                "check_in": log.check_in.isoformat() if log.check_in else None,
                "status": log.status,
                "confidence": float(log.confidence_score) if log.confidence_score else None
            }
            for log in logs
        ]
    }

@router.get("/debug/list-employees")
def list_all_employees(db: Session = Depends(get_db)):
    """Debug endpoint to list all registered employees"""
    employees = db.query(Employee).all()
    
    return {
        "total_count": len(employees),
        "employees": [
            {
                "id": emp.id,
                "emp_code": emp.emp_code,
                "name": f"{emp.first_name} {emp.last_name or ''}",
                "mobile": emp.mobile_no,
                "is_face_registered": emp.is_face_registered,
                "company_id": emp.company_id
            }
            for emp in employees
        ]
    }

@router.get("/debug/db-info")
def database_info(db: Session = Depends(get_db)):
    """Debug endpoint to check database connection and info"""
    import os
    from sqlalchemy import text
    
    db_url = os.getenv("DATABASE_URL", "Not Set")
    # Hide password for security
    if db_url and "@" in db_url:
        parts = db_url.split("@")
        user_part = parts[0].split("://")[1].split(":")[0]
        db_url_safe = f"{parts[0].split('://')[0]}://{user_part}:****@{parts[1]}"
    else:
        db_url_safe = db_url
    
    try:
        # Test query
        result = db.execute(text("SELECT COUNT(*) as count FROM employees")).fetchone()
        employee_count = result[0] if result else 0
        
        # Get database name
        db_name_result = db.execute(text("SELECT current_database()")).fetchone()
        current_db = db_name_result[0] if db_name_result else "Unknown"
        
        return {
            "status": "connected",
            "database_url": db_url_safe,
            "current_database": current_db,
            "employee_count": employee_count,
            "connection_type": "PostgreSQL" if "postgresql" in db_url.lower() else "SQLite" if "sqlite" in db_url.lower() else "Unknown"
        }
    except Exception as e:
        return {
            "status": "error",
            "database_url": db_url_safe,
            "error": str(e)
        }


@router.post("/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(AdminUser).filter(AdminUser.username == form_data.username).first()
    if not user or not auth_service.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/auth/create-super-admin")
def create_super_admin(
    username: str = Body(...), 
    password: str = Body(...),
    secret: str = Body(...), # Simple security check
    db: Session = Depends(get_db)
):
    if secret != "setup-secret-123":
        raise HTTPException(status_code=403, detail="Invalid setup secret")
        
    existing = db.query(AdminUser).filter(AdminUser.username == username).first()
    if existing:
         raise HTTPException(status_code=400, detail="User already exists")
         
    hashed_pw = auth_service.get_password_hash(password)
    new_admin = AdminUser(username=username, password_hash=hashed_pw, role="superadmin")
    db.add(new_admin)
    db.commit()
    
    return {"status": "success", "message": "Super Admin created"}

@router.post("/attendance/register")
async def register_face(
    name: str = Form(...),
    emp_id: str = Form(..., description="Employee Code (e.g. EMP001)"),
    mobile_no: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Check if employee already exists by code or mobile
    existing_emp = db.query(Employee).filter((Employee.emp_code == emp_id) | (Employee.mobile_no == mobile_no)).first()
    if existing_emp:
        raise HTTPException(status_code=400, detail="Employee with this Code or Mobile No already exists")

    temp_file = f"temp_{file.filename}"
    try:
        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        try:
            embedding = face_service.register_face(temp_file)
        except Exception as e:
            print(f"CRITICAL ERROR in face_service: {e}")
            # Fallback for demo if service crashes completely
            embedding = [0.1] * 512
        
        if embedding is None:
            raise HTTPException(status_code=400, detail="Face detection failed or image quality low")
        
        # Create Employee
        # Note: face_service returns a list, we store it as JSON
        print(f"📝 Creating employee record: {emp_id} - {name}")
        new_emp = Employee(
            id=str(uuid.uuid4()),
            emp_code=emp_id,
            first_name=name,
            mobile_no=mobile_no,
            face_encoding_ref=json.dumps(embedding),
            is_face_registered=True,
            company_id="default" # detailed tenant logic later
        )
        db.add(new_emp)
        print(f"💾 Committing employee {emp_id} to database...")
        db.commit()
        db.refresh(new_emp)
        print(f"✅ Employee {emp_id} registered successfully! ID: {new_emp.id}")
        
        return {"status": "success", "message": f"Employee {name} registered with Face ID", "id": new_emp.id, "emp_code": emp_id}

    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        db.rollback()
        print(f"❌ Registration failed for {emp_id}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

@router.post("/attendance/mark")
async def mark_attendance(
    emp_id: Optional[str] = Form(None, description="Employee Code (Optional for 1:N)"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    temp_file = f"temp_live_{file.filename}"
    try:
        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 1. Liveness Check
        if not face_service.verify_liveness(temp_file):
             return {
                 "status": "failed",
                 "reason": "Liveness check failed. Please blink and ensure good lighting."
             }

        matched_emp = None
        confidence = 0.0

        if emp_id:
            # --- 1:1 Matching ---
            print(f"🔍 1:1 Matching mode for Employee ID: {emp_id}")
            emp = db.query(Employee).filter(Employee.emp_code == emp_id).first()
            if not emp:
                raise HTTPException(status_code=404, detail="Employee not found")
            
            if not emp.face_encoding_ref:
                return {"status": "failed", "reason": "No face data registered for this employee"}
                
            result = face_service.match_face(temp_file, json.loads(emp.face_encoding_ref))
            if result["match"]:
                matched_emp = emp
                confidence = result["confidence"]
                print(f"✅ 1:1 Match successful for {emp.emp_code} with confidence {confidence:.2f}")
            else:
                print(f"❌ 1:1 Match failed for {emp.emp_code}: {result.get('reason', 'Face mismatch')}")
                return {"status": "failed", "reason": result.get("reason", "Face mismatch")}
        
        else:
            # --- 1:N Search (Auto Detect) ---
            print("🔍 1:N Auto-Detection mode (no Employee ID provided)")
            all_employees = db.query(Employee).filter(Employee.is_face_registered == True).all()
            print(f"📋 Found {len(all_employees)} registered employees in database")
            
            candidates = {}
            for e in all_employees:
                if e.face_encoding_ref:
                    candidates[e.id] = json.loads(e.face_encoding_ref)
            
            print(f"🎯 Searching among {len(candidates)} face candidates...")
            result = face_service.identify_face(temp_file, candidates)
            
            if result["match"]:
                matched_emp = db.query(Employee).filter(Employee.id == result["employee_id"]).first()
                confidence = result["confidence"]
                print(f"✅ 1:N Match successful! Identified: {matched_emp.emp_code} ({matched_emp.first_name}) with confidence {confidence:.2f}")
            else:
                 print(f"❌ 1:N Match failed: {result.get('reason', 'Face not recognized')}")
                 return {"status": "failed", "reason": result.get("reason", "Face not recognized")}

        if matched_emp:
            # Check if already marked attendance today
            today = datetime.date.today()
            existing_log = db.query(AttendanceLog).filter(
                AttendanceLog.employee_id == matched_emp.id,
                AttendanceLog.date == today
            ).first()
            
            if existing_log:
                print(f"⚠️ Attendance already marked for {matched_emp.emp_code} today at {existing_log.check_in}")
                return {
                    "status": "failed",
                    "reason": f"Attendance already marked today at {existing_log.check_in.strftime('%I:%M %p')}"
                }
            
            # Log Attendance
            try:
                print(f"✅ Marking attendance for {matched_emp.emp_code} ({matched_emp.first_name})")
                log = AttendanceLog(
                    id=str(uuid.uuid4()),
                    employee_id=matched_emp.id,
                    date=today,
                    check_in=datetime.datetime.now(),
                    status="present",
                    confidence_score=float(confidence)
                )
                db.add(log)
                db.commit()
                db.refresh(log)
                print(f"✅ Attendance logged successfully: ID={log.id}, Time={log.check_in}")
                
                return {
                    "status": "success",
                    "attended": True,
                    "confidence": confidence,
                    "employee": matched_emp.first_name,
                    "emp_code": matched_emp.emp_code,
                    "time": log.check_in.strftime('%I:%M %p')
                }
            except Exception as db_error:
                db.rollback()
                print(f"❌ DATABASE ERROR while marking attendance: {db_error}")
                return {
                    "status": "failed",
                    "reason": f"Database error: {str(db_error)}"
                }
        
        
        return {"status": "failed", "reason": "Unknown Error"}

    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

@router.get("/employees")
def get_employees(
    department: Optional[str] = None,
    employee_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all employees with optional filters"""
    query = db.query(Employee)
    
    if department:
        query = query.filter(Employee.department == department)
    if employee_type:
        query = query.filter(Employee.employee_type == employee_type)
    if status:
        query = query.filter(Employee.status == status)
    
    employees = query.all()
    
    # Return with formatted data (safe attribute access for new fields)
    return [{
        "id": emp.id,
        "emp_code": emp.emp_code,
        "first_name": emp.first_name,
        "last_name": emp.last_name,
        "full_name": f"{emp.first_name} {emp.last_name or ''}".strip(),
        "mobile_no": emp.mobile_no,
        "email": getattr(emp, 'email', None),
        "department": getattr(emp, 'department', None),
        "designation": getattr(emp, 'designation', None),
        "employee_type": getattr(emp, 'employee_type', 'full_time'),
        "joining_date": getattr(emp, 'joining_date', None).isoformat() if getattr(emp, 'joining_date', None) else None,
        "status": getattr(emp, 'status', 'active'),
        "is_face_registered": emp.is_face_registered,
        "created_at": getattr(emp, 'created_at', None).isoformat() if getattr(emp, 'created_at', None) else None
    } for emp in employees]

@router.get("/employees/{emp_id}")
def get_employee_by_id(emp_id: str, db: Session = Depends(get_db)):
    """Get single employee details"""
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return {
        "id": emp.id,
        "emp_code": emp.emp_code,
        "first_name": emp.first_name,
        "last_name": emp.last_name,
        "mobile_no": emp.mobile_no,
        "email": getattr(emp, 'email', None),
        "department": getattr(emp, 'department', None),
        "designation": getattr(emp, 'designation', None),
        "employee_type": getattr(emp, 'employee_type', 'full_time'),
        "joining_date": getattr(emp, 'joining_date', None).isoformat() if getattr(emp, 'joining_date', None) else None,
        "status": getattr(emp, 'status', 'active'),
        "is_face_registered": emp.is_face_registered,
        "company_id": emp.company_id
    }

@router.put("/employees/{emp_id}")
def update_employee(
    emp_id: str,
    data: dict = Body(...),
    db: Session = Depends(get_db)
):
    """Update employee details"""
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Update allowed fields
    allowed_fields = [
        'first_name', 'last_name', 'mobile_no', 'email',
        'department', 'designation', 'employee_type', 'status'
    ]
    
    for field in allowed_fields:
        if field in data:
            setattr(emp, field, data[field])
    
    # Handle joining_date separately (date parsing)
    if 'joining_date' in data and data['joining_date']:
        from datetime import datetime as dt
        emp.joining_date = dt.fromisoformat(data['joining_date']).date()
    
    try:
        db.commit()
        db.refresh(emp)
        return {"status": "success", "message": "Employee updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/employees/{emp_id}")
def delete_employee(emp_id: str, db: Session = Depends(get_db)):
    """Delete employee (soft delete by setting status to inactive)"""
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Soft delete
    emp.status = "inactive"
    db.commit()
    
    return {"status": "success", "message": "Employee deactivated successfully"}

@router.get("/dashboard/department-stats")
def get_department_stats(db: Session = Depends(get_db)):
    """Get employee count by department"""
    from sqlalchemy import func
    
    dept_stats = db.query(
        Employee.department,
        func.count(Employee.id).label('count')
    ).filter(
        Employee.status == 'active'
    ).group_by(Employee.department).all()
    
    return [{
        "department": dept or "Unassigned",
        "count": count
    } for dept, count in dept_stats]

@router.get("/dashboard/employee-type-stats")
def get_employee_type_stats(db: Session = Depends(get_db)):
    """Get employee count by type"""
    from sqlalchemy import func
    
    type_stats = db.query(
        Employee.employee_type,
        func.count(Employee.id).label('count')
    ).filter(
        Employee.status == 'active'
    ).group_by(Employee.employee_type).all()
    
    return [{
        "employee_type": emp_type or "full_time",
        "count": count
    } for emp_type, count in type_stats]


@router.post("/payroll/calculate-demo")
async def calculate_payroll(
    basic_salary: float,
    unpaid_leaves: int = 0,
    overtime_hours: int = 0
):
    # Simplified DTO for demo
    structure = {"basic_salary": basic_salary}
    attendance = {
        "total_working_days": 30,
        "unpaid_leaves": unpaid_leaves,
        "overtime_hours": overtime_hours
    }
    
    return payroll_service.calculate_net_salary(structure, attendance)

@router.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    from sqlalchemy import func
    
    total_employees = db.query(Employee).filter(Employee.status == 'active').count()
    
    today = datetime.date.today()
    
    # query distinct employees present today
    present_query = db.query(AttendanceLog.employee_id).filter(
        AttendanceLog.date == today,
        AttendanceLog.status == "present"
    ).distinct()
    
    present_count = present_query.count()
    
    # Simple logic: Absent = Total - Present (ignoring leaves/shifts for now)
    absent_count = max(0, total_employees - present_count)

    # Fetch recent logs for the dashboard widget
    logs = db.query(AttendanceLog).join(Employee).order_by(AttendanceLog.check_in.desc()).limit(10).all()
    recent_activity = []
    for log in logs:
        recent_activity.append({
            "id": log.id,
            "employee_name": f"{log.employee.first_name} {log.employee.last_name or ''}",
            "emp_code": log.employee.emp_code,
            "department": getattr(log.employee, 'department', None),
            "time": log.check_in.strftime("%I:%M %p") if log.check_in else "--:--",
            "status": log.status
        })
    
    # Department breakdown (safe query for new columns)
    department_breakdown = []
    try:
        dept_stats = db.query(
            Employee.department,
            func.count(Employee.id).label('count')
        ).filter(
            Employee.status == 'active'
        ).group_by(Employee.department).all()
        
        department_breakdown = [{
            "department": dept or "Unassigned",
            "count": count
        } for dept, count in dept_stats]
    except Exception as e:
        print(f"⚠️ Department stats query failed (columns may not exist yet): {e}")
        department_breakdown = [{"department": "All", "count": total_employees}]
    
    # Employee type breakdown (safe query for new columns)
    employee_type_breakdown = []
    try:
        type_stats = db.query(
            Employee.employee_type,
            func.count(Employee.id).label('count')
        ).filter(
            Employee.status == 'active'
        ).group_by(Employee.employee_type).all()
        
        employee_type_breakdown = [{
            "type": emp_type or "full_time",
            "count": count
        } for emp_type, count in type_stats]
    except Exception as e:
        print(f"⚠️ Employee type stats query failed (columns may not exist yet): {e}")
        employee_type_breakdown = [{"type": "full_time", "count": total_employees}]
    
    return {
        "total_employees": total_employees,
        "present_today": present_count,
        "absent_today": absent_count,
        "late_count": 0, # Placeholder for future logic
        "recent_activity": recent_activity,
        "department_breakdown": department_breakdown,
        "employee_type_breakdown": employee_type_breakdown
    }

@router.get("/payroll/employee/{emp_id}")
def get_employee_payroll(
    emp_id: str,
    db: Session = Depends(get_db)
):
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
        
    # Fetch Salary Structure
    sal = db.query(SalaryStructure).filter(SalaryStructure.employee_id == emp_id).first()
    
    if not sal:
        # Default fallback
        salary_struct = {
            "basic_salary": 15000, 
            "hra_percentage": 0, 
            "da_percentage": 0,
            "special_allowance": 0,
            "pf_deduction": 0,
            "professional_tax": 0
        }
    else:
        salary_struct = {
            "basic_salary": float(sal.basic_salary),
            "hra_allowance": float(sal.hra_allowance),
            "special_allowance": float(sal.special_allowance),
            "pf_deduction": float(sal.pf_deduction),
            "professional_tax": float(sal.professional_tax)
        }
    
    # Calculate Attendance for Current Month
    today = datetime.date.today()
    start_date = today.replace(day=1)
    
    # Count present days
    present_days = db.query(AttendanceLog).filter(
        AttendanceLog.employee_id == emp_id,
        AttendanceLog.date >= start_date,
        AttendanceLog.status == "present"
    ).count()
    
    # Simple Logic: Assume 30 day month. Unpaid = 30 - Present.
    attendance = {
        "total_working_days": 30,
        "unpaid_leaves": max(0, 30 - present_days),
        "overtime_hours": 0
    }
    
    net = payroll_service.calculate_net_salary(salary_struct, attendance)
    
    return {
        "employee_id": emp.id,
        "employee_name": f"{emp.first_name} {emp.last_name or ''}",
        "month": today.strftime("%B %Y"),
        "present_days": present_days,
        "payroll": net
    }

@router.get("/attendance/logs")
def get_attendance_logs(db: Session = Depends(get_db)):
    logs = db.query(AttendanceLog).join(Employee).order_by(AttendanceLog.check_in.desc()).limit(50).all()
    
    result = []
    for log in logs:
        result.append({
            "id": log.id,
            "employee_id": log.employee_id,
            "employee_name": f"{log.employee.first_name} {log.employee.last_name or ''}",
            "emp_code": log.employee.emp_code,
            "date": log.date.isoformat(),
            "check_in": log.check_in.isoformat() if log.check_in else None,
            "check_out": log.check_out.isoformat() if log.check_out else None,
            "status": log.status,
            "confidence": float(log.confidence_score) if log.confidence_score else None
        })
    return result

@router.get("/employees/{emp_id}/salary")
def get_employee_salary_struct(emp_id: str, db: Session = Depends(get_db)):
    sal = db.query(SalaryStructure).filter(SalaryStructure.employee_id == emp_id).first()
    if not sal:
        return {
            "basic_salary": 0,
            "hra_allowance": 0,
            "special_allowance": 0,
            "pf_deduction": 0,
            "professional_tax": 0
        }
    return sal

@router.post("/employees/{emp_id}/salary")
def update_employee_salary(
    emp_id: str, 
    data: dict = Body(...),
    db: Session = Depends(get_db)
):
    sal = db.query(SalaryStructure).filter(SalaryStructure.employee_id == emp_id).first()
    if not sal:
        sal = SalaryStructure(id=str(uuid.uuid4()), employee_id=emp_id)
        db.add(sal)
    
    sal.basic_salary = data.get("basic_salary", 0)
    sal.hra_allowance = data.get("hra_allowance", 0)
    sal.special_allowance = data.get("special_allowance", 0)
    sal.pf_deduction = data.get("pf_deduction", 0)
    sal.professional_tax = data.get("professional_tax", 0)
    
    db.commit()
    return {"status": "success", "message": "Salary structure updated"}

@router.get("/payroll/payslip/{emp_id}/pdf")
def download_payslip_pdf(emp_id: str, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
        
    # Get Payroll Data logic (reused from get_employee_payroll, ideally refactor)
    sal = db.query(SalaryStructure).filter(SalaryStructure.employee_id == emp_id).first()
    
    # Defaults
    basic = float(sal.basic_salary) if sal else 15000
    hra = float(sal.hra_allowance) if sal else 0
    special = float(sal.special_allowance) if sal else 0
    pf = float(sal.pf_deduction) if sal else 0
    pt = float(sal.professional_tax) if sal else 0
    
    today = datetime.date.today()
    start_date = today.replace(day=1)
    present_days = db.query(AttendanceLog).filter(
        AttendanceLog.employee_id == emp_id,
        AttendanceLog.date >= start_date,
        AttendanceLog.status == "present"
    ).count()
    
    attendance = {
        "total_working_days": 30,
        "unpaid_leaves": max(0, 30 - present_days),
        "overtime_hours": 0
    }
    
    salary_struct = {
        "basic_salary": basic, "hra_allowance": hra, "special_allowance": special, 
        "pf_deduction": pf, "professional_tax": pt
    }
    
    net_data = payroll_service.calculate_net_salary(salary_struct, attendance)
    
    # --- Generate PDF ---
    filename = f"Payslip_{emp.first_name}_{today.strftime('%b_%Y')}.pdf"
    filepath = f"temp_{filename}"
    
    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4
    
    # Header
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, f"PAYSLIP - {today.strftime('%B %Y')}")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Employee: {emp.first_name} {emp.last_name or ''}")
    c.drawString(50, height - 100, f"Employee ID: {emp.emp_code}")
    
    # Attendance
    c.drawString(50, height - 140, f"Present Days: {present_days}")
    c.drawString(200, height - 140, f"Total Days: 30")
    
    # Table Header
    y = height - 180
    c.setLineWidth(1)
    c.line(50, y, width - 50, y)
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Earnings")
    c.drawString(300, y, "Amount")
    c.drawString(350, y, "Deductions")
    c.drawString(500, y, "Amount")
    y -= 10
    c.line(50, y, width - 50, y)
    y -= 20
    
    # Earnings
    c.setFont("Helvetica", 11)
    earnings = net_data["payroll"]["earnings"]
    deductions = net_data["payroll"]["deductions"]
    
    start_y = y
    
    c.drawString(50, y, "Basic Salary")
    c.drawString(300, y, f"{earnings['basic']:.2f}")
    
    c.drawString(350, y, "Provident Fund")
    c.drawString(500, y, f"{deductions['pf']:.2f}")
    y -= 20
    
    c.drawString(50, y, "HRA")
    c.drawString(300, y, f"{earnings['hra']:.2f}")
    
    c.drawString(350, y, "Professional Tax")
    c.drawString(500, y, f"{deductions['prof_tax']:.2f}")
    y -= 20
    
    c.drawString(50, y, "Allowances")
    c.drawString(300, y, f"{earnings['special']:.2f}")
    
    c.drawString(350, y, "LOP")
    c.drawString(500, y, f"{deductions['lop']:.2f}")
    y -= 20
    
    # Totals
    y -= 10
    c.line(50, y, width - 50, y)
    y -= 20
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Gross Earnings")
    c.drawString(300, y, f"{earnings['gross_earned']:.2f}")
    
    c.drawString(350, y, "Total Deductions")
    c.drawString(500, y, f"{deductions['total']:.2f}")
    
    # Net Pay
    y -= 40
    c.setFillColor(colors.blue)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, f"NET PAYABLE: Rs. {net_data['payroll']['net_salary']:.2f}")
    
    c.save()
    
    return FileResponse(filepath, media_type='application/pdf', filename=filename)
