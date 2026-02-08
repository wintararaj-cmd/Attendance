"""
Deployment Migration Runner
Runs all database migrations in the correct order
Works on all platforms (Windows, Linux, macOS)
"""
import os
import sys
import subprocess
from pathlib import Path

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color
    
    @staticmethod
    def disable_on_windows():
        """Disable colors on Windows if not supported"""
        if os.name == 'nt':
            Colors.RED = ''
            Colors.GREEN = ''
            Colors.YELLOW = ''
            Colors.BLUE = ''
            Colors.NC = ''

# Disable colors on Windows for compatibility
if os.name == 'nt':
    Colors.disable_on_windows()

def print_header(text):
    """Print a formatted header"""
    print("=" * 60)
    print(text)
    print("=" * 60)
    print()

def print_step(step_num, text):
    """Print a step message"""
    print(f"{Colors.YELLOW}[STEP {step_num}]{Colors.NC} {text}")

def print_success(text):
    """Print a success message"""
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {text}")

def print_error(text):
    """Print an error message"""
    print(f"{Colors.RED}[ERROR]{Colors.NC} {text}")

def print_warn(text):
    """Print a warning message"""
    print(f"{Colors.YELLOW}[WARN]{Colors.NC} {text}")

def print_info(text):
    """Print an info message"""
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {text}")

def run_migration(script_name, description, critical=True):
    """
    Run a migration script
    
    Args:
        script_name: Name of the Python migration script
        description: Description of what the migration does
        critical: If True, exit on failure. If False, continue with warning
    
    Returns:
        bool: True if successful, False otherwise
    """
    script_path = Path(__file__).parent / script_name
    
    if not script_path.exists():
        print_error(f"Migration script not found: {script_name}")
        return False
    
    print(description)
    
    try:
        # Run the migration script
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )
        
        # Print the output
        if result.stdout:
            print(result.stdout)
        
        if result.returncode == 0:
            print_success(f"{script_name} completed successfully!")
            return True
        else:
            if result.stderr:
                print(result.stderr)
            
            if critical:
                print_error(f"{script_name} failed!")
                return False
            else:
                print_warn(f"{script_name} had warnings (this may be expected)")
                return True
                
    except subprocess.TimeoutExpired:
        print_error(f"{script_name} timed out!")
        return False
    except Exception as e:
        print_error(f"Error running {script_name}: {str(e)}")
        return False

def main():
    """Main deployment migration runner"""
    print_header("DEPLOYMENT MIGRATION RUNNER")
    
    # Check if we're in the correct directory
    if not Path("add_employee_id_column.py").exists():
        print_error("Migration scripts not found!")
        print("Please run this script from the backend directory")
        return 1
    
    print_info("Starting database migrations...")
    print()
    
    # Migration steps
    migrations = [
        {
            "script": "add_employee_id_column.py",
            "description": "Adding employee_id column to salary_structures table...",
            "critical": True,
            "step": 1
        },
        {
            "script": "migrate_salary_structure.py",
            "description": "Adding comprehensive salary components...",
            "critical": False,  # Not critical as columns may already exist
            "step": 2
        }
    ]
    
    # Run each migration
    all_success = True
    for migration in migrations:
        print_step(migration["step"], migration["description"])
        success = run_migration(
            migration["script"],
            "",
            migration["critical"]
        )
        
        if not success and migration["critical"]:
            all_success = False
            break
        
        print()
    
    # Final status
    print_header("MIGRATION COMPLETE" if all_success else "MIGRATION FAILED")
    
    if all_success:
        print("All migrations completed successfully!")
        print()
        print("Next steps:")
        print("1. Restart your application server")
        print("2. Test the salary configuration feature")
        print()
        return 0
    else:
        print("Some migrations failed. Please check the errors above.")
        print()
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print()
        print_warn("Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print()
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
