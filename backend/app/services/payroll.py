from decimal import Decimal

class PayrollService:
    def calculate_net_salary(self, salary_structure: dict, attendance_summary: dict) -> dict:
        """
        Calculate the payroll for a single employee based on structure and attendance.
        All monetary inputs should be standard python numeric types, converted to Decimal internally.
        """
        
        # 1. Inputs & Safe Conversion
        try:
            basic_salary = Decimal(str(salary_structure.get("basic_salary", 0)))
            hra_pct = Decimal(str(salary_structure.get("hra_percentage", 40)))
            da_pct = Decimal(str(salary_structure.get("da_percentage", 0)))
            special_allowance = Decimal(str(salary_structure.get("special_allowance", 0)))
            
            # Attendance
            total_days = Decimal(str(attendance_summary.get("total_working_days", 30)))
            if total_days == 0: total_days = Decimal(30)
            
            unpaid_leaves = Decimal(str(attendance_summary.get("unpaid_leaves", 0)))
            overtime_hours = Decimal(str(attendance_summary.get("overtime_hours", 0)))
        except Exception as e:
            return {"error": f"Invalid input format: {e}"}
        
        # 2. Earnings Calculation
        hra = basic_salary * (hra_pct / 100)
        da = basic_salary * (da_pct / 100)
        
        # Gross (Standard)
        gross_standard = basic_salary + hra + da + special_allowance
        
        # Loss of Pay Deduction
        per_day_salary = gross_standard / total_days
        lop_deduction = per_day_salary * unpaid_leaves
        
        # Overtime Pay (Approximation: 240 hours/month)
        hourly_rate = basic_salary / Decimal(240)
        ot_pay = hourly_rate * Decimal(1.5) * overtime_hours
        
        # Actual Gross Earned
        gross_earned = gross_standard - lop_deduction + ot_pay

        # 3. Deductions
        # PF: 12% of Basic
        pf_employee = basic_salary * Decimal(0.12)
        
        # ESI: 0.75% of Gross if Gross < 21k
        esi_employee = Decimal(0)
        if gross_earned < 21000:
            esi_employee = gross_earned * Decimal(0.0075)
            
        # Professional Tax (Simplified)
        prof_tax = Decimal(200) if gross_earned > 15000 else Decimal(0)

        total_deductions = pf_employee + esi_employee + prof_tax

        # 4. Net Pay
        net_salary = gross_earned - total_deductions
        
        return {
            "earnings": {
                "basic": round(basic_salary, 2),
                "hra": round(hra, 2),
                "da": round(da, 2),
                "special": round(special_allowance, 2),
                "overtime": round(ot_pay, 2),
                "gross_earned": round(gross_earned, 2)
            },
            "deductions": {
                "pf": round(pf_employee, 2),
                "esi": round(esi_employee, 2),
                "prof_tax": round(prof_tax, 2),
                "lop": round(lop_deduction, 2),
                "total": round(total_deductions, 2)
            },
            "net_salary": round(net_salary, 2)
        }

payroll_service = PayrollService()
