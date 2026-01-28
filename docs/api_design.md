# API Design Specification

The API is built using **FastAPI** and auto-generates interactive documentation at `/docs` (Swagger UI) and `/redoc`.

## Base URL
`http://api.attendance-sys.com/v1`

## Key Endpoints

### 1. Authentication Module
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/auth/login` | Admin/HR login (Email + Password) |
| `POST` | `/auth/refresh` | Refresh JWT Token |
| `POST` | `/auth/biometric-challenge` | Initiate mobile biometric login |

### 2. Employee Management
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/employees` | List all employees (Filter by Dept, Status) |
| `POST` | `/employees` | Create new employee profile |
| `POST` | `/employees/{id}/face-register` | Upload 3-5 images to train/store face embedding |
| `GET` | `/employees/{id}` | Get detailed profile |

### 3. Attendance AI Module
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/attendance/mark` | **Core**: Upload Selfie + Geo + Device Info. Returns Success/Accruacy/Error. |
| `GET` | `/attendance/today` | Live dashboard of who is present/absent |
| `GET` | `/attendance/reports` | Date-range reports for CSV/Excel export |

### 4. Payroll Module
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/payroll/calculate` | Run batch calculation for a specific month |
| `GET` | `/payroll/payslip/{employee_id}` | Generate and download PDF payslip |
| `POST` | `/payroll/salary-structure` | Configure company-wide salary rules |

## Data Models (JSON Schemas)

### AttendanceRequest
```json
{
  "employee_id": "uuid",
  "geo_location": {"lat": 12.9716, "long": 77.5946},
  "timestamp": "2023-10-27T09:00:00Z",
  "image_data": "base64_string_or_multipart_form_data"
}
```

### AttendanceResponse
```json
{
  "status": "success",
  "check_in_time": "09:05:00",
  "confidence": 0.98,
  "warnings": ["Late Entry"]
}
```
