-- Database Schema for Employee Attendance & Payroll System
-- Target: PostgreSQL

CREATE TYPE employee_status AS ENUM ('active', 'inactive', 'suspended');
CREATE TYPE attendance_status AS ENUM ('present', 'absent', 'half_day', 'late', 'weekly_off', 'holiday');
CREATE TYPE verification_method AS ENUM ('face_recognition', 'biometric_device', 'manual_override', 'mobile_auth');

-- 1. Companies / Tenants (Multi-tenancy support)
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(100) UNIQUE,
    timezone VARCHAR(50) DEFAULT 'Asia/Kolkata',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Departments
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    company_id UUID REFERENCES companies(id),
    name VARCHAR(100) NOT NULL,
    UNIQUE(company_id, name)
);

-- 3. Employees
CREATE TABLE employees (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    emp_code VARCHAR(50) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE,
    department_id INT REFERENCES departments(id),
    designation VARCHAR(100),
    joining_date DATE NOT NULL,
    status employee_status DEFAULT 'active',
    
    -- Face Recognition Data (Encrypted paths or references, NOT raw data if possible)
    face_encoding_ref VARCHAR(512), -- Reference to vector storage or encrypted blob
    is_face_registered BOOLEAN DEFAULT FALSE,
    consent_date TIMESTAMP WITH TIME ZONE, -- DPDP Compliance
    
    salary_structure_id INT, -- Link to salary rules
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, emp_code)
);

-- 4. Attendance
CREATE TABLE attendance_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID REFERENCES employees(id),
    date DATE NOT NULL,
    check_in TIMESTAMP WITH TIME ZONE,
    check_out TIMESTAMP WITH TIME ZONE,
    
    -- Verification details
    check_in_method verification_method,
    check_out_method verification_method,
    check_in_location GEOGRAPHY(POINT), -- GPS Coordinates
    check_out_location GEOGRAPHY(POINT),
    check_in_image_url VARCHAR(512), -- S3 URL for audit
    
    -- Audit
    confidence_score FLOAT, -- AI Confidence
    is_liveness_verified BOOLEAN DEFAULT FALSE,
    
    status attendance_status,
    total_hours INTERVAL,
    remarks TEXT,
    
    UNIQUE(employee_id, date)
);

-- 5. Payroll Configuration (Salary Structure)
CREATE TABLE salary_structures (
    id SERIAL PRIMARY KEY,
    company_id UUID REFERENCES companies(id),
    name VARCHAR(100) NOT NULL,
    basic_salary DECIMAL(12,2) NOT NULL,
    hra_percentage DECIMAL(5,2),
    da_percentage DECIMAL(5,2),
    travel_allowance DECIMAL(12,2),
    pf_employer_contribution DECIMAL(5,2),
    pf_employee_contribution DECIMAL(5,2),
    esi_employer_contribution DECIMAL(5,2),
    esi_employee_contribution DECIMAL(5,2),
    tax_regime VARCHAR(50) DEFAULT 'new',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. Payroll Records (Monthly Generation)
CREATE TABLE payrolls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID REFERENCES employees(id),
    month INT NOT NULL,
    year INT NOT NULL,
    
    -- Earnings
    basic_earned DECIMAL(12,2),
    hra_earned DECIMAL(12,2),
    special_allowance DECIMAL(12,2),
    overtime_hours DECIMAL(5,2),
    overtime_pay DECIMAL(12,2),
    
    -- Deductions
    pf_deduction DECIMAL(12,2),
    esi_deduction DECIMAL(12,2),
    professional_tax DECIMAL(12,2),
    tds DECIMAL(12,2), -- Tax Deducted at Source
    leaves_taken INT,
    loss_of_pay DECIMAL(12,2), -- Salary deduction for unpaid leaves
    
    net_salary DECIMAL(12,2) NOT NULL,
    payment_status VARCHAR(50) DEFAULT 'pending', -- pending, paid, failed
    transaction_ref VARCHAR(100),
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(employee_id, month, year)
);

-- Indexes for Performance
CREATE INDEX idx_emp_company ON employees(company_id);
CREATE INDEX idx_attendance_date ON attendance_logs(date);
CREATE INDEX idx_attendance_emp ON attendance_logs(employee_id);
