#!/usr/bin/env python
"""
Test database connection using Django settings.
This script tests the PostgreSQL database connection configured in settings.py
"""
import os
import sys
import django
from pathlib import Path

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection
from django.conf import settings
from django.core.management.color import color_style

style = color_style()

def test_database_connection():
    """Test the database connection and display connection info."""
    print("\n" + "="*60)
    print(style.SUCCESS("TESTING DATABASE CONNECTION"))
    print("="*60 + "\n")
    
    # Display connection settings (without password)
    db_config = settings.DATABASES['default']
    print(style.HTTP_INFO("Database Configuration:"))
    print(f"   Engine:    {db_config['ENGINE']}")
    print(f"   Name:      {db_config['NAME']}")
    print(f"   User:      {db_config['USER']}")
    print(f"   Host:      {db_config.get('HOST', 'localhost')}")
    print(f"   Port:      {db_config.get('PORT', '5432')}")
    print(f"   Password:  {'*' * len(db_config.get('PASSWORD', ''))}")
    print()
    
    try:
        # Test connection
        print(style.HTTP_INFO("Testing connection..."))
        with connection.cursor() as cursor:
            # Test 1: Basic connection
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(style.SUCCESS("   [OK] Connection successful!"))
            print(f"   PostgreSQL Version: {version.split(',')[0]}")
            print()
            
            # Test 2: Database name
            cursor.execute("SELECT current_database();")
            db_name = cursor.fetchone()[0]
            print(style.SUCCESS(f"   [OK] Connected to database: {db_name}"))
            print()
            
            # Test 3: List tables
            print(style.HTTP_INFO("Database Tables:"))
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """)
            tables = cursor.fetchall()
            
            if tables:
                custom_tables = [t[0] for t in tables if not t[0].startswith(('auth_', 'django_'))]
                django_tables = [t[0] for t in tables if t[0].startswith(('auth_', 'django_'))]
                
                print(f"   Total tables: {len(tables)}")
                if custom_tables:
                    print(f"   Custom tables: {len(custom_tables)}")
                    for table in custom_tables[:10]:  # Show first 10
                        print(f"      - {table}")
                    if len(custom_tables) > 10:
                        print(f"      ... and {len(custom_tables) - 10} more")
                if django_tables:
                    print(f"   Django tables: {len(django_tables)}")
            else:
                print("   No tables found (database might be empty)")
            print()
            
            # Test 4: Test a simple query
            print(style.HTTP_INFO("Running test query..."))
            cursor.execute("SELECT 1 as test_value;")
            result = cursor.fetchone()[0]
            if result == 1:
                print(style.SUCCESS("   [OK] Query execution successful!"))
            print()
            
            # Test 5: Check if migrations are needed
            print(style.HTTP_INFO("Django Migrations Status:"))
            try:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name LIKE 'django_%'
                """)
                django_table_count = cursor.fetchone()[0]
                if django_table_count > 0:
                    print(style.SUCCESS(f"   [OK] Django tables found: {django_table_count}"))
                    print("   Note: Run 'python manage.py migrate' if needed")
                else:
                    print(style.WARNING("   [WARNING] No Django tables found"))
                    print("   Run 'python manage.py migrate' to create Django tables")
            except Exception as e:
                print(style.ERROR(f"   [ERROR] Error checking Django tables: {e}"))
            print()
        
        print("="*60)
        print(style.SUCCESS("DATABASE CONNECTION TEST PASSED!"))
        print("="*60 + "\n")
        return True
        
    except Exception as e:
        print("="*60)
        print(style.ERROR("DATABASE CONNECTION TEST FAILED!"))
        print("="*60)
        print(style.ERROR(f"\nError: {str(e)}\n"))
        print(style.WARNING("Troubleshooting tips:"))
        print("   1. Check if PostgreSQL is running")
        print("   2. Verify database credentials in .env file")
        print("   3. Ensure database exists: CREATE DATABASE emphasis_db;")
        print("   4. Check firewall/network settings")
        print("   5. Verify PostgreSQL is listening on the correct port\n")
        return False

if __name__ == '__main__':
    success = test_database_connection()
    sys.exit(0 if success else 1)

