"""Initial migration

Revision ID: 0001
Revises: 
Create Date: 2024-01-15

"""
from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('status', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('parent_id', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('verification_token', sa.String(255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['parent_id'], ['users.id'], ondelete='SET NULL'),
        # This creates the unique index automatically with the name 'ix_users_email'
        sa.UniqueConstraint('email', name='ix_users_email')
    )
    # REMOVED: redundant op.create_index calls that caused the DuplicateTable error

    # Create roles table
    op.create_table('roles',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='uq_roles_name')
    )

    # Create user_roles table
    op.create_table('user_roles',
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('role_id', sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint('user_id', 'role_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE')
    )

    # Create projects table
    op.create_table('projects',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('client', sa.String(255), nullable=False),
        sa.Column('status', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('manager_id', sa.BigInteger(), nullable=False),
        sa.Column('reporting_area', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['manager_id'], ['users.id'], ondelete='RESTRICT')
    )

    # Create project_members table
    op.create_table('project_members',
        sa.Column('project_id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('bill_rate', sa.DECIMAL(10, 2), nullable=True),
        sa.PrimaryKeyConstraint('project_id', 'user_id'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )

    # Create time_entries table
    op.create_table('time_entries',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('project_id', sa.BigInteger(), nullable=False),
        sa.Column('work_date', sa.Date(), nullable=False),
        sa.Column('hours', sa.DECIMAL(5, 2), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='PENDING'),
        sa.Column('approved_by_id', sa.BigInteger(), nullable=True),
        sa.Column('approval_date', sa.DateTime(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('resubmission_notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['approved_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('user_id', 'project_id', 'work_date', name='uq_time_entries_user_project_date'),
        sa.CheckConstraint('hours >= 0 AND hours <= 24', name='check_hours_range')
    )

def downgrade() -> None:
    op.drop_table('time_entries')
    op.drop_table('project_members')
    op.drop_table('projects')
    op.drop_table('user_roles')
    op.drop_table('roles')
    op.drop_table('users')



