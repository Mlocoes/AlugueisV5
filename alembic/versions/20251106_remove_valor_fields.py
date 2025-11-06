"""remove campos de valor individuais, manter apenas valor_total

Revision ID: remove_valor_fields
Revises: 742793b
Create Date: 2025-11-06

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'remove_valor_fields'
down_revision = '20251106_add_participacao_versoes'
branch_labels = None
depends_on = None


def upgrade():
    # Remover colunas desnecessárias da tabela alugueis_mensais
    op.drop_column('alugueis_mensais', 'valor_aluguel')
    op.drop_column('alugueis_mensais', 'valor_condominio')
    op.drop_column('alugueis_mensais', 'valor_iptu')
    op.drop_column('alugueis_mensais', 'valor_luz')
    op.drop_column('alugueis_mensais', 'valor_agua')
    op.drop_column('alugueis_mensais', 'valor_gas')
    op.drop_column('alugueis_mensais', 'valor_internet')
    op.drop_column('alugueis_mensais', 'outros_valores')


def downgrade():
    # Recriar as colunas removidas (para rollback)
    op.add_column('alugueis_mensais', sa.Column('valor_aluguel', sa.Float(), nullable=False, default=0.0))
    op.add_column('alugueis_mensais', sa.Column('valor_condominio', sa.Float(), nullable=False, default=0.0))
    op.add_column('alugueis_mensais', sa.Column('valor_iptu', sa.Float(), nullable=False, default=0.0))
    op.add_column('alugueis_mensais', sa.Column('valor_luz', sa.Float(), nullable=False, default=0.0))
    op.add_column('alugueis_mensais', sa.Column('valor_agua', sa.Float(), nullable=False, default=0.0))
    op.add_column('alugueis_mensais', sa.Column('valor_gas', sa.Float(), nullable=False, default=0.0))
    op.add_column('alugueis_mensais', sa.Column('valor_internet', sa.Float(), nullable=False, default=0.0))
    op.add_column('alugueis_mensais', sa.Column('outros_valores', sa.Float(), nullable=False, default=0.0))