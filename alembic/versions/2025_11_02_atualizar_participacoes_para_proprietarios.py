"""atualizar_participacoes_para_proprietarios

Revision ID: 93d2d3c62163
Revises: 56b513dc45c9
Create Date: 2025-11-02 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '93d2d3c62163'
down_revision = '56b513dc45c9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Atualiza a tabela participacoes para usar proprietarios em vez de usuarios
    """
    
    # 1. Remover a constraint FK antiga
    op.drop_constraint('participacoes_proprietario_id_fkey', 'participacoes', type_='foreignkey')
    
    # 2. Criar a nova constraint FK para proprietarios
    op.create_foreign_key(
        'participacoes_proprietario_id_fkey',
        'participacoes', 'proprietarios',
        ['proprietario_id'], ['id'],
        ondelete='CASCADE'
    )
    
    print("✅ Migração de participações concluída")


def downgrade() -> None:
    """
    Reverte as mudanças
    """
    
    # Remover FK de proprietarios
    op.drop_constraint('participacoes_proprietario_id_fkey', 'participacoes', type_='foreignkey')
    
    # Restaurar FK para usuarios
    op.create_foreign_key(
        'participacoes_proprietario_id_fkey',
        'participacoes', 'usuarios',
        ['proprietario_id'], ['id'],
        ondelete='CASCADE'
    )
