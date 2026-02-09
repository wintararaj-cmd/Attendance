import uuid
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime, Date, Numeric, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base
import enum

# Enums
class EmployeeStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    HALF_DAY = "half_day"
    LATE = "late"
    WEEKLY_OFF = "weekly_off"
    HOLIDAY = "holiday"

class Models(Base):
    __abstract__ = True
    # Helper for mixins if needed

class AdminUser(Base):
    __tablename__ = "admin_users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="admin") # superadmin, hr, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Company(Base):
    __tablename__ = "companies"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    domain = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    employees = relationship("Employee", back_populates="company")

class Department(Base):
    __tablename__ = "departments"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String, ForeignKey("companies.id"))
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    department_head = Column(String, nullable=True)  # Employee name or ID
    status = Column(String, default="active")  # 'active', 'inactive'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    company = relationship("Company", backref="departments")


class Employee(Base):
    __tablename__ = "employees"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String, ForeignKey("companies.id"))
    emp_code = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String)
    mobile_no = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=True)
    
    # Employment Details
    department = Column(String, nullable=True)  # 'IT', 'HR', 'Finance', 'Operations', etc.
    designation = Column(String, nullable=True)  # 'Manager', 'Developer', 'Analyst', etc.
    employee_type = Column(String, default="full_time")  # 'full_time', 'part_time', 'contract', 'intern'
    joining_date = Column(Date, nullable=True)
    status = Column(String, default="active")  # 'active', 'inactive', 'suspended'
    
    # AI / Biometric Data references
    face_encoding_ref = Column(String, nullable=True) # Path to storage or vector ID
    is_face_registered = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    company = relationship("Company", back_populates="employees")
    attendance_logs = relationship("AttendanceLog", back_populates="employee")

class AttendanceLog(Base):
    __tablename__ = "attendance_logs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(String, ForeignKey("employees.id"))
    date = Column(Date, nullable=False)
    check_in = Column(DateTime(timezone=True), nullable=True)
    check_out = Column(DateTime(timezone=True), nullable=True)
    
    status = Column(String) # Cast Enum to string for SQLite compatibility if needed
    confidence_score = Column(Numeric(5, 2), nullable=True)
    
    # Overtime tracking
    ot_hours = Column(Numeric(5, 2), default=0.0)  # Regular weekday OT hours
    ot_weekend_hours = Column(Numeric(5, 2), default=0.0)  # Weekend OT hours
    ot_holiday_hours = Column(Numeric(5, 2), default=0.0)  # Holiday OT hours
    total_hours_worked = Column(Numeric(5, 2), default=0.0)  # Total hours worked that day
    
    employee = relationship("Employee", back_populates="attendance_logs")

class SalaryStructure(Base):
    __tablename__ = "salary_structures"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(String, ForeignKey("employees.id"), unique=True)
    
    # Basic Components
    basic_salary = Column(Numeric(12, 2), default=0.0)
    
    # Allowances
    hra = Column(Numeric(12, 2), default=0.0)  # House Rent Allowance
    conveyance_allowance = Column(Numeric(12, 2), default=0.0)
    medical_allowance = Column(Numeric(12, 2), default=0.0)
    special_allowance = Column(Numeric(12, 2), default=0.0)
    education_allowance = Column(Numeric(12, 2), default=0.0)
    other_allowance = Column(Numeric(12, 2), default=0.0)
    
    # Deductions
    pf_employee = Column(Numeric(12, 2), default=0.0)  # Employee PF Contribution
    pf_employer = Column(Numeric(12, 2), default=0.0)  # Employer PF Contribution
    esi_employee = Column(Numeric(12, 2), default=0.0)  # Employee ESI
    esi_employer = Column(Numeric(12, 2), default=0.0)  # Employer ESI
    professional_tax = Column(Numeric(12, 2), default=0.0)
    tds = Column(Numeric(12, 2), default=0.0)  # Tax Deducted at Source
    
    # Other Benefits
    bonus = Column(Numeric(12, 2), default=0.0)
    incentive = Column(Numeric(12, 2), default=0.0)
    
    # Calculation Settings
    is_pf_applicable = Column(Boolean, default=True)
    is_esi_applicable = Column(Boolean, default=False)
    
    # Part-time / Contract / Hourly Worker Settings
    is_hourly_based = Column(Boolean, default=False)  # True for hourly workers
    hourly_rate = Column(Numeric(12, 2), default=0.0)  # Rate per hour for part-time/contract
    contract_rate_per_day = Column(Numeric(12, 2), default=0.0)  # Daily rate for contract workers
    
    # Overtime Settings
    ot_rate_multiplier = Column(Numeric(5, 2), default=1.5)  # Default 1.5x for weekday OT
    ot_weekend_multiplier = Column(Numeric(5, 2), default=2.0)  # 2x for weekend OT
    ot_holiday_multiplier = Column(Numeric(5, 2), default=2.5)  # 2.5x for holiday OT
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    employee = relationship("Employee", back_populates="salary_structure")

# Update Employee relationship
Employee.salary_structure = relationship("SalaryStructure", uselist=False, back_populates="employee")

