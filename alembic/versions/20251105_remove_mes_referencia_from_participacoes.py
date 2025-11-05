"""remove mes_referencia from participacoes

Revision ID: remove_mes_referencia
Revises: remove_valor_participacao
Create Date: 2025-11-05 17:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'remove_mes_referencia'
down_revision = 'remove_valor_participacao'
branch_labels = None
depends_on = None


def upgrade():
    # Remove the mes_referencia column from participacoes table
    op.drop_column('participacoes', 'mes_referencia')


def downgrade():
    # Add back the mes_referencia column
    op.add_column('participacoes', sa.Column('mes_referencia', sa.String(7), nullable=False))