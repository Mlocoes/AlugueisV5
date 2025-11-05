"""make proprietario_id nullable in imoveis

Revision ID: nullable_proprietario
Revises: add_status_imoveis
Create Date: 2025-11-05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'nullable_proprietario'
down_revision = 'add_status_imoveis'
depends_on = None


def upgrade():
    # Alterar coluna proprietario_id para nullable
    op.alter_column('imoveis', 'proprietario_id',
                    existing_type=sa.Integer(),
                    nullable=True)


def downgrade():
    # Reverter para not null
    op.alter_column('imoveis', 'proprietario_id',
                    existing_type=sa.Integer(),
                    nullable=False)
