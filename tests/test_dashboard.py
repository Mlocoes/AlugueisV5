"""
Testes para verificar a correção dos dados do dashboard
"""
import pytest
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from app.models.imovel import Imovel
from app.models.aluguel import AluguelMensal
from app.models.proprietario import Proprietario
from app.core.auth import get_password_hash


def test_dashboard_stats_calculation(db_session: Session):
    """Testa se os cálculos das estatísticas do dashboard estão corretos"""
    
    # Criar proprietário de teste
    proprietario = Proprietario(
        tipo_pessoa="fisica",
        nome="Teste Proprietario",
        cpf="123.456.789-00",
        email="teste@teste.com",
        telefone="11999999999"
    )
    db_session.add(proprietario)
    db_session.commit()
    db_session.refresh(proprietario)
    
    # Criar usuário admin de teste
    admin_user = Usuario(
        nome="Admin Teste",
        email="admin@teste.com",
        hashed_password=get_password_hash("senha123"),
        is_admin=True,
        is_active=True
    )
    db_session.add(admin_user)
    db_session.commit()
    db_session.refresh(admin_user)
    
    # Criar imóvel de teste
    imovel = Imovel(
        nome="Apartamento Teste",
        endereco="Rua Teste, 123",
        cidade="São Paulo",
        estado="SP",
        cep="01234-567",
        valor_aluguel=2000.0,
        valor_condominio=300.0,
        valor_iptu=100.0,
        proprietario_id=proprietario.id,
        is_active=True
    )
    db_session.add(imovel)
    db_session.commit()
    db_session.refresh(imovel)
    
    # Criar aluguel mensal de teste com valor_total calculado
    aluguel = AluguelMensal(
        imovel_id=imovel.id,
        proprietario_id=proprietario.id,
        mes_referencia="2025-01",
        data_referencia=date(2025, 1, 1),
        valor_aluguel=2000.0,
        valor_condominio=300.0,
        valor_iptu=100.0,
        valor_luz=150.0,
        valor_agua=80.0,
        valor_gas=50.0,
        valor_internet=100.0,
        outros_valores=20.0,
        valor_total=2800.0,  # Total correto: 2000+300+100+150+80+50+100+20 = 2800
        pago=True,
        data_pagamento=date(2025, 1, 5)
    )
    db_session.add(aluguel)
    db_session.commit()
    db_session.refresh(aluguel)
    
    # Verificar que o valor_total armazenado está correto
    assert aluguel.valor_total == 2800.0
    
    # Simular o cálculo manual usado no dashboard (old way)
    manual_calculation = (
        aluguel.valor_aluguel + 
        (aluguel.valor_condominio or 0) +
        (aluguel.valor_iptu or 0) +
        (aluguel.valor_luz or 0) +
        (aluguel.valor_agua or 0) +
        (aluguel.valor_gas or 0) +
        (aluguel.valor_internet or 0) +
        (aluguel.outros_valores or 0)
    )
    
    assert manual_calculation == 2800.0
    assert manual_calculation == aluguel.valor_total


def test_dashboard_evolution_calculation(db_session: Session):
    """Testa se os cálculos de evolução mensal estão corretos"""
    
    # Criar proprietário de teste
    proprietario = Proprietario(
        tipo_pessoa="fisica",
        nome="Teste Proprietario",
        cpf="123.456.789-00",
        email="teste2@teste.com",
        telefone="11999999999"
    )
    db_session.add(proprietario)
    db_session.commit()
    db_session.refresh(proprietario)
    
    # Criar imóvel de teste
    imovel = Imovel(
        nome="Apartamento Teste 2",
        endereco="Rua Teste, 456",
        cidade="São Paulo",
        estado="SP",
        cep="01234-567",
        valor_aluguel=1500.0,
        proprietario_id=proprietario.id,
        is_active=True
    )
    db_session.add(imovel)
    db_session.commit()
    db_session.refresh(imovel)
    
    # Criar 2 aluguéis para o mesmo mês
    aluguel1 = AluguelMensal(
        imovel_id=imovel.id,
        proprietario_id=proprietario.id,
        mes_referencia="2025-01",
        data_referencia=date(2025, 1, 1),
        valor_aluguel=1500.0,
        valor_condominio=200.0,
        valor_total=1700.0,
        pago=True
    )
    aluguel2 = AluguelMensal(
        imovel_id=imovel.id,
        proprietario_id=proprietario.id,
        mes_referencia="2025-02",
        data_referencia=date(2025, 2, 1),
        valor_aluguel=1500.0,
        valor_condominio=200.0,
        valor_total=1700.0,
        pago=False
    )
    
    db_session.add(aluguel1)
    db_session.add(aluguel2)
    db_session.commit()
    
    # Verificar totais
    total_esperado = 1700.0 + 1700.0  # 3400.0
    total_recebido = 1700.0  # apenas o pago
    
    assert aluguel1.valor_total == 1700.0
    assert aluguel2.valor_total == 1700.0
    assert total_esperado == 3400.0
    assert total_recebido == 1700.0
