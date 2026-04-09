"""新增租户与认证表

Revision ID: 002_tenant_auth
Revises: 001_initial
Create Date: 2026-04-08
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '002_tenant_auth'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 租户表
    op.create_table(
        'tenants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('plan', sa.String(length=20), nullable=False, server_default='free'),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )

    # 用户表
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False, unique=True),
        sa.Column('union_id', sa.String(length=100), nullable=True),
        sa.Column('nickname', sa.String(length=100), nullable=False, server_default=''),
        sa.Column('avatar', sa.String(length=500), nullable=False, server_default=''),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('last_login_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_users_phone', 'users', ['phone'])
    op.create_index('ix_users_union_id', 'users', ['union_id'])

    # 租户成员表
    op.create_table(
        'tenant_members',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False, server_default='viewer'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('invited_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'user_id'),
    )
    op.create_index('ix_tenant_members_tenant_id', 'tenant_members', ['tenant_id'])
    op.create_index('ix_tenant_members_user_id', 'tenant_members', ['user_id'])


def downgrade() -> None:
    op.drop_table('tenant_members')
    op.drop_table('users')
    op.drop_table('tenants')
