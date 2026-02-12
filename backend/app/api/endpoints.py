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
from ..models.models import Employee, AttendanceLog, SalaryStructure, AdminUser, Department, Payroll, PayrollStatus
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

@router.post("/debug/fix-salary-schema")
def fix_salary_schema(db: Session = Depends(get_db)):
    """Add missing columns to salary_structures table"""
    from sqlalchemy import inspect, text
    
    try:
        inspector = inspect(engine)
        
        if 'salary_structures' not in inspector.get_table_names():
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "salary_structures table does not exist"}
            )
        
        columns = inspector.get_columns('salary_structures')
        column_names = [col['name'] for col in columns]
        
        # Define all required columns with their SQL types
        required_columns = {
            'special_allowance': 'NUMERIC(12, 2) DEFAULT 0.0',
            'professional_tax': 'NUMERIC(12, 2) DEFAULT 0.0',
            'hra': 'NUMERIC(12, 2) DEFAULT 0.0',
            'conveyance_allowance': 'NUMERIC(12, 2) DEFAULT 0.0',
            'medical_allowance': 'NUMERIC(12, 2) DEFAULT 0.0',
            'education_allowance': 'NUMERIC(12, 2) DEFAULT 0.0',
            'other_allowance': 'NUMERIC(12, 2) DEFAULT 0.0',
            'pf_employee': 'NUMERIC(12, 2) DEFAULT 0.0',
            'pf_employer': 'NUMERIC(12, 2) DEFAULT 0.0',
            'esi_employee': 'NUMERIC(12, 2) DEFAULT 0.0',
            'esi_employer': 'NUMERIC(12, 2) DEFAULT 0.0',
            'tds': 'NUMERIC(12, 2) DEFAULT 0.0',
            'bonus': 'NUMERIC(12, 2) DEFAULT 0.0',
            'incentive': 'NUMERIC(12, 2) DEFAULT 0.0',
            'is_pf_applicable': 'BOOLEAN DEFAULT TRUE',
            'is_esi_applicable': 'BOOLEAN DEFAULT FALSE'
        }
        
        added = []
        skipped = []
        errors = []
        
        with engine.connect() as conn:
            for col_name, col_type in required_columns.items():
                if col_name not in column_names:
                    try:
                        sql = f"ALTER TABLE salary_structures ADD COLUMN {col_name} {col_type}"
                        conn.execute(text(sql))
                        conn.commit()
                        added.append(col_name)
                    except Exception as e:
                        errors.append({"column": col_name, "error": str(e)})
                else:
                    skipped.append(col_name)
        
        return {
            "status": "success" if not errors else "partial",
            "added_columns": added,
            "skipped_columns": skipped,
            "errors": errors,
            "message": f"Added {len(added)} columns, skipped {len(skipped)} existing columns"
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

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
            
            # Calculate total hours worked
            if existing_log.check_in:
                # Ensure check_in is timezone aware or handle naive
                check_in_time = existing_log.check_in
                if check_in_time.tzinfo is None:
                    # If check_in stored as naive UTC (common in some setups), localize it
                    # But here likely it's already relevant to the session or DB type
                    pass 
                
                # Simple calculation if both are aware or both naive
                # Simple calculation if both are aware or both naive
                # Simple calculation if both are aware or both naive
                try:
                    # Normalize timestamps to ensure compatibility
                    check_in_time = existing_log.check_in
                    
                    # If check_in is naive (no timezone), assume it matches now_ist's timezone (IST)
                    # This happens with some DBs like SQLite that strip timezone info
                    if check_in_time.tzinfo is None:
                        check_in_time = check_in_time.replace(tzinfo=now_ist.tzinfo)
                    
                    duration = now_ist - check_in_time
                    raw_hours = duration.total_seconds() / 3600
                    
                    print(f"⏱️ Time Calc - In: {check_in_time}, Out: {now_ist}")
                    print(f"⏱️ Raw Duration: {raw_hours:.2f} hours")
                    
                    # Tiffin/Break Deduction (30 mins = 0.5 hours)
                    deduction = 0.5
                    net_hours = max(0, raw_hours - deduction)
                    
                    existing_log.total_hours_worked = round(net_hours, 2)
                    print(f"✅ Net Hours (after {deduction}h deduction): {existing_log.total_hours_worked}")
                    
                    # Enhanced OT Calculation
                    # Check if weekend (Saturday=5, Sunday=6)
                    is_weekend = now_ist.weekday() >= 5
                    
                    # Standard work day (Net hours)
                    # Assuming 8 hours is the standard full day after break
                    standard_work_hours = 8.0
                    
                    if is_weekend:
                         # Weekend OT
                         existing_log.ot_weekend_hours = round(net_hours, 2)
                         existing_log.ot_hours = 0.0
                    else:
                        # Weekday OT
                        if net_hours > standard_work_hours:
                            raw_ot = net_hours - standard_work_hours
                            
                            # Rule: Minimum 2 hours OT required
                            if raw_ot < 2.0:
                                existing_log.ot_hours = 0.0
                            # Rule: OT slots of 2 hours.
                            elif raw_ot < 4.0:
                                existing_log.ot_hours = 2.0
                            # Rule: Maximum OT cap at 4 hours
                            else:
                                existing_log.ot_hours = 4.0
                        else:
                            existing_log.ot_hours = 0.0
                            
                except Exception as e:
                    print(f"❌ Error calculating hours: {e}")
                    import traceback
                    traceback.print_exc()
            
            db.commit()
            
            return {
                "status": "success",
                "employee": matched_emp.first_name,
                "emp_code": matched_emp.emp_code,
                "check_out_time": now_ist.strftime('%I:%M %p'),
                "total_hours": existing_log.total_hours_worked,
                "ot_hours": existing_log.ot_hours if not is_weekend else existing_log.ot_weekend_hours
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
    try:
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
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Error fetching employees: {e}\n{error_trace}")
        print(f"Error fetching employees: {e}\n{error_trace}")
        raise HTTPException(status_code=500, detail=str(e))

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
    try:
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
        except Exception:
            pass

        return {
            "total_employees": total_employees,
            "present_today": present_count,
            "absent_today": absent_count,
            "recent_activity": recent_activity,
            "department_breakdown": department_breakdown, # Fixed key name to match frontend expectation
            "employee_type_breakdown": [] # TODO: Add this stats query
        }
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Error fetching dashboard stats: {e}\n{error_trace}")
        print(f"Error fetching dashboard stats: {e}\n{error_trace}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/payroll/generate")
def generate_payroll(
    month: int = Body(..., ge=1, le=12),
    year: int = Body(..., ge=2000, le=2100),
    db: Session = Depends(get_db)
):
    """
    Generate payroll for all active employees for a specific month/year.
    Calculates salaries based on attendance logs.
    """
    from sqlalchemy import extract
    import calendar
    
    # 1. Get all active employees with salary structure
    employees = db.query(Employee).filter(
        Employee.status == 'active'
    ).all()
    
    generated_count = 0
    errors = []
    
    total_days_in_month = calendar.monthrange(year, month)[1]
    
    for emp in employees:
        try:
            if not emp.salary_structure:
                errors.append(f"Skipped {emp.emp_code}: No salary structure found")
                continue
                
            # 2. Fetch Attendance Logs for the month
            logs = db.query(AttendanceLog).filter(
                AttendanceLog.employee_id == emp.id,
                extract('month', AttendanceLog.date) == month,
                extract('year', AttendanceLog.date) == year
            ).all()
            
            # 3. Aggregate Attendance
            # Create a map of date -> log for quick lookup
            logs_by_date = {log.date: log for log in logs}
            
            real_present = 0.0
            paid_days = 0.0
            
            # Check safely for hourly based status
            is_worker_type = getattr(emp.salary_structure, 'is_hourly_based', False)
            
            import datetime
            
            for day in range(1, total_days_in_month + 1):
                current_date = datetime.date(year, month, day)
                is_weekend = current_date.weekday() >= 5 # 5=Sat, 6=Sun
                
                log = logs_by_date.get(current_date)
                
                if log:
                    # Present/Half-day/Leave
                    status = log.status.lower() if log.status else ""
                    if status == 'present':
                        real_present += 1.0
                        paid_days += 1.0
                    elif status == 'half_day':
                        real_present += 0.5
                        paid_days += 0.5
                    elif status in ['leave_paid', 'holiday', 'weekend']: 
                        # Explicit paid statuses if logged
                        paid_days += 1.0 
                    # If absent/unpaid_leave, add 0
                else:
                    # No log
                    if not is_worker_type and is_weekend:
                        paid_days += 1.0
                    # Else (Worker or Staff Weekday): 0 (Absent/Unpaid)
            
            total_ot_hours = sum(float(log.ot_hours or 0) for log in logs)
            total_ot_weekend = sum(float(log.ot_weekend_hours or 0) for log in logs)
            total_ot_holiday = sum(float(log.ot_holiday_hours or 0) for log in logs)
            
            attendance_summary = {
                "total_days_in_month": total_days_in_month,
                "present_days": real_present,
                "ot_hours": total_ot_hours,
                "ot_weekend_hours": total_ot_weekend,
                "ot_holiday_hours": total_ot_holiday,
                "paid_days": paid_days, 
                "loan_deduction": 0 # TODO: Fetch from loan table if exists
            }
            
            # 4. Calculate Salary
            # Convert SQLAlchemy model to dict for service
            structure_dict = {c.name: getattr(emp.salary_structure, c.name) for c in emp.salary_structure.__table__.columns}
            
            result = payroll_service.calculate_net_salary(
                structure_dict, 
                attendance_summary, 
                employee_type=emp.employee_type or "full_time"
            )
            
            if "error" in result:
                errors.append(f"Error for {emp.emp_code}: {result['error']}")
                continue
                
            payroll_data = result["payroll"]
            
            # 5. Save/Update Payroll Record
            # Check if exists
            existing_payroll = db.query(Payroll).filter(
                Payroll.employee_id == emp.id,
                Payroll.month == month,
                Payroll.year == year
            ).first()
            
            if existing_payroll:
                if existing_payroll.status == 'locked':
                    errors.append(f"Skipped {emp.emp_code}: Payroll already locked for this month")
                    continue
                payroll_record = existing_payroll
            else:
                payroll_record = Payroll(
                    id=str(uuid.uuid4()),
                    employee_id=emp.id,
                    month=month,
                    year=year
                )
            
            # Update fields
            payroll_record.total_days = total_days_in_month
            payroll_record.working_days = total_days_in_month # Assuming standard? Or strict working days?
            payroll_record.present_days = real_present
            payroll_record.ot_hours = total_ot_hours + total_ot_weekend + total_ot_holiday
            
            payroll_record.basic_earned = payroll_data["earnings"]["basic_earned"] # Use explicit key
            # Mapping result back to model columns
            # Note: payroll_service returns generic structure, model has specific columns
            # We map best effort or update service to match model strictly?
            # Service returns: basic, hra, conveyance, washing, education, other
            earnings = payroll_data["earnings"]
            deductions = payroll_data["deductions"]
            
            payroll_record.basic_earned = earnings.get("basic_earned", 0)
            payroll_record.hra_earned = earnings.get("hra", 0)
            payroll_record.conveyance_earned = earnings.get("conveyance", 0)
            payroll_record.washing_allowance = earnings.get("washing", 0)
            
            # Group other allowances into the single column 'other_allowances'
            # Include: Medical, Special, Education, Other, Bonus, Incentive
            other_total = (
                earnings.get("medical", 0) +
                earnings.get("special", 0) +
                earnings.get("education", 0) +
                earnings.get("other", 0) +
                earnings.get("bonus", 0) +
                earnings.get("incentive", 0)
            )
            payroll_record.other_allowances = other_total
            
            payroll_record.gross_salary = earnings.get("gross_salary", 0)
            
            payroll_record.pf_amount = deductions.get("pf", 0)
            payroll_record.esi_amount = deductions.get("esi", 0)
            payroll_record.pt_amount = deductions.get("pt", 0)
            payroll_record.welfare_fund = deductions.get("welfare", 0)
            payroll_record.loan_deduction = deductions.get("loan", 0)
            payroll_record.total_deductions = deductions.get("total_deduction", 0)
            
            payroll_record.net_salary = payroll_data["net_salary"]
            payroll_record.status = "draft"
            
            db.add(payroll_record)
            generated_count += 1
            
        except Exception as e:
            errors.append(f"Failed {emp.emp_code}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    db.commit()
    
    return {
        "status": "success",
        "message": f"Generated payroll for {generated_count} employees",
        "errors": errors
    }

@router.post("/payroll/generate/{emp_id}")
def generate_single_payroll(
    emp_id: str,
    month: int = Body(..., ge=1, le=12),
    year: int = Body(..., ge=2000, le=2100),
    db: Session = Depends(get_db)
):
    """Generate payroll for a single employee"""
    from sqlalchemy import extract
    import calendar
    import datetime
    
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
        
    if not emp.salary_structure:
        raise HTTPException(status_code=400, detail="Employee salary structure not configured")
        
    total_days_in_month = calendar.monthrange(year, month)[1]
    
    # 2. Fetch Attendance Logs
    logs = db.query(AttendanceLog).filter(
        AttendanceLog.employee_id == emp.id,
        extract('month', AttendanceLog.date) == month,
        extract('year', AttendanceLog.date) == year
    ).all()
    
    # 3. Aggregate Attendance
    logs_by_date = {log.date: log for log in logs}
    real_present = 0.0
    paid_days = 0.0
    is_worker_type = getattr(emp.salary_structure, 'is_hourly_based', False)
    
    current_actual_date = datetime.date.today()
    
    for day in range(1, total_days_in_month + 1):
        current_date = datetime.date(year, month, day)
        
        # Don't count future days
        if current_date > current_actual_date:
            continue
            
        is_weekend = current_date.weekday() >= 5
        log = logs_by_date.get(current_date)
        
        if log:
            status = log.status.lower() if log.status else ""
            if status == 'present':
                real_present += 1.0
                paid_days += 1.0
            elif status == 'half_day':
                real_present += 0.5
                paid_days += 0.5
            elif status in ['leave_paid', 'holiday', 'weekend']: 
                paid_days += 1.0 
        else:
            if not is_worker_type and is_weekend:
                paid_days += 1.0
    
    total_ot_hours = sum(float(log.ot_hours or 0) for log in logs)
    total_ot_weekend = sum(float(log.ot_weekend_hours or 0) for log in logs)
    total_ot_holiday = sum(float(log.ot_holiday_hours or 0) for log in logs)
    
    attendance_summary = {
        "total_days_in_month": total_days_in_month,
        "present_days": real_present,
        "ot_hours": total_ot_hours,
        "ot_weekend_hours": total_ot_weekend,
        "ot_holiday_hours": total_ot_holiday,
        "paid_days": paid_days,
        "loan_deduction": 0
    }
    
    # 4. Calculate Salary
    structure_dict = {c.name: getattr(emp.salary_structure, c.name) for c in emp.salary_structure.__table__.columns}
    
    result = payroll_service.calculate_net_salary(
        structure_dict, 
        attendance_summary, 
        employee_type=emp.employee_type or "full_time"
    )
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result['error'])
        
    payroll_data = result["payroll"]
    
    # 5. Save/Update Payroll Record
    existing_payroll = db.query(Payroll).filter(
        Payroll.employee_id == emp.id,
        Payroll.month == month,
        Payroll.year == year
    ).first()
    
    if existing_payroll:
        if existing_payroll.status == 'locked':
             raise HTTPException(status_code=400, detail="Payroll already locked for this month")
        payroll_record = existing_payroll
    else:
        payroll_record = Payroll(
            id=str(uuid.uuid4()),
            employee_id=emp.id,
            month=month,
            year=year
        )
    
    payroll_record.total_days = total_days_in_month
    payroll_record.working_days = total_days_in_month
    payroll_record.present_days = real_present
    payroll_record.ot_hours = total_ot_hours + total_ot_weekend + total_ot_holiday
    
    earnings = payroll_data["earnings"]
    deductions = payroll_data["deductions"]
    
    payroll_record.basic_earned = earnings.get("basic_earned", 0)
    payroll_record.hra_earned = earnings.get("hra", 0)
    payroll_record.conveyance_earned = earnings.get("conveyance", 0)
    payroll_record.washing_allowance = earnings.get("washing", 0)
    
    other_total = (
        earnings.get("medical", 0) +
        earnings.get("special", 0) +
        earnings.get("education", 0) +
        earnings.get("other", 0) +
        earnings.get("bonus", 0) +
        earnings.get("incentive", 0)
    )
    payroll_record.other_allowances = other_total
    
    payroll_record.gross_salary = earnings.get("gross_salary", 0)
    
    payroll_record.pf_amount = deductions.get("pf", 0)
    payroll_record.esi_amount = deductions.get("esi", 0)
    payroll_record.pt_amount = deductions.get("pt", 0)
    payroll_record.welfare_fund = deductions.get("welfare", 0)
    payroll_record.loan_deduction = deductions.get("loan", 0)
    payroll_record.total_deductions = deductions.get("total_deduction", 0)
    
    payroll_record.net_salary = payroll_data["net_salary"]
    payroll_record.status = "draft"
    
    if not existing_payroll:
        db.add(payroll_record)
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
        
    return {"status": "success", "message": "Payroll generated successfully", "net_salary": payroll_record.net_salary}

@router.get("/payroll/list")
def get_payrolls(
    month: Optional[int] = None,
    year: Optional[int] = None,
    employee_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Payroll).join(Employee)
    
    if month:
        query = query.filter(Payroll.month == month)
    if year:
        query = query.filter(Payroll.year == year)
    if employee_id:
        query = query.filter(Payroll.employee_id == employee_id)
        
    payrolls = query.all()
    
    return [{
        "id": p.id,
        "employee_id": p.employee_id,
        "emp_code": p.employee.emp_code,
        "employee_name": p.employee.first_name + " " + (p.employee.last_name or ""),
        "department": getattr(p.employee, 'department', ''),
        "employee_type": getattr(p.employee, 'employee_type', 'full_time'),
        "month": p.month,
        "year": p.year,
        "working_days": float(p.working_days),
        "present_days": float(p.present_days),
        "ot_hours": float(p.ot_hours),
        
        # Earnings
        "basic_earned": float(p.basic_earned),
        "hra_earned": float(p.hra_earned) if p.hra_earned else 0,
        "conveyance_earned": float(p.conveyance_earned) if p.conveyance_earned else 0,
        "washing_allowance": float(p.washing_allowance) if p.washing_allowance else 0,
        "other_allowances": float(p.other_allowances) if p.other_allowances else 0,
        "gross_salary": float(p.gross_salary),
        
        # Derived for display if needed
        "ot_amount": float(p.gross_salary) - (float(p.basic_earned) + float(p.hra_earned or 0) + float(p.conveyance_earned or 0) + float(p.washing_allowance or 0) + float(p.other_allowances or 0)), # Approx if OT not stored explicitly as amount
                
        # Deductions
        "pf_amount": float(p.pf_amount) if p.pf_amount else 0,
        "esi_amount": float(p.esi_amount) if p.esi_amount else 0,
        "pt_amount": float(p.pt_amount) if p.pt_amount else 0,
        "welfare_fund": float(p.welfare_fund) if p.welfare_fund else 0,
        "loan_deduction": float(p.loan_deduction) if p.loan_deduction else 0,
        "total_deductions": float(p.total_deductions),
        
        "net_salary": float(p.net_salary),
        "status": p.status
    } for p in payrolls]

@router.get("/payroll/employee/{emp_id}")
def get_employee_payroll(
    emp_id: str,
    month: Optional[int] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Get employee type
    employee_type = getattr(emp, 'employee_type', 'full_time')
        
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
            "is_esi_applicable": False,
            "is_hourly_based": False,
            "hourly_rate": 0,
            "contract_rate_per_day": 0,
            "ot_rate_multiplier": 1.5,
            "ot_weekend_multiplier": 2.0,
            "ot_holiday_multiplier": 2.5
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
            "is_esi_applicable": sal.is_esi_applicable if hasattr(sal, 'is_esi_applicable') else False,
            "is_hourly_based": sal.is_hourly_based if hasattr(sal, 'is_hourly_based') else False,
            "hourly_rate": float(sal.hourly_rate) if hasattr(sal, 'hourly_rate') and sal.hourly_rate else 0,
            "contract_rate_per_day": float(sal.contract_rate_per_day) if hasattr(sal, 'contract_rate_per_day') and sal.contract_rate_per_day else 0,
            "ot_rate_multiplier": float(sal.ot_rate_multiplier) if hasattr(sal, 'ot_rate_multiplier') and sal.ot_rate_multiplier else 1.5,
            "ot_weekend_multiplier": float(sal.ot_weekend_multiplier) if hasattr(sal, 'ot_weekend_multiplier') and sal.ot_weekend_multiplier else 2.0,
            "ot_holiday_multiplier": float(sal.ot_holiday_multiplier) if hasattr(sal, 'ot_holiday_multiplier') and sal.ot_holiday_multiplier else 2.5
        }
    
    # Calculate Attendance for Target Month
    import datetime
    current_actual_date = datetime.date.today()
    
    if month and year:
        # Create date object for the 1st of the requested month
        target_date = datetime.date(year, month, 1)
    else:
        target_date = current_actual_date

    # start_date = target_date.replace(day=1) # Not used?
    
    import calendar
    from sqlalchemy import extract
    total_days_in_month = calendar.monthrange(target_date.year, target_date.month)[1]
    
    # Fetch all logs for the month
    month_logs = db.query(AttendanceLog).filter(
        AttendanceLog.employee_id == emp_id,
        extract('month', AttendanceLog.date) == target_date.month,
        extract('year', AttendanceLog.date) == target_date.year
    ).all()
    
    # Aggregate Attendance Logic
    logs_by_date = {log.date: log for log in month_logs}
    
    real_present = 0.0
    paid_days = 0.0
    
    # Check safely for hourly based status
    is_worker_type = False
    if sal and hasattr(sal, 'is_hourly_based'):
        is_worker_type = sal.is_hourly_based
    
    for day in range(1, total_days_in_month + 1):
        loop_date = datetime.date(target_date.year, target_date.month, day)
        
        # Don't count days strictly in the ACTUAL future for attendance presence
        # e.g. if today is Feb 17, don't auto-mark Feb 18 as absent/present unless log exists (unlikely)
        if loop_date > current_actual_date:
            continue
            
        is_weekend = loop_date.weekday() >= 5 # 5=Sat, 6=Sun
        
        log = logs_by_date.get(loop_date)
        
        if log:
            # Present/Half-day/Leave
            status = log.status.lower() if log.status else ""
            if status == 'present':
                real_present += 1.0
                paid_days += 1.0
            elif status == 'half_day':
                real_present += 0.5
                paid_days += 0.5
            elif status in ['leave_paid', 'holiday', 'weekend']: 
                paid_days += 1.0 
        else:
            # No log
            if not is_worker_type and is_weekend:
                paid_days += 1.0
            # Else (Worker or Staff Weekday): 0 (Absent/Unpaid)
    
    # OT Aggregation from logs
    ot_hours = sum(float(log.ot_hours or 0) for log in month_logs)
    ot_weekend_hours = sum(float(log.ot_weekend_hours or 0) for log in month_logs)
    ot_holiday_hours = sum(float(log.ot_holiday_hours or 0) for log in month_logs)
    
    attendance = {
        "total_days_in_month": total_days_in_month,
        "present_days": real_present,
        "paid_days": paid_days,
        "ot_hours": ot_hours,
        "ot_weekend_hours": ot_weekend_hours,
        "ot_holiday_hours": ot_holiday_hours
    }
    
    # Calculate payroll with employee type
    result = payroll_service.calculate_net_salary(salary_struct, attendance, employee_type)
    
    return {
        "employee_id": emp.id,
        "employee_name": f"{emp.first_name} {emp.last_name or ''}",
        "employee_type": employee_type,
        "month": target_date.strftime("%B %Y"),
        "present_days": real_present,
        "rates": {
            "hourly_rate": salary_struct.get("hourly_rate"),
            "contract_rate_per_day": salary_struct.get("contract_rate_per_day"),
            "base_hourly_rate": 0,
            "ot_rate_multiplier": salary_struct.get("ot_rate_multiplier"),
            "ot_weekend_multiplier": salary_struct.get("ot_weekend_multiplier"),
            "ot_holiday_multiplier": salary_struct.get("ot_holiday_multiplier")
        },
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
            "confidence": float(log.confidence_score) if log.confidence_score else None,
            "total_hours_worked": float(log.total_hours_worked) if log.total_hours_worked else 0,
            "ot_hours": float(log.ot_hours) if log.ot_hours else 0,
            "ot_weekend_hours": float(log.ot_weekend_hours) if log.ot_weekend_hours else 0,
            "ot_holiday_hours": float(log.ot_holiday_hours) if log.ot_holiday_hours else 0
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
        writer.writerow(['Date', 'Employee Name', 'Employee Code', 'Department', 'Check In', 'Check Out', 'Status', 'Total Hours', 'OT Hours', 'Weekend OT', 'Holiday OT', 'Confidence Score'])
        
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
                f"{float(log.total_hours_worked):.2f}" if log.total_hours_worked else '0.00',
                f"{float(log.ot_hours):.2f}" if log.ot_hours else '0.00',
                f"{float(log.ot_weekend_hours):.2f}" if log.ot_weekend_hours else '0.00',
                f"{float(log.ot_holiday_hours):.2f}" if log.ot_holiday_hours else '0.00',
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
            "is_esi_applicable": False,
            "is_hourly_based": False,
            "hourly_rate": 0,
            "contract_rate_per_day": 0,
            "ot_rate_multiplier": 1.5,
            "ot_weekend_multiplier": 2.0,
            "ot_holiday_multiplier": 2.5
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
        "is_esi_applicable": sal.is_esi_applicable if hasattr(sal, 'is_esi_applicable') else False,
        "is_hourly_based": sal.is_hourly_based if hasattr(sal, 'is_hourly_based') else False,
        "hourly_rate": float(sal.hourly_rate) if hasattr(sal, 'hourly_rate') and sal.hourly_rate else 0,
        "contract_rate_per_day": float(sal.contract_rate_per_day) if hasattr(sal, 'contract_rate_per_day') and sal.contract_rate_per_day else 0,
        "ot_rate_multiplier": float(sal.ot_rate_multiplier) if hasattr(sal, 'ot_rate_multiplier') and sal.ot_rate_multiplier else 1.5,
        "ot_weekend_multiplier": float(sal.ot_weekend_multiplier) if hasattr(sal, 'ot_weekend_multiplier') and sal.ot_weekend_multiplier else 2.0,
        "ot_holiday_multiplier": float(sal.ot_holiday_multiplier) if hasattr(sal, 'ot_holiday_multiplier') and sal.ot_holiday_multiplier else 2.5
    }

@router.post("/employees/{emp_id}/salary")
def update_employee_salary(
    emp_id: str, 
    data: dict = Body(...),
    db: Session = Depends(get_db)
):
    import traceback
    try:
        logger.info(f"Updating salary for employee {emp_id}")
        logger.info(f"Received data: {data}")
        
        sal = db.query(SalaryStructure).filter(SalaryStructure.employee_id == emp_id).first()
        if not sal:
            logger.info(f"Creating new salary structure for {emp_id}")
            sal = SalaryStructure(id=str(uuid.uuid4()), employee_id=emp_id)
            db.add(sal)
        else:
            logger.info(f"Updating existing salary structure for {emp_id}")
        
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
        
        # New fields for part-time/contract workers and OT
        if hasattr(sal, 'is_hourly_based'):
            sal.is_hourly_based = data.get("is_hourly_based", False)
        if hasattr(sal, 'hourly_rate'):
            sal.hourly_rate = data.get("hourly_rate", 0)
        if hasattr(sal, 'contract_rate_per_day'):
            sal.contract_rate_per_day = data.get("contract_rate_per_day", 0)
        if hasattr(sal, 'ot_rate_multiplier'):
            sal.ot_rate_multiplier = data.get("ot_rate_multiplier", 1.5)
        if hasattr(sal, 'ot_weekend_multiplier'):
            sal.ot_weekend_multiplier = data.get("ot_weekend_multiplier", 2.0)
        if hasattr(sal, 'ot_holiday_multiplier'):
            sal.ot_holiday_multiplier = data.get("ot_holiday_multiplier", 2.5)
        
        logger.info("Committing salary structure to database...")
        db.commit()
        logger.info("✅ Salary structure saved successfully")
        return {"status": "success", "message": "Salary structure updated"}
    
    except Exception as e:
        db.rollback()
        error_msg = str(e)
        error_trace = traceback.format_exc()
        
        # Log to both logger and stdout for visibility
        print(f"\n{'='*60}")
        print(f"ERROR SAVING SALARY STRUCTURE")
        print(f"{'='*60}")
        print(f"Employee ID: {emp_id}")
        print(f"Error: {error_msg}")
        print(f"Traceback:\n{error_trace}")
        print(f"{'='*60}\n")
        
        logger.error(f"❌ Error saving salary structure: {error_msg}")
        logger.error(f"Full traceback:\n{error_trace}")
        
        # Check if it's a column missing error
        if "column" in error_msg.lower() and "does not exist" in error_msg.lower():
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": "Database schema is outdated. Migration needs to run.",
                    "detail": error_msg,
                    "traceback": error_trace,
                    "action": "Contact administrator to run database migration"
                }
            )
        
        # Generic error
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Failed to save salary structure",
                "detail": error_msg,
                "traceback": error_trace
            }
        )

@router.get("/payroll/summary")
def get_payroll_summary(
    month: Optional[int] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get aggregated payroll statistics for a specific month/year"""
    from sqlalchemy import func
    
    if not month:
        month = datetime.date.today().month
    if not year:
        year = datetime.date.today().year
        
    # Query Payroll table
    query = db.query(Payroll).filter(
        Payroll.month == month,
        Payroll.year == year
    )
    
    payrolls = query.all()
    
    total_employees = len(payrolls)
    total_gross = sum(p.gross_salary for p in payrolls)
    total_net = sum(p.net_salary for p in payrolls)
    total_pf = sum(p.pf_amount for p in payrolls)
    total_esi = sum(p.esi_amount for p in payrolls)
    total_welfare = sum(p.welfare_fund for p in payrolls)
    
    # Breakdown by Status
    status_counts = {}
    for p in payrolls:
        status_counts[p.status] = status_counts.get(p.status, 0) + 1
        
    return {
        "month": month,
        "year": year,
        "total_employees": total_employees,
        "total_gross_salary": float(total_gross),
        "total_net_salary": float(total_net),
        "total_pf_deduction": float(total_pf),
        "total_esi_deduction": float(total_esi),
        "total_welfare_deduction": float(total_welfare),
        "status_breakdown": status_counts
    }

@router.get("/payroll/payslip/{emp_id}/pdf")
def download_payslip_pdf(
    emp_id: str, 
    month: Optional[int] = None, 
    year: Optional[int] = None, 
    db: Session = Depends(get_db)
):
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
        
    # Determine period
    if not month or not year:
        today = datetime.date.today()
        month = today.month
        year = today.year
    else:
        today = datetime.date(year, month, 1) # Placeholder for display
        # If looking at past month, use last day of that month for display date?
        import calendar
        last_day = calendar.monthrange(year, month)[1]
        today = datetime.date(year, month, last_day)

    # 1. Try to fetch existing Payroll Record
    payroll_record = db.query(Payroll).filter(
        Payroll.employee_id == emp_id,
        Payroll.month == month,
        Payroll.year == year
    ).first()
    
    payroll_data = {}
    
    if payroll_record:
        # Use stored data
        payroll_data = {
            "earnings": {
                "Basic Salary": float(payroll_record.basic_earned),
                "HRA": float(payroll_record.hra_earned or 0),
                "Conveyance": float(payroll_record.conveyance_earned or 0),
                "Washing Allowance": float(payroll_record.washing_allowance or 0),
                "Other Allowances": float(payroll_record.other_allowances or 0), # Grouped in DB
                "Overtime": float(payroll_record.gross_salary) - (float(payroll_record.basic_earned) + float(payroll_record.hra_earned or 0) + float(payroll_record.conveyance_earned or 0) + float(payroll_record.washing_allowance or 0) + float(payroll_record.other_allowances or 0)), # Derive OT roughly or store it?
                # improved derivation: Gross - (Sum of known earnings)
            },
            "deductions": {
                "Provident Fund": float(payroll_record.pf_amount or 0),
                "ESI": float(payroll_record.esi_amount or 0),
                "Professional Tax": float(payroll_record.pt_amount or 0),
                "Welfare Fund": float(payroll_record.welfare_fund or 0),
                "Loan Deduction": float(payroll_record.loan_deduction or 0),
            },
            "gross": float(payroll_record.gross_salary),
            "total_deductions": float(payroll_record.total_deductions),
            "net": float(payroll_record.net_salary),
            "present_days": float(payroll_record.present_days),
            "total_days": float(payroll_record.working_days),
            "ot_hours": float(payroll_record.ot_hours)
        }
        
        # Refine Earnings Key Names
        # To match the "Other Allowances" grouping in DB, we might want to split if needed, 
        # but DB only stores the aggregate. So display as "Other Allowances".
        pass
        
    else:
        # 2. Calculate On-the-Fly (Draft)
        sal = db.query(SalaryStructure).filter(SalaryStructure.employee_id == emp_id).first()
        if not sal:
             # Basic Fallback
             payroll_data = { "earnings": {"Basic": 0}, "deductions": {}, "gross": 0, "net": 0, "present_days": 0, "total_days": 30, "ot_hours": 0 }
        else:
            # Construct Salary Struct
            salary_struct = {c.name: getattr(sal, c.name) for c in sal.__table__.columns}
            
            # Calculate Attendance (Reusing Logic)
            import calendar
            total_days_in_month = calendar.monthrange(year, month)[1]
            month_logs = db.query(AttendanceLog).filter(
                AttendanceLog.employee_id == emp_id,
                extract('month', AttendanceLog.date) == month,
                extract('year', AttendanceLog.date) == year
            ).all()
            
            logs_by_date = {log.date: log for log in month_logs}
            real_present = 0.0
            paid_days = 0.0
            is_worker_type = getattr(sal, 'is_hourly_based', False)
            
            for day in range(1, total_days_in_month + 1):
                d_date = datetime.date(year, month, day)
                # Count everything up to end of month (even if future, assume absent/unpaid? Or projected?)
                # For "Draft", usually calculate based on passed days or assume perfect?
                # Let's count *up to today*.
                if d_date > datetime.date.today():
                    continue 

                is_weekend = d_date.weekday() >= 5
                log = logs_by_date.get(d_date)
                
                if log:
                    st = log.status.lower() if log.status else ""
                    if st == 'present':
                        real_present += 1.0
                        paid_days += 1.0
                    elif st == 'half_day':
                        real_present += 0.5
                        paid_days += 0.5
                    elif st in ['leave_paid', 'holiday', 'weekend']:
                         paid_days += 1.0
                else:
                    if not is_worker_type and is_weekend:
                        paid_days += 1.0
            
            ot_hours = sum(float(log.ot_hours or 0) for log in month_logs)
            ot_weekend = sum(float(log.ot_weekend_hours or 0) for log in month_logs)
            ot_holiday = sum(float(log.ot_holiday_hours or 0) for log in month_logs)
            
            attendance_summary = {
                "total_days_in_month": total_days_in_month,
                "present_days": real_present,
                "paid_days": paid_days,
                "ot_hours": ot_hours,
                "ot_weekend_hours": ot_weekend, 
                "ot_holiday_hours": ot_holiday
            }
            
            calc_result = payroll_service.calculate_net_salary(salary_struct, attendance_summary, getattr(emp, 'employee_type', 'full_time'))
            
            p_earn = calc_result["payroll"]["earnings"]
            p_ded = calc_result["payroll"]["deductions"]
            
            payroll_data = {
                "earnings": {
                    "Basic Salary": p_earn.get("basic_earned", 0),
                    "HRA": p_earn.get("hra", 0),
                    "Conveyance": p_earn.get("conveyance", 0),
                    "Washing Allowance": p_earn.get("washing", 0),
                    "Medical Allowance": p_earn.get("medical", 0),
                    "Special Allowance": p_earn.get("special", 0),
                    "Education Allowance": p_earn.get("education", 0),
                    "Other Allowances": p_earn.get("other", 0),
                    "Bonus": p_earn.get("bonus", 0),
                    "Incentive": p_earn.get("incentive", 0),
                    "Overtime": p_earn.get("ot_amount", 0)
                },
                "deductions": {
                    "Provident Fund": p_ded.get("pf", 0),
                    "ESI": p_ded.get("esi", 0),
                    "Professional Tax": p_ded.get("pt", 0),
                    "Welfare Fund": p_ded.get("welfare", 0),
                    "Loan Deduction": p_ded.get("loan", 0),
                    "TDS": p_ded.get("tds", 0)
                },
                "gross": p_earn.get("gross_salary", 0),
                "total_deductions": p_ded.get("total_deduction", 0),
                "net": calc_result["payroll"]["net_salary"],
                "present_days": real_present,
                "total_days": total_days_in_month,
                "ot_hours": ot_hours + ot_weekend + ot_holiday
            }

    # --- Generate PDF ---
    filename = f"Payslip_{emp.first_name}_{today.strftime('%b_%Y')}.pdf"
    filepath = f"temp_{filename}"
    
    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4
    
    # 1. Header
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 50, "PAYSLIP")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 70, f"Period: {today.strftime('%B %Y')}")
    
    # 2. Employee Details Box
    c.rect(48, height - 160, width - 96, 80)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(60, height - 100, f"Name: {emp.first_name} {emp.last_name or ''}")
    c.drawString(300, height - 100, f"Designation: {getattr(emp, 'designation', 'N/A')}")
    
    c.setFont("Helvetica", 11)
    c.drawString(60, height - 120, f"ID: {emp.emp_code}")
    c.drawString(300, height - 120, f"Department: {getattr(emp, 'department', 'N/A')}")
    
    c.drawString(60, height - 140, f"Date of Join: {getattr(emp, 'joining_date', 'N/A')}")
    c.drawString(300, height - 140, f"Days Worked: {payroll_data['present_days']}")
    
    # 3. Table Header
    y = height - 190
    c.setFillColor(colors.lightgrey)
    c.rect(48, y - 20, width - 96, 25, fill=1)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(60, y - 13, "EARNINGS")
    c.drawString(240, y - 13, "AMOUNT")
    c.drawString(310, y - 13, "DEDUCTIONS")
    c.drawString(490, y - 13, "AMOUNT")
    
    y -= 35
    start_y = y
    
    # 4. List Items
    # We list side-by-side. 
    earn_items = [(k, v) for k, v in payroll_data["earnings"].items() if v > 0]
    ded_items = [(k, v) for k, v in payroll_data["deductions"].items() if v > 0]
    
    max_items = max(len(earn_items), len(ded_items))
    
    c.setFont("Helvetica", 10)
    
    for i in range(max_items):
        # Earnings Left
        if i < len(earn_items):
            label, amount = earn_items[i]
            c.drawString(60, y, label)
            c.drawRightString(290, y, f"{amount:.2f}")
            
        # Deductions Right
        if i < len(ded_items):
            label, amount = ded_items[i]
            c.drawString(310, y, label)
            c.drawRightString(540, y, f"{amount:.2f}")
            
        y -= 15
    
    # Bottom Lines
    y -= 10
    c.line(48, y, width - 48, y)
    y -= 25
    
    # 5. Totals
    c.setFont("Helvetica-Bold", 11)
    c.drawString(60, y, "Total Earnings")
    c.drawRightString(290, y, f"{payroll_data['gross']:.2f}")
    
    c.drawString(310, y, "Total Deductions")
    c.drawRightString(540, y, f"{payroll_data['total_deductions']:.2f}")
    
    # Net Pay Box
    y -= 40
    c.setFillColor(colors.aliceblue)
    c.rect(48, y - 10, width - 96, 30, fill=1, stroke=1)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(60, y + 2, "NET SALARY PAYABLE")
    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(540, y, f"Rs. {payroll_data['net']:.2f}")
    
    # Footer
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(width / 2, 50, "This is a system generated payslip.")
    
    c.save()
    
    return FileResponse(filepath, media_type='application/pdf', filename=filename)

# ==================== DEPARTMENT MANAGEMENT ====================

@router.get("/departments")
def get_departments(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all departments with optional status filter"""
    try:
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
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Error fetching departments: {e}\n{error_trace}")
        print(f"Error fetching departments: {e}\n{error_trace}") # Print to stdout for visibility
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/departments/{dept_id}")
def get_department_by_id(dept_id: str, db: Session = Depends(get_db)):
    """Get single department details"""
    try:
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
    except Exception as e:
        logger.error(f"Error fetching department {dept_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/departments")
def create_department(
    data: dict = Body(...),
    db: Session = Depends(get_db)
):
    """Create a new department"""
    try:
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
    except Exception as e:
        db.rollback()
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Error creating department: {e}\n{error_trace}")
        print(f"Error creating department: {e}\n{error_trace}")
        raise HTTPException(status_code=500, detail=str(e))

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


@router.post("/debug/recalculate-hours")
def recalculate_hours(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_user)
):
    """
    Force recalculate total hours and OT for logs in the last 'days' (default 30).
    Useful if schema was updated after checkouts.
    """
    try:
        IST = timezone(timedelta(hours=5, minutes=30))
        today = datetime.datetime.now(IST).date()
        start_date = today - timedelta(days=days)
        
        logger.info(f"Recalculating hours from {start_date} to {today}")
        
        logs = db.query(AttendanceLog).filter(
            AttendanceLog.date >= start_date,
            AttendanceLog.check_out != None
        ).all()
        
        count = 0
        updated_count = 0
        
        for log in logs:
            if log.check_in and log.check_out:
                # Normalize check_in
                c_in = log.check_in
                if c_in.tzinfo is None:
                    c_in = c_in.replace(tzinfo=IST)
                else:
                    c_in = c_in.astimezone(IST)
                
                # Normalize check_out
                c_out = log.check_out
                if c_out.tzinfo is None:
                    c_out = c_out.replace(tzinfo=IST)
                else:
                    c_out = c_out.astimezone(IST)
                
                # Calculate duration
                duration = c_out - c_in
                raw_hours = duration.total_seconds() / 3600
                
                # Deduct 0.5 hours (30 mins break)
                deduction = 0.5
                net_hours = max(0, raw_hours - deduction)
                
                old_total = float(log.total_hours_worked or 0)
                
                log.total_hours_worked = round(net_hours, 2)
                
                # OT Calc
                # Use log.date for correct weekday check
                log_date = log.date
                is_weekend = log_date.weekday() >= 5
                standard_work = 8.0
                
                if is_weekend:
                    log.ot_weekend_hours = round(net_hours, 2)
                    log.ot_hours = 0
                else:
                    # Weekday OT Logic
                    if net_hours > standard_work:
                        raw_ot = net_hours - standard_work
                        
                        if raw_ot < 2.0:
                            log.ot_hours = 0.0
                        elif raw_ot < 4.0:
                            log.ot_hours = 2.0
                        else:
                            log.ot_hours = 4.0
                    else:
                        log.ot_hours = 0
                
                count += 1
                if abs(old_total - log.total_hours_worked) > 0.01:
                    updated_count += 1
        
        db.commit()
        return {
            "status": "success", 
            "message": f"Processed {count} logs. Updated {updated_count} records from {start_date} to {today}"
        }
        
    except Exception as e:
        db.rollback()
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))



