#!/usr/bin/env python3
"""
Test script to verify frontend setup
"""

import sys
import importlib

def test_imports():
    """Test if all required packages can be imported"""
    required_packages = [
        'streamlit',
        'pandas',
        'sqlalchemy',
        'plotly',
        'requests',
        'psycopg2',
        'alembic'
    ]
    
    print("🧪 Testing package imports...")
    print("=" * 50)
    
    failed_imports = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            failed_imports.append(package)
    
    print("=" * 50)
    
    if failed_imports:
        print(f"❌ Failed to import: {', '.join(failed_imports)}")
        print("Please run: pip install -r requirements.txt")
        return False
    else:
        print("✅ All packages imported successfully!")
        return True

def test_streamlit():
    """Test Streamlit functionality"""
    print("\n🚀 Testing Streamlit...")
    print("=" * 50)
    
    try:
        import streamlit as st
        print(f"✅ Streamlit version: {st.__version__}")
        
        # Test basic Streamlit functionality
        import streamlit.components.v1 as components
        print("✅ Streamlit components available")
        
        return True
    except Exception as e:
        print(f"❌ Streamlit test failed: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("\n🗄️ Testing database connection...")
    print("=" * 50)
    
    try:
        import os
        from sqlalchemy import create_engine
        
        # Check if DATABASE_URL is set
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("⚠️ DATABASE_URL not set in environment variables")
            print("Please set DATABASE_URL in your .env file")
            return False
        
        # Try to create engine (don't actually connect)
        engine = create_engine(database_url)
        print("✅ Database URL is valid")
        print(f"✅ Database type: {engine.dialect.name}")
        
        return True
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🏗️ Pontum Frontend Setup Test")
    print("=" * 50)
    
    tests = [
        ("Package Imports", test_imports),
        ("Streamlit", test_streamlit),
        ("Database Connection", test_database_connection)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Frontend setup is ready.")
        print("\nTo run the application:")
        print("  ./run.sh")
        print("  or")
        print("  streamlit run app.py")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
