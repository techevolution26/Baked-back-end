"""add: template model_tier_row with safe data backfill

Revision ID: 5a7e90acfcfc
Revises: b1f76789a43c
Create Date: 2026-07-26 15:11:51.934114

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Keeps File 1's correct tracking timeline
revision = '5a7e90acfcfc'
down_revision = 'b1f76789a43c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Uses File 2's smart backfill strategy
    op.add_column(
        "design_templates",
        sa.Column("tiers", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
    )

    # Convert old flat string shapes into structured JSON configuration data
    op.execute(
        """
        UPDATE design_templates
        SET tiers = jsonb_build_array(
            jsonb_build_object(
                'shape', CASE WHEN base_shape = 'square' THEN 'square' ELSE 'round' END
            )
        )
        WHERE tiers = '[]'::jsonb
        """
    )

    op.drop_column("design_templates", "base_shape")


def downgrade() -> None:
    # Reverse transformation if you ever need to rollback
    op.add_column("design_templates", sa.Column("base_shape", sa.String(length=50), nullable=True))
    op.execute(
        """
        UPDATE design_templates
        SET base_shape = COALESCE(tiers->0->>'shape', 'round')
        """
    )
    op.alter_column("design_templates", "base_shape", nullable=False)
    op.drop_column("design_templates", "tiers")
