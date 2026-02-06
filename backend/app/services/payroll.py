from decimal import Decimal

class PayrollService:
    def calculate_net_salary(self, salary_structure: dict, attendance_summary: dict) -> dict:
        """
        Calculate comprehensive payroll for an employee based on Indian salary standards.
        Includes: Basic, HRA, Allowances, PF, ESI, PT, TDS, LOP, Overtime
        """
        
        # 1. Extract Salary Components (Safe Conversion)
        try:
            # Basic Components
            basic_salary = Decimal(str(salary_structure.get("basic_salary", 0)))
            
            # Allowances
            hra = Decimal(str(salary_structure.get("hra", 0)))
            conveyance = Decimal(str(salary_structure.get("conveyance_allowance", 0)))
            medical = Decimal(str(salary_structure.get("medical_allowance", 0)))
            special = Decimal(str(salary_structure.get("special_allowance", 0)))
            education = Decimal(str(salary_structure.get("education_allowance", 0)))
            other = Decimal(str(salary_structure.get("other_allowance", 0)))
            
            # Benefits
            bonus = Decimal(str(salary_structure.get("bonus", 0)))
            incentive = Decimal(str(salary_structure.get("incentive", 0)))
            
            # Deduction Settings
            is_pf_applicable = salary_structure.get("is_pf_applicable", True)
            is_esi_applicable = salary_structure.get("is_esi_applicable", False)
            
            # Attendance Data
            total_days = Decimal(str(attendance_summary.get("total_working_days", 30)))
            if total_days == 0:
                total_days = Decimal(30)
            
            present_days = Decimal(str(attendance_summary.get("present_days", total_days)))
            unpaid_leaves = total_days - present_days
            overtime_hours = Decimal(str(attendance_summary.get("overtime_hours", 0)))
            
        except Exception as e:
            return {"error": f"Invalid input format: {e}"}
        
        # 2. Calculate Gross Salary (Standard)
        gross_salary = (
            basic_salary + hra + conveyance + medical + 
            special + education + other
        )
        
        # 3. Calculate Earnings
        # Per day salary for LOP calculation
        per_day_salary = gross_salary / total_days
        
        # Loss of Pay (LOP) Deduction
        lop_deduction = per_day_salary * unpaid_leaves
        
        # Overtime Pay (1.5x hourly rate, assuming 8 hours/day, 30 days/month = 240 hours)
        hourly_rate = basic_salary / Decimal(240)
        overtime_pay = hourly_rate * Decimal(1.5) * overtime_hours
        
        # Actual Gross Earned (after LOP, before deductions)
        gross_earned = gross_salary - lop_deduction + overtime_pay + bonus + incentive
        
        # 4. Calculate Deductions
        
        # PF (Provident Fund) - 12% of Basic (both employee and employer)
        # Only if Basic <= 15,000 (statutory limit) or if opted
        pf_employee = Decimal(0)
        pf_employer = Decimal(0)
        if is_pf_applicable and basic_salary > 0:
            pf_base = min(basic_salary, Decimal(15000))  # PF ceiling
            pf_employee = pf_base * Decimal(0.12)
            pf_employer = pf_base * Decimal(0.12)
        
        # ESI (Employee State Insurance) - Applicable if gross <= 21,000
        # Employee: 0.75%, Employer: 3.25%
        esi_employee = Decimal(0)
        esi_employer = Decimal(0)
        if is_esi_applicable or gross_salary <= 21000:
            esi_employee = gross_salary * Decimal(0.0075)
            esi_employer = gross_salary * Decimal(0.0325)
        
        # Professional Tax (PT) - State-specific, simplified calculation
        # Maharashtra: Rs. 200/month if gross > 10,000
        professional_tax = Decimal(0)
        if gross_earned > 10000:
            professional_tax = Decimal(200)
        
        # TDS (Tax Deducted at Source) - Simplified, can be customized
        tds = Decimal(str(salary_structure.get("tds", 0)))
        
        # Total Deductions (Employee side only)
        total_deductions = pf_employee + esi_employee + professional_tax + tds + lop_deduction
        
        # 5. Net Salary
        net_salary = gross_earned - total_deductions
        
        # 6. Cost to Company (CTC) - Employer's total cost
        ctc = gross_salary + pf_employer + esi_employer + bonus + incentive
        
        return {
            "payroll": {
                "earnings": {
                    "basic": float(round(basic_salary, 2)),
                    "hra": float(round(hra, 2)),
                    "conveyance": float(round(conveyance, 2)),
                    "medical": float(round(medical, 2)),
                    "special": float(round(special, 2)),
                    "education": float(round(education, 2)),
                    "other": float(round(other, 2)),
                    "bonus": float(round(bonus, 2)),
                    "incentive": float(round(incentive, 2)),
                    "overtime": float(round(overtime_pay, 2)),
                    "gross_salary": float(round(gross_salary, 2)),
                    "gross_earned": float(round(gross_earned, 2))
                },
                "deductions": {
                    "pf": float(round(pf_employee, 2)),
                    "esi": float(round(esi_employee, 2)),
                    "prof_tax": float(round(professional_tax, 2)),
                    "tds": float(round(tds, 2)),
                    "lop": float(round(lop_deduction, 2)),
                    "total": float(round(total_deductions, 2))
                },
                "employer_contributions": {
                    "pf": float(round(pf_employer, 2)),
                    "esi": float(round(esi_employer, 2)),
                    "total": float(round(pf_employer + esi_employer, 2))
                },
                "net_salary": float(round(net_salary, 2)),
                "ctc": float(round(ctc, 2))
            },
            "attendance": {
                "total_days": float(total_days),
                "present_days": float(present_days),
                "unpaid_leaves": float(unpaid_leaves),
                "overtime_hours": float(overtime_hours)
            }
        }

payroll_service = PayrollService()
