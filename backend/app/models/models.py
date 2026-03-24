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

class PayrollStatus(str, enum.Enum):
    DRAFT = "draft"
    LOCKED = "locked"
    PAID = "paid"

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
    washing_allowance = Column(Numeric(12, 2), default=0.0)
    casting_allowance = Column(Numeric(12, 2), default=0.0)  # Casting allowance
    ttb_allowance = Column(Numeric(12, 2), default=0.0)  # TTB allowance
    plating_allowance = Column(Numeric(12, 2), default=0.0)  # Plating allowance
    
    # Deductions
    pf_employee = Column(Numeric(12, 2), default=0.0)  # Employee PF Contribution
    pf_employer = Column(Numeric(12, 2), default=0.0)  # Employer PF Contribution
    esi_employee = Column(Numeric(12, 2), default=0.0)  # Employee ESI
    esi_employer = Column(Numeric(12, 2), default=0.0)  # Employer ESI
    professional_tax = Column(Numeric(12, 2), default=0.0)
    welfare_deduction = Column(Numeric(12, 2), default=0.0)
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

class Payroll(Base):
    __tablename__ = "payrolls"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(String, ForeignKey("employees.id"))
    month = Column(Integer, nullable=False) # 1-12
    year = Column(Integer, nullable=False)
    
    # Snapshot of calculations
    total_days = Column(Numeric(5, 2), default=0.0)
    working_days = Column(Numeric(5, 2), default=0.0)
    present_days = Column(Numeric(5, 2), default=0.0)
    ot_hours = Column(Numeric(5, 2), default=0.0)
    
    basic_earned = Column(Numeric(12, 2), default=0.0)
    hra_earned = Column(Numeric(12, 2), default=0.0)
    conveyance_earned = Column(Numeric(12, 2), default=0.0)
    washing_allowance = Column(Numeric(12, 2), default=0.0)
    other_allowances = Column(Numeric(12, 2), default=0.0)
    casting_allowance = Column(Numeric(12, 2), default=0.0)  # Casting allowance earned
    ttb_allowance = Column(Numeric(12, 2), default=0.0)  # TTB allowance earned
    plating_allowance = Column(Numeric(12, 2), default=0.0)  # Plating allowance earned
    
    gross_salary = Column(Numeric(12, 2), default=0.0)
    
    # Deductions
    pf_amount = Column(Numeric(12, 2), default=0.0)
    esi_amount = Column(Numeric(12, 2), default=0.0)
    pt_amount = Column(Numeric(12, 2), default=0.0)
    welfare_fund = Column(Numeric(12, 2), default=0.0)
    loan_deduction = Column(Numeric(12, 2), default=0.0)
    total_deductions = Column(Numeric(12, 2), default=0.0)
    
    net_salary = Column(Numeric(12, 2), default=0.0)
    
    status = Column(String, default="draft") # draft, locked, paid
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    employee = relationship("Employee")

class EmployeePayrollRules(Base):
    """Customizable payroll rules per employee - overrides global defaults"""
    __tablename__ = "employee_payroll_rules"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(String, ForeignKey("employees.id"), unique=True)
    
    # Attendance-based Allowance Rules (thresholds for multiplier)
    # Days required for full allowance (default 21)
    allowance_full_days = Column(Integer, default=21)
    # Days required for half allowance (default 15)
    allowance_half_days = Column(Integer, default=15)
    # Multiplier values (as percentages: 100 = 100%, 50 = 50%)
    allowance_full_multiplier = Column(Numeric(5, 2), default=100.0)
    allowance_half_multiplier = Column(Numeric(5, 2), default=50.0)
    allowance_none_multiplier = Column(Numeric(5, 2), default=0.0)
    
    # Overtime Rules
    # Standard working hours per day (for OT calculation)
    standard_working_hours = Column(Numeric(5, 2), default=8.0)
    # OT rate multipliers (can override SalaryStructure defaults)
    ot_rate_multiplier = Column(Numeric(5, 2), default=1.5)  # Weekday OT
    ot_weekend_multiplier = Column(Numeric(5, 2), default=2.0)  # Weekend OT
    ot_holiday_multiplier = Column(Numeric(5, 2), default=2.5)  # Holiday OT
    
    # PF (Provident Fund) Rules
    pf_employee_rate = Column(Numeric(5, 2), default=12.0)  # 12% employee contribution
    pf_employer_rate = Column(Numeric(5, 2), default=12.0)  # 12% employer contribution
    pf_wage_ceiling = Column(Numeric(12, 2), default=15000.0)  # Max wage for PF calculation
    
    # ESI (Employee State Insurance) Rules
    esi_employee_rate = Column(Numeric(5, 2), default=0.75)  # 0.75% employee contribution
    esi_employer_rate = Column(Numeric(5, 2), default=3.25)  # 3.25% employer contribution
    esi_wage_ceiling = Column(Numeric(12, 2), default=21000.0)  # Max gross salary for ESI
    
    # Professional Tax Rules
    pt_threshold = Column(Numeric(12, 2), default=10000.0)  # Salary threshold for PT
    pt_amount = Column(Numeric(12, 2), default=200.0)  # Default PT amount
    
    # Welfare Fund Rules
    welfare_deduction = Column(Numeric(12, 2), default=3.0)  # Default welfare deduction
    
    # Staff-specific: Days in month for calculation (default 30)
    staff_month_days = Column(Integer, default=30)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    employee = relationship("Employee", back_populates="payroll_rules")


# Update Employee relationship
Employee.salary_structure = relationship("SalaryStructure", uselist=False, back_populates="employee")
Employee.payroll_rules = relationship("EmployeePayrollRules", uselist=False, back_populates="employee")


class LoanType(str, enum.Enum):
    LOAN = "loan"
    ADVANCE = "advance"

class LoanStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PaymentStatus(str, enum.Enum):
    PAID = "paid"
    PENDING = "pending"
    FAILED = "failed"


class EmployeeLoan(Base):
    """Employee Loan/Advance records with EMI deduction from salary"""
    __tablename__ = "employee_loans"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False)
    
    # Loan Type: 'loan' or 'advance'
    loan_type = Column(String, nullable=False)  # 'loan' or 'advance'
    
    # Loan Details
    loan_amount = Column(Numeric(12, 2), nullable=False)  # Total loan amount
    emi_amount = Column(Numeric(12, 2), nullable=False)  # EMI amount per month
    total_emis = Column(Integer, nullable=False, default=1)  # Total number of EMIs
    remaining_emis = Column(Integer, nullable=False, default=1)  # Remaining EMIs
    
    # Dates
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    
    # Additional Info
    reason = Column(Text, nullable=True)
    status = Column(String, default="active")  # 'active', 'completed', 'cancelled'
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    employee = relationship("Employee", back_populates="loans")
    payments = relationship("LoanPayment", back_populates="loan", cascade="all, delete-orphan")


class LoanPayment(Base):
    """Loan EMI Payment Records"""
    __tablename__ = "loan_payments"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    loan_id = Column(String, ForeignKey("employee_loans.id"), nullable=False)
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False)
    
    # Payment Details
    payment_date = Column(Date, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    month = Column(Integer, nullable=False)  # 1-12
    year = Column(Integer, nullable=False)
    status = Column(String, default="paid")  # 'paid', 'pending', 'failed'
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    loan = relationship("EmployeeLoan", back_populates="payments")
    employee = relationship("Employee")


# Update Employee relationship for loans
Employee.loans = relationship("EmployeeLoan", back_populates="employee")

