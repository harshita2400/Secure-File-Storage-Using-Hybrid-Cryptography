"""
Test script to verify the setup is complete
"""
import os
import sys

def check_dependencies():
    """Check if all required packages are installed"""
    print("Checking dependencies...")
    required = ['flask', 'flask_cors', 'bcrypt', 'mysql.connector', 'PIL', 'Crypto']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - MISSING")
            missing.append(package)
    
    return len(missing) == 0

def check_files():
    """Check if required files exist"""
    print("\nChecking files...")
    required_files = [
        'app.py',
        'database.py',
        'input.png',
        '.env',
        'routes/auth_routes.py',
        'routes/file_routes.py',
        'routes/admin_routes.py',
        'services/encryption_service.py',
        'services/stego_service.py',
        'services/file_service.py'
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - MISSING")
            all_exist = False
    
    return all_exist

def check_directories():
    """Check if required directories exist"""
    print("\nChecking directories...")
    required_dirs = ['uploads', 'stego', 'routes', 'services', 'models', 'utils']
    
    all_exist = True
    for dir in required_dirs:
        if os.path.exists(dir):
            print(f"  ✓ {dir}/")
        else:
            print(f"  ✗ {dir}/ - MISSING")
            all_exist = False
    
    return all_exist

def check_env():
    """Check .env configuration"""
    print("\nChecking .env configuration...")
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']
    all_set = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if var == 'DB_PASSWORD':
                print(f"  ✓ {var} = ****")
            else:
                print(f"  ✓ {var} = {value}")
        else:
            print(f"  ✗ {var} - NOT SET")
            all_set = False
    
    return all_set

def check_database():
    """Check database connection"""
    print("\nChecking database connection...")
    try:
        from database import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        required_tables = ['users', 'files', 'file_shares', 'file_downloads']
        all_exist = True
        
        for table in required_tables:
            if table in tables:
                print(f"  ✓ Table '{table}' exists")
            else:
                print(f"  ✗ Table '{table}' - MISSING")
                all_exist = False
        
        cursor.close()
        conn.close()
        return all_exist
        
    except Exception as e:
        print(f"  ✗ Database connection failed: {e}")
        return False

def main():
    print("=" * 60)
    print("SecureVault Setup Verification")
    print("=" * 60)
    
    results = {
        'Dependencies': check_dependencies(),
        'Files': check_files(),
        'Directories': check_directories(),
        'Environment': check_env(),
        'Database': check_database()
    }
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    all_passed = True
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{check:20} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 All checks passed! You're ready to start the server.")
        print("\nRun: python app.py")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\nFor database issues, run: python setup_db.py")
        print("For missing packages, run: pip install -r requirements.txt")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
