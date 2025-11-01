# 🚀 AlugueisV5 - Início Rápido

## ✅ Status do Projeto

### Implementado (Fase 1 - Completa)
- ✅ Estrutura completa do projeto
- ✅ Configuração Docker (PostgreSQL + FastAPI)
- ✅ Modelos SQLAlchemy (7 tabelas)
- ✅ Sistema de autenticação JWT com cookies
- ✅ Schemas Pydantic para validação
- ✅ Rotas de autenticação (/login, /logout, /register, /me, /refresh)
- ✅ Templates base (login funcional com dark theme)
- ✅ Alembic configurado
- ✅ Script de criação de admin
- ✅ CSS customizado + JS utilities

### Próximos Passos
- ⏳ Testar aplicação base
- ⏳ Criar CRUD de Imóveis
- ⏳ Criar CRUD de Proprietários
- ⏳ Criar sistema de Aluguéis com matriz
- ⏳ Criar sistema de Participações
- ⏳ Implementar importação Excel
- ⏳ Criar dashboard com gráficos

---

## 🏃 Como Executar (Docker)

### 1. Iniciar containers
```bash
cd AlugueisV5
docker-compose up -d
```

### 2. Aguardar banco de dados ficar pronto
```bash
# Verificar logs
docker-compose logs -f db
# Aguarde mensagem: "database system is ready to accept connections"
```

### 3. Executar migrações Alembic
```bash
# Criar migração inicial
docker-compose exec app alembic revision --autogenerate -m "initial migration"

# Aplicar migração
docker-compose exec app alembic upgrade head
```

### 4. Criar usuário admin
```bash
docker-compose exec app python create_admin.py
```

### 5. Acessar aplicação
```
http://localhost:8000
```

**Credenciais padrão:**
- Email: `admin@sistema.com`
- Senha: `admin123`

### 6. Acessar documentação da API
```
http://localhost:8000/docs
```

---

## 🏃 Como Executar (Local - sem Docker)

### 1. Instalar PostgreSQL 15+
```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# Criar banco e usuário
sudo -u postgres psql
CREATE DATABASE alugueis_v5;
CREATE USER alugueis_user WITH PASSWORD 'alugueis_pass_2024';
GRANT ALL PRIVILEGES ON DATABASE alugueis_v5 TO alugueis_user;
\q
```

### 2. Criar ambiente virtual e instalar dependências
```bash
cd AlugueisV5
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente
```bash
cp .env.example .env
# Editar .env com suas credenciais
```

### 4. Executar migrações
```bash
alembic revision --autogenerate -m "initial migration"
alembic upgrade head
```

### 5. Criar admin
```bash
python create_admin.py
```

### 6. Iniciar servidor
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Acessar
```
http://localhost:8000
```

---

## 🧪 Testar Login

### Via Interface Web
1. Acesse `http://localhost:8000`
2. Use: `admin@sistema.com` / `admin123`
3. Deve redirecionar para dashboard (temporário)

### Via cURL
```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sistema.com","password":"admin123"}' \
  -c cookies.txt

# Ver perfil (usando cookies)
curl -X GET http://localhost:8000/api/auth/me \
  -b cookies.txt

# Logout
curl -X POST http://localhost:8000/api/auth/logout \
  -b cookies.txt
```

---

## 🗂️ Estrutura das Tabelas

### 1. **usuarios**
- id, nome, email, hashed_password, cpf, telefone
- is_admin, is_active, created_at, updated_at

### 2. **imoveis**
- id, nome, endereco, cidade, estado, cep
- valor_aluguel, valor_condominio, valor_iptu
- proprietario_id (FK), is_active, timestamps

### 3. **alugueis_mensais**
- id, imovel_id (FK), mes_referencia (YYYY-MM)
- valores: aluguel, condominio, iptu, luz, agua, gas, internet, outros
- valor_total, pago, data_pagamento, observacoes, timestamps

### 4. **participacoes**
- id, imovel_id (FK), proprietario_id (FK)
- mes_referencia, percentual, valor_participacao
- observacoes, timestamps

### 5. **aliases**
- id, nome_alias, usuario_id (FK), timestamps

### 6. **transferencias**
- id, origem_id (FK), destino_id (FK)
- mes_referencia, valor, confirmada, data_confirmacao
- descricao, timestamps

### 7. **permissoes_financeiras**
- id, usuario_id (FK), tipo_permissao
- ativa, descricao, timestamps

---

## 🔧 Comandos Úteis

### Docker
```bash
# Ver logs
docker-compose logs -f app

# Parar containers
docker-compose down

# Rebuild
docker-compose up -d --build

# Acessar shell do container
docker-compose exec app bash

# Limpar tudo
docker-compose down -v  # Remove volumes (cuidado!)
```

### Alembic
```bash
# Criar nova migração
alembic revision --autogenerate -m "descrição"

# Aplicar migrações
alembic upgrade head

# Reverter última migração
alembic downgrade -1

# Ver histórico
alembic history
```

### Desenvolvimento
```bash
# Instalar dependências de desenvolvimento
pip install black flake8 pytest pytest-cov

# Formatar código
black app/

# Executar testes
pytest

# Com cobertura
pytest --cov=app tests/
```

---

## 📚 APIs Disponíveis

### Autenticação
- `POST /api/auth/login` - Login (retorna tokens + define cookies)
- `POST /api/auth/logout` - Logout (limpa cookies)
- `POST /api/auth/refresh` - Renovar token
- `GET /api/auth/me` - Perfil do usuário autenticado
- `POST /api/auth/register` - Registrar novo usuário

### Páginas
- `GET /` - Redireciona para /login
- `GET /login` - Página de login
- `GET /dashboard` - Dashboard (temporário)
- `GET /health` - Health check

---

## 🎨 Design System

### Cores
- **Primary**: #135bec (azul)
- **Background**: #101622 (dark)
- **Cards**: #1e293b (dark gray)
- **Border**: #334155 (gray)
- **Text**: #f6f6f8 (white)

### Fontes
- **Principal**: Manrope (Google Fonts)
- **Ícones**: Material Symbols Outlined

### Framework CSS
- TailwindCSS 3 (CDN)

---

## 🐛 Troubleshooting

### Erro de conexão com banco
```bash
# Verificar se PostgreSQL está rodando
docker-compose ps

# Ver logs do banco
docker-compose logs db

# Recriar containers
docker-compose down
docker-compose up -d
```

### Erro "table already exists"
```bash
# Resetar banco (CUIDADO: deleta dados)
docker-compose down -v
docker-compose up -d
# Aguardar banco iniciar
docker-compose exec app alembic upgrade head
docker-compose exec app python create_admin.py
```

### Erro de importação de módulos
```bash
# Garantir que está no diretório correto
pwd  # Deve mostrar .../AlugueisV5

# Reinstalar dependências
pip install -r requirements.txt
```

---

## 📝 Notas

- **Desenvolvimento**: DEBUG=True, docs em /docs
- **Produção**: Alterar SECRET_KEY, DEBUG=False, usar HTTPS
- **Senha Admin**: Mudar em produção via .env
- **Cookies**: HttpOnly + SameSite=Lax
- **Tokens**: JWT com expiração de 24h (access) e 7 dias (refresh)

---

## 🎯 Checklist de Implementação

### Fase 1 - Base (✅ COMPLETA)
- [x] Estrutura de diretórios
- [x] Docker Compose
- [x] Modelos SQLAlchemy
- [x] Autenticação JWT
- [x] Login funcional
- [x] Alembic + Admin

### Fase 2 - CRUD Básico (⏳ PRÓXIMO)
- [ ] CRUD de Imóveis
- [ ] CRUD de Proprietários
- [ ] Dashboard básico
- [ ] Relatórios simples

### Fase 3 - Recursos Avançados
- [ ] Matriz de Aluguéis
- [ ] Matriz de Participações
- [ ] Importação Excel
- [ ] Gráficos Chart.js
- [ ] Permissões financeiras
- [ ] Transferências

### Fase 4 - Polimento
- [ ] Templates completos
- [ ] Validações client-side
- [ ] Testes completos
- [ ] Deploy scripts
- [ ] Documentação final

---

**Versão**: 5.0.0  
**Data**: 2024  
**Status**: Fase 1 Completa ✅
