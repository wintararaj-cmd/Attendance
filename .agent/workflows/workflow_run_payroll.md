---
description: How to generate payroll for a month
---

Follow these steps to generate payroll:

1. **Ensure Backend is Running**:
   Use `npm run dev` or equivalent to start the backend.

2. **Generate Payroll**:
   Use an API client (like Postman or curl) to POST to `/api/v1/payroll/generate`.
   The request body should include the month and year.

   Example (using curl):
   ```bash
   curl -X POST "http://localhost:8000/api/v1/payroll/generate" \
        -H "Content-Type: application/json" \
        -d '{
            "month": 2, 
            "year": 2026
        }'
   ```

3. **Check Payroll Status**:
   Use GET `/api/v1/payroll/list` to view generated payrolls.

   Example:
   ```bash
   curl "http://localhost:8000/api/v1/payroll/list?month=2&year=2026"
   ```

4. **Verify Calculations**:
   - **Workers**: Check `basic_earned`, `ot_amount`, `gross_salary` (should be based on Worked Days).
   - **Staff**: Check `gross_salary`, `net_salary` (should be monthly based, with LOP if absent).

5. **Lock Payroll (Optional)**:
   (Feature to be implemented: Use `/api/v1/payroll/lock` to finalize payroll)
