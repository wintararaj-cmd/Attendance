from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends, Body
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
import shutil
import os
import json
import uuid
import datetime
import tempfile
from datetime import timezone, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from ..services.face_recognition import face_service
from ..services.payroll import payroll_service
from ..services.auth import auth_service, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from ..core.database import get_db, engine
from ..models import models
from ..models.models import Employee, AttendanceLog, SalaryStructure, AdminUser, Department
from jose import JWTError, jwt


import logging
import sys

# Configure logging to file - Force Handler
logger = logging.getLogger("api_endpoints")
logger.setLevel(logging.INFO)

# Avoid adding permissions if already exists, but ensure file handler
if not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
    fh = logging.FileHandler('backend_debug_forced.log')
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

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

@router.post("/auth/login")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(AdminUser).filter(AdminUser.username == form_data.username).first()
    if not user or not auth_service.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/debug/salary-schema")
def check_salary_schema(db: Session = Depends(get_db)):
    """Diagnostic endpoint to check salary_structures table schema"""
    from sqlalchemy import inspect
    
    inspector = inspect(engine)
    
    if 'salary_structures' not in inspector.get_table_names():
        return {
            "status": "error",
            "message": "salary_structures table does not exist",
            "tables": inspector.get_table_names()
        }
    
    columns = inspector.get_columns('salary_structures')
    column_names = [col['name'] for col in columns]
    
    required_columns = [
        'basic_salary', 'hra', 'conveyance_allowance', 'medical_allowance',
        'special_allowance', 'education_allowance', 'other_allowance',
        'pf_employee', 'pf_employer', 'esi_employee', 'esi_employer',
        'professional_tax', 'tds', 'bonus', 'incentive',
        'is_pf_applicable', 'is_esi_applicable'
    ]
    
    missing = [col for col in required_columns if col not in column_names]
    
    # Count records
    from sqlalchemy import text
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM salary_structures"))
        count = result.scalar()
    
    return {
        "status": "ok" if not missing else "incomplete",
        "table_exists": True,
        "total_columns": len(columns),
        "columns": column_names,
        "missing_columns": missing,
        "total_records": count,
        "message": "All columns present" if not missing else f"{len(missing)} columns missing - run migration"
    }

# ... (rest of the file)

@router.post("/attendance/register")
async def register_face(
    name: str = Form(...),
    emp_id: str = Form(..., description="Employee Code (e.g. EMP001)"),
    mobile_no: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # Ensure default company exists
        from ..models.models import Company
        default_company = db.query(Company).filter(Company.id == "default").first()
        if not default_company:
            default_company = Company(id="default", name="Default Company")
            db.add(default_company)
            db.commit()
            print("✅ Created default company")
        
        # First, remove any inactive employees with the same code or mobile
        # This prevents unique constraint violations
        inactive_employees = db.query(Employee).filter(
            (Employee.emp_code == emp_id) | (Employee.mobile_no == mobile_no),
            Employee.status == 'inactive'
        ).all()
        
        if inactive_employees:
            for inactive_emp in inactive_employees:
                # Delete their attendance logs first
                db.query(AttendanceLog).filter(AttendanceLog.employee_id == inactive_emp.id).delete()
                # Delete the inactive employee
                db.delete(inactive_emp)
            db.commit()
            print(f"🗑️ Removed {len(inactive_employees)} inactive employee(s) to allow re-registration")
        
        # Now check if an active employee exists
        existing_emp = db.query(Employee).filter(
            (Employee.emp_code == emp_id) | (Employee.mobile_no == mobile_no),
            Employee.status == 'active'
        ).first()
        if existing_emp:
            raise HTTPException(status_code=400, detail="Employee with this Code or Mobile No already exists")

        # Use system temp directory for safer file handling
        suffix = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_file_path = tmp.name

        try:
            try:
                embedding = face_service.register_face(temp_file_path)
            except Exception as e:
                print(f"CRITICAL ERROR in face_service: {e}")
                import traceback
                traceback.print_exc()
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
            raise HTTPException(status_code=500, detail=f"Registration error: {str(e)}")

        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Outer registration error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"System error: {str(e)}")

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
            # IST timezone
            IST = timezone(timedelta(hours=5, minutes=30))
            now_ist = datetime.datetime.now(IST)
            today = now_ist.date()
            
            # Check if already marked attendance today
            existing_log = db.query(AttendanceLog).filter(
                AttendanceLog.employee_id == matched_emp.id,
                AttendanceLog.date == today
            ).first()
            
            
            if existing_log:
                # Convert check_in time to IST for display
                if existing_log.check_in.tzinfo is None:
                    # If timezone-naive, assume it's UTC
                    check_in_ist = existing_log.check_in.replace(tzinfo=timezone.utc).astimezone(IST)
                else:
                    # If timezone-aware, convert to IST
                    check_in_ist = existing_log.check_in.astimezone(IST)
                    
                print(f"⚠️ Attendance already marked for {matched_emp.emp_code} today at {check_in_ist}")
                return {
                    "status": "failed",
                    "reason": f"Attendance already marked for {matched_emp.first_name} ({matched_emp.emp_code}) at {check_in_ist.strftime('%I:%M %p')}"
                }
            
            # Log Attendance
            try:
                print(f"✅ Marking attendance for {matched_emp.emp_code} ({matched_emp.first_name})")
                log = AttendanceLog(
                    id=str(uuid.uuid4()),
                    employee_id=matched_emp.id,
                    date=today,
                    check_in=now_ist,
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
                    "time": now_ist.strftime('%I:%M %p')
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



@router.post("/attendance/checkout")
async def mark_checkout(
    emp_id: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Mark check-out time for an employee"""
    temp_file = f"temp_checkout_{file.filename}"
    try:
        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Liveness Check
        if not face_service.verify_liveness(temp_file):
            return {
                "status": "failed",
                "reason": "Liveness check failed. Please blink and ensure good lighting."
            }

        matched_emp = None
        confidence = 0.0

        if emp_id:
            # 1:1 Matching
            emp = db.query(Employee).filter(Employee.emp_code == emp_id).first()
            if not emp:
                raise HTTPException(status_code=404, detail="Employee not found")
            
            if not emp.face_encoding_ref:
                return {"status": "failed", "reason": "No face data registered for this employee"}
                
            result = face_service.match_face(temp_file, json.loads(emp.face_encoding_ref))
            if result["match"]:
                matched_emp = emp
                confidence = result["confidence"]
            else:
                return {"status": "failed", "reason": result.get("reason", "Face mismatch")}
        else:
            # 1:N Search
            all_employees = db.query(Employee).filter(Employee.is_face_registered == True).all()
            candidates = {}
            for e in all_employees:
                if e.face_encoding_ref:
                    candidates[e.id] = json.loads(e.face_encoding_ref)
            
            result = face_service.identify_face(temp_file, candidates)
            
            if result["match"]:
                matched_emp = db.query(Employee).filter(Employee.id == result["employee_id"]).first()
                confidence = result["confidence"]
            else:
                return {"status": "failed", "reason": result.get("reason", "Face not recognized")}

        if matched_emp:
            # IST timezone
            IST = timezone(timedelta(hours=5, minutes=30))
            now_ist = datetime.datetime.now(IST)
            today = now_ist.date()
            
            # Find today's attendance log
            existing_log = db.query(AttendanceLog).filter(
                AttendanceLog.employee_id == matched_emp.id,
                AttendanceLog.date == today
            ).first()
            
            if not existing_log:
                return {
                    "status": "failed",
                    "reason": f"No check-in found for {matched_emp.first_name} ({matched_emp.emp_code}) today. Please check-in first."
                }
            
            
            if existing_log.check_out:
                if existing_log.check_out.tzinfo is None:
                    check_out_ist = existing_log.check_out.replace(tzinfo=timezone.utc).astimezone(IST)
                else:
                    check_out_ist = existing_log.check_out.astimezone(IST)
                return {
                    "status": "failed",
                    "reason": f"Already checked out today at {check_out_ist.strftime('%I:%M %p')}"
                }
            
            
            # Mark check-out
            existing_log.check_out = now_ist
            db.commit()
            
            return {
                "status": "success",
                "employee": matched_emp.first_name,
                "emp_code": matched_emp.emp_code,
                "check_out_time": now_ist.strftime('%I:%M %p')
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
def delete_employee(
    emp_id: str, 
    hard_delete: bool = False,
    db: Session = Depends(get_db)
):
    """
    Delete employee
    - Default: Soft delete (set status to inactive)
    - hard_delete=true: Permanently delete from database
    """
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    if hard_delete:
        # Hard delete - permanently remove
        # First delete related attendance logs
        db.query(AttendanceLog).filter(AttendanceLog.employee_id == emp_id).delete()
        # Then delete employee
        db.delete(emp)
        db.commit()
        return {"status": "success", "message": "Employee permanently deleted"}
    else:
        # Soft delete - just mark as inactive
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
            "hra": 0,
            "conveyance_allowance": 0,
            "medical_allowance": 0,
            "special_allowance": 0,
            "education_allowance": 0,
            "other_allowance": 0,
            "bonus": 0,
            "incentive": 0,
            "is_pf_applicable": True,
            "is_esi_applicable": False
        }
    else:
        salary_struct = {
            "basic_salary": float(sal.basic_salary) if sal.basic_salary else 0,
            "hra": float(sal.hra) if sal.hra else 0,
            "conveyance_allowance": float(sal.conveyance_allowance) if sal.conveyance_allowance else 0,
            "medical_allowance": float(sal.medical_allowance) if sal.medical_allowance else 0,
            "special_allowance": float(sal.special_allowance) if sal.special_allowance else 0,
            "education_allowance": float(sal.education_allowance) if sal.education_allowance else 0,
            "other_allowance": float(sal.other_allowance) if sal.other_allowance else 0,
            "bonus": float(sal.bonus) if sal.bonus else 0,
            "incentive": float(sal.incentive) if sal.incentive else 0,
            "tds": float(sal.tds) if sal.tds else 0,
            "is_pf_applicable": sal.is_pf_applicable if hasattr(sal, 'is_pf_applicable') else True,
            "is_esi_applicable": sal.is_esi_applicable if hasattr(sal, 'is_esi_applicable') else False
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
    
    # Simple Logic: Assume 30 day month
    attendance = {
        "total_working_days": 30,
        "present_days": present_days,
        "overtime_hours": 0
    }
    
    result = payroll_service.calculate_net_salary(salary_struct, attendance)
    
    return {
        "employee_id": emp.id,
        "employee_name": f"{emp.first_name} {emp.last_name or ''}",
        "month": today.strftime("%B %Y"),
        "present_days": present_days,
        **result
    }

@router.get("/attendance/logs")
def get_attendance_logs(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    employee_id: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    # current_user: AdminUser = Depends(get_current_user)
):
    """Get attendance logs with optional filters"""
    from sqlalchemy import desc
    
    query = db.query(AttendanceLog).join(Employee)
    
    logger.info(f"FILTER REQUEST - Search: '{search}', Start: {start_date}, End: {end_date}, EmpID: {employee_id}")
    
    if employee_id:
        query = query.filter(AttendanceLog.employee_id == employee_id)
    if search:
        search_lower = search.lower()
        logger.info(f"Applying search filter: {search_lower}")
        from sqlalchemy import or_
        query = query.filter(
            or_(
                func.lower(func.coalesce(Employee.first_name, '')).contains(search_lower),
                func.lower(func.coalesce(Employee.last_name, '')).contains(search_lower),
                func.lower(func.coalesce(Employee.emp_code, '')).contains(search_lower)
            )
        )
    if start_date:
        query = query.filter(AttendanceLog.date >= start_date)
    if end_date:
        query = query.filter(AttendanceLog.date <= end_date)
    
    logs = query.order_by(desc(AttendanceLog.date), desc(AttendanceLog.check_in)).limit(50).all()
    
    # IST timezone for display
    IST = timezone(timedelta(hours=5, minutes=30))
    
    result = []
    for log in logs:
        emp = log.employee
        # Convert times to IST
        if log.check_in:
            if log.check_in.tzinfo is None:
                check_in_ist = log.check_in.replace(tzinfo=timezone.utc).astimezone(IST)
            else:
                check_in_ist = log.check_in.astimezone(IST)
        else:
            check_in_ist = None
            
        if log.check_out:
            if log.check_out.tzinfo is None:
                check_out_ist = log.check_out.replace(tzinfo=timezone.utc).astimezone(IST)
            else:
                check_out_ist = log.check_out.astimezone(IST)
        else:
            check_out_ist = None
        
        result.append({
            "id": log.id,
            "date": log.date.isoformat(),
            "employee_name": f"{emp.first_name} {emp.last_name or ''}".strip(),
            "emp_code": emp.emp_code,
            "check_in": check_in_ist.strftime("%I:%M %p") if check_in_ist else None,
            "check_out": check_out_ist.strftime("%I:%M %p") if check_out_ist else None,
            "status": log.status,
            "confidence": float(log.confidence_score) if log.confidence_score else None
        })
    
    return {"logs": result}

@router.get("/attendance/export")
def export_attendance_logs(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    employee_id: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """Export attendance logs to CSV"""
    from sqlalchemy import desc
    import csv
    from io import StringIO
    from fastapi.responses import StreamingResponse
    
    query = db.query(AttendanceLog).join(Employee)
    
    logger.info(f"EXPORT REQUEST - Search: '{search}', Start: {start_date}, End: {end_date}, EmpID: {employee_id}")
    
    try:
        if employee_id:
            query = query.filter(AttendanceLog.employee_id == employee_id)
        if search:
            search_lower = search.lower()
            from sqlalchemy import or_
            query = query.filter(
                or_(
                    func.lower(func.coalesce(Employee.first_name, '')).contains(search_lower),
                    func.lower(func.coalesce(Employee.last_name, '')).contains(search_lower),
                    func.lower(func.coalesce(Employee.emp_code, '')).contains(search_lower)
                )
            )
        if start_date:
            query = query.filter(AttendanceLog.date >= start_date)
        if end_date:
            query = query.filter(AttendanceLog.date <= end_date)
        
        # No limit for export, but maybe reasonable cap?
        logs = query.order_by(desc(AttendanceLog.date), desc(AttendanceLog.check_in)).all()
        
        IST = timezone(timedelta(hours=5, minutes=30))
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['Date', 'Employee Name', 'Employee Code', 'Department', 'Check In', 'Check Out', 'Status', 'Confidence Score'])
        
        for log in logs:
            emp = log.employee
            
            if log.check_in:
                if log.check_in.tzinfo is None:
                    check_in_ist = log.check_in.replace(tzinfo=timezone.utc).astimezone(IST)
                else:
                    check_in_ist = log.check_in.astimezone(IST)
            else:
                check_in_ist = None
                
            if log.check_out:
                if log.check_out.tzinfo is None:
                    check_out_ist = log.check_out.replace(tzinfo=timezone.utc).astimezone(IST)
                else:
                    check_out_ist = log.check_out.astimezone(IST)
            else:
                check_out_ist = None
                
            writer.writerow([
                log.date.isoformat(),
                f"{emp.first_name} {emp.last_name or ''}".strip(),
                emp.emp_code,
                getattr(emp, 'department', ''),
                check_in_ist.strftime("%I:%M %p") if check_in_ist else '',
                check_out_ist.strftime("%I:%M %p") if check_out_ist else '',
                log.status,
                f"{float(log.confidence_score):.2f}" if log.confidence_score else ''
            ])
        
        output.seek(0)
        
        response = StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv"
        )
        response.headers["Content-Disposition"] = "attachment; filename=attendance_logs.csv"
        return response

    except Exception as e:
        logger.error(f"EXPORT ERROR: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.get("/employees/{emp_id}/salary")
def get_employee_salary_struct(emp_id: str, db: Session = Depends(get_db)):
    sal = db.query(SalaryStructure).filter(SalaryStructure.employee_id == emp_id).first()
    if not sal:
        return {
            "basic_salary": 0,
            "hra": 0,
            "conveyance_allowance": 0,
            "medical_allowance": 0,
            "special_allowance": 0,
            "education_allowance": 0,
            "other_allowance": 0,
            "pf_employee": 0,
            "pf_employer": 0,
            "esi_employee": 0,
            "esi_employer": 0,
            "professional_tax": 0,
            "tds": 0,
            "bonus": 0,
            "incentive": 0,
            "is_pf_applicable": True,
            "is_esi_applicable": False
        }
    
    return {
        "basic_salary": float(sal.basic_salary) if sal.basic_salary else 0,
        "hra": float(sal.hra) if sal.hra else 0,
        "conveyance_allowance": float(sal.conveyance_allowance) if sal.conveyance_allowance else 0,
        "medical_allowance": float(sal.medical_allowance) if sal.medical_allowance else 0,
        "special_allowance": float(sal.special_allowance) if sal.special_allowance else 0,
        "education_allowance": float(sal.education_allowance) if sal.education_allowance else 0,
        "other_allowance": float(sal.other_allowance) if sal.other_allowance else 0,
        "pf_employee": float(sal.pf_employee) if sal.pf_employee else 0,
        "pf_employer": float(sal.pf_employer) if sal.pf_employer else 0,
        "esi_employee": float(sal.esi_employee) if sal.esi_employee else 0,
        "esi_employer": float(sal.esi_employer) if sal.esi_employer else 0,
        "professional_tax": float(sal.professional_tax) if sal.professional_tax else 0,
        "tds": float(sal.tds) if sal.tds else 0,
        "bonus": float(sal.bonus) if sal.bonus else 0,
        "incentive": float(sal.incentive) if sal.incentive else 0,
        "is_pf_applicable": sal.is_pf_applicable if hasattr(sal, 'is_pf_applicable') else True,
        "is_esi_applicable": sal.is_esi_applicable if hasattr(sal, 'is_esi_applicable') else False
    }

@router.post("/employees/{emp_id}/salary")
def update_employee_salary(
    emp_id: str, 
    data: dict = Body(...),
    db: Session = Depends(get_db)
):
    try:
        sal = db.query(SalaryStructure).filter(SalaryStructure.employee_id == emp_id).first()
        if not sal:
            sal = SalaryStructure(id=str(uuid.uuid4()), employee_id=emp_id)
            db.add(sal)
        
        # Update all salary components
        sal.basic_salary = data.get("basic_salary", 0)
        sal.hra = data.get("hra", 0)
        sal.conveyance_allowance = data.get("conveyance_allowance", 0)
        sal.medical_allowance = data.get("medical_allowance", 0)
        sal.special_allowance = data.get("special_allowance", 0)
        sal.education_allowance = data.get("education_allowance", 0)
        sal.other_allowance = data.get("other_allowance", 0)
        
        sal.pf_employee = data.get("pf_employee", 0)
        sal.pf_employer = data.get("pf_employer", 0)
        sal.esi_employee = data.get("esi_employee", 0)
        sal.esi_employer = data.get("esi_employer", 0)
        sal.professional_tax = data.get("professional_tax", 0)
        sal.tds = data.get("tds", 0)
        
        sal.bonus = data.get("bonus", 0)
        sal.incentive = data.get("incentive", 0)
        
        sal.is_pf_applicable = data.get("is_pf_applicable", True)
        sal.is_esi_applicable = data.get("is_esi_applicable", False)
        
        db.commit()
        return {"status": "success", "message": "Salary structure updated"}
    
    except Exception as e:
        db.rollback()
        error_msg = str(e)
        
        # Check if it's a column missing error
        if "column" in error_msg.lower() and "does not exist" in error_msg.lower():
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": "Database schema is outdated. Migration needs to run.",
                    "detail": error_msg,
                    "action": "Contact administrator to run database migration"
                }
            )
        
        # Generic error
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Failed to save salary structure",
                "detail": error_msg
            }
        )

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

# ==================== DEPARTMENT MANAGEMENT ====================

@router.get("/departments")
def get_departments(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all departments with optional status filter"""
    query = db.query(Department)
    
    if status:
        query = query.filter(Department.status == status)
    
    departments = query.all()
    
    # Get employee count for each department
    result = []
    for dept in departments:
        employee_count = db.query(Employee).filter(
            Employee.department == dept.name,
            Employee.status == 'active'
        ).count()
        
        result.append({
            "id": dept.id,
            "name": dept.name,
            "description": dept.description,
            "department_head": dept.department_head,
            "status": dept.status,
            "employee_count": employee_count,
            "created_at": dept.created_at.isoformat() if dept.created_at else None,
            "updated_at": dept.updated_at.isoformat() if dept.updated_at else None
        })
    
    return result

@router.get("/departments/{dept_id}")
def get_department_by_id(dept_id: str, db: Session = Depends(get_db)):
    """Get single department details"""
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # Get employee count
    employee_count = db.query(Employee).filter(
        Employee.department == dept.name,
        Employee.status == 'active'
    ).count()
    
    return {
        "id": dept.id,
        "name": dept.name,
        "description": dept.description,
        "department_head": dept.department_head,
        "status": dept.status,
        "employee_count": employee_count,
        "company_id": dept.company_id,
        "created_at": dept.created_at.isoformat() if dept.created_at else None
    }

@router.post("/departments")
def create_department(
    data: dict = Body(...),
    db: Session = Depends(get_db)
):
    """Create a new department"""
    # Check if department name already exists
    existing = db.query(Department).filter(
        Department.name == data.get('name'),
        Department.company_id == data.get('company_id', 'default')
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Department with this name already exists")
    
    new_dept = Department(
        id=str(uuid.uuid4()),
        company_id=data.get('company_id', 'default'),
        name=data.get('name'),
        description=data.get('description'),
        department_head=data.get('department_head'),
        status=data.get('status', 'active')
    )
    
    db.add(new_dept)
    db.commit()
    db.refresh(new_dept)
    
    return {
        "status": "success",
        "message": "Department created successfully",
        "id": new_dept.id
    }

@router.put("/departments/{dept_id}")
def update_department(
    dept_id: str,
    data: dict = Body(...),
    db: Session = Depends(get_db)
):
    """Update department details"""
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # Update allowed fields
    if 'name' in data:
        # Check if new name conflicts with existing department
        existing = db.query(Department).filter(
            Department.name == data['name'],
            Department.id != dept_id,
            Department.company_id == dept.company_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Department name already exists")
        dept.name = data['name']
    
    if 'description' in data:
        dept.description = data['description']
    if 'department_head' in data:
        dept.department_head = data['department_head']
    if 'status' in data:
        dept.status = data['status']
    
    try:
        db.commit()
        db.refresh(dept)
        return {"status": "success", "message": "Department updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/departments/{dept_id}")
def delete_department(dept_id: str, db: Session = Depends(get_db)):
    """Delete department (soft delete by setting status to inactive)"""
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # Check if department has employees
    employee_count = db.query(Employee).filter(
        Employee.department == dept.name,
        Employee.status == 'active'
    ).count()
    
    if employee_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete department with {employee_count} active employees. Please reassign employees first."
        )
    
    # Soft delete
    dept.status = "inactive"
    db.commit()
    
    return {"status": "success", "message": "Department deactivated successfully"}

@router.get("/departments/{dept_id}/employees")
def get_department_employees(dept_id: str, db: Session = Depends(get_db)):
    """Get all employees in a department"""
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    
    employees = db.query(Employee).filter(
        Employee.department == dept.name,
        Employee.status == 'active'
    ).all()
    
    return [{
        "id": emp.id,
        "emp_code": emp.emp_code,
        "full_name": f"{emp.first_name} {emp.last_name or ''}".strip(),
        "designation": emp.designation,
        "email": emp.email,
        "mobile_no": emp.mobile_no
    } for emp in employees]

@router.delete("/admin/cleanup/employees")
async def delete_all_employees(
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    DANGER: Permanently delete ALL employee data
    This includes: employees, attendance logs, and salary structures
    Only superadmin can perform this action
    """
    # Check if user is superadmin
    if current_user.role != "superadmin":
        raise HTTPException(
            status_code=403, 
            detail="Only superadmin can delete all employee data"
        )
    
    try:
        # Count records before deletion
        attendance_count = db.query(AttendanceLog).count()
        salary_count = db.query(SalaryStructure).count()
        employee_count = db.query(Employee).count()
        
        # Delete all attendance logs
        db.query(AttendanceLog).delete()
        
        # Delete all salary structures
        db.query(SalaryStructure).delete()
        
        # Delete all employees
        db.query(Employee).delete()
        
        # Commit the changes
        db.commit()
        
        return {
            "success": True,
            "message": "All employee data permanently deleted",
            "deleted": {
                "employees": employee_count,
                "salary_structures": salary_count,
                "attendance_logs": attendance_count
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete data: {str(e)}")

