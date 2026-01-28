
import sys
import os

print("Starting test...")
try:
    from app.main import app
    print("Successfully imported app")
except Exception as e:
    print(f"Error importing app: {e}")
    import traceback
    traceback.print_exc()

print("Test complete")
