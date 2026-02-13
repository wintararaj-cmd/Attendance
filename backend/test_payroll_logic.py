import sys
import os
from decimal import Decimal

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.payroll import payroll_service

def test_worker_payroll():
    """Test Worker Payroll Logic (Daily Rate)"""
    print("\n--- Testing Worker Payroll ---")
    
    # Structure: Daily Rates
    salary_structure = {
        "basic_salary": 500, # Per Day
        "hra": 100,
        "conveyance_allowance": 50,
        "washing_allowance": 20,
        "education_allowance": 10,
        "other_allowance": 20,
        "bonus": 1000,
        "incentive": 500,
        "is_hourly_based": False, # Daily worker
        "ot_rate_multiplier": 1.0, # (Daily/8)*Hours
        "is_pf_applicable": True,
        "is_esi_applicable": True,
        "professional_tax": 0, # Auto-calc
        "welfare_deduction": 3
    }
    
    # Attendance: Working Days = 20
    attendance_summary = {
        "total_days_in_month": 30,
        "present_days": 20, # Worked 20 days
        "paid_days": 20,
        "ot_hours": 10,
        "ot_weekend_hours": 0,
        "ot_holiday_hours": 0,
        "loan_deduction": 0
    }
    
    # Expected:
    # Daily Total = 500+100+50+20+10+20 = 700
    # Wages = 700 * 20 = 14000
    # OT Rate = 700 / 8 = 87.5
    # OT Amount = 87.5 * 10 = 875
    # Gross = 14000 + 875 + 1000 + 500 = 16375
    
    # PF = 12% of Earned Basic? 
    # Earned Basic = 500 * 20 = 10000.
    # PF = 1200.
    
    # ESI = 0.75% of Gross (16375) = 122.81 -> 123
    
    # PT: Gross > 10000 -> 200
    # Welfare: 3
    
    # Total Deduction = 1200 + 123 + 200 + 3 = 1526
    # Net Salary = 16375 - 1526 = 14849
    
    result = payroll_service.calculate_net_salary(salary_structure, attendance_summary, employee_type="worker")
    
    payroll = result.get("payroll", result) # In case structured differently
    earnings = payroll.get("earnings", {})
    deductions = payroll.get("deductions", {})
    
    print(f"Daily Rate: {earnings.get('daily_rate')} (Expected 700.0)")
    print(f"Wages Total: {earnings.get('wages_total')} (Expected 14000.0)")
    print(f"OT Amount: {earnings.get('ot_amount')} (Expected 875.0)")
    print(f"Gross Salary: {earnings.get('gross_salary')} (Expected 16375.0)")
    
    print(f"PF: {deductions.get('pf')} (Expected 1200.0)")
    print(f"ESI: {deductions.get('esi')} (Expected 123.0)")
    print(f"Net Salary: {payroll.get('net_salary')} (Expected 14849.0)")
    
    assert earnings.get('gross_salary') == 16375.0
    assert deductions.get('pf') == 1200.0

def test_staff_payroll():
    """Test Staff Payroll Logic (Monthly Rate)"""
    print("\n--- Testing Staff Payroll ---")
    
    # Structure: Monthly Fixed
    salary_structure = {
        "basic_salary": 15000, # Monthly
        "hra": 3000,
        "conveyance_allowance": 1500,
        "washing_allowance": 500,
        "education_allowance": 0,
        "other_allowance": 0,
        "bonus": 0,
        "incentive": 0,
        "is_hourly_based": False,
        "is_pf_applicable": True,
        "is_esi_applicable": False, # Explicitly false
        "professional_tax": 200,
        "welfare_deduction": 3
    }
    
    # Attendance: 30 days month, 2 Unpaid Leaves
    attendance_summary = {
        "total_days_in_month": 30,
        "present_days": 28, # Assuming present means paid for staff minus leave
        "unpaid_leaves": 2,
        "ot_hours": 0,
        "ot_weekend_hours": 0,
        "ot_holiday_hours": 0,
        "loan_deduction": 0
    }
    
    # Expected:
    # Monthly Gross Components = 15000+3000+1500+500 = 20000
    # Per Day Gross = 20000 / 30 = 666.666...
    # LOP Deduction = 666.666 * 2 = 1333.33
    # Wages (Earned Gross) = 20000 - 1333.33 = 18666.67
    
    # Gross Salary = 18666.67
    
    # PF = 12% of Earned Basic.
    # Monthly Basic = 15000. Per Day Basic = 500.
    # Earned Basic = 500 * (30-2) = 14000.
    # PF = 0.12 * 14000 = 1680.
    
    # PT = 200. Welfare = 3.
    # Total Deduction = 1680 + 200 + 3 = 1883.
    # Net Salary = 18666.67 - 1883 = 16783.67
    
    result = payroll_service.calculate_net_salary(salary_structure, attendance_summary, employee_type="staff")
    
    payroll = result.get("payroll", result) # Direct dict
    earnings = payroll.get("earnings", {})
    deductions = payroll.get("deductions", {})
    
    print(f"Gross Salary: {earnings.get('gross_salary')} (Expected ~18666.67)")
    print(f"PF: {deductions.get('pf')} (Expected 1680.0)")
    print(f"Net Salary: {payroll.get('net_salary')} (Expected ~16783.67)")
    
    # Floating point comparison
    assert abs(earnings.get('gross_salary') - 18666.67) < 0.1
    assert abs(deductions.get('pf') - 1680.0) < 0.1

if __name__ == "__main__":
    try:
        test_worker_payroll()
        test_staff_payroll()
        print("\n[SUCCESS] All Tests Passed!")
    except AssertionError as e:
        print(f"\n[FAILURE] Test Failed: {e}")
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
