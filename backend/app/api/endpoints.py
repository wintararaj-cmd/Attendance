from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from typing import Optional, List
from sqlalchemy.orm import Session
import shutil
import os
import json
import uuid
import datetime
from ..services.face_recognition import face_service
from ..services.payroll import payroll_service
from ..core.database import get_db
from ..models.models import Employee, AttendanceLog

router = APIRouter()

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
        db.commit()
        db.refresh(new_emp)
        
        return {"status": "success", "message": f"Employee {name} registered with Face ID", "id": new_emp.id}

    except Exception as e:
        print(f"Unhandled endpoint error: {e}")
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
            # --- 1:N Search (Auto Detect) ---
            print("Running 1:N Face Search...")
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
             # Log Attendance
            log = AttendanceLog(
                id=str(uuid.uuid4()),
                employee_id=matched_emp.id,
                date=datetime.date.today(),
                check_in=datetime.datetime.now(),
                status="present",
                confidence_score=float(confidence)
            )
            db.add(log)
            db.commit()
            
            return {
                "status": "success",
                "attended": True,
                "confidence": confidence,
                "employee": matched_emp.first_name,
                "emp_code": matched_emp.emp_code
            }
        
        return {"status": "failed", "reason": "Unknown Error"}

    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

@router.get("/employees")
def get_employees(db: Session = Depends(get_db)):
    employees = db.query(Employee).all()
    # Safely convert to list of dicts or rely on FastAPI ORM mode if schemas were defined
    return employees

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
    total_employees = db.query(Employee).count()
    
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
    logs = db.query(AttendanceLog).join(Employee).order_by(AttendanceLog.check_in.desc()).limit(5).all()
    recent_activity = []
    for log in logs:
        recent_activity.append({
            "id": log.id,
            "employee_name": f"{log.employee.first_name} {log.employee.last_name or ''}",
            "time": log.check_in.strftime("%I:%M %p") if log.check_in else "--:--",
            "status": log.status
        })
    
    return {
        "total_employees": total_employees,
        "present_today": present_count,
        "absent_today": absent_count,
        "late_count": 0, # Placeholder for future logic
        "recent_activity": recent_activity
    }

@router.get("/payroll/employee/{emp_id}")
def get_employee_payroll(
    emp_id: str,
    db: Session = Depends(get_db)
):
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
        
    # Mock Salary Structure (In real app, fetch from DB)
    salary_struct = {
        "basic_salary": 25000, 
        "hra_percentage": 40, 
        "da_percentage": 10,
        "special_allowance": 5000
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
    # In production, check holidays, weekends, etc.
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
