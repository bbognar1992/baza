"""Add sample data to all tables

Revision ID: 7b40015340d2
Revises: 78a81eea8fdc
Create Date: 2025-10-18 13:53:02.568815

"""
from typing import Sequence, Union
from datetime import datetime, date
import sys
import os

from werkzeug.security import generate_password_hash

from alembic import op
import sqlalchemy as sa

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# revision identifiers, used by Alembic.
revision: str = '7b40015340d2'
down_revision: Union[str, Sequence[str], None] = '78a81eea8fdc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add sample data for users."""
    
    users_table = sa.table('users',
        sa.column('user_id', sa.Integer),
        sa.column('first_name', sa.String),
        sa.column('last_name', sa.String),
        sa.column('email', sa.String),
        sa.column('password_hash', sa.String),
        sa.column('role', sa.String),
        sa.column('department', sa.String),
        sa.column('phone', sa.String),
        sa.column('status', sa.String),
        sa.column('created_at', sa.DateTime),
        sa.column('updated_at', sa.DateTime)
    )
    
    now = datetime.now()
    # Insert one user
    users_data = [{
        'user_id': 1,
        'first_name': 'Nagy',
        'last_name': 'Sándor',
        'email': 'test@example.hu',
        'password_hash': generate_password_hash("test123", method='pbkdf2:sha256'),
        'role': 'Project Manager',
        'department': 'Operations',
        'phone': '+36 20 123 4567',
        'status': 'Active',
        'created_at': now,
        'updated_at': now
    }]
    
    op.bulk_insert(users_table, users_data)

def downgrade() -> None:
    """Remove sample data for users."""
    op.execute("DELETE FROM users")
