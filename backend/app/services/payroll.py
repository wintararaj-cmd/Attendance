from decimal import Decimal

class PayrollService:
    def calculate_net_salary(self, salary_structure: dict, attendance_summary: dict, employee_type: str = "full_time") -> dict:
        """
        Calculate comprehensive payroll for an employee based on Indian salary standards.
        Supports: Full-time, Part-time, Contract workers with OT calculation
        Includes: Basic, HRA, Allowances, PF, ESI, PT, TDS, LOP, Overtime
        """
        
        # 1. Extract Salary Components (Safe Conversion)
        try:
            # Check if hourly-based or contract-based
            is_hourly_based = salary_structure.get("is_hourly_based", False)
            hourly_rate = Decimal(str(salary_structure.get("hourly_rate", 0)))
            contract_rate_per_day = Decimal(str(salary_structure.get("contract_rate_per_day", 0)))
            
            # OT Multipliers
            ot_rate_multiplier = Decimal(str(salary_structure.get("ot_rate_multiplier", 1.5)))
            ot_weekend_multiplier = Decimal(str(salary_structure.get("ot_weekend_multiplier", 2.0)))
            ot_holiday_multiplier = Decimal(str(salary_structure.get("ot_holiday_multiplier", 2.5)))
            
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
            
            # OT Hours (different types)
            ot_hours = Decimal(str(attendance_summary.get("ot_hours", 0)))  # Regular weekday OT
            ot_weekend_hours = Decimal(str(attendance_summary.get("ot_weekend_hours", 0)))  # Weekend OT
            ot_holiday_hours = Decimal(str(attendance_summary.get("ot_holiday_hours", 0)))  # Holiday OT
            total_hours_worked = Decimal(str(attendance_summary.get("total_hours_worked", 0)))  # For hourly workers
            
        except Exception as e:
            return {"error": f"Invalid input format: {e}"}
        
        # 2. Calculate Gross Salary based on Employee Type
        if employee_type == "part_time" and is_hourly_based and hourly_rate > 0:
            # Part-time hourly worker
            # Calculate based on hours worked
            if total_hours_worked > 0:
                gross_salary = hourly_rate * total_hours_worked
            else:
                # Fallback: use standard hours (8 hours/day * present days)
                standard_hours = present_days * Decimal(8)
                gross_salary = hourly_rate * standard_hours
            
            # For part-time, allowances are typically not applicable
            # But we'll include them if configured
            gross_salary = gross_salary + hra + conveyance + medical + special + education + other
            
        elif employee_type == "contract" and contract_rate_per_day > 0:
            # Contract worker with daily rate
            gross_salary = contract_rate_per_day * present_days
            # Add any configured allowances
            gross_salary = gross_salary + hra + conveyance + medical + special + education + other
            
        else:
            # Full-time or standard monthly salary
            gross_salary = (
                basic_salary + hra + conveyance + medical + 
                special + education + other
            )
        
        # 3. Calculate Earnings
        # Per day salary for LOP calculation
        per_day_salary = gross_salary / total_days
        
        # Loss of Pay (LOP) Deduction
        lop_deduction = per_day_salary * unpaid_leaves
        
        # 4. Calculate Overtime Pay
        # Determine base hourly rate
        if is_hourly_based and hourly_rate > 0:
            base_hourly_rate = hourly_rate
        elif contract_rate_per_day > 0:
            # For contract workers: daily rate / 8 hours
            base_hourly_rate = contract_rate_per_day / Decimal(8)
        else:
            # For full-time: basic salary / 240 hours (30 days × 8 hours)
            base_hourly_rate = basic_salary / Decimal(240)
        
        # Calculate OT pay for different types
        ot_regular_pay = base_hourly_rate * ot_rate_multiplier * ot_hours
        ot_weekend_pay = base_hourly_rate * ot_weekend_multiplier * ot_weekend_hours
        ot_holiday_pay = base_hourly_rate * ot_holiday_multiplier * ot_holiday_hours
        total_overtime_pay = ot_regular_pay + ot_weekend_pay + ot_holiday_pay
        
        # Actual Gross Earned (after LOP, before deductions)
        gross_earned = gross_salary - lop_deduction + total_overtime_pay + bonus + incentive
        
        # 5. Calculate Deductions
        
        # PF (Provident Fund) - 12% of Basic (both employee and employer)
        # Only if Basic <= 15,000 (statutory limit) or if opted
        # Note: Part-time and contract workers may not be eligible for PF
        pf_employee = Decimal(0)
        pf_employer = Decimal(0)
        
        if employee_type == "full_time" and is_pf_applicable and basic_salary > 0:
            pf_base = min(basic_salary, Decimal(15000))  # PF ceiling
            pf_employee = pf_base * Decimal(0.12)
            pf_employer = pf_base * Decimal(0.12)
        elif employee_type in ["part_time", "contract"] and is_pf_applicable:
            # For part-time/contract, PF may be optional or calculated differently
            # If they have a basic salary configured, use it
            if basic_salary > 0:
                pf_base = min(basic_salary, Decimal(15000))
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
        # Part-time/contract workers may have different PT rules
        professional_tax = Decimal(0)
        if employee_type == "full_time":
            if gross_earned > 10000:
                professional_tax = Decimal(200)
        else:
            # For part-time/contract, PT may be prorated or not applicable
            if gross_earned > 10000:
                professional_tax = Decimal(200)
        
        # TDS (Tax Deducted at Source) - Simplified, can be customized
        tds = Decimal(str(salary_structure.get("tds", 0)))
        
        # Total Deductions (Employee side only)
        total_deductions = pf_employee + esi_employee + professional_tax + tds + lop_deduction
        
        # 6. Net Salary
        net_salary = gross_earned - total_deductions
        
        # 7. Cost to Company (CTC) - Employer's total cost
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
                    "overtime_regular": float(round(ot_regular_pay, 2)),
                    "overtime_weekend": float(round(ot_weekend_pay, 2)),
                    "overtime_holiday": float(round(ot_holiday_pay, 2)),
                    "overtime_total": float(round(total_overtime_pay, 2)),
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
                "ot_hours": float(ot_hours),
                "ot_weekend_hours": float(ot_weekend_hours),
                "ot_holiday_hours": float(ot_holiday_hours),
                "total_hours_worked": float(total_hours_worked)
            },
            "rates": {
                "hourly_rate": float(round(hourly_rate, 2)) if is_hourly_based else None,
                "contract_rate_per_day": float(round(contract_rate_per_day, 2)) if contract_rate_per_day > 0 else None,
                "base_hourly_rate": float(round(base_hourly_rate, 2)),
                "ot_rate_multiplier": float(ot_rate_multiplier),
                "ot_weekend_multiplier": float(ot_weekend_multiplier),
                "ot_holiday_multiplier": float(ot_holiday_multiplier)
            }
        }

payroll_service = PayrollService()
