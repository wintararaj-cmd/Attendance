# Quick Start: Production Enhancements

This guide helps you implement the most critical production features **immediately**.

---

## 🚨 Priority 1: Encrypt Existing Face Data (Do This First!)

### Step 1: Generate Encryption Key

```bash
cd backend
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copy the output and add to your `.env` file:
```bash
FACE_ENCRYPTION_KEY=your_generated_key_here
```

### Step 2: Update Requirements

Add to `backend/requirements.txt`:
```
cryptography==41.0.7
```

Install:
```bash
pip install cryptography
```

### Step 3: Migrate Existing Data

Create a migration script to encrypt existing face embeddings:

```python
# backend/migrate_encrypt_faces.py
from app.core.database import SessionLocal, engine
from app.models.models import Employee
from app.services.encryption import encryption_service
import json

def migrate_face_data():
    db = SessionLocal()
    
    try:
        employees = db.query(Employee).filter(
            Employee.face_encoding_ref != None
        ).all()
        
        print(f"Found {len(employees)} employees with face data")
        
        for emp in employees:
            try:
                # Check if already encrypted (encrypted data is much longer)
                if len(emp.face_encoding_ref) > 10000:
                    print(f"Skipping {emp.emp_code} - already encrypted")
                    continue
                
                # Decrypt from JSON
                embedding = json.loads(emp.face_encoding_ref)
                
                # Encrypt
                encrypted = encryption_service.encrypt_embedding(embedding)
                
                # Update
                emp.face_encoding_ref = encrypted
                
                print(f"✅ Encrypted face data for {emp.emp_code}")
            
            except Exception as e:
                print(f"❌ Failed for {emp.emp_code}: {e}")
        
        db.commit()
        print("\n✅ Migration complete!")
    
    finally:
        db.close()

if __name__ == "__main__":
    migrate_face_data()
```

Run migration:
```bash
python migrate_encrypt_faces.py
```

### Step 4: Update Registration Endpoint

Modify `backend/app/api/endpoints.py`:

```python
from ..services.encryption import encryption_service

@router.post("/attendance/register")
async def register_face(...):
    # ... existing code ...
    
    # BEFORE (insecure):
    # face_encoding_ref=json.dumps(embedding)
    
    # AFTER (secure):
    encrypted_embedding = encryption_service.encrypt_embedding(embedding)
    
    new_emp = Employee(
        # ... other fields ...
        face_encoding_ref=encrypted_embedding,  # Now encrypted!
        # ...
    )
```

### Step 5: Update Attendance Matching

```python
@router.post("/attendance/mark")
async def mark_attendance(...):
    # When retrieving stored embedding:
    
    # BEFORE:
    # stored_embedding = json.loads(emp.face_encoding_ref)
    
    # AFTER:
    stored_embedding = encryption_service.decrypt_embedding(emp.face_encoding_ref)
    
    # Continue with matching...
```

---

## 🚨 Priority 2: Add Consent Management

### Step 1: Create Database Tables

```bash
# Create migration
cd backend
alembic revision -m "add_consent_tables"
```

Edit the generated migration file:

```python
def upgrade():
    op.create_table(
        'employee_consents',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('employee_id', sa.String(), nullable=False),
        sa.Column('consent_type', sa.String(50), nullable=False),
        sa.Column('consent_given', sa.Boolean(), default=False),
        sa.Column('consent_timestamp', sa.DateTime(timezone=True)),
        sa.Column('withdrawn', sa.Boolean(), default=False),
        sa.Column('withdrawn_at', sa.DateTime(timezone=True)),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('device_info', sa.Text()),
        sa.Column('consent_version', sa.String(20), default='1.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'])
    )
    
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String()),
        sa.Column('employee_id', sa.String()),
        sa.Column('tenant_id', sa.String()),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('resource_id', sa.String()),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.Text()),
        sa.Column('details', sa.Text()),
        sa.Column('status', sa.String(20), default='success'),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('audit_logs')
    op.drop_table('employee_consents')
```

Run migration:
```bash
alembic upgrade head
```

### Step 2: Add Consent Endpoint

```python
# backend/app/api/endpoints.py

from ..models.consent import EmployeeConsent, AuditLog

@router.post("/employees/{emp_id}/consent")
def record_consent(
    emp_id: str,
    consent_data: dict = Body(...),
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Record employee consent for biometric data collection
    Required before face registration
    """
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Create consent record
    consent = EmployeeConsent(
        id=str(uuid.uuid4()),
        employee_id=emp_id,
        consent_type="face_data",
        consent_given=consent_data.get("consent_given", False),
        consent_timestamp=datetime.datetime.now() if consent_data.get("consent_given") else None,
        ip_address=request.client.host,
        device_info=request.headers.get("user-agent"),
        consent_version="1.0"
    )
    
    db.add(consent)
    db.commit()
    
    # Log the consent action
    audit = AuditLog(
        id=str(uuid.uuid4()),
        employee_id=emp_id,
        action="consent_recorded",
        resource_type="employee_consent",
        resource_id=consent.id,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        status="success"
    )
    db.add(audit)
    db.commit()
    
    return {"status": "success", "message": "Consent recorded"}


@router.get("/employees/{emp_id}/consent-status")
def check_consent(emp_id: str, db: Session = Depends(get_db)):
    """Check if employee has given consent for face data"""
    consent = db.query(EmployeeConsent).filter(
        EmployeeConsent.employee_id == emp_id,
        EmployeeConsent.consent_type == "face_data",
        EmployeeConsent.withdrawn == False
    ).first()
    
    return {
        "has_consent": consent.consent_given if consent else False,
        "consent_date": consent.consent_timestamp.isoformat() if consent and consent.consent_timestamp else None
    }
```

### Step 3: Enforce Consent Before Registration

```python
@router.post("/attendance/register")
async def register_face(...):
    # Check consent FIRST
    consent = db.query(EmployeeConsent).filter(
        EmployeeConsent.employee_id == new_emp.id,
        EmployeeConsent.consent_type == "face_data",
        EmployeeConsent.consent_given == True,
        EmployeeConsent.withdrawn == False
    ).first()
    
    if not consent:
        raise HTTPException(
            status_code=403,
            detail="Employee consent required before face registration"
        )
    
    # Continue with registration...
```

---

## 🚨 Priority 3: Add Audit Logging

### Create Audit Service

```python
# backend/app/services/audit.py
from sqlalchemy.orm import Session
from ..models.consent import AuditLog
import uuid
from datetime import datetime

class AuditService:
    @staticmethod
    def log_access(
        db: Session,
        user_id: str = None,
        employee_id: str = None,
        action: str = "",
        resource_type: str = "",
        resource_id: str = None,
        ip_address: str = None,
        user_agent: str = None,
        details: str = None,
        status: str = "success"
    ):
        """Log sensitive data access"""
        log = AuditLog(
            id=str(uuid.uuid4()),
            user_id=user_id,
            employee_id=employee_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
            status=status
        )
        db.add(log)
        db.commit()

audit_service = AuditService()
```

### Use in Endpoints

```python
@router.get("/employees/{emp_id}")
def get_employee(emp_id: str, request: Request, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    
    # Log the access
    audit_service.log_access(
        db=db,
        user_id=current_user.id,  # From JWT
        action="view",
        resource_type="employee",
        resource_id=emp_id,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return emp
```

---

## 🚨 Priority 4: Enable HTTPS (Production)

### Option A: Using Coolify (Automatic)

Coolify handles SSL automatically via Let's Encrypt. Just ensure your domain is configured.

### Option B: Manual Nginx Setup

```nginx
server {
    listen 443 ssl http2;
    server_name api.t3sol.in;
    
    ssl_certificate /etc/letsencrypt/live/t3sol.in/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/t3sol.in/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    location / {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name api.t3sol.in;
    return 301 https://$server_name$request_uri;
}
```

---

## 🚨 Priority 5: Rate Limiting

### Add to Requirements

```
slowapi==0.1.9
```

### Implement

```python
# backend/app/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Use in endpoints
@router.post("/attendance/mark")
@limiter.limit("10/minute")  # Max 10 requests per minute
async def mark_attendance(request: Request, ...):
    # ...
```

---

## Testing Checklist

After implementing these features:

- [ ] Test face data encryption/decryption
- [ ] Verify consent is required before registration
- [ ] Check audit logs are being created
- [ ] Confirm HTTPS is working
- [ ] Test rate limiting
- [ ] Review database backups
- [ ] Test data export (GDPR right to data portability)
- [ ] Verify data deletion works (GDPR right to be forgotten)

---

## Deployment Checklist

Before going to production:

- [ ] All face data encrypted
- [ ] Consent management active
- [ ] Audit logging enabled
- [ ] HTTPS enforced
- [ ] Rate limiting configured
- [ ] Database backups automated
- [ ] Monitoring setup (Sentry/Prometheus)
- [ ] Security headers configured
- [ ] CORS properly restricted
- [ ] Environment variables secured
- [ ] API documentation updated
- [ ] Load testing completed
- [ ] Penetration testing done
- [ ] Legal review of privacy policy
- [ ] DPDP compliance documentation ready

---

## Next Steps

1. ✅ Implement encryption (Priority 1)
2. ✅ Add consent management (Priority 2)
3. ✅ Enable audit logging (Priority 3)
4. Review the full PRODUCTION_ROADMAP.md
5. Plan Phase 2 features (Multi-tenancy, Advanced AI)

**Need help? Check the detailed roadmap or ask for specific implementation guidance!**
