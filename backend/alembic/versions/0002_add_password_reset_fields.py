"""Add password reset fields to users table

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-16

"""
from alembic import op
import sqlalchemy as sa

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add password_reset_token column
    op.add_column('users',
        sa.Column('password_reset_token', sa.String(255), nullable=True)
    )
    
    # Add password_reset_token_expires column
    op.add_column('users',
        sa.Column('password_reset_token_expires', sa.DateTime(), nullable=True)
    )

def downgrade() -> None:
    # Remove the columns
    op.drop_column('users', 'password_reset_token_expires')
    op.drop_column('users', 'password_reset_token')
