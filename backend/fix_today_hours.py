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
        
        # Debug: list all logs first
        all_logs = db.query(AttendanceLog).limit(5).all()
        print(f"DEBUG: Found {len(all_logs)} sample logs in DB.")
        for l in all_logs:
            print(f" - Log ID: {l.id}, Date: {l.date} (Type: {type(l.date)}), Check-out: {l.check_out}")

        logs = db.query(AttendanceLog).filter(
            AttendanceLog.date == today
        ).all()
        
        logs_with_checkout = [l for l in logs if l.check_out is not None]
        
        print(f"Found {len(logs)} logs today, {len(logs_with_checkout)} with checkout.")
        
        for log in logs_with_checkout:
            if log.check_in and log.check_out:
                # Normalize check_in
                c_in = log.check_in
                # If naive, assume it's naive local time (so attach timezone)
                # Or assume it matches valid awareness.
                
                # Normalize check_out
                c_out = log.check_out
                
                # Force naive for subtraction if mixed, or force aware?
                # Best is force aware for both.
                if c_in.tzinfo is None:
                    c_in = c_in.replace(tzinfo=IST)
                if c_out.tzinfo is None:
                    c_out = c_out.replace(tzinfo=IST)
                
                duration = c_out - c_in
                raw_hours = duration.total_seconds() / 3600
                
                # Deduct 0.5 hours
                deduction = 0.5
                net_hours = max(0, raw_hours - deduction)
                
                log.total_hours_worked = round(net_hours, 2)
                
                # OT Calc
                is_weekend = today.weekday() >= 5
                standard_work = 8.0
                
                if is_weekend:
                    log.ot_weekend_hours = round(net_hours, 2)
                    log.ot_hours = 0
                else:
                    if net_hours > standard_work:
                        log.ot_hours = round(net_hours - standard_work, 2)
                    else:
                        log.ot_hours = 0
                
                print(f"Updated Log {log.id}: Raw={raw_hours:.2f}h, Net={net_hours:.2f}h, OT={log.ot_hours}h")
                
        db.commit()
        print("Successfully updated today's logs.")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    fix_hours()
