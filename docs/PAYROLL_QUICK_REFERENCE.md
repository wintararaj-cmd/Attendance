# Payroll Quick Reference Card

## 📊 Standard Salary Components

### Earnings
| Component | Calculation | Example (₹30K CTC) |
|-----------|-------------|-------------------|
| **Basic Salary** | 40-50% of CTC | ₹15,000 |
| **HRA** | 40-50% of Basic | ₹7,500 |
| **Special Allowance** | Balance amount | ₹5,700 |

### Deductions
| Component | Calculation | Example |
|-----------|-------------|---------|
| **PF** | 12% of Basic | ₹1,800 |
| **Professional Tax** | State-specific | ₹200 |
| **ESI** | 0.75% of Gross (if ≤₹21K) | ₹150 |

---

## 🧮 Quick Formulas

### PF Calculation
```
Employee PF = Basic × 12%
Employer PF = Basic × 12%
```

### ESI Calculation
```
If Gross ≤ ₹21,000:
  Employee ESI = Gross × 0.75%
  Employer ESI = Gross × 3.25%
```

### HRA Calculation
```
Metro Cities: Basic × 50%
Non-Metro: Basic × 40%
```

### OT Calculation
```
Per Hour Rate = (Basic / 26 / 8)
Weekday OT = Per Hour × 1.5
Weekend OT = Per Hour × 2.0
Holiday OT = Per Hour × 2.5
```

### LOP (Loss of Pay)
```
Per Day = Basic / 26
LOP = Per Day × Absent Days
```

---

## 🏙️ Professional Tax by State

| State | Monthly PT |
|-------|-----------|
| Maharashtra | ₹200 |
| Karnataka | ₹200 |
| Tamil Nadu | ₹0-₹208 |
| Gujarat | ₹0-₹200 |
| West Bengal | ₹200 |
| Andhra Pradesh | ₹200 |
| Telangana | ₹200 |
| Madhya Pradesh | ₹208 |

---

## 📝 How to Configure Salary (Step-by-Step)

### Example: ₹30,000 CTC (Mumbai)

1. **Calculate Components:**
   ```
   Basic: ₹15,000 (50%)
   HRA: ₹7,500 (50% of Basic)
   Special: ₹5,700
   PF: ₹1,800 (12% of Basic)
   PT: ₹200 (Maharashtra)
   ```

2. **In System:**
   - Navigate to **Payroll Management**
   - Click **Configure** for employee
   - Enter values:
     - Basic Salary: `15000`
     - HRA Allowance: `7500`
     - Special Allowance: `5700`
     - PF Deduction: `1800`
     - Professional Tax: `200`
   - Click **Save**

3. **Verify:**
   ```
   Gross: ₹28,200
   Deductions: ₹2,000
   Net: ₹26,200
   ```

---

## 💡 Common Salary Structures

### ₹20,000 CTC
```
Basic: ₹10,000
HRA: ₹5,000
Special: ₹3,800
PF: ₹1,200
PT: ₹200
─────────────
Net: ₹17,400
```

### ₹30,000 CTC
```
Basic: ₹15,000
HRA: ₹7,500
Special: ₹5,700
PF: ₹1,800
PT: ₹200
─────────────
Net: ₹26,200
```

### ₹50,000 CTC
```
Basic: ₹25,000
HRA: ₹12,500
Special: ₹9,500
PF: ₹3,000
PT: ₹200
─────────────
Net: ₹43,800
```

---

## ⚡ Quick Tips

✅ **Basic Salary**: Always 40-50% of CTC  
✅ **HRA**: 50% of Basic (Metro), 40% (Non-Metro)  
✅ **PF**: Mandatory if 20+ employees  
✅ **ESI**: Only if Gross ≤ ₹21,000  
✅ **PT**: Check your state's rate  

---

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| Net salary is negative | Reduce deductions or increase earnings |
| PF seems wrong | Verify it's 12% of Basic |
| PT varies | PT is state-specific, check your state |
| ESI not applicable | ESI only for Gross ≤ ₹21,000 |

---

**For detailed information, see:** `PAYROLL_CONFIGURATION_GUIDE.md`
