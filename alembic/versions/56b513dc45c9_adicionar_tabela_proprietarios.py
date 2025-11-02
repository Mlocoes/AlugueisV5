"""Adicionar tabela proprietarios

Revision ID: 56b513dc45c9
Revises: bfe0965c6ad1
Create Date: 2025-11-02 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '56b513dc45c9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Criar tabela proprietarios
    op.create_table(
        'proprietarios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tipo_pessoa', sa.String(length=20), nullable=False),
        sa.Column('nome', sa.String(length=200), nullable=False),
        sa.Column('cpf', sa.String(length=14), nullable=True),
        sa.Column('rg', sa.String(length=20), nullable=True),
        sa.Column('razao_social', sa.String(length=200), nullable=True),
        sa.Column('nome_fantasia', sa.String(length=200), nullable=True),
        sa.Column('cnpj', sa.String(length=18), nullable=True),
        sa.Column('inscricao_estadual', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('telefone', sa.String(length=20), nullable=True),
        sa.Column('celular', sa.String(length=20), nullable=True),
        sa.Column('endereco', sa.String(length=500), nullable=True),
        sa.Column('numero', sa.String(length=10), nullable=True),
        sa.Column('complemento', sa.String(length=100), nullable=True),
        sa.Column('bairro', sa.String(length=100), nullable=True),
        sa.Column('cidade', sa.String(length=100), nullable=True),
        sa.Column('estado', sa.String(length=2), nullable=True),
        sa.Column('cep', sa.String(length=10), nullable=True),
        sa.Column('banco', sa.String(length=100), nullable=True),
        sa.Column('agencia', sa.String(length=20), nullable=True),
        sa.Column('conta', sa.String(length=20), nullable=True),
        sa.Column('tipo_conta', sa.String(length=20), nullable=True),
        sa.Column('pix', sa.String(length=100), nullable=True),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Criar índices
    op.create_index('ix_proprietarios_id', 'proprietarios', ['id'])
    op.create_index('ix_proprietarios_nome', 'proprietarios', ['nome'])
    op.create_index('ix_proprietarios_cpf', 'proprietarios', ['cpf'], unique=True)
    op.create_index('ix_proprietarios_cnpj', 'proprietarios', ['cnpj'], unique=True)
    op.create_index('ix_proprietarios_email', 'proprietarios', ['email'])
    
    # Migrar dados de usuários para proprietários
    # Inserir proprietários baseados nos usuários com imóveis
    op.execute("""
        INSERT INTO proprietarios (id, tipo_pessoa, nome, email, is_active, created_at, updated_at)
        SELECT DISTINCT u.id, 'fisica', u.nome, u.email, true, u.created_at, u.updated_at
        FROM usuarios u
        INNER JOIN imoveis i ON i.proprietario_id = u.id
        WHERE NOT u.is_admin
    """)
    
    # Atualizar foreign key de imoveis para apontar para proprietarios
    op.drop_constraint('imoveis_proprietario_id_fkey', 'imoveis', type_='foreignkey')
    op.create_foreign_key(
        'imoveis_proprietario_id_fkey', 
        'imoveis', 
        'proprietarios',
        ['proprietario_id'], 
        ['id']
    )


def downgrade():
    # Reverter foreign key de imoveis
    op.drop_constraint('imoveis_proprietario_id_fkey', 'imoveis', type_='foreignkey')
    op.create_foreign_key(
        'imoveis_proprietario_id_fkey',
        'imoveis',
        'usuarios',
        ['proprietario_id'],
        ['id']
    )
    
    # Remover índices
    op.drop_index('ix_proprietarios_email', 'proprietarios')
    op.drop_index('ix_proprietarios_cnpj', 'proprietarios')
    op.drop_index('ix_proprietarios_cpf', 'proprietarios')
    op.drop_index('ix_proprietarios_nome', 'proprietarios')
    op.drop_index('ix_proprietarios_id', 'proprietarios')
    
    # Remover tabela
    op.drop_table('proprietarios')
