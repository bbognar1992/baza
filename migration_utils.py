"""
Database migration utilities for automatic schema updates
"""

import os
import sys
from datetime import datetime
from typing import Optional, List
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from alembic.util import CommandError

# Add project root to path
sys.path.append(os.path.dirname(__file__))

from database import engine, DATABASE_URL
from models.base import Base


class AutoMigrationManager:
    """Manages automatic database migrations"""
    
    def __init__(self, alembic_cfg_path: str = "alembic.ini"):
        self.alembic_cfg = Config(alembic_cfg_path)
        self.engine = engine
        
    def check_migration_status(self) -> dict:
        """Check the current migration status"""
        try:
            with self.engine.connect() as connection:
                context = MigrationContext.configure(connection)
                current_rev = context.get_current_revision()
                
                script = ScriptDirectory.from_config(self.alembic_cfg)
                head_rev = script.get_current_head()
                
                return {
                    'current_revision': current_rev,
                    'head_revision': head_rev,
                    'is_up_to_date': current_rev == head_rev,
                    'needs_migration': current_rev != head_rev
                }
        except Exception as e:
            return {
                'error': str(e),
                'current_revision': None,
                'head_revision': None,
                'is_up_to_date': False,
                'needs_migration': True
            }
    
    def generate_migration(self, message: str = None) -> Optional[str]:
        """Generate a new migration based on model changes"""
        try:
            if not message:
                message = f"Auto migration {datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Generate migration
            command.revision(
                self.alembic_cfg,
                autogenerate=True,
                message=message
            )
            
            # Get the latest migration file
            script = ScriptDirectory.from_config(self.alembic_cfg)
            revisions = list(script.walk_revisions())
            if revisions:
                latest_revision = revisions[0]
                return latest_revision.revision
            
            return None
            
        except CommandError as e:
            print(f"Error generating migration: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error generating migration: {e}")
            return None
    
    def apply_migrations(self, target: str = "head") -> bool:
        """Apply pending migrations"""
        try:
            command.upgrade(self.alembic_cfg, target)
            return True
        except CommandError as e:
            print(f"Error applying migrations: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error applying migrations: {e}")
            return False
    
    def auto_migrate(self, force: bool = False) -> dict:
        """Automatically detect changes and apply migrations"""
        result = {
            'success': False,
            'migration_generated': False,
            'migration_applied': False,
            'message': '',
            'revision': None
        }
        
        try:
            # Check current status
            status = self.check_migration_status()
            
            if 'error' in status:
                result['message'] = f"Error checking migration status: {status['error']}"
                return result
            
            # Generate migration if there are changes
            if status['needs_migration'] or force:
                print("Detected model changes, generating migration...")
                revision = self.generate_migration()
                
                if revision:
                    result['migration_generated'] = True
                    result['revision'] = revision
                    print(f"Generated migration: {revision}")
                    
                    # Apply the migration
                    if self.apply_migrations():
                        result['migration_applied'] = True
                        result['success'] = True
                        result['message'] = f"Successfully applied migration {revision}"
                        print(f"Applied migration: {revision}")
                    else:
                        result['message'] = f"Generated migration {revision} but failed to apply it"
                else:
                    result['message'] = "Failed to generate migration"
            else:
                result['success'] = True
                result['message'] = "Database is up to date, no migrations needed"
                print("Database is up to date")
            
        except Exception as e:
            result['message'] = f"Auto-migration failed: {str(e)}"
            print(f"Auto-migration error: {e}")
        
        return result
    
    def create_initial_migration(self) -> bool:
        """Create the initial migration for existing models"""
        try:
            # Check if alembic_version table exists
            with self.engine.connect() as connection:
                inspector = inspect(connection)
                tables = inspector.get_table_names()
                
                if 'alembic_version' not in tables:
                    print("Creating initial migration...")
                    command.revision(
                        self.alembic_cfg,
                        autogenerate=True,
                        message="Initial migration"
                    )
                    
                    # Apply the initial migration
                    command.upgrade(self.alembic_cfg, "head")
                    print("Initial migration created and applied")
                    return True
                else:
                    print("Alembic version table already exists")
                    return True
                    
        except Exception as e:
            print(f"Error creating initial migration: {e}")
            return False
    
    def reset_migrations(self) -> bool:
        """Reset all migrations (DANGEROUS - use with caution)"""
        try:
            # Drop alembic version table
            with self.engine.connect() as connection:
                connection.execute(text("DROP TABLE IF EXISTS alembic_version"))
                connection.commit()
            
            # Remove all migration files
            versions_dir = os.path.join(os.path.dirname(self.alembic_cfg.config_file_name), "alembic", "versions")
            if os.path.exists(versions_dir):
                for file in os.listdir(versions_dir):
                    if file.endswith('.py'):
                        os.remove(os.path.join(versions_dir, file))
            
            print("Migrations reset successfully")
            return True
            
        except Exception as e:
            print(f"Error resetting migrations: {e}")
            return False


def auto_migrate_on_startup():
    """Convenience function to run auto-migration on application startup"""
    manager = AutoMigrationManager()
    
    # First, ensure we have an initial migration if needed
    if not manager.create_initial_migration():
        print("Warning: Failed to create initial migration")
        return False
    
    # Then run auto-migration
    result = manager.auto_migrate()
    
    if result['success']:
        print(f"Auto-migration completed: {result['message']}")
    else:
        print(f"Auto-migration failed: {result['message']}")
    
    return result['success']


def check_and_migrate():
    """Check for pending migrations and apply them"""
    manager = AutoMigrationManager()
    status = manager.check_migration_status()
    
    if status.get('needs_migration', False):
        print("Pending migrations detected, applying...")
        return manager.apply_migrations()
    else:
        print("Database is up to date")
        return True


if __name__ == "__main__":
    # Command line interface
    import argparse
    
    parser = argparse.ArgumentParser(description="Database migration utilities")
    parser.add_argument("command", choices=["auto", "status", "generate", "apply", "reset"], 
                       help="Migration command to run")
    parser.add_argument("--message", "-m", help="Migration message")
    parser.add_argument("--force", "-f", action="store_true", help="Force migration generation")
    
    args = parser.parse_args()
    
    manager = AutoMigrationManager()
    
    if args.command == "auto":
        result = manager.auto_migrate(force=args.force)
        print(f"Result: {result}")
    elif args.command == "status":
        status = manager.check_migration_status()
        print(f"Migration status: {status}")
    elif args.command == "generate":
        revision = manager.generate_migration(args.message)
        print(f"Generated migration: {revision}")
    elif args.command == "apply":
        success = manager.apply_migrations()
        print(f"Migration applied: {success}")
    elif args.command == "reset":
        success = manager.reset_migrations()
        print(f"Migrations reset: {success}")
