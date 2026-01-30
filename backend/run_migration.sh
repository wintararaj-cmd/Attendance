#!/bin/bash

# Database Migration Script for Production
# Run this on your production server to update the database schema

echo "🔄 Starting Database Migration..."
echo "=================================="

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ Error: DATABASE_URL environment variable is not set"
    echo "Please set DATABASE_URL before running this script"
    exit 1
fi

echo "✅ DATABASE_URL is set"
echo ""

# Run the migration
echo "📊 Running migration script..."
python migrate_db.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migration completed successfully!"
    echo "🔄 Please restart your application for changes to take effect"
else
    echo ""
    echo "❌ Migration failed!"
    echo "Please check the error messages above"
    exit 1
fi
