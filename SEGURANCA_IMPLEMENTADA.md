# 🔒 Sistema de Segurança - AlugueisV5

## 📋 Visão Geral

Implementação completa de **Rate Limiting** e **Validações Robustas** para proteger o sistema contra ataques comuns de segurança web.

**Status**: ✅ Implementado e Testado  
**Data**: 3 de Novembro de 2025  
**Versão**: 5.1.0  
**Prioridade**: Alta (Segurança Crítica)

---

## 🎯 Objetivos Alcançados

Conforme **relatorio_analise.md seção 1.3**:
- ✅ Implementar rate limiting para prevenir força bruta
- ✅ Validação robusta de entrada em todos os endpoints sensíveis
- ✅ Proteção contra XSS (Cross-Site Scripting)
- ✅ Proteção contra SQL Injection
- ✅ Sistema de blacklist temporária para IPs suspeitos
- ✅ Logs de segurança detalhados

---

## 🛡️ Proteções Implementadas

### 1. Rate Limiting (Limitação de Taxa)

**Arquivo**: `app/core/rate_limiter.py`

Implementado com **slowapi** para limitar número de requisições por IP:

| Endpoint | Limite | Descrição |
|----------|--------|-----------|
| `/api/auth/login` | 5 req/min | Autenticação (muito restritivo) |
| `/api/auth/register` | 5 req/min | Registro de usuários (muito restritivo) |
| `/api/auth/refresh` | 10 req/min | Renovação de token (moderado) |
| APIs padrão | 30 req/min | Endpoints normais |
| APIs leitura | 60 req/min | Apenas consultas |

**Exemplo de uso:**
```python
@router.post("/login")
@limiter.limit(get_rate_limit("auth_strict"))
async def login(request: Request, credentials: LoginRequest):
    # Máximo 5 tentativas por minuto
    ...
```

**Resposta ao exceder limite:**
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please slow down and try again later.",
  "retry_after": "42"
}
```

---

### 2. Blacklist Temporária de IPs

**Classe**: `IPBlacklist` em `app/core/rate_limiter.py`

Sistema automático de bloqueio de IPs após tentativas falhas:

- **5 tentativas falhas** → IP bloqueado por **15 minutos**
- Janela de detecção: 5 minutos
- Logs detalhados de todas as tentativas
- Desbloqueio automático após tempo expirar

**Fluxo:**
1. Usuário erra senha → Tentativa registrada
2. Após 5 erros em 5 min → IP bloqueado
3. Novas requisições → HTTP 429 (Too Many Requests)
4. Após 15 min → Desbloqueio automático

**Exemplo de log:**
```
2025-11-03 15:30:12 - security - WARNING - Failed login attempt from 192.168.1.100 on /api/auth/login. Total attempts: 3
2025-11-03 15:30:45 - security - ERROR - IP 192.168.1.100 has been BLOCKED for 900s due to excessive failed attempts
```

---

### 3. Validações Robustas

**Arquivo**: `app/core/validators.py`

Classe `InputValidator` com métodos de validação:

#### 3.1. Email
```python
validator.validate_email_address("user@example.com")
# Usa biblioteca email-validator
# Valida formato, domínio, normaliza email
```

#### 3.2. Senha Forte
```python
validator.validate_password("MyP@ssw0rd123")
# Requisitos:
# - Mínimo 8 caracteres
# - Pelo menos 1 maiúscula
# - Pelo menos 1 minúscula
# - Pelo menos 1 número
# - Pelo menos 1 caractere especial (!@#$%^&*...)
```

#### 3.3. CPF com Dígitos Verificadores
```python
validator.validate_cpf("123.456.789-09")
# Remove formatação
# Valida 11 dígitos
# Verifica dígitos verificadores
# Rejeita sequências repetidas (111.111.111-11)
```

#### 3.4. CNPJ
```python
validator.validate_cnpj("12.345.678/0001-90")
# Valida 14 dígitos
# Remove formatação
# Rejeita sequências repetidas
```

#### 3.5. Telefone Brasileiro
```python
validator.validate_phone("(11) 98765-4321")
# Remove formatação
# Valida 10 ou 11 dígitos
```

---

### 4. Proteção contra XSS

**Método**: `InputValidator.sanitize_string()`

Detecta e bloqueia padrões perigosos:

| Padrão | Exemplo |
|--------|---------|
| `<script>` tags | `<script>alert('XSS')</script>` |
| `javascript:` | `javascript:alert(1)` |
| Event handlers | `<img onerror="alert(1)">` |
| `<iframe>` | `<iframe src="evil.com">` |
| `<object>`, `<embed>` | Tags de embedding |

**Exemplo:**
```python
# Entrada maliciosa
nome = "<script>alert('XSS')</script>"

# Validação
validator.sanitize_string(nome)
# ❌ HTTPException: "Conteúdo potencialmente perigoso detectado"
```

---

### 5. Proteção contra SQL Injection

**Método**: `InputValidator.sanitize_string()`

Detecta padrões de SQL Injection:

| Padrão | Exemplo |
|--------|---------|
| UNION SELECT | `' UNION SELECT * FROM usuarios --` |
| OR 1=1 | `admin' OR 1=1 --` |
| Comentários SQL | `--`, `/*`, `*/` |
| DROP TABLE | `'; DROP TABLE usuarios; --` |

**Exemplo:**
```python
# Entrada maliciosa
email = "admin' OR '1'='1"

# Validação
validator.sanitize_string(email)
# ❌ HTTPException: "Conteúdo potencialmente perigoso detectado"
```

---

### 6. Logs de Segurança

**Arquivo**: `logs/security.log`

Logger específico registra todos os eventos de segurança:

```python
from app.core.rate_limiter import security_logger

# Login bem-sucedido
security_logger.info(f"Successful login for user {email} from IP {ip}")

# Tentativa falha
security_logger.warning(f"Failed login attempt for email {email} from IP {ip}")

# IP bloqueado
security_logger.error(f"IP {ip} has been BLOCKED for {duration}s")

# XSS detectado
security_logger.warning(f"XSS attempt detected: {text[:100]}")

# SQL Injection detectado
security_logger.warning(f"SQL Injection attempt detected: {text[:100]}")
```

**Exemplo de logs:**
```
2025-11-03 15:30:12 - security - WARNING - Failed login attempt for email hacker@test.com from IP 192.168.1.100
2025-11-03 15:30:15 - security - ERROR - IP 192.168.1.100 has been BLOCKED for 900s due to excessive failed attempts
2025-11-03 15:32:00 - security - WARNING - XSS attempt detected: <script>alert('XSS')</script>
2025-11-03 15:33:00 - security - WARNING - SQL Injection attempt detected: admin' OR '1'='1
2025-11-03 15:35:00 - security - INFO - Successful login for user admin@sistema.com (ID: 1) from IP 192.168.1.50
2025-11-03 15:36:00 - security - INFO - New user test@example.com (ID: 5) successfully registered by admin admin@sistema.com
2025-11-03 15:37:00 - security - INFO - User admin@sistema.com (ID: 1) logged out
```

---

## 🧪 Testes

**Arquivo**: `test_security.py`

Script executável com 6 baterias de testes automatizados:

### Executar Testes

```bash
python test_security.py
```

### Testes Incluídos

| # | Teste | Descrição |
|---|-------|-----------|
| 1 | Rate Limiting | Tenta 10 requisições, verifica bloqueio na 6ª |
| 2 | Bloqueio de IP | 5 tentativas falhas → IP bloqueado |
| 3 | Validação de Senha | Testa senhas fracas e fortes |
| 4 | Proteção XSS | Testa payloads XSS em campos de texto |
| 5 | Proteção SQL Injection | Testa payloads SQL no login |
| 6 | Validação CPF | Testa CPFs inválidos e válidos |

### Resultado Esperado

```
============================================================
 🔐 TESTES DO SISTEMA DE SEGURANÇA - AlugueisV5
============================================================

✅ PASSOU: Rate Limiting
✅ PASSOU: Bloqueio de IP
✅ PASSOU: Validação de Senha
✅ PASSOU: Proteção XSS
✅ PASSOU: Proteção SQL Injection
✅ PASSOU: Validação de CPF

============================================================
 Testes Passados: 6/6 (100.0%)
============================================================
```

---

## 📊 Impacto

### Antes (v5.0.0)
- ❌ Sem rate limiting → Vulnerável a força bruta
- ❌ Senhas fracas aceitas → Contas facilmente comprometidas
- ❌ Sem sanitização → Vulnerável a XSS e SQL Injection
- ❌ Sem logs de segurança → Ataques não detectados

### Depois (v5.1.0)
- ✅ Rate limiting ativo → Força bruta bloqueada automaticamente
- ✅ Senhas fortes obrigatórias → Contas mais seguras
- ✅ Sanitização completa → XSS e SQL Injection bloqueados
- ✅ Logs detalhados → Todos os eventos de segurança registrados

---

## 🔧 Configuração

### Variáveis de Ambiente

Nenhuma configuração adicional necessária. O sistema usa configurações seguras por padrão.

### Ajustar Limites

Edite `app/core/rate_limiter.py`:

```python
RATE_LIMITS = {
    "auth_strict": "5/minute",      # Login, registro
    "auth_moderate": "10/minute",   # Refresh token
    "api_standard": "30/minute",    # APIs normais
    "api_read": "60/minute",        # Apenas leitura
}
```

### Ajustar Blacklist

Edite `app/core/rate_limiter.py` na classe `IPBlacklist`:

```python
self.MAX_ATTEMPTS = 5          # Tentativas antes de bloquear
self.ATTEMPT_WINDOW = 300      # Janela de tempo (5 min)
self.BLACKLIST_DURATION = 900  # Duração do bloqueio (15 min)
```

---

## 📝 Arquivos Criados/Modificados

### Novos Arquivos
- `app/core/rate_limiter.py` - Sistema de rate limiting e blacklist
- `app/core/validators.py` - Validações robustas de entrada
- `test_security.py` - Script de testes de segurança
- `logs/.gitignore` - Ignora arquivos .log no git

### Arquivos Modificados
- `app/main.py` - Integração do rate limiter
- `app/routes/auth.py` - Aplicação de validações e rate limits
- `requirements.txt` - Adicionado slowapi==0.1.9

---

## 🚀 Próximos Passos (Futuro)

- [ ] Rate limiting com Redis (para múltiplos servidores)
- [ ] Autenticação 2FA (Two-Factor Authentication)
- [ ] CAPTCHA após 3 tentativas falhas
- [ ] Notificações por email de atividades suspeitas
- [ ] Dashboard de segurança com métricas
- [ ] Integração com SIEM (Security Information and Event Management)
- [ ] Análise de padrões com Machine Learning
- [ ] Honeypot endpoints para detectar bots

---

## 📚 Referências

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [SlowAPI Documentation](https://slowapi.readthedocs.io/)
- [Email Validator](https://github.com/JoshData/python-email-validator)
- **relatorio_analise.md** - Seção 1.3 (Análise de Vulnerabilidades)

---

## ✅ Checklist de Implementação

- [x] Instalar slowapi
- [x] Criar rate_limiter.py
- [x] Criar validators.py
- [x] Integrar em main.py
- [x] Aplicar em endpoints de auth
- [x] Implementar blacklist de IPs
- [x] Configurar logs de segurança
- [x] Criar testes automatizados
- [x] Documentar sistema
- [x] Testar em produção
- [x] Commit e push para repositório

---

**⚠️ IMPORTANTE**: Este sistema protege contra os ataques mais comuns, mas segurança é um processo contínuo. Sempre mantenha as dependências atualizadas e monitore os logs regularmente.

**✅ Status Final**: Sistema de segurança implementado e testado com sucesso! 🔒
