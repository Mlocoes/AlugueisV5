"""
Testes de integração para os endpoints do dashboard
"""
import pytest
from datetime import datetime, date
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from app.models.imovel import Imovel
from app.models.aluguel import AluguelMensal
from app.models.proprietario import Proprietario
from app.core.auth import get_password_hash


def test_dashboard_stats_endpoint(client: TestClient, db_session: Session):
    """Testa o endpoint de estatísticas do dashboard"""
    
    # Criar proprietário de teste
    proprietario = Proprietario(
        tipo_pessoa="fisica",
        nome="Teste Proprietario",
        cpf="111.111.111-11",
        email="prop@teste.com",
        telefone="11999999999"
    )
    db_session.add(proprietario)
    db_session.commit()
    db_session.refresh(proprietario)
    
    # Criar usuário admin de teste
    admin_user = Usuario(
        nome="Admin Teste",
        email="admin@integration.com",
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
    
    # Criar aluguéis de teste
    # Cenário: aluguel com valor_total diferente da soma manual para detectar o problema
    aluguel1 = AluguelMensal(
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
        valor_total=2800.0,  # Total correto
        pago=True,
        data_pagamento=date(2025, 1, 5)
    )
    
    # Aluguel não pago
    aluguel2 = AluguelMensal(
        imovel_id=imovel.id,
        proprietario_id=proprietario.id,
        mes_referencia="2025-02",
        data_referencia=date(2025, 2, 1),
        valor_aluguel=2000.0,
        valor_condominio=300.0,
        valor_iptu=100.0,
        valor_luz=200.0,
        valor_agua=90.0,
        valor_gas=60.0,
        valor_internet=100.0,
        outros_valores=50.0,
        valor_total=2900.0,  # Total diferente
        pago=False
    )
    
    db_session.add(aluguel1)
    db_session.add(aluguel2)
    db_session.commit()
    
    # Login como admin
    login_response = client.post(
        "/api/auth/login",
        json={"email": "admin@integration.com", "password": "senha123"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # Fazer request para o endpoint de stats
    response = client.get(
        "/api/dashboard/stats?ano=2025",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verificações
    assert data["total_imoveis"] >= 1
    assert data["total_alugueis"] == 2
    
    # Valores esperados vs recebidos
    # O problema está aqui: o dashboard pode estar calculando errado se não usar valor_total
    expected_total = 2800.0 + 2900.0  # 5700.0
    expected_received = 2800.0  # apenas o pago
    
    print(f"\nValores do teste:")
    print(f"Esperado (soma manual): {expected_total}")
    print(f"Esperado (API): {data['valor_total_esperado']}")
    print(f"Recebido (soma manual): {expected_received}")
    print(f"Recebido (API): {data['valor_total_recebido']}")
    
    # Verificar se os valores estão corretos
    assert data["valor_total_esperado"] == expected_total, f"Expected {expected_total}, got {data['valor_total_esperado']}"
    assert data["valor_total_recebido"] == expected_received, f"Expected {expected_received}, got {data['valor_total_recebido']}"
    
    # Taxa de recebimento
    expected_rate = (expected_received / expected_total * 100)
    assert abs(data["taxa_recebimento"] - expected_rate) < 0.1


def test_dashboard_with_valor_total_mismatch(client: TestClient, db_session: Session):
    """Testa cenário onde valor_total difere da soma manual - detecta o bug"""
    
    # Criar proprietário de teste
    proprietario = Proprietario(
        tipo_pessoa="fisica",
        nome="Teste Proprietario 2",
        cpf="222.222.222-22",
        email="prop2@teste.com",
        telefone="11999999999"
    )
    db_session.add(proprietario)
    db_session.commit()
    db_session.refresh(proprietario)
    
    # Criar usuário admin de teste
    admin_user = Usuario(
        nome="Admin Teste 2",
        email="admin2@integration.com",
        hashed_password=get_password_hash("senha123"),
        is_admin=True,
        is_active=True
    )
    db_session.add(admin_user)
    db_session.commit()
    db_session.refresh(admin_user)
    
    # Criar imóvel de teste
    imovel = Imovel(
        nome="Apartamento Teste 2",
        endereco="Rua Teste, 456",
        cidade="São Paulo",
        estado="SP",
        cep="01234-567",
        valor_aluguel=1000.0,
        proprietario_id=proprietario.id,
        is_active=True
    )
    db_session.add(imovel)
    db_session.commit()
    db_session.refresh(imovel)
    
    # Criar aluguel com valor_total DIFERENTE da soma manual
    # Isso simula um caso onde valor_total foi ajustado manualmente (desconto, ajuste, etc)
    aluguel = AluguelMensal(
        imovel_id=imovel.id,
        proprietario_id=proprietario.id,
        mes_referencia="2025-03",
        data_referencia=date(2025, 3, 1),
        valor_aluguel=1000.0,
        valor_condominio=200.0,
        valor_iptu=100.0,
        valor_luz=0.0,
        valor_agua=0.0,
        valor_gas=0.0,
        valor_internet=0.0,
        outros_valores=0.0,
        valor_total=1200.0,  # Soma manual seria 1300.0, mas foi aplicado desconto de 100
        pago=True
    )
    
    db_session.add(aluguel)
    db_session.commit()
    
    # Login como admin
    login_response = client.post(
        "/api/auth/login",
        json={"email": "admin2@integration.com", "password": "senha123"}
    )
    print(f"\nLogin response: {login_response.status_code}")
    if login_response.status_code != 200:
        print(f"Login error: {login_response.text}")
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # Fazer request para o endpoint de stats
    response = client.get(
        "/api/dashboard/stats?ano=2025",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    print(f"\n=== Teste de Mismatch ===")
    print(f"valor_total no DB: 1200.0")
    print(f"Soma manual dos campos: 1300.0 (1000+200+100)")
    print(f"Valor esperado pela API: {data['valor_total_esperado']}")
    print(f"Valor recebido pela API: {data['valor_total_recebido']}")
    
    # BUG ESPERADO: Se a API usar soma manual, vai retornar 1300.0 em vez de 1200.0
    # O correto seria usar valor_total = 1200.0
    manual_sum = 1000.0 + 200.0 + 100.0  # 1300.0
    correct_value = 1200.0  # valor_total armazenado
    
    # Este teste vai FALHAR se o bug existir (API retorna 1300 em vez de 1200)
    assert data["valor_total_esperado"] == correct_value, \
        f"BUG DETECTADO: API deveria retornar valor_total (1200.0), mas retornou {data['valor_total_esperado']}"
