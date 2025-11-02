"""add imovel fields

Revision ID: add_imovel_fields
Revises: 
Create Date: 2025-11-02

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_imovel_fields'
down_revision = None
depends_on = None


def upgrade():
    # Adicionar novos campos ao modelo Imovel
    op.add_column('imoveis', sa.Column('tipo', sa.String(50), nullable=True))
    op.add_column('imoveis', sa.Column('area_total', sa.Float, nullable=True))
    op.add_column('imoveis', sa.Column('area_construida', sa.Float, nullable=True))
    op.add_column('imoveis', sa.Column('valor_catastral', sa.Float, nullable=True))
    op.add_column('imoveis', sa.Column('valor_mercado', sa.Float, nullable=True))
    op.add_column('imoveis', sa.Column('iptu_anual', sa.Float, nullable=True))


def downgrade():
    op.drop_column('imoveis', 'iptu_anual')
    op.drop_column('imoveis', 'valor_mercado')
    op.drop_column('imoveis', 'valor_catastral')
    op.drop_column('imoveis', 'area_construida')
    op.drop_column('imoveis', 'area_total')
    op.drop_column('imoveis', 'tipo')
