from decimal import Decimal
import math
import json

def math_ceil(val):
    return Decimal(math.ceil(val))

# Default global rules (used when employee has no custom rules)
DEFAULT_PAYROLL_RULES = {
    "allowance_full_days": 21,
    "allowance_half_days": 15,
    "allowance_full_multiplier": 100.0,
    "allowance_half_multiplier": 50.0,
    "allowance_none_multiplier": 0.0,
    "standard_working_hours": 8.0,
    "ot_rate_multiplier": 1.5,
    "ot_weekend_multiplier": 2.0,
    "ot_holiday_multiplier": 2.5,
    "pf_employee_rate": 12.0,
    "pf_employer_rate": 12.0,
    "pf_wage_ceiling": 15000.0,
    "pf_use_slabs": False,
    "pf_slabs": json.dumps([
        {"min": 0, "max": 10000, "amount": 0},
        {"min": 10001, "max": 15000, "amount": 110},
        {"min": 15001, "max": 25000, "amount": 130},
        {"min": 25001, "max": 40000, "amount": 150},
        {"min": 40001, "max": None, "amount": 200}
    ]),
    "esi_employee_rate": 0.75,
    "esi_employer_rate": 3.25,
    "esi_wage_ceiling": 21000.0,
    "pt_threshold": 10000.0,
    "pt_amount": 200.0,
    "welfare_deduction": 3.0,
    "staff_month_days": 30,
}

class PayrollService:
    def calculate_net_salary(self, salary_structure: dict, attendance_summary: dict, employee_type: str = "full_time", custom_rules: dict = None) -> dict:
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
            # --- 0. Merge Custom Rules with Defaults ---
            rules = {**DEFAULT_PAYROLL_RULES}
            if custom_rules:
                rules.update(custom_rules)
            
            # Extract rule values
            allowance_full_days = int(rules.get("allowance_full_days", 21))
            allowance_half_days = int(rules.get("allowance_half_days", 15))
            allowance_full_mult = Decimal(str(rules.get("allowance_full_multiplier", 100.0))) / Decimal(100)
            allowance_half_mult = Decimal(str(rules.get("allowance_half_multiplier", 50.0))) / Decimal(100)
            allowance_none_mult = Decimal(str(rules.get("allowance_none_multiplier", 0.0))) / Decimal(100)
            standard_working_hours = Decimal(str(rules.get("standard_working_hours", 8.0)))
            
            # OT multipliers from rules (can be overridden by salary_structure)
            default_ot_mult = Decimal(str(rules.get("ot_rate_multiplier", 1.5)))
            default_ot_weekend_mult = Decimal(str(rules.get("ot_weekend_multiplier", 2.0)))
            default_ot_holiday_mult = Decimal(str(rules.get("ot_holiday_multiplier", 2.5)))
            
            # PF/ESI rates from rules
            pf_employee_rate = Decimal(str(rules.get("pf_employee_rate", 12.0))) / Decimal(100)
            pf_employer_rate = Decimal(str(rules.get("pf_employer_rate", 12.0))) / Decimal(100)
            pf_wage_ceiling = Decimal(str(rules.get("pf_wage_ceiling", 15000.0)))
            esi_employee_rate = Decimal(str(rules.get("esi_employee_rate", 0.75))) / Decimal(100)
            esi_employer_rate = Decimal(str(rules.get("esi_employer_rate", 3.25))) / Decimal(100)
            esi_wage_ceiling = Decimal(str(rules.get("esi_wage_ceiling", 21000.0)))
            
            # PT and Welfare from rules
            pt_threshold = Decimal(str(rules.get("pt_threshold", 10000.0)))
            pt_amount = Decimal(str(rules.get("pt_amount", 200.0)))
            welfare_default = Decimal(str(rules.get("welfare_deduction", 3.0)))
            staff_month_days = int(rules.get("staff_month_days", 30))
            
            # --- 1. Extract Components ---
            
            # Common Components
            basic = Decimal(str(salary_structure.get("basic_salary", 0)))
            hra = Decimal(str(salary_structure.get("hra", 0)))
            conveyance = Decimal(str(salary_structure.get("conveyance_allowance", 0)))
            washing = Decimal(str(salary_structure.get("washing_allowance", 0)))
            education = Decimal(str(salary_structure.get("education_allowance", 0)))
            other_allowance = Decimal(str(salary_structure.get("other_allowance", 0)))
            
            # Additional Allowances (Casting, TTB, Plating)
            casting = Decimal(str(salary_structure.get("casting_allowance", 0)))
            ttb = Decimal(str(salary_structure.get("ttb_allowance", 0)))
            plating = Decimal(str(salary_structure.get("plating_allowance", 0)))
            
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
            
            # --- Attendance-Based Allowance Multiplier (using custom thresholds) ---
            def get_allowance_multiplier(worked_days):
                if worked_days >= allowance_full_days:
                    return allowance_full_mult  # Full allowance
                elif worked_days >= allowance_half_days:
                    return allowance_half_mult  # Half allowance
                else:
                    return allowance_none_mult  # No allowance
            
            allowance_multiplier = get_allowance_multiplier(worked_days)
            
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
                # Apply attendance-based allowance multiplier to allowances
                hra_adjusted = hra * allowance_multiplier
                conveyance_adjusted = conveyance * allowance_multiplier
                washing_adjusted = washing * allowance_multiplier
                education_adjusted = education * allowance_multiplier
                other_adjusted = other_allowance * allowance_multiplier
                casting_adjusted = casting * allowance_multiplier
                ttb_adjusted = ttb * allowance_multiplier
                plating_adjusted = plating * allowance_multiplier
                
                daily_total_rate = basic + hra_adjusted + conveyance_adjusted + washing_adjusted + education_adjusted + other_adjusted + casting_adjusted + ttb_adjusted + plating_adjusted
                
                # Wages = Daily Total * Working Days
                wages = daily_total_rate * worked_days
                
                # OT Calculation: (Daily Total / standard_working_hours) * OT Hours
                ot_rate_per_hour = daily_total_rate / standard_working_hours
                
                # Use salary_structure multiplier if provided, else use custom rules default
                ot_rate_multiplier = Decimal(str(salary_structure.get("ot_rate_multiplier", default_ot_mult)))
                ot_weekend_mult = Decimal(str(salary_structure.get("ot_weekend_multiplier", default_ot_weekend_mult)))
                ot_holiday_mult = Decimal(str(salary_structure.get("ot_holiday_multiplier", default_ot_holiday_mult)))
                
                ot_pay_regular = ot_rate_per_hour * ot_rate_multiplier * ot_hours
                ot_pay_weekend = (daily_total_rate / standard_working_hours) * ot_weekend_mult * ot_weekend_hours
                ot_pay_holiday = (daily_total_rate / standard_working_hours) * ot_holiday_mult * ot_holiday_hours
                
                total_ot_pay = ot_pay_regular + ot_pay_weekend + ot_pay_holiday
                
                # Gross Salary = Wages + OT + Other Allowances (Bonus/Incentive typically)
                gross_salary = wages + total_ot_pay + bonus + incentive
                
                lop_deduction = Decimal(0) 

            else:
                # --- STAFF LOGIC (Monthly Based) ---
                # Components are Monthly Fixed
                # Apply attendance-based allowance multiplier to allowances
                hra_adjusted = hra * allowance_multiplier
                conveyance_adjusted = conveyance * allowance_multiplier
                washing_adjusted = washing * allowance_multiplier
                education_adjusted = education * allowance_multiplier
                other_adjusted = other_allowance * allowance_multiplier
                casting_adjusted = casting * allowance_multiplier
                ttb_adjusted = ttb * allowance_multiplier
                plating_adjusted = plating * allowance_multiplier
                
                monthly_gross_components = basic + hra_adjusted + conveyance_adjusted + washing_adjusted + education_adjusted + other_adjusted + casting_adjusted + ttb_adjusted + plating_adjusted
                
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
                
                # OT for Staff (if applicable) - using custom rules
                if ot_hours > 0 or ot_weekend_hours > 0 or ot_holiday_hours > 0:
                     # Staff OT base rate: basic / (staff_month_days * standard_working_hours)
                     ot_base_rate = basic / (Decimal(staff_month_days) * standard_working_hours)
                     ot_multiplier = Decimal(str(salary_structure.get("ot_rate_multiplier", default_ot_mult)))
                     
                     ot_pay_regular = ot_base_rate * ot_multiplier * ot_hours
                     # Use custom rule multipliers
                     ot_weekend_mult = Decimal(str(salary_structure.get("ot_weekend_multiplier", default_ot_weekend_mult)))
                     ot_holiday_mult = Decimal(str(salary_structure.get("ot_holiday_multiplier", default_ot_holiday_mult)))
                     
                     ot_pay_weekend = ot_base_rate * ot_weekend_mult * ot_weekend_hours
                     ot_pay_holiday = ot_base_rate * ot_holiday_mult * ot_holiday_hours
                     
                     total_ot_pay = ot_pay_regular + ot_pay_weekend + ot_pay_holiday
                
                gross_salary = wages + total_ot_pay + bonus + incentive

            # --- 3. Deductions (using custom rules) ---
            
            pf_employee = Decimal(0)
            pf_employer = Decimal(0)
            is_pf_applicable = salary_structure.get("is_pf_applicable", True)
            
            if is_pf_applicable:
                if is_worker:
                    earned_basic = basic * worked_days
                else:
                    per_day_basic = basic / total_days_in_month if total_days_in_month > 0 else 0
                    earned_basic = per_day_basic * (total_days_in_month - unpaid_leaves)
                
                # Check for Slab-based PF
                pf_use_slabs = rules.get("pf_use_slabs", False)
                if pf_use_slabs:
                    pf_slabs_raw = rules.get("pf_slabs")
                    try:
                        if isinstance(pf_slabs_raw, str):
                            pf_slabs = json.loads(pf_slabs_raw)
                        else:
                            pf_slabs = pf_slabs_raw
                        
                        # Find matching slab based on Gross Salary if requested (usually PF is on wages/basic, but let's see)
                        # The user said "above 40000--200", usually this is gross salary range.
                        # I'll use gross_salary for slab matching.
                        match_value = gross_salary
                        
                        for slab in pf_slabs:
                            s_min = Decimal(str(slab.get("min", 0)))
                            s_max = slab.get("max")
                            s_amount = Decimal(str(slab.get("amount", 0)))
                            
                            if match_value >= s_min and (s_max is None or match_value <= Decimal(str(s_max))):
                                pf_employee = s_amount
                                break
                        
                        # Employer contribution usually stays percentage-based or matches? 
                        # In many Indian systems, PF is percentage-based, and Professional Tax is slab-based.
                        # The user said "add a option for pf slabs", which sounds like they want fixed amount PF.
                        # I'll set employer to 0 or match employee? Usually employer also matches or is per rules.
                        # I'll keep employer percentage-based on earned_basic for now, or match employee if that's the intent.
                        # Actually, if it's slab-based fixed amount, usually both are fixed or just one.
                        # Let's match employer to employee for fixed amount if slab is used, or let it be 0.
                        # I'll set employer PF to 0 if slabs are used unless they specify.
                    except Exception as e:
                        print(f"Error parsing PF slabs: {e}")
                else:
                    # Use custom PF ceiling and rates (Percentage-based)
                    pf_base = min(earned_basic, pf_wage_ceiling)
                    pf_employee = pf_base * pf_employee_rate
                    pf_employer = pf_base * pf_employer_rate
            
            esi_employee = Decimal(0)
            esi_employer = Decimal(0)
            is_esi_applicable = salary_structure.get("is_esi_applicable", False)
            
            # Use custom ESI ceiling and rates
            if is_esi_applicable or (gross_salary <= esi_wage_ceiling and gross_salary > 0):
                esi_employee = math_ceil(gross_salary * esi_employee_rate) 
                esi_employer = math_ceil(gross_salary * esi_employer_rate)
            
            # Use custom PT threshold and amount
            pt = Decimal(str(salary_structure.get("professional_tax", 0)))
            if pt == 0 and gross_salary > pt_threshold:
                 pt = pt_amount
            
            # Use custom welfare deduction
            welfare = Decimal(str(salary_structure.get("welfare_deduction", 0)))
            if welfare == 0 and employee_type in ['worker', 'staff']:
                 welfare = welfare_default
            
            tds = Decimal(str(salary_structure.get("tds", 0)))
            loan_deduction = Decimal(str(attendance_summary.get("loan_deduction", 0)))
            
            total_deduction = pf_employee + esi_employee + pt + welfare + tds + loan_deduction
            
            # --- 4. Net Salary ---
            net_salary = gross_salary - total_deduction
            ctc = gross_salary + pf_employer + esi_employer
            
            # Use adjusted allowances for output
            if is_worker:
                hra_display = hra_adjusted * worked_days
                conveyance_display = conveyance_adjusted * worked_days
                washing_display = washing_adjusted * worked_days
                education_display = education_adjusted * worked_days
                other_display = other_adjusted * worked_days
                casting_display = casting_adjusted * worked_days
                ttb_display = ttb_adjusted * worked_days
                plating_display = plating_adjusted * worked_days
            else:
                hra_display = hra_adjusted
                conveyance_display = conveyance_adjusted
                washing_display = washing_adjusted
                education_display = education_adjusted
                other_display = other_adjusted
                casting_display = casting_adjusted
                ttb_display = ttb_adjusted
                plating_display = plating_adjusted
            
            return {
                "payroll": {
                    "employee_type": "Worker" if is_worker else "Staff",
                    "earnings": {
                        "basic_earned": float(round(earned_basic if is_pf_applicable else (wages if not is_worker else wages), 2)),
                        "basic": float(round(earned_basic if is_pf_applicable else (wages if not is_worker else wages), 2)), # Alias for frontend
                        "hra": float(round(hra_display, 2)),
                        "conveyance": float(round(conveyance_display, 2)),
                        "washing": float(round(washing_display, 2)),
                        "medical": float(round(salary_structure.get("medical_allowance", 0) if not is_worker else (Decimal(str(salary_structure.get("medical_allowance", 0))) * worked_days), 2)),
                        "special": float(round(salary_structure.get("special_allowance", 0) if not is_worker else (Decimal(str(salary_structure.get("special_allowance", 0))) * worked_days), 2)),
                        "education": float(round(education_display, 2)),
                        "other": float(round(other_display, 2)),
                        "casting": float(round(casting_display, 2)),
                        "ttb": float(round(ttb_display, 2)),
                        "plating": float(round(plating_display, 2)),
                        
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
                        "paid_days": float(paid_days) if not is_worker else float(worked_days),
                        "allowance_multiplier": float(allowance_multiplier),
                        "allowance_type": "full" if allowance_multiplier == allowance_full_mult else ("half" if allowance_multiplier == allowance_half_mult else "none"),
                        "rules_applied": {
                            "allowance_full_days": allowance_full_days,
                            "allowance_half_days": allowance_half_days,
                            "standard_working_hours": float(standard_working_hours),
                            "pf_employee_rate_percent": float(pf_employee_rate * 100),
                            "pf_employer_rate_percent": float(pf_employer_rate * 100),
                            "pf_wage_ceiling": float(pf_wage_ceiling),
                            "pf_use_slabs": pf_use_slabs,
                            "esi_employee_rate_percent": float(esi_employee_rate * 100),
                            "esi_employer_rate_percent": float(esi_employer_rate * 100),
                            "esi_wage_ceiling": float(esi_wage_ceiling),
                            "pt_threshold": float(pt_threshold),
                            "pt_amount": float(pt_amount),
                            "welfare_deduction": float(welfare_default),
                            "is_custom_rules": custom_rules is not None
                        }
                    }
                }
            }
        except Exception as e:
            return {"error": f"Calculation Error: {str(e)}"}

payroll_service = PayrollService()
