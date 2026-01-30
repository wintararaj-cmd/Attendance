"""
Database models for consent management (DPDP Act 2023 compliance)
"""

import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from ..core.database import Base


class EmployeeConsent(Base):
    """
    Tracks explicit consent for biometric data collection
    Required for DPDP Act 2023 compliance
    """
    __tablename__ = "employee_consents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False)
    
    # Type of consent
    consent_type = Column(String(50), nullable=False)  # 'face_data', 'biometric', 'location', 'payroll_data'
    
    # Consent status
    consent_given = Column(Boolean, default=False)
    consent_timestamp = Column(DateTime(timezone=True), nullable=True)
    
    # Withdrawal tracking
    withdrawn = Column(Boolean, default=False)
    withdrawn_at = Column(DateTime(timezone=True), nullable=True)
    
    # Audit trail
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    device_info = Column(Text, nullable=True)  # User agent, device type
    consent_version = Column(String(20), default="1.0")  # Track policy version
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AuditLog(Base):
    """
    Immutable audit log for all sensitive data access
    Required for compliance and security audits
    """
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Who accessed
    user_id = Column(String, nullable=True)  # Admin/HR user
    employee_id = Column(String, nullable=True)  # If employee self-access
    tenant_id = Column(String, nullable=True)  # Multi-tenancy
    
    # What was accessed
    action = Column(String(50), nullable=False)  # 'view', 'create', 'update', 'delete', 'export'
    resource_type = Column(String(50), nullable=False)  # 'employee_face', 'payroll', 'attendance'
    resource_id = Column(String, nullable=True)  # Specific resource ID
    
    # When and where
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Additional context
    details = Column(Text, nullable=True)  # JSON string with extra info
    status = Column(String(20), default="success")  # 'success', 'failed', 'unauthorized'
