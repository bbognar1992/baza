#!/usr/bin/env python3
"""
Simple script to run database migrations
Usage: python run_migrations.py [command]
Commands:
  auto    - Automatically detect and apply migrations
  status  - Check migration status
  generate - Generate a new migration
  apply   - Apply pending migrations
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(__file__))

from migration_utils import AutoMigrationManager

def main():
    if len(sys.argv) < 2:
        command = "auto"
    else:
        command = sys.argv[1]
    
    manager = AutoMigrationManager()
    
    if command == "auto":
        print("Running automatic migration...")
        result = manager.auto_migrate()
        print(f"Result: {result}")
        
    elif command == "status":
        print("Checking migration status...")
        status = manager.check_migration_status()
        print(f"Current revision: {status.get('current_revision', 'None')}")
        print(f"Head revision: {status.get('head_revision', 'None')}")
        print(f"Up to date: {status.get('is_up_to_date', False)}")
        print(f"Needs migration: {status.get('needs_migration', False)}")
        
    elif command == "generate":
        message = sys.argv[2] if len(sys.argv) > 2 else None
        print("Generating migration...")
        revision = manager.generate_migration(message)
        if revision:
            print(f"Generated migration: {revision}")
        else:
            print("Failed to generate migration")
            
    elif command == "apply":
        print("Applying migrations...")
        success = manager.apply_migrations()
        print(f"Migration applied: {success}")
        
    elif command == "init":
        print("Creating initial migration...")
        success = manager.create_initial_migration()
        print(f"Initial migration created: {success}")
        
    else:
        print(f"Unknown command: {command}")
        print("Available commands: auto, status, generate, apply, init")

if __name__ == "__main__":
    main()
