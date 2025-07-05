"""add reason to orders"""

from alembic import op
import sqlalchemy as sa

# ✅ Hash-ka migration-kan
revision = 'd0e1734afe60'

# ✅ Haddii uu yahay migration-kii ugu horreeyey
down_revision = None

branch_labels = None
depends_on = None

def upgrade():
    """Upgrade schema: Add 'reason' column to 'orders' table."""
    op.add_column('orders', sa.Column('reason', sa.String(length=255), nullable=True))

def downgrade():
    """Downgrade schema: Remove 'reason' column from 'orders' table."""
    op.drop_column('orders', 'reason')
