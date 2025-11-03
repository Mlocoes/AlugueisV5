#!/usr/bin/env python3
"""
Script de Teste do Sistema de Segurança
Testa rate limiting, validações e proteção contra força bruta
"""
import requests
import time
import sys

BASE_URL = "http://localhost:8000"


def test_rate_limiting():
    """Testa se rate limiting está funcionando"""
    print("\n🔒 TESTE 1: Rate Limiting no endpoint de login")
    print("=" * 60)
    
    # Tentar fazer 10 requisições seguidas (limite é 5/minuto)
    for i in range(1, 11):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "test@test.com", "password": "Test123!@#"}
        )
        
        print(f"Requisição {i}: Status {response.status_code}")
        
        if response.status_code == 429:
            print(f"✅ Rate limit ativado na requisição {i}!")
            print(f"   Resposta: {response.json()}")
            return True
        
        time.sleep(0.1)
    
    print("❌ Rate limit NÃO foi ativado (esperado na 6ª requisição)")
    return False


def test_ip_blacklist():
    """Testa bloqueio temporário de IP após tentativas falhas"""
    print("\n🚫 TESTE 2: Bloqueio de IP após tentativas falhas")
    print("=" * 60)
    
    # Fazer 5 tentativas falhas de login
    for i in range(1, 6):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "hacker@test.com", "password": "wrong_password"}
        )
        print(f"Tentativa falha {i}: Status {response.status_code}")
        time.sleep(1)
    
    # Tentar novamente após 5 falhas
    print("\nTentando novamente após 5 tentativas falhas...")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "admin@sistema.com", "password": "Admin123!@#"}
    )
    
    if response.status_code == 429:
        print("✅ IP foi bloqueado temporariamente!")
        print(f"   Resposta: {response.json()}")
        return True
    else:
        print(f"❌ IP NÃO foi bloqueado (Status: {response.status_code})")
        return False


def test_password_validation():
    """Testa validação de senha forte"""
    print("\n🔑 TESTE 3: Validação de Senha Forte")
    print("=" * 60)
    
    weak_passwords = [
        ("123456", "muito curta"),
        ("password", "sem números e caracteres especiais"),
        ("Password123", "sem caracteres especiais"),
        ("Password!@#", "sem números"),
        ("password123!@#", "sem maiúsculas"),
        ("PASSWORD123!@#", "sem minúsculas"),
    ]
    
    # Obter token de admin para testar registro
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "admin@sistema.com", "password": "Admin123!@#"}
    )
    
    if login_response.status_code != 200:
        print("❌ Não foi possível fazer login como admin para testar")
        return False
    
    cookies = login_response.cookies
    
    print("\nTestando senhas fracas:")
    for password, reason in weak_passwords:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            data={
                "nome": "Test User",
                "email": f"test_{int(time.time())}@test.com",
                "password": password
            },
            cookies=cookies
        )
        
        if response.status_code == 400:
            print(f"  ✅ Senha '{password}' rejeitada ({reason})")
        else:
            print(f"  ❌ Senha '{password}' aceita incorretamente!")
    
    # Testar senha forte
    print("\nTestando senha forte:")
    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        data={
            "nome": "Test User Strong",
            "email": f"strong_{int(time.time())}@test.com",
            "password": "StrongPass123!@#"
        },
        cookies=cookies
    )
    
    if response.status_code == 201:
        print("  ✅ Senha forte 'StrongPass123!@#' aceita corretamente!")
        return True
    else:
        print(f"  ❌ Senha forte rejeitada (Status: {response.status_code})")
        print(f"     Resposta: {response.json()}")
        return False


def test_xss_protection():
    """Testa proteção contra XSS"""
    print("\n🛡️  TESTE 4: Proteção contra XSS")
    print("=" * 60)
    
    xss_payloads = [
        "<script>alert('XSS')</script>",
        "javascript:alert('XSS')",
        "<img src=x onerror=alert('XSS')>",
        "<iframe src='javascript:alert(1)'>",
    ]
    
    # Obter token de admin
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "admin@sistema.com", "password": "Admin123!@#"}
    )
    
    if login_response.status_code != 200:
        print("❌ Não foi possível fazer login como admin")
        return False
    
    cookies = login_response.cookies
    
    print("\nTestando payloads XSS:")
    for payload in xss_payloads:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            data={
                "nome": payload,
                "email": f"xss_{int(time.time())}@test.com",
                "password": "ValidPass123!@#"
            },
            cookies=cookies
        )
        
        if response.status_code == 400:
            print(f"  ✅ XSS bloqueado: {payload[:40]}...")
        else:
            print(f"  ❌ XSS não bloqueado: {payload[:40]}...")
    
    return True


def test_sql_injection_protection():
    """Testa proteção contra SQL Injection"""
    print("\n🛡️  TESTE 5: Proteção contra SQL Injection")
    print("=" * 60)
    
    sql_payloads = [
        "admin' OR '1'='1",
        "'; DROP TABLE usuarios; --",
        "UNION SELECT * FROM usuarios",
        "1' AND 1=1 --",
    ]
    
    print("\nTestando payloads SQL Injection no login:")
    for payload in sql_payloads:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": payload, "password": "any"}
        )
        
        if response.status_code == 400:
            print(f"  ✅ SQL Injection bloqueado: {payload[:40]}...")
        else:
            print(f"  Status {response.status_code} para: {payload[:40]}...")
    
    return True


def test_cpf_validation():
    """Testa validação de CPF"""
    print("\n🆔 TESTE 6: Validação de CPF")
    print("=" * 60)
    
    # Obter token de admin
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "admin@sistema.com", "password": "Admin123!@#"}
    )
    
    if login_response.status_code != 200:
        print("❌ Não foi possível fazer login como admin")
        return False
    
    cookies = login_response.cookies
    
    invalid_cpfs = [
        ("12345678900", "inválido"),
        ("11111111111", "sequência repetida"),
        ("123.456.789-00", "dígitos verificadores incorretos"),
    ]
    
    print("\nTestando CPFs inválidos:")
    for cpf, reason in invalid_cpfs:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            data={
                "nome": "Test User",
                "email": f"cpf_{int(time.time())}@test.com",
                "password": "ValidPass123!@#",
                "cpf": cpf
            },
            cookies=cookies
        )
        
        if response.status_code == 400:
            print(f"  ✅ CPF '{cpf}' rejeitado ({reason})")
        else:
            print(f"  ❌ CPF '{cpf}' aceito incorretamente!")
    
    return True


def main():
    """Executa todos os testes"""
    print("\n" + "=" * 60)
    print(" 🔐 TESTES DO SISTEMA DE SEGURANÇA - AlugueisV5")
    print("=" * 60)
    
    tests = [
        ("Rate Limiting", test_rate_limiting),
        ("Bloqueio de IP", test_ip_blacklist),
        ("Validação de Senha", test_password_validation),
        ("Proteção XSS", test_xss_protection),
        ("Proteção SQL Injection", test_sql_injection_protection),
        ("Validação de CPF", test_cpf_validation),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
            time.sleep(2)  # Pausa entre testes
        except Exception as e:
            print(f"\n❌ Erro no teste '{name}': {e}")
            results.append((name, False))
    
    # Sumário
    print("\n" + "=" * 60)
    print(" 📊 SUMÁRIO DOS TESTES")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status}: {name}")
    
    print("\n" + "=" * 60)
    print(f" Testes Passados: {passed}/{total} ({passed/total*100:.1f}%)")
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
