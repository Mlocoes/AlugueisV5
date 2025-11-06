"""add participacao_versoes table

Revision ID: 20251106_add_participacao_versoes
Revises: remove_mes_referencia
Create Date: 2025-11-06

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251106_add_participacao_versoes'
down_revision = 'remove_mes_referencia'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('participacao_versoes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=200), nullable=False),
        sa.Column('dados_json', sa.Text(), nullable=False),
        sa.Column('observacoes', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_participacao_versoes_id'), 'participacao_versoes', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_participacao_versoes_id'), table_name='participacao_versoes')
    op.drop_table('participacao_versoes')
