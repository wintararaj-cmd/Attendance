# Payroll Configuration Guide

## Overview
This guide explains how to configure and manage payroll in the Attendance System, including salary structures, overtime rules, PF, ESI, and other statutory deductions.

---

## Table of Contents
1. [Basic Salary Configuration](#basic-salary-configuration)
2. [Understanding Salary Components](#understanding-salary-components)
3. [Overtime (OT) Rules](#overtime-ot-rules)
4. [Provident Fund (PF) Calculation](#provident-fund-pf-calculation)
5. [ESI (Employee State Insurance)](#esi-employee-state-insurance)
6. [HRA (House Rent Allowance) Rules](#hra-house-rent-allowance-rules)
7. [Professional Tax](#professional-tax)
8. [Step-by-Step Configuration](#step-by-step-configuration)

---

## Basic Salary Configuration

### How to Configure Employee Salary

1. **Navigate to Payroll Management**
   - Click on "Payroll" in the sidebar
   - You'll see a list of all active employees

2. **Click "Configure" Button**
   - Find the employee you want to configure
   - Click the "Configure" button next to their name

3. **Enter Salary Components**
   - **Basic Salary**: The base salary (typically 40-50% of CTC)
   - **HRA Allowance**: House Rent Allowance
   - **Special Allowance**: Any additional allowances
   - **PF Deduction**: Provident Fund deduction
   - **Professional Tax**: State-specific tax

4. **Save Configuration**
   - Click "Save Salary Configuration"
   - The system will calculate and display the net salary

---

## Understanding Salary Components

### Earnings Components

#### 1. **Basic Salary**
- **Definition**: The core component of salary
- **Typical Range**: 40-50% of CTC
- **Example**: For ₹30,000 CTC, Basic = ₹15,000

#### 2. **HRA (House Rent Allowance)**
- **Definition**: Allowance for housing expenses
- **Standard Calculation**:
  - **Metro Cities**: 50% of Basic
  - **Non-Metro Cities**: 40% of Basic
- **Example**: Basic ₹15,000 → HRA = ₹7,500 (Metro)

#### 3. **Special Allowance**
- **Definition**: Additional allowances (Transport, Medical, etc.)
- **Calculation**: Remaining amount after Basic + HRA + Statutory deductions
- **Example**: CTC ₹30,000 - Basic ₹15,000 - HRA ₹7,500 - PF ₹1,800 = ₹5,700

### Deduction Components

#### 1. **Provident Fund (PF)**
- **Employee Contribution**: 12% of Basic
- **Employer Contribution**: 12% of Basic (not deducted from salary)
- **Applicability**: Mandatory for companies with 20+ employees
- **Example**: Basic ₹15,000 → PF = ₹1,800

#### 2. **Professional Tax**
- **Definition**: State-specific tax
- **Varies by State**:
  - Maharashtra: ₹200/month
  - Karnataka: ₹200/month
  - Tamil Nadu: ₹0-₹208/month (based on salary)
  - Some states: No PT

#### 3. **ESI (Employee State Insurance)**
- **Employee Contribution**: 0.75% of Gross Salary
- **Employer Contribution**: 3.25% of Gross Salary
- **Applicability**: Gross salary ≤ ₹21,000/month
- **Example**: Gross ₹20,000 → ESI = ₹150

---

## Overtime (OT) Rules

### Standard OT Calculation

#### Formula
```
OT Rate = (Basic Salary / 26 / 8) × OT Multiplier
```

#### OT Multipliers
- **Regular OT (Weekday)**: 1.5x
- **Weekend OT**: 2x
- **Holiday OT**: 2.5x

#### Example Calculation
```
Basic Salary: ₹15,000
Per Day Rate: ₹15,000 / 26 = ₹576.92
Per Hour Rate: ₹576.92 / 8 = ₹72.12

Weekday OT (1 hour): ₹72.12 × 1.5 = ₹108.18
Weekend OT (1 hour): ₹72.12 × 2.0 = ₹144.24
Holiday OT (1 hour): ₹72.12 × 2.5 = ₹180.30
```

### How to Configure OT
*(Feature to be implemented)*
1. Set standard working hours (default: 8 hours/day)
2. Define OT multipliers for different scenarios
3. System auto-calculates based on attendance logs

---

## Provident Fund (PF) Calculation

### PF Rules (As per EPFO)

#### Contribution Breakdown
```
Employee Contribution: 12% of Basic + DA
Employer Contribution: 12% of Basic + DA
  ├─ EPF (Employee Provident Fund): 3.67%
  ├─ EPS (Employee Pension Scheme): 8.33% (max ₹1,250)
  └─ EDLI (Insurance): 0.5%
```

#### Calculation Example
```
Basic Salary: ₹15,000
DA (Dearness Allowance): ₹0 (if applicable)

Employee PF: ₹15,000 × 12% = ₹1,800
Employer PF: ₹15,000 × 12% = ₹1,800
  ├─ EPF: ₹15,000 × 3.67% = ₹550.50
  ├─ EPS: Min(₹15,000 × 8.33%, ₹1,250) = ₹1,249.50
  └─ EDLI: ₹15,000 × 0.5% = ₹75

Total PF (Employee Account): ₹1,800 + ₹550.50 = ₹2,350.50
```

#### Current System Configuration
- Enter **Employee PF Deduction** (12% of Basic)
- System deducts this from gross salary
- Employer contribution is tracked separately (not deducted from salary)

---

## ESI (Employee State Insurance)

### ESI Eligibility
- **Wage Ceiling**: Gross salary ≤ ₹21,000/month
- **Coverage**: Medical benefits for employee and family

### ESI Contribution Rates
```
Employee Contribution: 0.75% of Gross Salary
Employer Contribution: 3.25% of Gross Salary
```

### Calculation Example
```
Gross Salary: ₹20,000

Employee ESI: ₹20,000 × 0.75% = ₹150
Employer ESI: ₹20,000 × 3.25% = ₹650
```

### How to Configure ESI
*(To be implemented in enhanced version)*
1. System checks if Gross ≤ ₹21,000
2. Auto-calculates 0.75% of Gross
3. Deducts from salary if applicable

---

## HRA (House Rent Allowance) Rules

### HRA Tax Exemption Rules

The **least** of the following is exempt from tax:
1. Actual HRA received
2. 50% of Basic (Metro) or 40% of Basic (Non-Metro)
3. Rent paid - 10% of Basic

### Standard HRA Calculation
```
Metro Cities (Mumbai, Delhi, Kolkata, Chennai):
  HRA = 50% of Basic Salary

Non-Metro Cities:
  HRA = 40% of Basic Salary
```

### Example
```
Basic Salary: ₹15,000
Location: Mumbai (Metro)

HRA = ₹15,000 × 50% = ₹7,500
```

### How to Configure
1. In salary configuration, enter HRA amount
2. Recommended: Use 40-50% of Basic as guideline
3. System includes HRA in gross earnings

---

## Professional Tax

### State-wise Professional Tax Rates

| State | Monthly PT |
|-------|-----------|
| Maharashtra | ₹200 |
| Karnataka | ₹200 |
| West Bengal | ₹200 |
| Tamil Nadu | ₹0-₹208 (slab-based) |
| Andhra Pradesh | ₹200 |
| Telangana | ₹200 |
| Gujarat | ₹0-₹200 (slab-based) |
| Madhya Pradesh | ₹208 |
| Others | Varies or ₹0 |

### How to Configure
1. Enter the applicable PT amount for your state
2. Common values: ₹0, ₹200, ₹208
3. System deducts this from gross salary

---

## Step-by-Step Configuration

### Example: Configuring Salary for an Employee

**Employee Details:**
- Name: Rajesh Kumar
- Location: Mumbai
- CTC: ₹30,000/month

**Step 1: Calculate Components**
```
CTC: ₹30,000

Basic Salary (50% of CTC): ₹15,000
HRA (50% of Basic - Metro): ₹7,500
PF (12% of Basic): ₹1,800
Professional Tax (Maharashtra): ₹200

Special Allowance = CTC - Basic - HRA - Employer PF
                  = ₹30,000 - ₹15,000 - ₹7,500 - ₹1,800
                  = ₹5,700
```

**Step 2: Enter in System**
1. Go to Payroll Management
2. Click "Configure" for Rajesh Kumar
3. Enter:
   - Basic Salary: `15000`
   - HRA Allowance: `7500`
   - Special Allowance: `5700`
   - PF Deduction: `1800`
   - Professional Tax: `200`
4. Click "Save Salary Configuration"

**Step 3: Verify Calculation**
```
Gross Salary: ₹15,000 + ₹7,500 + ₹5,700 = ₹28,200
Total Deductions: ₹1,800 + ₹200 = ₹2,000
Net Salary: ₹28,200 - ₹2,000 = ₹26,200
```

---

## Salary Calculation Formula

### Current System Formula

```
Gross Salary = Basic + HRA + Special Allowance

Total Deductions = PF + Professional Tax + LOP

Net Salary = Gross Salary - Total Deductions
```

### LOP (Loss of Pay) Calculation
```
Per Day Salary = Basic Salary / 26
LOP Amount = Per Day Salary × Absent Days
```

---

## Common Salary Structures

### Structure 1: Basic CTC ₹20,000
```
Basic Salary: ₹10,000 (50%)
HRA: ₹5,000 (50% of Basic)
Special Allowance: ₹3,800
PF: ₹1,200 (12% of Basic)
Professional Tax: ₹200

Gross: ₹18,800
Deductions: ₹1,400
Net: ₹17,400
```

### Structure 2: CTC ₹50,000
```
Basic Salary: ₹25,000 (50%)
HRA: ₹12,500 (50% of Basic)
Special Allowance: ₹9,500
PF: ₹3,000 (12% of Basic)
Professional Tax: ₹200

Gross: ₹47,000
Deductions: ₹3,200
Net: ₹43,800
```

---

## Best Practices

### 1. Salary Structure Design
- Keep Basic at 40-50% of CTC
- HRA should be 40-50% of Basic
- Ensure compliance with minimum wage laws

### 2. Statutory Compliance
- PF is mandatory for companies with 20+ employees
- ESI is mandatory for employees earning ≤ ₹21,000
- Professional Tax varies by state

### 3. Documentation
- Maintain salary breakup documents
- Keep PF and ESI registration certificates
- Document any special allowances

### 4. Regular Reviews
- Review salary structures annually
- Update for statutory changes
- Adjust for inflation and performance

---

## Troubleshooting

### Issue: Net Salary is Negative
**Solution**: Check if deductions exceed gross salary. Adjust components.

### Issue: PF Amount Seems Wrong
**Solution**: PF should be 12% of Basic. Verify Basic Salary is correct.

### Issue: Professional Tax Varies
**Solution**: PT is state-specific. Verify the correct rate for your state.

---

## Future Enhancements

The following features are planned for future releases:

1. **Automated OT Calculation**
   - Based on attendance logs
   - Configurable OT rates
   - Weekend/Holiday detection

2. **ESI Auto-Calculation**
   - Auto-detect eligibility (Gross ≤ ₹21,000)
   - Calculate 0.75% automatically
   - Generate ESI reports

3. **Gratuity Calculation**
   - For employees with 5+ years service
   - Formula: (Basic × Years × 15) / 26

4. **Bonus Calculation**
   - Annual/Festival bonus
   - Performance-based bonus

5. **Salary Templates**
   - Pre-defined salary structures
   - Quick apply to multiple employees

6. **Payroll Reports**
   - Monthly payroll summary
   - PF/ESI challans
   - Tax reports

---

## Support

For questions or issues:
1. Check this documentation
2. Review the system's built-in help
3. Contact your HR administrator

---

**Last Updated**: January 30, 2026
**Version**: 1.0
