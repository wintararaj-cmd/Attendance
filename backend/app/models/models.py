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

class Company(Base):
    __tablename__ = "companies"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    domain = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    employees = relationship("Employee", back_populates="company")

class Employee(Base):
    __tablename__ = "employees"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String, ForeignKey("companies.id"))
    emp_code = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String)
    mobile_no = Column(String, unique=True, nullable=False)
    
    # AI / Biometric Data references
    face_encoding_ref = Column(String, nullable=True) # Path to storage or vector ID
    is_face_registered = Column(Boolean, default=False)
    
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
    
    employee = relationship("Employee", back_populates="attendance_logs")

class SalaryStructure(Base):
    __tablename__ = "salary_structures"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    basic_salary = Column(Numeric(12, 2))
    hra_percentage = Column(Numeric(5, 2))
    # ... Add other fields as per schema
