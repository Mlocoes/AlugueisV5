"""add status field to imoveis

Revision ID: add_status_imoveis
Revises: add_imovel_fields, 93d2d3c62163
Create Date: 2025-11-05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_status_imoveis'
down_revision = ('add_imovel_fields', '93d2d3c62163')
depends_on = None


def upgrade():
    # Adicionar campo status com valores permitidos: 'disponivel' ou 'alugado'
    op.add_column('imoveis', sa.Column('status', sa.String(20), nullable=False, server_default='disponivel'))
    
    # Atualizar imóveis com is_active=True para 'disponivel' (padrão já aplicado)
    # Imóveis inativos continuam com o default 'disponivel' mas is_active=False controlará visibilidade


def downgrade():
    op.drop_column('imoveis', 'status')
