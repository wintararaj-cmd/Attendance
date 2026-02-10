import os
import sys
from dotenv import load_dotenv

# Add backend to path so imports work
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Load environment variables (Postgres)
load_dotenv(os.path.join(os.getcwd(), 'backend', '.env'))

print(f"DEBUG ENV URL: {os.environ.get('DATABASE_URL')}")

from app.core.database import SessionLocal
from app.models.models import AttendanceLog
import datetime
from datetime import timezone, timedelta


def fix_hours():
    # Only if DATABASE_URL is set will it use Postgres
    db = SessionLocal()
    try:
        IST = timezone(timedelta(hours=5, minutes=30))
        today = datetime.datetime.now(IST).date()
        
        # Look back 7 days
        start_date = today - timedelta(days=7)
        print(f"Checking logs from {start_date} to {today}...")
        
        logs = db.query(AttendanceLog).filter(
            AttendanceLog.date >= start_date,
            AttendanceLog.check_out != None
        ).all()
        
        print(f"Found {len(logs)} logs with checkout to update.")
        
        updated_count = 0
        for log in logs:
            if log.check_in and log.check_out:
                # Normalize check_in
                c_in = log.check_in
                if c_in.tzinfo is None:
                    c_in = c_in.replace(tzinfo=IST)
                
                # Normalize check_out
                c_out = log.check_out
                if c_out.tzinfo is None:
                    c_out = c_out.replace(tzinfo=IST)
                
                duration = c_out - c_in
                raw_hours = duration.total_seconds() / 3600
                
                # Deduct 0.5 hours (30 mins break)
                deduction = 0.5
                net_hours = max(0, raw_hours - deduction)
                
                log.total_hours_worked = round(net_hours, 2)
                
                # OT Calc
                # Use log.date, not today, for correct weekend check
                log_date = log.date
                is_weekend = log_date.weekday() >= 5
                standard_work = 8.0
                
                if is_weekend:
                    log.ot_weekend_hours = round(net_hours, 2)
                    log.ot_hours = 0
                else:
                    if net_hours > standard_work:
                        log.ot_hours = round(net_hours - standard_work, 2)
                    else:
                        log.ot_hours = 0
                
                print(f"Updated Log {log.id} ({log_date}): Raw={raw_hours:.2f}h, Net={net_hours:.2f}h, OT={log.ot_hours}h")
                updated_count += 1
                
        db.commit()
        print(f"Successfully updated {updated_count} logs.")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    fix_hours()
