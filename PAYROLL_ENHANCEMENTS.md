# Enhanced Payroll Configuration for Part-time and Contract Workers with OT Support

## Overview

The payroll system has been enhanced to support:
- **Part-time workers** with hourly-based pay
- **Contract workers** with daily rate pay
- **Overtime tracking** with configurable multipliers (weekday, weekend, holiday)
- **Flexible payroll calculation** based on employee type

## Changes Made

### 1. Database Schema Updates

#### New Columns in `salary_structures` table:
- `is_hourly_based` (BOOLEAN) - Flag to indicate if employee is paid hourly
- `hourly_rate` (NUMERIC) - Hourly rate for part-time workers
- `contract_rate_per_day` (NUMERIC) - Daily rate for contract workers
- `ot_rate_multiplier` (NUMERIC) - Overtime multiplier for weekdays (default: 1.5x)
- `ot_weekend_multiplier` (NUMERIC) - Overtime multiplier for weekends (default: 2.0x)
- `ot_holiday_multiplier` (NUMERIC) - Overtime multiplier for holidays (default: 2.5x)

#### New Columns in `attendance_logs` table:
- `ot_hours` (NUMERIC) - Regular weekday overtime hours
- `ot_weekend_hours` (NUMERIC) - Weekend overtime hours
- `ot_holiday_hours` (NUMERIC) - Holiday overtime hours
- `total_hours_worked` (NUMERIC) - Total hours worked (for hourly workers)

### 2. Backend Enhancements

#### Updated Files:
1. **`backend/app/models/models.py`**
   - Added new fields to `SalaryStructure` model
   - Added OT tracking fields to `AttendanceLog` model

2. **`backend/app/services/payroll.py`**
   - Enhanced payroll calculation to support different employee types
   - Added hourly-based salary calculation for part-time workers
   - Added daily rate calculation for contract workers
   - Implemented comprehensive OT calculation with different multipliers
   - PF/ESI rules adjusted for different employee types

3. **`backend/app/api/endpoints.py`**
   - Updated `/payroll/employee/{emp_id}` endpoint to:
     - Fetch employee type
     - Aggregate OT hours from attendance logs
     - Pass employee type to payroll service
   - Updated `/employees/{emp_id}/salary` GET endpoint to return new fields
   - Updated `/employees/{emp_id}/salary` POST endpoint to save new fields

### 3. Migration Script

Created `backend/migrate_payroll_enhancements.py` to add new database columns.

## How to Run the Migration

### Prerequisites
Ensure you have `psycopg2-binary` installed (for PostgreSQL):
```bash
cd backend
python -m pip install psycopg2-binary
```

### Run Migration
```bash
cd backend
python migrate_payroll_enhancements.py
```

**Note:** Make sure your `.env` file has the correct `DATABASE_URL` configured.

## Payroll Calculation Logic

### Full-time Employees
- **Calculation**: Monthly salary with standard allowances
- **Gross Salary** = Basic + HRA + Allowances
- **OT Pay** = (Basic / 240 hours) × OT Multiplier × OT Hours
- **Deductions**: PF (12% of Basic up to ₹15,000), ESI (if applicable), PT, TDS

### Part-time Employees (Hourly-based)
- **Calculation**: Based on hours worked
- **Gross Salary** = Hourly Rate × Total Hours Worked
- **OT Pay** = Hourly Rate × OT Multiplier × OT Hours
- **Deductions**: PF (optional), ESI (if gross ≤ ₹21,000), PT, TDS

### Contract Employees (Daily rate)
- **Calculation**: Based on days worked
- **Gross Salary** = Daily Rate × Present Days
- **OT Pay** = (Daily Rate / 8 hours) × OT Multiplier × OT Hours
- **Deductions**: PF (optional), ESI (if applicable), PT, TDS

### Overtime Multipliers
- **Weekday OT**: 1.5x base rate (configurable)
- **Weekend OT**: 2.0x base rate (configurable)
- **Holiday OT**: 2.5x base rate (configurable)

## Example Configurations

### Example 1: Full-time Employee with OT
```json
{
  "basic_salary": 15000,
  "hra": 7500,
  "conveyance_allowance": 1600,
  "medical_allowance": 1250,
  "special_allowance": 2850,
  "is_pf_applicable": true,
  "is_esi_applicable": false,
  "is_hourly_based": false,
  "ot_rate_multiplier": 1.5,
  "ot_weekend_multiplier": 2.0,
  "ot_holiday_multiplier": 2.5
}
```

**Payroll Calculation:**
- Gross Salary: ₹28,200
- OT Hours (weekday): 10 hours
- OT Pay: (15000/240) × 1.5 × 10 = ₹937.50
- Total Earnings: ₹29,137.50
- Deductions (PF + PT): ₹2,000
- **Net Salary: ₹27,137.50**

### Example 2: Part-time Hourly Worker
```json
{
  "is_hourly_based": true,
  "hourly_rate": 200,
  "is_pf_applicable": false,
  "is_esi_applicable": false,
  "ot_rate_multiplier": 1.5,
  "ot_weekend_multiplier": 2.0
}
```

**Payroll Calculation:**
- Hours Worked: 120 hours
- Gross Salary: 200 × 120 = ₹24,000
- OT Hours (weekday): 5 hours
- OT Pay: 200 × 1.5 × 5 = ₹1,500
- Total Earnings: ₹25,500
- Deductions (PT only): ₹200
- **Net Salary: ₹25,300**

### Example 3: Contract Worker (Daily Rate)
```json
{
  "contract_rate_per_day": 1500,
  "is_pf_applicable": false,
  "is_esi_applicable": false,
  "ot_rate_multiplier": 1.5
}
```

**Payroll Calculation:**
- Days Worked: 22 days
- Gross Salary: 1500 × 22 = ₹33,000
- OT Hours (weekday): 8 hours
- OT Pay: (1500/8) × 1.5 × 8 = ₹2,250
- Total Earnings: ₹35,250
- Deductions (PT only): ₹200
- **Net Salary: ₹35,050**

## API Usage

### Get Employee Payroll
```http
GET /api/v1/payroll/employee/{emp_id}
```

**Response:**
```json
{
  "employee_id": "...",
  "employee_name": "John Doe",
  "employee_type": "part_time",
  "month": "February 2026",
  "present_days": 22,
  "payroll": {
    "earnings": {
      "basic": 0,
      "hra": 0,
      "overtime_regular": 937.50,
      "overtime_weekend": 500.00,
      "overtime_holiday": 625.00,
      "overtime_total": 2062.50,
      "gross_salary": 24000,
      "gross_earned": 26062.50
    },
    "deductions": {
      "pf": 0,
      "esi": 0,
      "prof_tax": 200,
      "tds": 0,
      "lop": 0,
      "total": 200
    },
    "net_salary": 25862.50,
    "ctc": 24000
  },
  "attendance": {
    "total_days": 30,
    "present_days": 22,
    "unpaid_leaves": 8,
    "ot_hours": 5,
    "ot_weekend_hours": 2,
    "ot_holiday_hours": 2,
    "total_hours_worked": 120
  },
  "rates": {
    "hourly_rate": 200,
    "contract_rate_per_day": null,
    "base_hourly_rate": 200,
    "ot_rate_multiplier": 1.5,
    "ot_weekend_multiplier": 2.0,
    "ot_holiday_multiplier": 2.5
  }
}
```

### Configure Employee Salary
```http
POST /api/v1/employees/{emp_id}/salary
Content-Type: application/json

{
  "is_hourly_based": true,
  "hourly_rate": 200,
  "contract_rate_per_day": 0,
  "ot_rate_multiplier": 1.5,
  "ot_weekend_multiplier": 2.0,
  "ot_holiday_multiplier": 2.5,
  "is_pf_applicable": false,
  "is_esi_applicable": false
}
```

## Frontend Integration

1. **✅ Payroll Configuration UI (Done):**
   - Added "Employment Type & Rates" section to Payroll Management
   - Added toggle for "Hourly-based" payment
   - Added fields for Hourly Rate and Contract Rate
   - Added OT multiplier configuration fields (Weekday, Weekend, Holiday)

2. **Attendance Tracking (Done):**
   - ✅ Add fields to track OT hours (weekday, weekend, holiday)
   - ✅ Add field to track total hours worked (for hourly workers)
   - ✅ Auto-calculate OT based on check-in/check-out times

3. **Payslip Display (Done):**
   - ✅ Show OT breakdown (weekday, weekend, holiday)
   - ✅ Display hourly rate or daily rate (if applicable)
   - ✅ Show hours worked (for hourly workers)

## Benefits

✅ **Flexible Payroll**: Support for different employment types
✅ **Accurate OT Calculation**: Different multipliers for different OT types
✅ **Compliance**: Proper PF/ESI handling for different worker types
✅ **Transparency**: Detailed breakdown of earnings and deductions
✅ **Scalability**: Easy to add more employee types or pay structures

## Next Steps

1. **Run the migration** to add new database columns
2. **Test the payroll calculation** with different employee types
3. **Update the frontend** to support new configuration options
4. **Add OT tracking** in the attendance system
5. **Generate payslips** with OT details

## Support

For questions or issues, refer to:
- `backend/app/services/payroll.py` - Payroll calculation logic
- `backend/app/api/endpoints.py` - API endpoints
- `backend/app/models/models.py` - Database models

---

**Last Updated**: February 9, 2026
**Version**: 1.0
