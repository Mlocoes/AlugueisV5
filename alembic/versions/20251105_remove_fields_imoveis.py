"""remove iptu_anual and proprietario_id from imoveis

Revision ID: remove_fields_imoveis
Revises: nullable_proprietario
Create Date: 2025-11-05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'remove_fields_imoveis'
down_revision = 'nullable_proprietario'
depends_on = None


def upgrade():
    # Remover coluna iptu_anual (redundante com valor_iptu)
    op.drop_column('imoveis', 'iptu_anual')

    # Remover coluna proprietario_id (propriedade definida por participacoes)
    op.drop_column('imoveis', 'proprietario_id')


def downgrade():
    # Recriar coluna proprietario_id
    op.add_column('imoveis', sa.Column('proprietario_id', sa.Integer(), nullable=True))

    # Recriar coluna iptu_anual
    op.add_column('imoveis', sa.Column('iptu_anual', sa.Float(), nullable=True))
