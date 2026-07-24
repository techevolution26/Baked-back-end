"""multi-tenant domains + username-based, tenant-scoped accounts

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-23

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Bakery domain resolution -------------------------------------
    op.add_column("bakeries", sa.Column("subdomain", sa.String(63), nullable=True))
    op.add_column("bakeries", sa.Column("custom_domain", sa.String(255), nullable=True))
    op.create_unique_constraint("uq_bakeries_subdomain", "bakeries", ["subdomain"])
    op.create_unique_constraint("uq_bakeries_custom_domain", "bakeries", ["custom_domain"])
    op.create_index("ix_bakeries_subdomain", "bakeries", ["subdomain"])
    op.create_index("ix_bakeries_custom_domain", "bakeries", ["custom_domain"])

    # --- Users: username-based login, tenant-scoped, lightweight signup
    op.add_column("users", sa.Column("username", sa.String(50), nullable=True))
    # Backfill: anything seeded under the old phone-based scheme keeps
    # working by using its phone number as its initial username.
    op.execute("UPDATE users SET username = phone WHERE username IS NULL")
    op.alter_column("users", "username", nullable=False)

    op.add_column(
        "users",
        sa.Column("bakery_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key("fk_users_bakery_id", "users", "bakeries", ["bakery_id"], ["id"])
    op.create_index("ix_users_bakery_id", "users", ["bakery_id"])

    # Old identity fields become optional -- collected later via
    # account/bakery settings instead of at signup.
    op.alter_column("users", "phone", nullable=True)
    op.alter_column("users", "name", nullable=True)

    # Drop the old global-uniqueness constraints (auto-named by Postgres
    # from the column-level unique=True in migration 0001) and the now-
    # unused phone index, then add the composite constraint that scopes
    # uniqueness to (username, bakery_id) instead.
    op.drop_constraint("users_phone_key", "users", type_="unique")
    op.drop_constraint("users_email_key", "users", type_="unique")
    op.drop_index("ix_users_phone", table_name="users")
    op.create_unique_constraint("uq_users_username_bakery", "users", ["username", "bakery_id"])


def downgrade() -> None:
    op.drop_constraint("uq_users_username_bakery", "users", type_="unique")
    op.create_index("ix_users_phone", "users", ["phone"])
    op.create_unique_constraint("users_email_key", "users", ["email"])
    op.create_unique_constraint("users_phone_key", "users", ["phone"])

    op.alter_column("users", "name", nullable=False)
    op.alter_column("users", "phone", nullable=False)

    op.drop_index("ix_users_bakery_id", table_name="users")
    op.drop_constraint("fk_users_bakery_id", "users", type_="foreignkey")
    op.drop_column("users", "bakery_id")

    op.drop_column("users", "username")

    op.drop_index("ix_bakeries_custom_domain", table_name="bakeries")
    op.drop_index("ix_bakeries_subdomain", table_name="bakeries")
    op.drop_constraint("uq_bakeries_custom_domain", "bakeries", type_="unique")
    op.drop_constraint("uq_bakeries_subdomain", "bakeries", type_="unique")
    op.drop_column("bakeries", "custom_domain")
    op.drop_column("bakeries", "subdomain")
