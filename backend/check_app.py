import sys
import os

# Set CWD to backend dir to emulate running from there
os.chdir(os.path.dirname(os.path.abspath(__file__)))

with open("import_status.txt", "w") as f:
    try:
        from app.main import app
        f.write("APP IMPORT SUCCESS")
    except Exception as e:
        import traceback
        f.write(f"APP IMPORT FAIL: {e}\n")
        traceback.print_exc(file=f)
