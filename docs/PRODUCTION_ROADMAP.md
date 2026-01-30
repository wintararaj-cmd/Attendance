# Production-Ready SaaS Enhancement Roadmap
## Employee Attendance & Payroll Management System

**Current Status**: ✅ MVP Working (Face Recognition + Basic Payroll)  
**Target**: 🎯 Production SaaS for 10,000+ employees

---

## Phase 1: Security & Compliance Hardening (Week 1-2)

### 1.1 Data Protection & DPDP Act 2023 Compliance

#### ✅ Already Implemented:
- JWT authentication
- Password hashing (bcrypt)
- HTTPS/TLS support

#### 🔧 Required Enhancements:

**A. Face Data Encryption**
```python
# backend/app/services/encryption.py
from cryptography.fernet import Fernet
import os

class FaceDataEncryption:
    def __init__(self):
        # Store key in environment variable or AWS Secrets Manager
        self.key = os.getenv("FACE_ENCRYPTION_KEY").encode()
        self.cipher = Fernet(self.key)
    
    def encrypt_embedding(self, embedding_json: str) -> str:
        """Encrypt face embedding before storing in DB"""
        return self.cipher.encrypt(embedding_json.encode()).decode()
    
    def decrypt_embedding(self, encrypted_data: str) -> str:
        """Decrypt face embedding for matching"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
```

**B. Consent Management**
```sql
-- Add to database schema
CREATE TABLE employee_consents (
    id UUID PRIMARY KEY,
    employee_id UUID REFERENCES employees(id),
    consent_type VARCHAR(50), -- 'face_data', 'biometric', 'location'
    consent_given BOOLEAN DEFAULT FALSE,
    consent_timestamp TIMESTAMP,
    ip_address VARCHAR(45),
    device_info TEXT,
    withdrawn_at TIMESTAMP NULL
);
```

**C. Audit Logging**
```python
# backend/app/services/audit.py
from datetime import datetime
from sqlalchemy.orm import Session

class AuditLogger:
    @staticmethod
    def log_sensitive_access(
        db: Session,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        ip_address: str
    ):
        """Log all access to sensitive data (immutable)"""
        audit_log = AuditLog(
            id=str(uuid.uuid4()),
            user_id=user_id,
            action=action,  # 'view', 'create', 'update', 'delete'
            resource_type=resource_type,  # 'employee_face', 'payroll', etc.
            resource_id=resource_id,
            ip_address=ip_address,
            timestamp=datetime.utcnow()
        )
        db.add(audit_log)
        db.commit()
```

---

## Phase 2: Advanced Face Recognition (Week 2-3)

### 2.1 Production-Grade AI Service

#### Current Limitations:
- ❌ Mock mode in production
- ❌ No liveness detection
- ❌ Single model (VGG-Face)

#### Enhancements:

**A. Multi-Model Ensemble**
```python
# backend/app/services/face_recognition_v2.py
class ProductionFaceService:
    def __init__(self):
        self.models = ["VGG-Face", "Facenet512", "ArcFace"]
        self.threshold = 0.35  # Stricter for production
        
    def register_face_multi_model(self, image_path: str) -> dict:
        """Generate embeddings using multiple models for better accuracy"""
        embeddings = {}
        for model in self.models:
            try:
                emb = DeepFace.represent(
                    img_path=image_path,
                    model_name=model,
                    enforce_detection=True,
                    detector_backend="retinaface"  # More accurate than default
                )
                embeddings[model] = emb[0]["embedding"]
            except Exception as e:
                print(f"Model {model} failed: {e}")
        
        return embeddings
    
    def verify_multi_model(self, live_img: str, stored_embeddings: dict) -> dict:
        """Verify using ensemble voting"""
        votes = []
        confidences = []
        
        for model in self.models:
            if model not in stored_embeddings:
                continue
                
            live_emb = DeepFace.represent(
                img_path=live_img,
                model_name=model,
                enforce_detection=True
            )[0]["embedding"]
            
            distance = cosine(live_emb, stored_embeddings[model])
            votes.append(distance < self.threshold)
            confidences.append(1 - distance)
        
        # Require majority vote
        match = sum(votes) >= len(votes) / 2
        avg_confidence = sum(confidences) / len(confidences)
        
        return {
            "match": match,
            "confidence": avg_confidence,
            "votes": f"{sum(votes)}/{len(votes)}"
        }
```

**B. Advanced Liveness Detection**
```python
# backend/app/services/liveness.py
import cv2
import numpy as np

class LivenessDetector:
    def __init__(self):
        # Load pre-trained liveness model
        self.model = cv2.dnn.readNetFromCaffe(
            "models/liveness_deploy.prototxt",
            "models/liveness.caffemodel"
        )
    
    def detect_liveness(self, image_path: str) -> dict:
        """
        Advanced liveness detection using:
        1. Texture analysis
        2. Motion detection (if video)
        3. 3D depth estimation
        """
        frame = cv2.imread(image_path)
        
        # Preprocess
        blob = cv2.dnn.blobFromImage(
            frame, 1.0, (224, 224),
            (104.0, 177.0, 123.0), swapRB=False, crop=False
        )
        
        self.model.setInput(blob)
        predictions = self.model.forward()
        
        # Get confidence scores
        fake_confidence = predictions[0][0]
        real_confidence = predictions[0][1]
        
        is_live = real_confidence > 0.7
        
        return {
            "is_live": is_live,
            "confidence": float(real_confidence),
            "reason": "Real person detected" if is_live else "Possible spoof attack"
        }
```

---

## Phase 3: Multi-Tenancy & Scalability (Week 3-4)

### 3.1 SaaS Multi-Tenancy Architecture

**Database Schema Enhancement:**
```sql
-- Tenant isolation
CREATE TABLE tenants (
    id UUID PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    subdomain VARCHAR(100) UNIQUE, -- company.yoursaas.com
    plan_type VARCHAR(50), -- 'free', 'basic', 'premium', 'enterprise'
    max_employees INTEGER,
    features JSONB, -- Feature flags
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Add tenant_id to all tables
ALTER TABLE employees ADD COLUMN tenant_id UUID REFERENCES tenants(id);
ALTER TABLE attendance_logs ADD COLUMN tenant_id UUID REFERENCES tenants(id);
ALTER TABLE salary_structures ADD COLUMN tenant_id UUID REFERENCES tenants(id);

-- Create indexes for tenant queries
CREATE INDEX idx_employees_tenant ON employees(tenant_id);
CREATE INDEX idx_attendance_tenant ON attendance_logs(tenant_id);
```

**Tenant Middleware:**
```python
# backend/app/middleware/tenant.py
from fastapi import Request, HTTPException
from sqlalchemy.orm import Session

async def tenant_middleware(request: Request, call_next):
    """Extract tenant from subdomain or header"""
    host = request.headers.get("host", "")
    subdomain = host.split(".")[0]
    
    # Store tenant context
    request.state.tenant_id = get_tenant_id_from_subdomain(subdomain)
    
    if not request.state.tenant_id:
        raise HTTPException(status_code=400, detail="Invalid tenant")
    
    response = await call_next(request)
    return response

# Usage in endpoints
@router.get("/employees")
def get_employees(request: Request, db: Session = Depends(get_db)):
    tenant_id = request.state.tenant_id
    employees = db.query(Employee).filter(
        Employee.tenant_id == tenant_id
    ).all()
    return employees
```

### 3.2 Horizontal Scaling Strategy

**Load Balancing:**
```nginx
# nginx.conf
upstream backend_servers {
    least_conn;  # Load balancing algorithm
    server backend1:8000 weight=3;
    server backend2:8000 weight=3;
    server backend3:8000 weight=2;
}

server {
    listen 443 ssl http2;
    server_name api.yoursaas.com;
    
    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;
    
    location / {
        proxy_pass http://backend_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Tenant-ID $http_x_tenant_id;
    }
}
```

**Redis Caching:**
```python
# backend/app/services/cache.py
import redis
import json
from typing import Optional

class CacheService:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST"),
            port=6379,
            decode_responses=True
        )
    
    def get_employee_cache(self, tenant_id: str, emp_id: str) -> Optional[dict]:
        """Cache employee data for faster lookups"""
        key = f"tenant:{tenant_id}:employee:{emp_id}"
        data = self.redis_client.get(key)
        return json.loads(data) if data else None
    
    def set_employee_cache(self, tenant_id: str, emp_id: str, data: dict, ttl=3600):
        """Cache with 1-hour TTL"""
        key = f"tenant:{tenant_id}:employee:{emp_id}"
        self.redis_client.setex(key, ttl, json.dumps(data))
```

---

## Phase 4: Advanced Payroll Features (Week 4-5)

### 4.1 Flexible Payroll Engine

**Configurable Salary Components:**
```python
# backend/app/services/payroll_v2.py
from decimal import Decimal
from typing import Dict, List

class PayrollEngine:
    def __init__(self, tenant_config: dict):
        self.config = tenant_config
        
    def calculate_salary(
        self,
        employee: Employee,
        salary_structure: SalaryStructure,
        attendance_data: dict,
        month: int,
        year: int
    ) -> dict:
        """
        Advanced payroll calculation with:
        - Configurable components
        - Attendance-based deductions
        - Overtime calculations
        - Tax slabs
        - PF/ESI compliance
        """
        
        # 1. Calculate Earnings
        basic = Decimal(salary_structure.basic_salary)
        hra = self._calculate_hra(basic, self.config.get("hra_percentage", 40))
        special_allowance = Decimal(salary_structure.special_allowance)
        overtime_pay = self._calculate_overtime(
            attendance_data.get("overtime_hours", 0),
            basic
        )
        
        gross_earnings = basic + hra + special_allowance + overtime_pay
        
        # 2. Calculate Deductions
        pf = self._calculate_pf(basic)  # 12% of basic (employee contribution)
        esi = self._calculate_esi(gross_earnings)  # If gross < 21,000
        professional_tax = Decimal(salary_structure.professional_tax)
        
        # Loss of Pay (LOP) for absences
        lop = self._calculate_lop(
            basic,
            attendance_data.get("absent_days", 0),
            attendance_data.get("total_working_days", 30)
        )
        
        # Income Tax (TDS)
        tds = self._calculate_tds(gross_earnings, employee.tax_regime)
        
        total_deductions = pf + esi + professional_tax + lop + tds
        
        # 3. Net Salary
        net_salary = gross_earnings - total_deductions
        
        return {
            "employee_id": employee.id,
            "month": month,
            "year": year,
            "earnings": {
                "basic": float(basic),
                "hra": float(hra),
                "special_allowance": float(special_allowance),
                "overtime": float(overtime_pay),
                "gross": float(gross_earnings)
            },
            "deductions": {
                "pf": float(pf),
                "esi": float(esi),
                "professional_tax": float(professional_tax),
                "lop": float(lop),
                "tds": float(tds),
                "total": float(total_deductions)
            },
            "net_salary": float(net_salary),
            "attendance_summary": attendance_data
        }
    
    def _calculate_pf(self, basic: Decimal) -> Decimal:
        """PF = 12% of basic (capped at 15,000 basic)"""
        pf_base = min(basic, Decimal("15000"))
        return pf_base * Decimal("0.12")
    
    def _calculate_esi(self, gross: Decimal) -> Decimal:
        """ESI = 0.75% if gross < 21,000"""
        if gross < Decimal("21000"):
            return gross * Decimal("0.0075")
        return Decimal("0")
    
    def _calculate_lop(self, basic: Decimal, absent_days: int, total_days: int) -> Decimal:
        """Loss of Pay for absences"""
        per_day_salary = basic / Decimal(total_days)
        return per_day_salary * Decimal(absent_days)
    
    def _calculate_overtime(self, overtime_hours: int, basic: Decimal) -> Decimal:
        """Overtime = 2x hourly rate"""
        hourly_rate = basic / Decimal("208")  # 26 days * 8 hours
        return hourly_rate * Decimal(overtime_hours) * Decimal("2")
```

### 4.2 Payslip Generation

**Enhanced PDF Generation:**
```python
# backend/app/services/payslip_generator.py
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

class PayslipGenerator:
    def generate_payslip(self, payroll_data: dict, employee: Employee, company: Tenant) -> str:
        """Generate professional payslip PDF"""
        filename = f"payslip_{employee.emp_code}_{payroll_data['month']}_{payroll_data['year']}.pdf"
        filepath = f"temp/{filename}"
        
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # Company Header
        elements.append(Paragraph(f"<b>{company.company_name}</b>", styles['Title']))
        elements.append(Spacer(1, 12))
        
        # Payslip Title
        month_year = f"{payroll_data['month']}/{payroll_data['year']}"
        elements.append(Paragraph(f"<b>PAYSLIP FOR {month_year}</b>", styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        # Employee Details Table
        emp_data = [
            ['Employee Name:', f"{employee.first_name} {employee.last_name or ''}"],
            ['Employee ID:', employee.emp_code],
            ['Department:', employee.department or 'N/A'],
            ['Designation:', employee.designation or 'N/A']
        ]
        emp_table = Table(emp_data, colWidths=[150, 300])
        emp_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.grey),
        ]))
        elements.append(emp_table)
        elements.append(Spacer(1, 20))
        
        # Earnings and Deductions Table
        salary_data = [
            ['EARNINGS', 'AMOUNT (₹)', 'DEDUCTIONS', 'AMOUNT (₹)'],
            ['Basic Salary', f"{payroll_data['earnings']['basic']:.2f}", 
             'Provident Fund', f"{payroll_data['deductions']['pf']:.2f}"],
            ['HRA', f"{payroll_data['earnings']['hra']:.2f}",
             'ESI', f"{payroll_data['deductions']['esi']:.2f}"],
            ['Special Allowance', f"{payroll_data['earnings']['special_allowance']:.2f}",
             'Professional Tax', f"{payroll_data['deductions']['professional_tax']:.2f}"],
            ['Overtime', f"{payroll_data['earnings']['overtime']:.2f}",
             'LOP', f"{payroll_data['deductions']['lop']:.2f}"],
            ['', '', 'TDS', f"{payroll_data['deductions']['tds']:.2f}"],
            ['GROSS EARNINGS', f"₹ {payroll_data['earnings']['gross']:.2f}",
             'TOTAL DEDUCTIONS', f"₹ {payroll_data['deductions']['total']:.2f}"]
        ]
        
        salary_table = Table(salary_data, colWidths=[150, 100, 150, 100])
        salary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        elements.append(salary_table)
        elements.append(Spacer(1, 20))
        
        # Net Salary
        net_para = Paragraph(
            f"<b>NET SALARY: ₹ {payroll_data['net_salary']:.2f}</b>",
            styles['Heading1']
        )
        elements.append(net_para)
        
        doc.build(elements)
        return filepath
```

---

## Phase 5: Mobile App & Biometric Integration (Week 5-6)

### 5.1 Flutter Mobile App Architecture

**Key Features:**
```dart
// lib/main.dart
import 'package:flutter/material.dart';
import 'package:local_auth/local_auth.dart';
import 'package:camera/camera.dart';
import 'package:geolocator/geolocator.dart';

class AttendanceApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Attendance System',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: AttendanceHomePage(),
    );
  }
}

class AttendanceService {
  final LocalAuthentication _localAuth = LocalAuthentication();
  
  // Biometric Authentication
  Future<bool> authenticateWithBiometric() async {
    try {
      bool canCheckBiometrics = await _localAuth.canCheckBiometrics;
      if (!canCheckBiometrics) return false;
      
      return await _localAuth.authenticate(
        localizedReason: 'Verify your identity to mark attendance',
        options: const AuthenticationOptions(
          stickyAuth: true,
          biometricOnly: true,
        ),
      );
    } catch (e) {
      print('Biometric auth error: $e');
      return false;
    }
  }
  
  // Face Capture & Upload
  Future<void> markAttendanceWithFace(String employeeId) async {
    // 1. Get biometric confirmation
    bool bioAuth = await authenticateWithBiometric();
    if (!bioAuth) {
      throw Exception('Biometric authentication failed');
    }
    
    // 2. Capture face image
    final cameras = await availableCameras();
    final frontCamera = cameras.firstWhere(
      (camera) => camera.lensDirection == CameraLensDirection.front
    );
    
    // Navigate to camera screen
    final imagePath = await Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => FaceCaptureScreen(camera: frontCamera))
    );
    
    // 3. Get location (if geofencing enabled)
    Position position = await Geolocator.getCurrentPosition();
    
    // 4. Upload to backend
    await _uploadAttendance(employeeId, imagePath, position);
  }
  
  Future<void> _uploadAttendance(
    String empId,
    String imagePath,
    Position location
  ) async {
    var request = http.MultipartRequest(
      'POST',
      Uri.parse('https://api.yoursaas.com/api/v1/attendance/mark')
    );
    
    request.fields['emp_id'] = empId;
    request.fields['latitude'] = location.latitude.toString();
    request.fields['longitude'] = location.longitude.toString();
    request.files.add(await http.MultipartFile.fromPath('file', imagePath));
    
    var response = await request.send();
    // Handle response
  }
}
```

### 5.2 Geofencing Validation

**Backend Geofence Check:**
```python
# backend/app/services/geofence.py
from math import radians, cos, sin, asin, sqrt

class GeofenceService:
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in meters"""
        R = 6371000  # Earth radius in meters
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        return R * c
    
    @staticmethod
    def is_within_geofence(
        user_lat: float,
        user_lon: float,
        office_lat: float,
        office_lon: float,
        radius_meters: int = 100
    ) -> bool:
        """Check if user is within allowed radius"""
        distance = GeofenceService.haversine_distance(
            user_lat, user_lon, office_lat, office_lon
        )
        return distance <= radius_meters

# Usage in attendance endpoint
@router.post("/attendance/mark")
async def mark_attendance(
    emp_id: str = Form(...),
    latitude: float = Form(None),
    longitude: float = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Get company geofence settings
    company = db.query(Tenant).filter(Tenant.id == employee.tenant_id).first()
    
    if company.geofence_enabled and latitude and longitude:
        is_valid = GeofenceService.is_within_geofence(
            latitude, longitude,
            company.office_latitude,
            company.office_longitude,
            company.geofence_radius
        )
        
        if not is_valid:
            return {
                "status": "failed",
                "reason": "You are outside the allowed location"
            }
    
    # Continue with face verification...
```

---

## Phase 6: Deployment & DevOps (Week 6-7)

### 6.1 Docker Containerization

**Backend Dockerfile:**
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Download face recognition models
RUN python -c "from deepface import DeepFace; DeepFace.build_model('VGG-Face')"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**Docker Compose:**
```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: attendance_db
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://admin:${DB_PASSWORD}@postgres:5432/attendance_db
      REDIS_HOST: redis
      FACE_ENCRYPTION_KEY: ${FACE_ENCRYPTION_KEY}
      JWT_SECRET: ${JWT_SECRET}
    depends_on:
      - postgres
      - redis
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl
    depends_on:
      - backend

volumes:
  postgres_data:
```

### 6.2 Kubernetes Deployment (For Scale)

**Kubernetes Manifests:**
```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: attendance-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: attendance-backend
  template:
    metadata:
      labels:
        app: attendance-backend
    spec:
      containers:
      - name: backend
        image: yourdockerhub/attendance-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: attendance-backend-service
spec:
  selector:
    app: attendance-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

---

## Phase 7: Monitoring & Observability (Week 7)

### 7.1 Application Monitoring

**Prometheus + Grafana:**
```python
# backend/app/middleware/metrics.py
from prometheus_client import Counter, Histogram, generate_latest
import time

# Metrics
attendance_requests = Counter(
    'attendance_requests_total',
    'Total attendance marking requests',
    ['status', 'tenant_id']
)

face_recognition_duration = Histogram(
    'face_recognition_duration_seconds',
    'Time spent on face recognition'
)

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    
    if "/attendance/mark" in request.url.path:
        face_recognition_duration.observe(duration)
        attendance_requests.labels(
            status=response.status_code,
            tenant_id=request.state.tenant_id
        ).inc()
    
    return response

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### 7.2 Error Tracking (Sentry)

```python
# backend/app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
    environment="production"
)
```

---

## Implementation Priority

### Critical Path (Must Have for Production):
1. ✅ **Week 1**: Face data encryption + Consent management
2. ✅ **Week 2**: Advanced liveness detection + Multi-model ensemble
3. ✅ **Week 3**: Multi-tenancy architecture
4. ✅ **Week 4**: Production payroll engine
5. ✅ **Week 5**: Mobile app with biometric auth
6. ✅ **Week 6**: Docker deployment + CI/CD
7. ✅ **Week 7**: Monitoring setup

### Nice to Have (Post-MVP):
- Shift management
- Leave management integration
- Advanced reporting & analytics
- Mobile app offline mode
- Bulk employee import
- Integration with HR systems (SAP, Workday)

---

## Cost Estimation (AWS)

**For 10,000 employees:**
- **EC2 Instances** (3x t3.large): ~$150/month
- **RDS PostgreSQL** (db.t3.medium): ~$100/month
- **ElastiCache Redis**: ~$50/month
- **S3 Storage** (face images): ~$30/month
- **CloudFront CDN**: ~$50/month
- **Total**: ~$380/month + bandwidth costs

**Scaling to 100,000 employees:**
- Increase to 10x EC2 instances
- RDS upgrade to db.r5.xlarge
- Estimated: ~$2,000/month

---

## Security Checklist

- [ ] Face embeddings encrypted at rest
- [ ] TLS 1.3 for all communications
- [ ] JWT tokens with short expiry (15 min)
- [ ] Rate limiting on all endpoints
- [ ] SQL injection prevention (parameterized queries)
- [ ] CORS properly configured
- [ ] Audit logs for all sensitive operations
- [ ] Regular security audits
- [ ] Penetration testing before launch
- [ ] GDPR/DPDP compliance documentation

---

## Next Steps

1. Review this roadmap
2. Prioritize features based on business needs
3. Set up development sprints
4. Begin with Phase 1 (Security hardening)
5. Parallel track: Mobile app development

**Questions? Let's discuss implementation details!**
