"""remove campos desnecessarios data_pagamento, observacoes, updated_at, atualizado_em

Revision ID: remove_unused_fields
Revises: remove_valor_fields
Create Date: 2025-11-06

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'remove_unused_fields'
down_revision = 'remove_valor_fields'
branch_labels = None
depends_on = None


def upgrade():
    # Remover colunas desnecessárias da tabela alugueis_mensais
    op.drop_column('alugueis_mensais', 'data_pagamento')
    op.drop_column('alugueis_mensais', 'observacoes')
    op.drop_column('alugueis_mensais', 'updated_at')
    op.drop_column('alugueis_mensais', 'atualizado_em')


def downgrade():
    # Recriar as colunas removidas (para rollback)
    op.add_column('alugueis_mensais', sa.Column('data_pagamento', sa.Date(), nullable=True))
    op.add_column('alugueis_mensais', sa.Column('observacoes', sa.String(length=1000), nullable=True))
    op.add_column('alugueis_mensais', sa.Column('updated_at', sa.DateTime(), nullable=True))
    op.add_column('alugueis_mensais', sa.Column('atualizado_em', sa.DateTime(), nullable=True))