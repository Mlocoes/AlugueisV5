"""remove valor_participacao from participacoes

Revision ID: remove_valor_participacao
Revises: remove_fields_imoveis
Create Date: 2025-11-05 17:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'remove_valor_participacao'
down_revision = 'remove_fields_imoveis'
branch_labels = None
depends_on = None


def upgrade():
    # Remove the valor_participacao column from participacoes table
    op.drop_column('participacoes', 'valor_participacao')


def downgrade():
    # Add back the valor_participacao column
    op.add_column('participacoes', sa.Column('valor_participacao', sa.Float(), nullable=False, default=0.0))