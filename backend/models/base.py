"""
Base SQLAlchemy configuration and utilities for Pontum Construction Management System
"""

from sqlalchemy import create_engine, MetaData, Column, Integer, String, Text, DateTime, Boolean, Numeric, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from sqlalchemy import event
from datetime import datetime
import os

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres.idohoalwmovuewvcpqcn:Cyrtoz-ziqrad-kummo8@aws-1-eu-north-1.pooler.supabase.com:5432/postgres')

# SSL Certificate configuration
SSL_CERT_PATH = os.getenv('SSL_CERT_PATH')  # Path to client certificate
SSL_KEY_PATH = os.getenv('SSL_KEY_PATH')    # Path to client private key
SSL_CA_PATH = os.getenv('SSL_CA_PATH')      # Path to CA certificate
SSL_MODE = os.getenv('SSL_MODE', 'require') # SSL mode: disable, allow, prefer, require, verify-ca, verify-full

# Build connection arguments for SSL
connect_args = {}
if SSL_CERT_PATH and SSL_KEY_PATH:
    connect_args['sslcert'] = SSL_CERT_PATH
    connect_args['sslkey'] = SSL_KEY_PATH
if SSL_CA_PATH:
    connect_args['sslrootcert'] = SSL_CA_PATH
if SSL_MODE:
    connect_args['sslmode'] = SSL_MODE

# Create engine with SSL support
engine = create_engine(
    DATABASE_URL,
    echo=os.getenv('SQLALCHEMY_ECHO', 'False').lower() == 'true',
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args=connect_args
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)

# Create declarative base
Base = declarative_base()

# Metadata for database operations
metadata = MetaData()

# Alias for easier imports in model files
db = Column

# Database session dependency
def get_db():
    """Get database session"""
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

# Base model with common fields and methods
class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps"""
    created_at = db(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

# Event listener to update updated_at timestamp
@event.listens_for(Base, 'before_update', propagate=True)
def receive_before_update(mapper, connection, target):
    """Update the updated_at timestamp before any update operation"""
    target.updated_at = datetime.utcnow()

# Database utilities
def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def drop_db():
    """Drop all database tables"""
    Base.metadata.drop_all(bind=engine)

def reset_db():
    """Reset database (drop and recreate all tables)"""
    drop_db()
    init_db()
