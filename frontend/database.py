"""
Database configuration and utilities for ÉpítAI Construction Management System
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

# Database configuration - using same env vars as test_db.py
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

# Construct DATABASE_URL from individual components
if USER and PASSWORD and HOST and PORT and DBNAME:
    DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"
else:
    raise ValueError("Missing required database configuration")

# Create engine with appropriate configuration
if DATABASE_URL.startswith('sqlite'):
    # SQLite configuration for development/testing
    engine = create_engine(
        DATABASE_URL,
        echo=os.getenv('SQLALCHEMY_ECHO', 'False').lower() == 'true',
        poolclass=StaticPool,
        connect_args={'check_same_thread': False}
    )
else:
    # PostgreSQL configuration for production with SSL support
    engine = create_engine(
        DATABASE_URL,
        echo=os.getenv('SQLALCHEMY_ECHO', 'False').lower() == 'true',
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=10,
        max_overflow=20
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)

@contextmanager
def get_db_session():
    """Get database session with automatic cleanup"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def get_db():
    """Get database session (for dependency injection)"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def create_tables():
    """Create all database tables"""
    from models.base import Base
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """Drop all database tables"""
    from models.base import Base
    Base.metadata.drop_all(bind=engine)

def reset_database():
    """Reset database (drop and recreate all tables)"""
    drop_tables()
    create_tables()

def check_database_connection():
    """Check if database connection is working"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

def get_database_info():
    """Get database information"""
    try:
        with engine.connect() as connection:
            if DATABASE_URL.startswith('postgresql'):
                result = connection.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                return {
                    'type': 'PostgreSQL',
                    'version': version,
                    'url': DATABASE_URL.replace(DATABASE_URL.split('@')[0].split('://')[1], '***')
                }
            elif DATABASE_URL.startswith('sqlite'):
                result = connection.execute(text("SELECT sqlite_version()"))
                version = result.fetchone()[0]
                return {
                    'type': 'SQLite',
                    'version': version,
                    'url': DATABASE_URL
                }
            else:
                return {
                    'type': 'Unknown',
                    'version': 'Unknown',
                    'url': DATABASE_URL
                }
    except Exception as e:
        return {
            'type': 'Error',
            'version': str(e),
            'url': DATABASE_URL
        }

# Database initialization
def initialize_database():
    """Initialize database with sample data"""
    try:
        # Run auto-migration first
        from migration_utils import auto_migrate_on_startup
        print("Running auto-migration...")
        auto_migrate_on_startup()
        
        # Create tables (fallback if migration fails)
        create_tables()
        
        # Check if we need to populate with sample data
        with get_db_session() as session:
            from models.user import User
            from models.profession_type import ProfessionType
            from models.project_type import ProjectType
            
            # Check if database is empty
            user_count = session.query(User).count()
            if user_count == 0:
                print("Database is empty, populating with sample data...")
                populate_sample_data(session)
            else:
                print(f"Database already contains {user_count} users, skipping sample data")
                
    except Exception as e:
        print(f"Database initialization failed: {e}")
        raise

def populate_sample_data(session):
    """Populate database with sample data"""
    try:
        from models.profession_type import ProfessionType
        from models.project_type import ProjectType
        from models.user import User
        
        # Add profession types
        profession_types = [
            ProfessionType(name="Kőműves", description="Falazat, betonozás, vakolás", level="Szakmunkás"),
            ProfessionType(name="Villanyszerelő", description="Elektromos hálózatok, kapcsolók, csatlakozók", level="Szakmunkás"),
            ProfessionType(name="Víz-gáz-fűtésszerelő", description="Vízvezetékek, fűtés, szellőztetés", level="Szakmunkás"),
            ProfessionType(name="Ács", description="Fa szerkezetek, tetőfedés", level="Szakmunkás"),
            ProfessionType(name="Burkoló", description="Padló, falburkolatok", level="Szakmunkás"),
            ProfessionType(name="Festő", description="Festés, tapétázás", level="Szakmunkás"),
            ProfessionType(name="Műszaki vezető", description="Projekt koordináció, minőségbiztosítás", level="Vezető"),
            ProfessionType(name="Építésvezető", description="Teljes építkezés irányítása", level="Vezető"),
        ]
        
        for pt in profession_types:
            session.add(pt)
        
        # Add project types
        project_types = [
            ProjectType(name="Földszintes ház", description="Egyszintes családi ház"),
            ProjectType(name="Tetőteres ház", description="Beépített tetőterű családi ház"),
        ]
        
        for pt in project_types:
            session.add(pt)
        
        # Add sample users
        users = [
            User(first_name="John", last_name="Smith", email="john.smith@epitai.hu", 
                 role="Project Manager", department="Operations", phone="+36 20 123 4567"),
            User(first_name="Sarah", last_name="Johnson", email="sarah.johnson@epitai.hu", 
                 role="Engineer", department="Engineering", phone="+36 30 234 5678"),
            User(first_name="Mike", last_name="Wilson", email="mike.wilson@epitai.hu", 
                 role="Designer", department="Creative", phone="+36 70 345 6789"),
        ]
        
        # Set default passwords for sample users
        for user in users:
            user.set_password("admin123")  # Default password for all sample users
            session.add(user)
        
        session.commit()
        print("Sample data populated successfully!")
        
    except Exception as e:
        session.rollback()
        print(f"Failed to populate sample data: {e}")
        raise

# Auto-migration functions
def auto_migrate():
    """Run automatic database migration"""
    try:
        from migration_utils import AutoMigrationManager
        manager = AutoMigrationManager()
        return manager.auto_migrate()
    except Exception as e:
        print(f"Auto-migration failed: {e}")
        return {'success': False, 'message': str(e)}

def check_migration_status():
    """Check current migration status"""
    try:
        from migration_utils import AutoMigrationManager
        manager = AutoMigrationManager()
        return manager.check_migration_status()
    except Exception as e:
        print(f"Error checking migration status: {e}")
        return {'error': str(e)}

def generate_migration(message: str = None):
    """Generate a new migration"""
    try:
        from migration_utils import AutoMigrationManager
        manager = AutoMigrationManager()
        return manager.generate_migration(message)
    except Exception as e:
        print(f"Error generating migration: {e}")
        return None

def apply_migrations():
    """Apply pending migrations"""
    try:
        from migration_utils import AutoMigrationManager
        manager = AutoMigrationManager()
        return manager.apply_migrations()
    except Exception as e:
        print(f"Error applying migrations: {e}")
        return False

# Export commonly used functions
__all__ = [
    'engine',
    'SessionLocal',
    'get_db_session',
    'get_db',
    'create_tables',
    'drop_tables',
    'reset_database',
    'check_database_connection',
    'get_database_info',
    'initialize_database',
    'auto_migrate',
    'check_migration_status',
    'generate_migration',
    'apply_migrations'
]
