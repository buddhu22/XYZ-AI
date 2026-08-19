"""Phase 6 schema: users hashed_password and escalations table

Revision ID: 7a3f891b2c4e
Revises: 0d56eba94397
Create Date: 2026-08-20 00:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a3f891b2c4e'
down_revision: Union[str, None] = '0d56eba94397'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add hashed_password column to users table
    op.add_column('users', sa.Column('hashed_password', sa.String(length=255), nullable=True))

    # 2. Create escalations table
    op.create_table(
        'escalations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('query', sa.Text(), nullable=False),
        sa.Column('reason', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), server_default='OPEN', nullable=False),
        sa.Column('priority', sa.String(length=50), server_default='MEDIUM', nullable=False),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('resolved_by', sa.Integer(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['resolved_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_escalations_id'), 'escalations', ['id'], unique=False)
    op.create_index(op.f('ix_escalations_status'), 'escalations', ['status'], unique=False)
    op.create_index(op.f('ix_escalations_user_id'), 'escalations', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_escalations_user_id'), table_name='escalations')
    op.drop_index(op.f('ix_escalations_status'), table_name='escalations')
    op.drop_index(op.f('ix_escalations_id'), table_name='escalations')
    op.drop_table('escalations')
    op.drop_column('users', 'hashed_password')
