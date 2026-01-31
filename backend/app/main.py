from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Attendance & Payroll System API",
    description="Backend API for Face Recognition Attendance and Payroll",
    version="1.0.0"
)

# Initialize Database
# Initialize Database
from .core.database import engine, SessionLocal
from .models import models
from .models.models import AdminUser
from .services.auth import auth_service

models.Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def init_data():
    db = SessionLocal()
    try:
        # Create default admin if not exists
        username = "admin"
        user = db.query(AdminUser).filter(AdminUser.username == username).first()
        if not user:
            print(f"🚀 Creating default admin user: {username}")
            try:
                hashed_password = auth_service.get_password_hash("password123")
                new_user = AdminUser(username=username, password_hash=hashed_password, role="superadmin")
                db.add(new_user)
                db.commit()
                print("✅ Default admin created.")
            except Exception as e:
                print(f"❌ Failed to create admin: {e}")
    finally:
        db.close()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://t3sol.in",
        "https://www.t3sol.in",
        "https://terminal.t3sol.in",
        "https://api.t3sol.in",
        "https://backend.140.245.242.116.sslip.io",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from .api import endpoints
app.include_router(endpoints.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"status": "active", "message": "Attendance System API is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    error_details = traceback.format_exc()
    print(f"🔥 GLOBAL 500 ERROR: {str(exc)}\n{error_details}")
    origin = request.headers.get("origin")
    allow_origin = origin if origin in [
        "https://t3sol.in",
        "https://www.t3sol.in",
        "https://terminal.t3sol.in",
        "http://localhost:3000", 
        "http://localhost:5173"
    ] else "*"

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error": str(exc)},
        headers={
            "Access-Control-Allow-Origin": allow_origin,
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        },
    )
