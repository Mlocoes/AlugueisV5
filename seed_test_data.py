#!/usr/bin/env python3
"""
Script para popular o banco de dados com dados de teste
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.auth import get_password_hash
from app.models.usuario import Usuario
from app.models.imovel import Imovel


def create_test_data():
    """Cria dados de teste"""
    db: Session = SessionLocal()
    
    try:
        print("🔧 Criando dados de teste...")
        
        # Verificar se já existem dados
        existing_users = db.query(Usuario).filter(Usuario.id > 1).count()
        if existing_users > 0:
            print("⚠️  Dados de teste já existem. Pulando...")
            return
        
        # Criar proprietários de teste
        proprietarios_data = [
            {
                "nome": "João Silva",
                "email": "joao@example.com",
                "hashed_password": get_password_hash("senha123"),
                "cpf": "123.456.789-00",
                "telefone": "(11) 98765-4321",
                "is_admin": False,
                "is_active": True
            },
            {
                "nome": "Maria Santos",
                "email": "maria@example.com",
                "hashed_password": get_password_hash("senha123"),
                "cpf": "987.654.321-00",
                "telefone": "(11) 91234-5678",
                "is_admin": False,
                "is_active": True
            },
            {
                "nome": "Pedro Oliveira",
                "email": "pedro@example.com",
                "hashed_password": get_password_hash("senha123"),
                "cpf": "456.789.123-00",
                "telefone": "(11) 95555-1234",
                "is_admin": False,
                "is_active": True
            }
        ]
        
        proprietarios = []
        for data in proprietarios_data:
            prop = Usuario(**data)
            db.add(prop)
            proprietarios.append(prop)
        
        db.commit()
        for prop in proprietarios:
            db.refresh(prop)
        
        print(f"✅ {len(proprietarios)} proprietários criados")
        
        # Criar imóveis de teste
        imoveis_data = [
            {
                "nome": "Apartamento Centro",
                "endereco": "Rua das Flores, 123 - Apto 501",
                "cidade": "São Paulo",
                "estado": "SP",
                "cep": "01234-567",
                "valor_aluguel": 2500.00,
                "valor_condominio": 450.00,
                "valor_iptu": 150.00,
                "proprietario_id": proprietarios[0].id,
                "is_active": True
            },
            {
                "nome": "Casa Jardim América",
                "endereco": "Av. Brasil, 456",
                "cidade": "São Paulo",
                "estado": "SP",
                "cep": "01456-789",
                "valor_aluguel": 4500.00,
                "valor_condominio": 0.00,
                "valor_iptu": 300.00,
                "proprietario_id": proprietarios[0].id,
                "is_active": True
            },
            {
                "nome": "Kitnet Vila Mariana",
                "endereco": "Rua Aurora, 789",
                "cidade": "São Paulo",
                "estado": "SP",
                "cep": "04567-890",
                "valor_aluguel": 1200.00,
                "valor_condominio": 200.00,
                "valor_iptu": 80.00,
                "proprietario_id": proprietarios[1].id,
                "is_active": True
            },
            {
                "nome": "Cobertura Moema",
                "endereco": "Av. Ibirapuera, 321 - Cobertura",
                "cidade": "São Paulo",
                "estado": "SP",
                "cep": "04567-123",
                "valor_aluguel": 8000.00,
                "valor_condominio": 1200.00,
                "valor_iptu": 600.00,
                "proprietario_id": proprietarios[1].id,
                "is_active": True
            },
            {
                "nome": "Sala Comercial Paulista",
                "endereco": "Av. Paulista, 1000 - Sala 1205",
                "cidade": "São Paulo",
                "estado": "SP",
                "cep": "01311-000",
                "valor_aluguel": 5500.00,
                "valor_condominio": 800.00,
                "valor_iptu": 400.00,
                "proprietario_id": proprietarios[2].id,
                "is_active": True
            },
            {
                "nome": "Apartamento Pinheiros",
                "endereco": "Rua Teodoro Sampaio, 567 - Apto 302",
                "cidade": "São Paulo",
                "estado": "SP",
                "cep": "05406-000",
                "valor_aluguel": 3200.00,
                "valor_condominio": 550.00,
                "valor_iptu": 180.00,
                "proprietario_id": proprietarios[2].id,
                "is_active": True
            }
        ]
        
        imoveis = []
        for data in imoveis_data:
            imovel = Imovel(**data)
            db.add(imovel)
            imoveis.append(imovel)
        
        db.commit()
        print(f"✅ {len(imoveis)} imóveis criados")
        
        print("\n" + "="*50)
        print("✅ Dados de teste criados com sucesso!")
        print("="*50)
        print("\n📊 Resumo:")
        print(f"   • {len(proprietarios)} proprietários")
        print(f"   • {len(imoveis)} imóveis")
        print(f"   • Valor total mensal: R$ {sum(i.valor_aluguel for i in imoveis):,.2f}")
        print("\n🔑 Credenciais dos proprietários:")
        print("   • joao@example.com / senha123")
        print("   • maria@example.com / senha123")
        print("   • pedro@example.com / senha123")
        print("\n🔐 Admin:")
        print("   • admin@sistema.com / admin123")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Erro ao criar dados de teste: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_test_data()
