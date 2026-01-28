# Payroll Calculation Engine (Python)

This module implements the logic for calculating monthly salary based on attendance data and configured salary structures.

```python
from decimal import Decimal

class PayrollCalculator:
    def __init__(self):
        pass

    def calculate_net_salary(self, employee_data, salary_structure, attendance_summary):
        """
        Calculate the payroll for a single employee.
        
        Args:
            employee_data (dict): Basic info
            salary_structure (dict): Rules (Basic, HRA %, DA %, etc.)
            attendance_summary (dict): Days present, leaves, overtime hours
        """
        
        # 1. Inputs
        basic_salary = Decimal(salary_structure.get("basic_salary", 0))
        total_working_days = Decimal(attendance_summary.get("total_working_days", 30))
        days_present = Decimal(attendance_summary.get("days_present", 0))
        approved_leaves = Decimal(attendance_summary.get("approved_leaves", 0))
        unpaid_leaves = Decimal(attendance_summary.get("unpaid_leaves", 0)) # Loss of Pay
        overtime_hours = Decimal(attendance_summary.get("overtime_hours", 0))
        
        # 2. Earnings Calculation
        # HRA (House Rent Allowance)
        hra = basic_salary * (Decimal(salary_structure.get("hra_percentage", 40)) / 100)
        
        # DA (Dearness Allowance)
        da = basic_salary * (Decimal(salary_structure.get("da_percentage", 0)) / 100)
        
        # Special / Other Allowances
        special_allowance = Decimal(salary_structure.get("special_allowance", 0))
        
        # Gross Monthly (Without Loss of Pay)
        gross_standard = basic_salary + hra + da + special_allowance
        
        # Loss of Pay Calculation (Pro-rata basis)
        # Formula: (Gross / Total Days) * Unpaid Days
        per_day_salary = gross_standard / total_working_days
        lop_deduction = per_day_salary * unpaid_leaves
        
        # Overtime Pay
        # Formula: (Basic / 240 hours) * 1.5 * OT Hours (Standard Assumption)
        hourly_rate = basic_salary / Decimal(240) # Assuming 8 hours * 30 days roughly
        ot_pay = hourly_rate * Decimal(1.5) * overtime_hours
        
        gross_earned = gross_standard - lop_deduction + ot_pay

        # 3. Deductions
        # PF (Provident Fund) - 12% of Basic (capped usually, but simplified here)
        pf_employee = basic_salary * Decimal(0.12)
        
        # ESI (Employee State Insurance) - 0.75% of Gross if Gross < 21000
        esi_employee = Decimal(0)
        if gross_earned < 21000:
            esi_employee = gross_earned * Decimal(0.0075)
            
        # Professional Tax (State dependent, simplified flat 200)
        prof_tax = Decimal(200)
        
        # TDS (Tax Deducted at Source) - Placeholder for tax engine
        tds = Decimal(0) 

        total_deductions = pf_employee + esi_employee + prof_tax + tds

        # 4. Net Pay
        net_salary = gross_earned - total_deductions
        
        return {
            "employee_id": employee_data["id"],
            "earnings": {
                "basic": round(basic_salary, 2),
                "hra": round(hra, 2),
                "da": round(da, 2),
                "overtime": round(ot_pay, 2),
                "gross_earned": round(gross_earned, 2)
            },
            "deductions": {
                "pf": round(pf_employee, 2),
                "esi": round(esi_employee, 2),
                "prof_tax": round(prof_tax, 2),
                "lop": round(lop_deduction, 2),
                "total_deductions": round(total_deductions, 2)
            },
            "net_salary": round(net_salary, 2)
        }

# Example Usage
if __name__ == "__main__":
    structure = {
        "basic_salary": 15000,
        "hra_percentage": 40,
        "da_percentage": 10,
        "special_allowance": 2000
    }
    
    attendance = {
        "total_working_days": 30,
        "days_present": 28,
        "approved_leaves": 1,
        "unpaid_leaves": 1,
        "overtime_hours": 10
    }
    
    payroll = PayrollCalculator()
    result = payroll.calculate_net_salary({"id": "EMP001"}, structure, attendance)
    print(result)
```
