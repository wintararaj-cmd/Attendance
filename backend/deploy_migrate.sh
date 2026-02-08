#!/bin/bash
# Deployment Migration Script
# This script runs database migrations automatically during deployment

set -e  # Exit on error

echo "============================================================"
echo "DEPLOYMENT MIGRATION SCRIPT"
echo "============================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "add_employee_id_column.py" ]; then
    echo -e "${RED}[ERROR]${NC} Migration script not found!"
    echo "Please run this script from the backend directory"
    exit 1
fi

echo -e "${GREEN}[INFO]${NC} Starting database migrations..."
echo ""

# Run the employee_id column migration
echo -e "${YELLOW}[STEP 1]${NC} Adding employee_id column to salary_structures..."
python add_employee_id_column.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}[SUCCESS]${NC} employee_id column migration completed!"
else
    echo -e "${RED}[FAILED]${NC} employee_id column migration failed!"
    exit 1
fi

echo ""

# Run the comprehensive salary structure migration
echo -e "${YELLOW}[STEP 2]${NC} Adding comprehensive salary components..."
python migrate_salary_structure.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}[SUCCESS]${NC} Salary structure migration completed!"
else
    echo -e "${YELLOW}[WARN]${NC} Salary structure migration had warnings (this may be expected)"
fi

echo ""
echo "============================================================"
echo -e "${GREEN}[COMPLETE]${NC} All migrations finished!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "1. Restart your application server"
echo "2. Test the salary configuration feature"
echo ""
