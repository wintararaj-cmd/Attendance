from decimal import Decimal

class PayrollService:
    def calculate_net_salary(self, salary_structure: dict, attendance_summary: dict, employee_type: str = "full_time") -> dict:
        """
        Calculate comprehensive payroll based on Employee Type (Worker vs Staff).
        
        Worker (Daily Rate):
        - Daily Total = Basic + HRA + Conv + Washing + Edu + Other (All per day)
        - Wages = Daily Total * Working Days
        - OT Amount = (Daily Total / 8) * OT Hours
        - Gross = Wages + OT + Bonus/Incentive
        
        Staff (Monthly):
        - Gross = Fixed Monthly Basic + HRA + Conv + Washing + Edu + Other
        - Prorated for LOP
        """
        
        try:
            # --- 1. Extract Components ---
            
            # Common Components
            basic = Decimal(str(salary_structure.get("basic_salary", 0)))
            hra = Decimal(str(salary_structure.get("hra", 0)))
            conveyance = Decimal(str(salary_structure.get("conveyance_allowance", 0)))
            washing = Decimal(str(salary_structure.get("washing_allowance", 0)))
            education = Decimal(str(salary_structure.get("education_allowance", 0)))
            other_allowance = Decimal(str(salary_structure.get("other_allowance", 0)))
            
            # Additional Benefits
            bonus = Decimal(str(salary_structure.get("bonus", 0)))
            incentive = Decimal(str(salary_structure.get("incentive", 0)))
            
            # Attendance Data
            total_days_in_month = Decimal(str(attendance_summary.get("total_days_in_month", 30))) # e.g., 30 or 31
            worked_days = Decimal(str(attendance_summary.get("present_days", 0)))
            # For workers, "Working Days" usually means days they actually worked (present days).
            # For staff, we usually pay for the whole month minus LOP.
            
            ot_hours = Decimal(str(attendance_summary.get("ot_hours", 0)))
            ot_weekend_hours = Decimal(str(attendance_summary.get("ot_weekend_hours", 0)))
            ot_holiday_hours = Decimal(str(attendance_summary.get("ot_holiday_hours", 0)))
            
            is_worker = salary_structure.get("is_hourly_based", False) or employee_type in ["worker", "daily_wage"]
            
            # --- 2. Gross Salary Calculation ---
            
            gross_salary = Decimal(0)
            wages = Decimal(0)
            total_ot_pay = Decimal(0)
            daily_total_rate = Decimal(0)
            
            # Initialize OT breakdown
            ot_pay_regular = Decimal(0)
            ot_pay_weekend = Decimal(0)
            ot_pay_holiday = Decimal(0)

            if is_worker:
                # --- WORKER LOGIC (Daily Based) ---
                # All components are considered "Per Day"
                daily_total_rate = basic + hra + conveyance + washing + education + other_allowance
                
                # Wages = Daily Total * Working Days
                wages = daily_total_rate * worked_days
                
                # OT Calculation: (Daily Total / 8) * OT Hours
                ot_rate_per_hour = daily_total_rate / Decimal(8)
                
                ot_rate_multiplier = Decimal(str(salary_structure.get("ot_rate_multiplier", 1.0)))
                
                ot_pay_regular = ot_rate_per_hour * ot_rate_multiplier * ot_hours
                ot_pay_weekend = (daily_total_rate / Decimal(8)) * Decimal(str(salary_structure.get("ot_weekend_multiplier", 2.0))) * ot_weekend_hours
                ot_pay_holiday = (daily_total_rate / Decimal(8)) * Decimal(str(salary_structure.get("ot_holiday_multiplier", 2.0))) * ot_holiday_hours
                
                total_ot_pay = ot_pay_regular + ot_pay_weekend + ot_pay_holiday
                
                # Gross Salary = Wages + OT + Other Allowances (Bonus/Incentive typically)
                gross_salary = wages + total_ot_pay + bonus + incentive
                
                lop_deduction = Decimal(0) 

            else:
                # --- STAFF LOGIC (Monthly Based) ---
                # Components are Monthly Fixed
                monthly_gross_components = basic + hra + conveyance + washing + education + other_allowance
                
                # Wages equivalent (Gross - LOP)
                # Recalculate LOP logic based on latest rigorous requirements? 
                # Keeping existing LOP logic:
                paid_days = Decimal(str(attendance_summary.get("paid_days", worked_days))) 
                unpaid_leaves = Decimal(str(attendance_summary.get("unpaid_leaves", 0)))
                if "unpaid_leaves" not in attendance_summary and "paid_days" in attendance_summary:
                     unpaid_leaves = total_days_in_month - paid_days
                
                per_day_gross = monthly_gross_components / total_days_in_month if total_days_in_month > 0 else 0
                lop_deduction = per_day_gross * unpaid_leaves
                
                wages = monthly_gross_components - lop_deduction
                
                # OT for Staff (if applicable)
                if ot_hours > 0 or ot_weekend_hours > 0 or ot_holiday_hours > 0:
                     ot_base_rate = basic / Decimal(240) # 30 days * 8 hours
                     ot_multiplier = Decimal(str(salary_structure.get("ot_rate_multiplier", 1.5)))
                     
                     ot_pay_regular = ot_base_rate * ot_multiplier * ot_hours
                     # Assuming multipliers for staff match worker or default
                     ot_weekend_mult = Decimal(str(salary_structure.get("ot_weekend_multiplier", 2.0)))
                     ot_holiday_mult = Decimal(str(salary_structure.get("ot_holiday_multiplier", 2.5)))
                     
                     ot_pay_weekend = ot_base_rate * ot_weekend_mult * ot_weekend_hours
                     ot_pay_holiday = ot_base_rate * ot_holiday_mult * ot_holiday_hours
                     
                     total_ot_pay = ot_pay_regular + ot_pay_weekend + ot_pay_holiday
                
                gross_salary = wages + total_ot_pay + bonus + incentive

            # --- 3. Deductions ---
            
            # ... (Deductions logic remains - PF, ESI, etc. needs no change usually) ...
            # Re-implementing briefly to ensure variable scope or just assuming access? 
            # We are inside the function, need to ensure we don't cut off logic.
            # Copying deductions logic from previous read but ensuring indentation matches.
            
            pf_employee = Decimal(0)
            pf_employer = Decimal(0)
            is_pf_applicable = salary_structure.get("is_pf_applicable", True)
            
            if is_pf_applicable:
                if is_worker:
                    earned_basic = basic * worked_days
                else:
                    per_day_basic = basic / total_days_in_month if total_days_in_month > 0 else 0
                    earned_basic = per_day_basic * (total_days_in_month - unpaid_leaves)
                
                pf_base = min(earned_basic, Decimal(15000))
                pf_employee = pf_base * Decimal(0.12)
                pf_employer = pf_base * Decimal(0.12)
            
            esi_employee = Decimal(0)
            esi_employer = Decimal(0)
            is_esi_applicable = salary_structure.get("is_esi_applicable", False)
            
            if is_esi_applicable or (gross_salary <= 21000 and gross_salary > 0):
                esi_employee = math_ceil(gross_salary * Decimal(0.0075)) 
                esi_employer = math_ceil(gross_salary * Decimal(0.0325))
            
            pt = Decimal(str(salary_structure.get("professional_tax", 0)))
            if pt == 0 and gross_salary > 10000:
                 pt = Decimal(200)
            
            welfare = Decimal(str(salary_structure.get("welfare_deduction", 0)))
            if welfare == 0 and employee_type in ['worker', 'staff']:
                 welfare = Decimal(3)
            
            tds = Decimal(str(salary_structure.get("tds", 0)))
            loan_deduction = Decimal(str(attendance_summary.get("loan_deduction", 0)))
            
            total_deduction = pf_employee + esi_employee + pt + welfare + tds + loan_deduction
            
            # --- 4. Net Salary ---
            net_salary = gross_salary - total_deduction
            ctc = gross_salary + pf_employer + esi_employer
            
            return {
                "payroll": {
                    "employee_type": "Worker" if is_worker else "Staff",
                    "earnings": {
                        "basic_earned": float(round(earned_basic if is_pf_applicable else (wages if not is_worker else wages), 2)),
                        "basic": float(round(earned_basic if is_pf_applicable else (wages if not is_worker else wages), 2)), # Alias for frontend
                        "hra": float(round(hra if not is_worker else (hra * worked_days), 2)),
                        "conveyance": float(round(conveyance if not is_worker else (conveyance * worked_days), 2)),
                        "washing": float(round(washing if not is_worker else (washing * worked_days), 2)),
                        "medical": float(round(salary_structure.get("medical_allowance", 0) if not is_worker else (Decimal(str(salary_structure.get("medical_allowance", 0))) * worked_days), 2)),
                        "special": float(round(salary_structure.get("special_allowance", 0) if not is_worker else (Decimal(str(salary_structure.get("special_allowance", 0))) * worked_days), 2)),
                        "education": float(round(education if not is_worker else (education * worked_days), 2)),
                        "other": float(round(other_allowance if not is_worker else (other_allowance * worked_days), 2)),
                        
                        "daily_rate": float(round(daily_total_rate, 2)) if is_worker else None,
                        "wages_total": float(round(wages, 2)),
                        "ot_amount": float(round(total_ot_pay, 2)),
                        "overtime_regular": float(round(ot_pay_regular, 2)),
                        "overtime_weekend": float(round(ot_pay_weekend, 2)),
                        "overtime_holiday": float(round(ot_pay_holiday, 2)),
                        "overtime_total": float(round(total_ot_pay, 2)),
                        
                        "bonus": float(round(bonus, 2)),
                        "incentive": float(round(incentive, 2)),
                        "gross_salary": float(round(gross_salary, 2)),
                        "gross_earned": float(round(gross_salary, 2)) # Alias for frontend
                    },
                    "deductions": {
                        "pf": float(round(pf_employee, 2)),
                        "esi": float(round(esi_employee, 2)),
                        "pt": float(round(pt, 2)),
                        "prof_tax": float(round(pt, 2)), # Alias
                        "welfare": float(round(welfare, 2)),
                        "loan": float(round(loan_deduction, 2)),
                        "tds": float(round(tds, 2)),
                        "lop": float(round(lop_deduction, 2)), # Add LOP explicitly
                        "total_deduction": float(round(total_deduction, 2)),
                        "total": float(round(total_deduction, 2)) # Alias
                    },
                    "employer_contributions": {
                        "pf": float(round(pf_employer, 2)),
                        "esi": float(round(esi_employer, 2)),
                        "total": float(round(pf_employer + esi_employer, 2))
                    },
                    "net_salary": float(round(net_salary, 2)),
                    "ctc": float(round(ctc, 2)),
                    "metadata": {
                        "working_days": float(worked_days),
                        "ot_hours": float(ot_hours),
                        "total_days_in_month": float(total_days_in_month),
                        "paid_days": float(paid_days) if not is_worker else float(worked_days)
                    }
                }
            }
        except Exception as e:
            return {"error": f"Calculation Error: {str(e)}"}

def math_ceil(val):
    import math
    return Decimal(math.ceil(val))

payroll_service = PayrollService()
