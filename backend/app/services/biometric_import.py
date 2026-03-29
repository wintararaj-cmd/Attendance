import pandas as pd
import datetime
import uuid
import re
import calendar
from sqlalchemy.orm import Session
from ..models import models
from ..models.models import Employee, AttendanceLog, Company
import logging

logger = logging.getLogger("biometric_import")

class BiometricImportService:
    @staticmethod
    def import_from_excel(file_path: str, db: Session):
        try:
            # Read the Excel file
            df = pd.read_excel(file_path, header=None)
            
            # HYBRID MODE: Let AI analyze the file layout
            from .ai_service import ai_service
            layout = ai_service.get_excel_layout(df)
            status_cache = {} # Cache AI mapping for the duration of this import
            
            # 1. Parse Month and Year from header
            header_text = ""
            for r_idx in [2, 3]: # try row 3 or 4
                if len(df) > r_idx:
                    val = str(df.iloc[r_idx, 7])
                    if "Month of" in val:
                        header_text = val
                        break
            
            my_match = re.search(r"Month of (\w+), (\d{4})", header_text)
            if not my_match and layout and 'month_year_text' in layout:
                my_match = re.search(r"(\w+), (\d{4})", layout['month_year_text'])
            
            months = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7, 
                      'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}
            
            if my_match:
                month_name = my_match.group(1).title()
                year = int(my_match.group(2))
                month_idx = months.get(month_name, datetime.datetime.now().month)
            else:
                month_idx = datetime.datetime.now().month
                year = datetime.datetime.now().year

            # Get number of days in this specific month
            _, num_days = calendar.monthrange(year, month_idx)

            # Ensure default company
            if not db.query(Company).filter(Company.id == "default").first():
                db.add(Company(id="default", name="Default Company"))
                db.commit()

            def parse_val(v, date_context=None):
                if pd.isna(v): return None
                if date_context and isinstance(v, (datetime.time, datetime.datetime)):
                    t = v if isinstance(v, datetime.time) else v.time()
                    return datetime.datetime.combine(date_context, t)

                # Handle numeric values (e.g. 7.0 from pandas)
                if isinstance(v, (int, float)):
                    if date_context:
                        hours = int(v)
                        minutes = int(round((v - hours) * 100))  # e.g. 7.30 -> 7:30
                        if minutes >= 60:
                            minutes = 59
                        return datetime.datetime.combine(date_context, datetime.time(hours, minutes))
                    return float(v)

                s = str(v).strip()
                if not s or s.lower() == "nan": return None

                if date_context:
                    # Try common time formats including decimal H.M and hour-only
                    for fmt in ["%H:%M", "%H:%M:%S", "%I:%M %p", "%I:%M:%S %p", "%H.%M", "%H"]:
                        try:
                            return datetime.datetime.combine(date_context, datetime.datetime.strptime(s, fmt).time())
                        except: continue
                try: return float(s)
                except: return 0.0

            imported_count = 0
            new_emp_count = 0
            
            # Dynamic Day Column Start Detection
            if layout and 'day_1_column_index' in layout:
                day_1_col = int(layout['day_1_column_index'])
                logger.info(f"AI Detected Day 1 Column Index: {day_1_col}")
            else:
                day_1_col = 8 # Default fallback
                if len(df) > 4:
                    row_5 = df.iloc[4]
                    for c_idx in range(len(row_5)):
                        item = str(row_5.iloc[c_idx]).strip()
                        if item in ["01", "1"]:
                            day_1_col = c_idx
                            break
            
            # Row-by-row scan for employee headers
            for i in range(5, len(df)):
                code = str(df.iloc[i, 0]).strip()
                if not re.match(r"^\d+$", code): continue
                
                name = str(df.iloc[i, 1]).strip()
                employee = db.query(Employee).filter(Employee.emp_code == code).first()
                if not employee:
                    employee = Employee(
                        id=str(uuid.uuid4()), emp_code=code, first_name=name,
                        mobile_no=f"999{code[-7:].zfill(7)}", status='active', company_id="default"
                    )
                    db.add(employee); db.flush(); new_emp_count += 1

                # Locate labels within 15 rows of the header
                rows = {}
                for j in range(i + 1, min(i + 15, len(df))):
                    label = str(df.iloc[j, 0]).strip().lower()
                    if "in time" in label: rows['in'] = j
                    elif "out time" in label: rows['out'] = j
                    elif "work" in label: rows['work'] = j
                    elif "ot" in label: rows['ot'] = j
                    elif "status" in label: rows['status'] = j
                    if j > i + 1 and re.match(r"^\d+$", str(df.iloc[j, 0]).strip()): break

                if 'status' in rows:
                    for day in range(1, num_days + 1):
                        col = day_1_col + (day - 1)
                        if col >= len(df.columns): break
                        
                        try:
                            dt = datetime.date(year, month_idx, day)
                            is_wk = dt.weekday() >= 5
                            
                            st_raw = df.iloc[rows['status'], col]
                            st_val = str(st_raw).strip().upper()
                            
                            # Skip only if truly empty/NaN and no times provided
                            cin = parse_val(df.iloc[rows['in'], col], dt) if 'in' in rows else None
                            cout = parse_val(df.iloc[rows['out'], col], dt) if 'out' in rows else None
                            if pd.isna(st_raw) and not (cin or cout): continue
                            
                            if cin and cout and cout < cin: cout += datetime.timedelta(days=1)
                            
                            wk_h = parse_val(df.iloc[rows['work'], col]) if 'work' in rows else 0.0
                            ot_h = parse_val(df.iloc[rows['ot'], col]) if 'ot' in rows else 0.0

                            # Determine status
                            # Normal: PP, PPl are present. AA is absent. WW is weekly off.
                            if st_val in ["AA", "AB"]:
                                final_status = "absent"
                            elif cin or wk_h > 0 or "P" in st_val:
                                final_status = "present"
                            elif "W" in st_val or is_wk:
                                # Default to weekly_off if it's a weekend or marked 'W' and no work hours
                                final_status = "weekly_off"
                            else:
                                # AI Fallback for unknown status codes with local caching
                                if st_val not in status_cache:
                                    status_cache[st_val] = ai_service.map_unknown_status(st_val) or "absent"
                                final_status = status_cache[st_val]

                            log = db.query(AttendanceLog).filter(AttendanceLog.employee_id == employee.id, AttendanceLog.date == dt).first()
                            if log:
                                log.check_in, log.check_out, log.total_hours_worked, log.status = cin, cout, wk_h, final_status
                                if is_wk: log.ot_weekend_hours, log.ot_hours = ot_h, 0.0
                                else: log.ot_hours, log.ot_weekend_hours = ot_h, 0.0
                            else:
                                db.add(AttendanceLog(
                                    id=str(uuid.uuid4()), employee_id=employee.id, date=dt,
                                    check_in=cin, check_out=cout, status=final_status,
                                    total_hours_worked=wk_h, ot_hours=ot_h if not is_wk else 0.0,
                                    ot_weekend_hours=ot_h if is_wk else 0.0
                                ))
                            imported_count += 1
                        except Exception as day_err:
                            logger.error(f"Error processing day {day} for {name}: {day_err}")
                            continue

            db.commit()
            return {
                "status": "success", "logs_processed": imported_count, "new_employees": new_emp_count,
                "message": f"Successfully imported {imported_count} records. {new_emp_count} new employees added."
            }
        except Exception as e:
            db.rollback(); logger.error(f"Critical import error: {e}"); raise e

biometric_service = BiometricImportService()
