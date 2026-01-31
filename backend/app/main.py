from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Attendance & Payroll System API",
    description="Backend API for Face Recognition Attendance and Payroll",
    version="1.0.0"
)

# Initialize Database
from .core.database import engine
from .models import models
models.Base.metadata.create_all(bind=engine)

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
