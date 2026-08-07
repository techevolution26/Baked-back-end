"""add_blueprint_category

Revision ID: 3ac02456f4c7
Revises: efc667731c6d
Create Date: 2026-08-04 10:03:30.923020

"""
from alembic import op
import sqlalchemy as sa


revision = '3ac02456f4c7'
down_revision = 'efc667731c6d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add the category column with a server default to handle existing rows
    op.add_column(
        'blueprints', 
        sa.Column('category', sa.String(length=50), nullable=False, server_default='vanilla')
    )
    # Optional: Remove the server default if you only want it handled by application logic moving forward
    op.alter_column('blueprints', 'category', server_default=None)


def downgrade() -> None:
    # Drop the category column if rolling back
    op.drop_column('blueprints', 'category')
