from app.core.database import SessionLocal, engine
from app.models import models
from app.models.models import AdminUser
from app.services.auth import auth_service
import sys
import os

# Ensure backend directory is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_admin():
    # Ensure tables exist
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        username = "admin"
        password = "password123" # Default password
        
        user = db.query(AdminUser).filter(AdminUser.username == username).first()
        if not user:
            print(f"Creating default admin user: {username}")
            hashed_password = auth_service.get_password_hash(password)
            new_user = AdminUser(username=username, password_hash=hashed_password, role="superadmin")
            db.add(new_user)
            db.commit()
            print(f"Admin user created successfully. Username: {username}, Password: {password}")
        else:
            print(f"Admin user '{username}' already exists.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
