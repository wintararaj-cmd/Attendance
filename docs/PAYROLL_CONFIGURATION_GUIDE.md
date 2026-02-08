# Payroll Configuration Guide

## Overview
This guide explains how to configure and manage payroll in the Attendance System, including salary structures, overtime rules, PF, ESI, and other statutory deductions.

---

## Table of Contents
1. [Basic Salary Configuration](#basic-salary-configuration)
2. [Understanding Salary Components](#understanding-salary-components)
   - [Earnings Components](#earnings-components)
   - [Deduction Components](#deduction-components)
   - [Benefits Components](#benefits-components)
3. [Overtime (OT) Rules](#overtime-ot-rules)
4. [Provident Fund (PF) Calculation](#provident-fund-pf-calculation)
5. [ESI (Employee State Insurance)](#esi-employee-state-insurance)
6. [HRA (House Rent Allowance) Rules](#hra-house-rent-allowance-rules)
7. [Professional Tax](#professional-tax)
8. [TDS (Tax Deducted at Source)](#tds-tax-deducted-at-source)
9. [Step-by-Step Configuration](#step-by-step-configuration)
10. [Salary Calculation Formula](#salary-calculation-formula)
11. [Common Salary Structures](#common-salary-structures)
12. [Best Practices](#best-practices)
13. [Troubleshooting](#troubleshooting)
14. [Future Enhancements](#future-enhancements)

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

#### 3. **Conveyance Allowance**
- **Definition**: Allowance for commuting/transportation expenses
- **Tax Exemption**: Up to ₹1,600/month (₹19,200/year) is tax-free
- **Typical Range**: ₹800 - ₹1,600/month
- **Example**: ₹1,600/month

#### 4. **Medical Allowance**
- **Definition**: Allowance for medical expenses
- **Tax Exemption**: Up to ₹15,000/year on actual medical bills
- **Typical Range**: ₹1,250/month (₹15,000/year)
- **Example**: ₹1,250/month

#### 5. **Education Allowance**
- **Definition**: Allowance for children's education expenses
- **Tax Exemption**: Up to ₹100/month per child (max 2 children)
- **Typical Range**: ₹0 - ₹200/month
- **Example**: ₹100/month per child

#### 6. **Other Allowance**
- **Definition**: Any other miscellaneous allowances
- **Examples**: Telephone allowance, uniform allowance, etc.
- **Typical Range**: Varies based on company policy
- **Example**: ₹500/month

#### 7. **Special Allowance**
- **Definition**: Balancing component to reach desired CTC
- **Calculation**: CTC - (Basic + HRA + Other Allowances + Statutory deductions)
- **Note**: Fully taxable
- **Example**: CTC ₹30,000 - Basic ₹15,000 - HRA ₹7,500 - Conveyance ₹1,600 - Medical ₹1,250 - PF ₹1,800 = ₹2,850

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

### Benefits Components

#### 1. **Bonus**
- **Definition**: Annual or festival bonus paid to employees
- **Common Types**:
  - **Performance Bonus**: Based on individual/company performance
  - **Festival Bonus**: Diwali, Eid, Christmas bonuses
  - **Statutory Bonus**: As per Payment of Bonus Act, 1965
- **Calculation**: Varies by company policy
- **Tax Treatment**: Fully taxable
- **Example**: ₹5,000 annual bonus = ₹417/month

#### 2. **Incentive**
- **Definition**: Performance-based variable pay
- **Common Types**:
  - **Sales Incentive**: Based on sales targets
  - **Production Incentive**: Based on production output
  - **Attendance Incentive**: For perfect attendance
- **Calculation**: Varies by company policy and performance
- **Tax Treatment**: Fully taxable
- **Example**: ₹2,000/month for meeting targets

---

## Overtime (OT) Rules

### Standard OT Calculation

#### Formula
```
Hourly Rate = Basic Salary / 240 hours
(240 hours = 30 days × 8 hours/day)

OT Pay = Hourly Rate × OT Multiplier × OT Hours
```

#### OT Multipliers
- **Regular OT (Weekday)**: 1.5x
- **Weekend OT**: 2x
- **Holiday OT**: 2.5x

#### Example Calculation
```
Basic Salary: ₹15,000
Hourly Rate: ₹15,000 / 240 = ₹62.50

Weekday OT (1 hour): ₹62.50 × 1.5 = ₹93.75
Weekend OT (1 hour): ₹62.50 × 2.0 = ₹125.00
Holiday OT (1 hour): ₹62.50 × 2.5 = ₹156.25

Example: 10 hours weekday OT = ₹62.50 × 1.5 × 10 = ₹937.50
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
Employee Contribution: 12% of Basic + DA (subject to ceiling)
Employer Contribution: 12% of Basic + DA (subject to ceiling)
  ├─ EPF (Employee Provident Fund): 3.67%
  ├─ EPS (Employee Pension Scheme): 8.33% (max ₹1,250)
  └─ EDLI (Insurance): 0.5%

PF Ceiling: ₹15,000
(PF is calculated on Basic or ₹15,000, whichever is lower)
```

#### Calculation Example 1 (Basic ≤ ₹15,000)
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

#### Calculation Example 2 (Basic > ₹15,000)
```
Basic Salary: ₹25,000
PF Base: ₹15,000 (ceiling applied)

Employee PF: ₹15,000 × 12% = ₹1,800
Employer PF: ₹15,000 × 12% = ₹1,800
  ├─ EPF: ₹15,000 × 3.67% = ₹550.50
  ├─ EPS: ₹1,250 (maximum limit)
  └─ EDLI: ₹15,000 × 0.5% = ₹75

Note: Even though Basic is ₹25,000, PF is calculated on ₹15,000 only
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

## TDS (Tax Deducted at Source)

### TDS Overview
- **Definition**: Tax deducted by employer on behalf of employee
- **Applicability**: Based on annual income and tax slabs
- **Governed by**: Income Tax Act, 1961

### When is TDS Applicable?
TDS is deducted if annual income exceeds the basic exemption limit:
- **FY 2023-24**: ₹2,50,000 (Old Regime) / ₹3,00,000 (New Regime)
- **Senior Citizens (60-80 years)**: ₹3,00,000
- **Super Senior Citizens (80+ years)**: ₹5,00,000

### Income Tax Slabs (New Regime - FY 2023-24)
| Annual Income | Tax Rate |
|---------------|----------|
| Up to ₹3,00,000 | Nil |
| ₹3,00,001 - ₹6,00,000 | 5% |
| ₹6,00,001 - ₹9,00,000 | 10% |
| ₹9,00,001 - ₹12,00,000 | 15% |
| ₹12,00,001 - ₹15,00,000 | 20% |
| Above ₹15,00,000 | 30% |

### How to Calculate TDS
```
Step 1: Calculate Annual Gross Salary
Annual Gross = Monthly Gross × 12

Step 2: Deduct Exemptions
- Standard Deduction: ₹50,000
- HRA Exemption (if applicable)
- 80C Deductions (PF, LIC, etc.)
- Other deductions (80D, 80E, etc.)

Step 3: Calculate Taxable Income
Taxable Income = Annual Gross - Exemptions

Step 4: Apply Tax Slabs
Calculate tax based on applicable slab

Step 5: Monthly TDS
Monthly TDS = Annual Tax / 12
```

### Example TDS Calculation
```
Annual Gross: ₹6,00,000
Less: Standard Deduction: ₹50,000
Less: 80C (PF): ₹21,600
Taxable Income: ₹5,28,400

Tax Calculation (New Regime):
  On ₹3,00,000: Nil
  On ₹2,28,400 (₹5,28,400 - ₹3,00,000): 5% = ₹11,420
  
Annual Tax: ₹11,420
Monthly TDS: ₹11,420 / 12 = ₹952

Note: Add 4% Health & Education Cess = ₹952 × 1.04 = ₹990
```

### How to Configure TDS
1. Calculate annual tax liability
2. Divide by 12 for monthly TDS
3. Enter in salary configuration
4. System deducts this amount monthly

### TDS Exemptions
- **HRA**: Least of (Actual HRA, 50% of Basic, Rent - 10% of Basic)
- **Standard Deduction**: ₹50,000/year
- **80C**: Up to ₹1,50,000 (PF, PPF, LIC, ELSS, etc.)
- **80D**: Medical insurance premiums
- **80E**: Education loan interest

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
Conveyance Allowance: ₹1,600
Medical Allowance: ₹1,250
Education Allowance: ₹100
PF (12% of Basic): ₹1,800
Professional Tax (Maharashtra): ₹200

Special Allowance = CTC - Basic - HRA - Conveyance - Medical - Education - Employer PF
                  = ₹30,000 - ₹15,000 - ₹7,500 - ₹1,600 - ₹1,250 - ₹100 - ₹1,800
                  = ₹2,750
```

**Step 2: Enter in System**
1. Go to Payroll Management
2. Click "Configure" for Rajesh Kumar
3. Enter:
   - Basic Salary: `15000`
   - HRA Allowance: `7500`
   - Conveyance Allowance: `1600`
   - Medical Allowance: `1250`
   - Education Allowance: `100`
   - Special Allowance: `2750`
   - PF Deduction: `1800`
   - Professional Tax: `200`
   - ESI: `0` (not applicable as gross > ₹21,000)
   - TDS: `0` (if applicable, calculate separately)
   - Bonus: `0` (if applicable)
   - Incentive: `0` (if applicable)
4. Click "Save Salary Configuration"

**Step 3: Verify Calculation**
```
Gross Salary: ₹15,000 + ₹7,500 + ₹1,600 + ₹1,250 + ₹100 + ₹2,750 = ₹28,200
Total Deductions: ₹1,800 + ₹200 = ₹2,000
Net Salary: ₹28,200 - ₹2,000 = ₹26,200
CTC: ₹28,200 + ₹1,800 (Employer PF) = ₹30,000
```

---

## Salary Calculation Formula

### Current System Formula

#### Step 1: Calculate Gross Salary (Standard)
```
Gross Salary = Basic + HRA + Conveyance + Medical + 
               Special + Education + Other Allowances
```

#### Step 2: Calculate Per Day Salary
```
Per Day Salary = Gross Salary / Total Working Days
(Default: 30 days, configurable based on month)
```

#### Step 3: Calculate Earnings Adjustments
```
LOP (Loss of Pay) = Per Day Salary × Unpaid Leave Days

Overtime Pay = (Basic / 240) × 1.5 × Overtime Hours

Gross Earned = Gross Salary - LOP + Overtime + Bonus + Incentive
```

#### Step 4: Calculate Deductions
```
PF = Min(Basic, ₹15,000) × 12% (if applicable)

ESI = Gross Salary × 0.75% (if Gross ≤ ₹21,000 and applicable)

Professional Tax = State-specific amount (e.g., ₹200 for Maharashtra)

TDS = As configured (if applicable)

Total Deductions = PF + ESI + Professional Tax + TDS + LOP
```

#### Step 5: Calculate Net Salary
```
Net Salary = Gross Earned - Total Deductions
```

#### Step 6: Calculate CTC (Cost to Company)
```
CTC = Gross Salary + Employer PF + Employer ESI + Bonus + Incentive
```

### Complete Example
```
Input:
  Basic: ₹15,000
  HRA: ₹7,500
  Conveyance: ₹1,600
  Medical: ₹1,250
  Special: ₹2,850
  Bonus: ₹500
  Incentive: ₹1,000
  
  Working Days: 30
  Present Days: 28
  Unpaid Leaves: 2
  Overtime Hours: 10
  
  PF Applicable: Yes
  ESI Applicable: No
  State: Maharashtra

Calculation:
  Gross Salary = 15,000 + 7,500 + 1,600 + 1,250 + 2,850 = ₹28,200
  Per Day = 28,200 / 30 = ₹940
  
  LOP = 940 × 2 = ₹1,880
  Overtime = (15,000 / 240) × 1.5 × 10 = ₹937.50
  
  Gross Earned = 28,200 - 1,880 + 937.50 + 500 + 1,000 = ₹28,757.50
  
  Deductions:
    PF = 15,000 × 12% = ₹1,800
    ESI = ₹0 (not applicable)
    PT = ₹200
    TDS = ₹0
    Total = ₹1,800 + ₹200 + ₹1,880 (LOP) = ₹3,880
  
  Net Salary = 28,757.50 - 3,880 = ₹24,877.50
  
  CTC = 28,200 + 1,800 (Employer PF) + 500 + 1,000 = ₹31,500
```

---

## Common Salary Structures

### Structure 1: Basic CTC ₹20,000
```
Earnings:
  Basic Salary: ₹10,000 (50%)
  HRA: ₹5,000 (50% of Basic)
  Conveyance: ₹1,600
  Medical: ₹1,250
  Education: ₹100
  Special Allowance: ₹850
  ─────────────────────
  Gross: ₹18,800

Deductions:
  PF: ₹1,200 (12% of Basic)
  Professional Tax: ₹200
  ─────────────────────
  Total Deductions: ₹1,400

Net Salary: ₹17,400
CTC: ₹20,000 (Gross + Employer PF)
```

### Structure 2: CTC ₹30,000
```
Earnings:
  Basic Salary: ₹15,000 (50%)
  HRA: ₹7,500 (50% of Basic)
  Conveyance: ₹1,600
  Medical: ₹1,250
  Education: ₹100
  Special Allowance: ₹2,750
  ─────────────────────
  Gross: ₹28,200

Deductions:
  PF: ₹1,800 (12% of Basic)
  Professional Tax: ₹200
  ─────────────────────
  Total Deductions: ₹2,000

Net Salary: ₹26,200
CTC: ₹30,000 (Gross + Employer PF)
```

### Structure 3: CTC ₹50,000
```
Earnings:
  Basic Salary: ₹25,000 (50%)
  HRA: ₹12,500 (50% of Basic)
  Conveyance: ₹1,600
  Medical: ₹1,250
  Education: ₹200
  Special Allowance: ₹6,450
  ─────────────────────
  Gross: ₹47,000

Deductions:
  PF: ₹1,800 (12% of ₹15,000 ceiling)
  Professional Tax: ₹200
  TDS: ₹500 (if applicable)
  ─────────────────────
  Total Deductions: ₹2,500

Net Salary: ₹44,500
CTC: ₹50,000 (Gross + Employer PF + Benefits)
```

### Structure 4: Low Income (ESI Applicable) - CTC ₹18,000
```
Earnings:
  Basic Salary: ₹9,000 (50%)
  HRA: ₹4,500 (50% of Basic)
  Conveyance: ₹1,600
  Medical: ₹1,250
  Special Allowance: ₹570
  ─────────────────────
  Gross: ₹16,920

Deductions:
  PF: ₹1,080 (12% of Basic)
  ESI: ₹127 (0.75% of Gross)
  Professional Tax: ₹0
  ─────────────────────
  Total Deductions: ₹1,207

Net Salary: ₹15,713
CTC: ₹18,000 (Gross + Employer PF + Employer ESI)

Note: ESI applicable as Gross ≤ ₹21,000
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

**Last Updated**: February 8, 2026  
**Version**: 2.0  
**Changes in v2.0**:
- Added comprehensive allowance documentation (Conveyance, Medical, Education, Other)
- Added Benefits section (Bonus, Incentive)
- Added detailed TDS calculation guide
- Updated OT calculation to match system implementation (240 hours)
- Added PF ceiling limit documentation (₹15,000)
- Enhanced salary calculation formula with all components
- Added ESI-applicable salary structure example
- Updated all examples with realistic allowance breakdowns

