"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-07-23

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # create_type=False tells SQLAlchemy not to also try creating these
    # enum types itself when the columns below are added to a table --
    # we create them explicitly, once, right here. Without this, the
    # table creation triggers a second "CREATE TYPE" for the same name
    # and Postgres raises "type already exists".
    user_role = postgresql.ENUM(
        "customer", "bakery_owner", "admin", name="userrole", create_type=False
    )
    order_status = postgresql.ENUM(
        "submitted", "accepted", "rejected", "baking", "ready", "delivered",
        name="orderstatus", create_type=False,
    )
    payment_status = postgresql.ENUM(
        "pending", "paid", "failed", "refunded", name="paymentstatus", create_type=False
    )

    bind = op.get_bind()
    user_role.create(bind, checkfirst=True)
    order_status.create(bind, checkfirst=True)
    payment_status.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("phone", sa.String(20), nullable=False, unique=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(255), nullable=True, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", user_role, nullable=False, server_default="customer"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_phone", "users", ["phone"])

    op.create_table(
        "bakeries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, unique=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("location", sa.String(255), nullable=False),
        sa.Column("mpesa_till", sa.String(20), nullable=True),
        sa.Column("verified", sa.Boolean(), server_default=sa.false()),
        sa.Column("rating", sa.Numeric(3, 2), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "design_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("bakery_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bakeries.id"), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("base_shape", sa.String(50), nullable=False),
        sa.Column("base_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("cover_image_url", sa.String(500), nullable=False),
        sa.Column("tags", postgresql.JSONB(), server_default="[]"),
        sa.Column("customizable_fields", postgresql.JSONB(), server_default="{}"),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true()),
    )
    op.create_index("ix_design_templates_bakery_id", "design_templates", ["bakery_id"])

    op.create_table(
        "sticker_assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("bakery_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bakeries.id"), nullable=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("thumbnail_url", sa.String(500), nullable=False),
        sa.Column("category", sa.String(80), nullable=False),
    )

    op.create_table(
        "color_palettes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("bakery_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bakeries.id"), nullable=True),
        sa.Column("name", sa.String(80), nullable=False),
        sa.Column("hex", sa.String(7), nullable=False),
        sa.Column("swatch_image", sa.String(500), nullable=True),
    )

    op.create_table(
        "blueprints",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("design_templates.id"), nullable=True),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("bakery_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bakeries.id"), nullable=False),
        sa.Column("layers", postgresql.JSONB(), nullable=False),
        sa.Column("preview_render_url", sa.String(500), nullable=True),
        sa.Column("printable_elements", postgresql.JSONB(), server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_blueprints_customer_id", "blueprints", ["customer_id"])
    op.create_index("ix_blueprints_bakery_id", "blueprints", ["bakery_id"])

    op.create_table(
        "orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("blueprint_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("blueprints.id"), nullable=False, unique=True),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("bakery_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bakeries.id"), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("payment_status", payment_status, nullable=False, server_default="pending"),
        sa.Column("order_status", order_status, nullable=False, server_default="submitted"),
        sa.Column("mpesa_transaction_id", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_orders_customer_id", "orders", ["customer_id"])
    op.create_index("ix_orders_bakery_id", "orders", ["bakery_id"])


def downgrade() -> None:
    op.drop_table("orders")
    op.drop_table("blueprints")
    op.drop_table("color_palettes")
    op.drop_table("sticker_assets")
    op.drop_table("design_templates")
    op.drop_table("bakeries")
    op.drop_table("users")

    bind = op.get_bind()
    postgresql.ENUM(name="paymentstatus", create_type=False).drop(bind, checkfirst=True)
    postgresql.ENUM(name="orderstatus", create_type=False).drop(bind, checkfirst=True)
    postgresql.ENUM(name="userrole", create_type=False).drop(bind, checkfirst=True)
