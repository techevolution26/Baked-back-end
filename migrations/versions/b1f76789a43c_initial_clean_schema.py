"""initial_clean_schema

Revision ID: b1f76789a43c
Revises: 
Create Date: 2026-07-26 02:44:15.045399

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'b1f76789a43c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create Bakeries table first (Omitting the users foreign key initially to prevent dependency crashes)
    op.create_table('bakeries',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('owner_user_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=150), nullable=False),
    sa.Column('location', sa.String(length=255), nullable=False),
    sa.Column('mpesa_till', sa.String(length=20), nullable=True),
    sa.Column('verified', sa.Boolean(), nullable=False),
    sa.Column('rating', sa.Numeric(precision=3, scale=2), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('subdomain', sa.String(length=63), nullable=True),
    sa.Column('custom_domain', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('owner_user_id')
    )
    op.create_index(op.f('ix_bakeries_custom_domain'), 'bakeries', ['custom_domain'], unique=True)
    op.create_index(op.f('ix_bakeries_subdomain'), 'bakeries', ['subdomain'], unique=True)

    # 2. Create Users table safely (References bakeries.id which exists now)
    op.create_table('users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=True),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('role', sa.Enum('customer', 'bakery_owner', 'admin', name='userrole'), nullable=False),
    sa.Column('bakery_id', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['bakery_id'], ['bakeries.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username', 'bakery_id', name='uq_users_username_bakery')
    )
    op.create_index(op.f('ix_users_bakery_id'), 'users', ['bakery_id'], unique=False)

    # 3. Inject the foreign key mapping from bakeries -> users back into the system
    op.create_foreign_key(
        'fk_bakeries_owner_user_id_users',
        'bakeries', 'users',
        ['owner_user_id'], ['id']
    )

    # 4. Create remaining dependent schema items safely
    op.create_table('color_palettes',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('bakery_id', sa.UUID(), nullable=True),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('hex', sa.String(length=7), nullable=False),
    sa.Column('swatch_image', sa.String(length=500), nullable=True),
    sa.ForeignKeyConstraint(['bakery_id'], ['bakeries.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('design_templates',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('bakery_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=150), nullable=False),
    sa.Column('story', sa.Text(), nullable=True),
    sa.Column('base_shape', sa.String(length=50), nullable=False),
    sa.Column('base_price', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('cover_image_url', sa.String(length=500), nullable=False),
    sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('layers', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('customizable_fields', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['bakery_id'], ['bakeries.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_design_templates_bakery_id'), 'design_templates', ['bakery_id'], unique=False)
    op.create_table('sticker_assets',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('bakery_id', sa.UUID(), nullable=True),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('thumbnail_url', sa.String(length=500), nullable=False),
    sa.Column('category', sa.String(length=80), nullable=False),
    sa.ForeignKeyConstraint(['bakery_id'], ['bakeries.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('blueprints',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('template_id', sa.UUID(), nullable=True),
    sa.Column('customer_id', sa.UUID(), nullable=False),
    sa.Column('bakery_id', sa.UUID(), nullable=False),
    sa.Column('layers', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('preview_render_url', sa.String(length=500), nullable=True),
    sa.Column('printable_elements', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['bakery_id'], ['bakeries.id'], ),
    sa.ForeignKeyConstraint(['customer_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['template_id'], ['design_templates.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_blueprints_bakery_id'), 'blueprints', ['bakery_id'], unique=False)
    op.create_index(op.f('ix_blueprints_customer_id'), 'blueprints', ['customer_id'], unique=False)
    op.create_table('orders',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('blueprint_id', sa.UUID(), nullable=False),
    sa.Column('customer_id', sa.UUID(), nullable=False),
    sa.Column('bakery_id', sa.UUID(), nullable=False),
    sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('payment_status', sa.Enum('pending', 'paid', 'failed', 'refunded', name='paymentstatus'), nullable=False),
    sa.Column('order_status', sa.Enum('submitted', 'accepted', 'rejected', 'baking', 'ready', 'delivered', name='orderstatus'), nullable=False),
    sa.Column('mpesa_transaction_id', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['bakery_id'], ['bakeries.id'], ),
    sa.ForeignKeyConstraint(['blueprint_id'], ['blueprints.id'], ),
    sa.ForeignKeyConstraint(['customer_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('blueprint_id')
    )
    op.create_index(op.f('ix_orders_bakery_id'), 'orders', ['bakery_id'], unique=False)
    op.create_index(op.f('ix_orders_customer_id'), 'orders', ['customer_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_orders_customer_id'), table_name='orders')
    op.drop_index(op.f('ix_orders_bakery_id'), table_name='orders')
    op.drop_table('orders')
    op.drop_index(op.f('ix_blueprints_customer_id'), table_name='blueprints')
    op.drop_index(op.f('ix_blueprints_bakery_id'), table_name='blueprints')
    op.drop_table('blueprints')
    op.drop_table('sticker_assets')
    op.drop_index(op.f('ix_design_templates_bakery_id'), table_name='design_templates')
    op.drop_table('design_templates')
    op.drop_table('color_palettes')
    
    # Drop injected foreign key relation before stripping users table structure
    op.drop_constraint('fk_bakeries_owner_user_id_users', 'bakeries', type_='foreignkey')
    
    op.drop_index(op.f('ix_users_bakery_id'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_bakeries_subdomain'), table_name='bakeries')
    op.drop_index(op.f('ix_bakeries_custom_domain'), table_name='bakeries')
    op.drop_table('bakeries')
