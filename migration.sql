-- Database Migration SQL Script
-- Run this directly in PostgreSQL to add missing columns

-- Add missing columns to employees table
ALTER TABLE employees ADD COLUMN IF NOT EXISTS email VARCHAR;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS department VARCHAR;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS designation VARCHAR;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS employee_type VARCHAR DEFAULT 'full_time';
ALTER TABLE employees ADD COLUMN IF NOT EXISTS joining_date DATE;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE;

-- Create departments table
CREATE TABLE IF NOT EXISTS departments (
    id VARCHAR PRIMARY KEY,
    company_id VARCHAR,
    name VARCHAR NOT NULL,
    description TEXT,
    department_head VARCHAR,
    status VARCHAR DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

-- Verify the changes
SELECT 'Migration completed successfully!' as status;
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'employees'
ORDER BY ordinal_position;
