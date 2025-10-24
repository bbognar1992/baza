#!/usr/bin/env python3
"""
Test script to check FastAPI application startup and routes
"""

import sys
import os

# Add current directory to path
sys.path.append('.')

try:
    from main import app
    print("✅ FastAPI app loaded successfully")
    
    print("\n📋 Available routes:")
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            methods = ', '.join(route.methods) if route.methods else 'N/A'
            print(f"  {route.path} - {methods}")
        elif hasattr(route, 'path'):
            print(f"  {route.path} - N/A")
    
    print(f"\n📊 Total routes found: {len(app.routes)}")
    
    # Check if all expected endpoints are present
    expected_endpoints = [
        "/api/v1/users",
        "/api/v1/projects", 
        "/api/v1/resources",
        "/api/v1/materials",
        "/api/v1/tasks",
        "/api/v1/phases",
        "/api/v1/profession-types",
        "/api/v1/project-types",
        "/api/v1/weather"
    ]
    
    print("\n🔍 Checking for expected endpoints:")
    found_endpoints = []
    for route in app.routes:
        if hasattr(route, 'path'):
            for expected in expected_endpoints:
                if route.path.startswith(expected):
                    found_endpoints.append(route.path)
                    break
    
    for expected in expected_endpoints:
        if any(ep.startswith(expected) for ep in found_endpoints):
            print(f"  ✅ {expected}")
        else:
            print(f"  ❌ {expected} - MISSING")
    
    print(f"\n🎯 Found {len(found_endpoints)} expected endpoints")
    
except Exception as e:
    print(f"❌ Error loading FastAPI app: {e}")
    import traceback
    traceback.print_exc()
