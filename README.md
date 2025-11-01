# 🏢 AlugueisV5 - Sistema de Gestão de Aluguéis

Sistema completo de gestão de imóveis e aluguéis com controle de participações, permissões financeiras e relatórios detalhados. Desenvolvido com FastAPI, PostgreSQL e design moderno dark theme.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Características Principais](#-características-principais)
- [Stack Tecnológico](#-stack-tecnológico)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Instalação](#-instalação)
- [Uso](#-uso)
- [Funcionalidades](#-funcionalidades)
- [API](#-api)
- [Capturas de Tela](#-capturas-de-tela)
- [Contribuindo](#-contribuindo)

---

## 🎯 Visão Geral

O **AlugueisV5** é uma aplicação web moderna para gestão completa de propriedades imobiliárias, permitindo:

- 📊 **Dashboard** com métricas em tempo real (receita mensal, anual, variação e disponibilidade)
- 👥 **Gestão de Proprietários** com controle de participações
- 🏠 **Gestão de Imóveis** com status e informações detalhadas
- 💰 **Visualização Matricial de Aluguéis** - inovador grid imóveis × proprietários
- 📈 **Relatórios Personalizados** com exportação para Excel
- 🔒 **Controle de Permissões Financeiras** granular por usuário
- 📥 **Importação de Excel** em lote (proprietários, imóveis, participações, aluguéis)
- 🎨 **Dark Theme Moderno** com Material Symbols

---

## ✨ Características Principais

### 🔐 Autenticação e Segurança
- Sistema de login com JWT (JSON Web Tokens)
- Senhas criptografadas com bcrypt
- Controle de acesso baseado em roles (Administrador/Usuário)
- Permissões financeiras configuráveis por usuário

### 📊 Visualizações Inovadoras
- **Matriz de Aluguéis**: Tabela cruzada mostrando valores por imóvel e proprietário
- **Matriz de Participações**: Percentuais de participação editáveis
- **Gráficos Interativos**: Chart.js com barras, donut e tendências

### 💼 Gestão Completa
- CRUD completo de Proprietários e Imóveis
- Sistema de Alias para agrupar proprietários
- Transferências financeiras entre proprietários
- Histórico de participações por data

### 📱 Responsivo e Moderno
- Mobile-first design
- Bottom navigation bar
- Sticky columns em tabelas
- Dark theme completo

---

## 🛠 Stack Tecnológico

### Backend
- **Python 3.11+**
- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy 2.0** - ORM para Python
- **PostgreSQL 15+** - Banco de dados relacional
- **Alembic** - Migrações de banco de dados
- **Pydantic** - Validação de dados
- **PyJWT** - Autenticação JWT
- **Passlib** - Criptografia de senhas
- **Pandas** - Processamento de Excel
- **Uvicorn** - Servidor ASGI

### Frontend
- **HTML5 + Jinja2** - Templates dinâmicos
- **TailwindCSS** - Framework CSS utility-first
- **JavaScript Vanilla** - Sem frameworks pesados
- **Chart.js** - Gráficos interativos
- **Handsontable** - Tabelas editáveis tipo Excel
- **Material Symbols** - Ícones do Google

### DevOps
- **Docker & Docker Compose** - Containerização
- **PostgreSQL Container** - Banco isolado
- **Nginx** (opcional) - Proxy reverso

---

## 📁 Estrutura do Projeto

```
AlugueisV5/
├── app/
│   ├── main.py                     # Aplicação FastAPI principal
│   ├── core/
│   │   ├── auth.py                 # Sistema de autenticação JWT
│   │   ├── config.py               # Configurações da aplicação
│   │   ├── database.py             # Conexão com PostgreSQL
│   │   └── permissions.py          # Controle de permissões
│   ├── models/
│   │   ├── __init__.py
│   │   ├── usuario.py              # Modelo de Usuário/Proprietário
│   │   ├── imovel.py               # Modelo de Imóvel
│   │   ├── participacao.py         # Modelo de Participações
│   │   ├── aluguel.py              # Modelo de Aluguéis Mensais
│   │   ├── alias.py                # Modelo de Alias (grupos)
│   │   ├── transferencia.py        # Modelo de Transferências
│   │   └── permissao_financeira.py # Modelo de Permissões
│   ├── routes/
│   │   ├── auth.py                 # Rotas de autenticação
│   │   ├── dashboard.py            # Rotas do dashboard
│   │   ├── usuarios.py             # CRUD de usuários
│   │   ├── imoveis.py              # CRUD de imóveis
│   │   ├── participacoes.py        # Gestão de participações
│   │   ├── alugueis.py             # Gestão de aluguéis + matriz
│   │   ├── relatorios.py           # Relatórios e exportação
│   │   ├── permissoes_financeiras.py # Gestão de permissões
│   │   └── import_routes.py        # Importação de Excel
│   ├── schemas/
│   │   └── __init__.py             # Schemas Pydantic
│   ├── services/
│   │   ├── aluguel_service.py      # Lógica de negócio de aluguéis
│   │   ├── import_service.py       # Processamento de Excel
│   │   └── participacao_service.py # Validação de participações
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css           # Estilos customizados
│   │   └── js/
│   │       ├── main.js             # Funções JS globais
│   │       ├── dashboard.js        # Lógica do dashboard
│   │       ├── visualizar_alugueis.js # Matriz de aluguéis
│   │       └── handsontable_config.js # Config de tabelas
│   └── templates/
│       ├── base.html               # Template base
│       ├── login.html              # Tela de login
│       ├── dashboard.html          # Dashboard principal
│       ├── proprietarios.html      # Gestão de proprietários
│       ├── imoveis.html            # Gestão de imóveis
│       ├── participacoes.html      # Matriz de participações
│       ├── visualizar_alugueis.html # Matriz de aluguéis (NOVO)
│       ├── relatorios.html         # Relatórios
│       └── administracao.html      # Painel admin
├── alembic/
│   ├── versions/                   # Migrações do banco
│   └── env.py                      # Config do Alembic
├── tests/
│   └── test_*.py                   # Testes unitários
├── docker-compose.yml              # Orquestração de containers
├── Dockerfile                      # Build da aplicação
├── requirements.txt                # Dependências Python
├── alembic.ini                     # Configuração Alembic
├── .env.example                    # Variáveis de ambiente
├── .gitignore
└── README.md
```

---

## 🚀 Instalação

### Pré-requisitos

- **Docker** e **Docker Compose** instalados
- **Python 3.11+** (para desenvolvimento local)
- **PostgreSQL 15+** (se não usar Docker)

### Opção 1: Com Docker (Recomendado)

```bash
# 1. Clone o repositório
git clone https://github.com/Mlocoes/AlugueisV5.git
cd AlugueisV5

# 2. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas configurações

# 3. Inicie os containers
docker-compose up -d

# 4. Execute as migrações
docker-compose exec app alembic upgrade head

# 5. Acesse a aplicação
# http://localhost:8000
```

### Opção 2: Instalação Local

```bash
# 1. Clone o repositório
git clone https://github.com/Mlocoes/AlugueisV5.git
cd AlugueisV5

# 2. Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure o banco de dados PostgreSQL
# Edite o .env com suas credenciais

# 5. Execute as migrações
alembic upgrade head

# 6. Inicie o servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📖 Uso

### Primeiro Acesso

1. Acesse `http://localhost:8000/login`
2. Use as credenciais padrão (criadas automaticamente):
   - **Email**: admin@sistema.com
   - **Senha**: admin123

3. ⚠️ **IMPORTANTE**: Altere a senha padrão em "Administração > Meu Perfil"

### Fluxo Básico de Uso

#### 1️⃣ Cadastrar Proprietários
- Acesse **"Proprietários"** no menu
- Clique em **"+ Cadastrar"**
- Preencha: Nome, Email, Telefone, Documento
- Salve

#### 2️⃣ Cadastrar Imóveis
- Acesse **"Imóveis"** no menu
- Clique em **"+ Cadastrar"**
- Preencha: Nome, Endereço, Tipo, Status
- Salve

#### 3️⃣ Definir Participações
- Acesse **"Participações"** no menu
- Visualize a matriz: Imóveis (linhas) × Proprietários (colunas)
- Clique em **"Editar"** em um imóvel
- Defina os percentuais (soma deve ser 100%)
- Salve

#### 4️⃣ Registrar Aluguéis
- Acesse **"Aluguéis"** no menu
- Selecione **Ano** e **Mês**
- Visualize a matriz de valores
- Clique em uma célula para editar
- Salve

#### 5️⃣ Gerar Relatórios
- Acesse **"Relatórios"** no menu
- Selecione filtros (ano, mês, proprietário)
- Clique em **"Exportar para Excel"**

---

## 🎨 Funcionalidades

### 🏠 Dashboard
- **Receita Mensal**: Valor total do último mês
- **Receita no Ano**: Acumulado do ano vigente
- **Variação Mensal**: Percentual de variação mês a mês
- **Imóveis Disponíveis**: Quantidade de imóveis livres
- **Gráfico de Receitas**: Barras com últimos 12 meses
- **Gráfico de Status**: Donut com imóveis alugados vs. disponíveis

### 👥 Gestão de Proprietários
- Listagem com filtros e busca
- Cadastro, edição e exclusão (admin)
- Visualização de informações completas
- Exportação para Excel

### 🏢 Gestão de Imóveis
- Listagem com status visual (Disponível/Alugado/Manutenção)
- Cadastro, edição e exclusão (admin)
- Campos: Nome, Endereço, Tipo, Área, Valores, IPTU
- Exportação para Excel

### 📊 Matriz de Participações
- Tabela imóveis × proprietários
- Células editáveis com percentuais
- Validação automática (soma = 100%)
- Histórico de versões por data

### 💰 Matriz de Aluguéis (NOVO!)
- Visualização cruzada imóveis × proprietários
- Mostra valor monetário por célula
- Filtros de ano e mês
- Células clicáveis para edição
- Sticky columns (primeira coluna fixa)
- Scroll horizontal suave

### 📈 Relatórios
- Filtros: Ano, Mês, Proprietário/Alias
- Colunas: Aluguel, DARF, Taxa de Administração
- Opção "Incluir Transferências"
- Exportação para Excel formatado

### 🔐 Permissões Financeiras
- Administradores definem o que cada usuário vê
- Controle por proprietário
- Usuários veem apenas dados autorizados
- Logs de acesso (futuro)

### 📥 Importação de Excel
- Upload de múltiplos arquivos
- Suporta:
  - **Proprietario.xlsx**: Nome, Documento, Email, etc.
  - **Imoveis.xlsx**: Nome, Endereço, Valores, etc.
  - **Participacao.xlsx**: Matriz de percentuais
  - **Aluguel.xlsx**: Múltiplas planilhas (uma por mês)
- Validação automática
- Preview antes de importar
- Relatório de erros/avisos

---

## 🔌 API

### Autenticação

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "senha123"
}

Response: {
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Dashboard

```http
GET /api/dashboard/stats
Authorization: Bearer {token}

Response: {
  "receita_mensal": 15750.00,
  "receita_anual": 180200.00,
  "variacao_mensal": 5.2,
  "imoveis_disponiveis": 8
}
```

### Matriz de Aluguéis (NOVO)

```http
GET /api/alugueis/matriz?ano=2024&mes=10
Authorization: Bearer {token}

Response: {
  "ano": 2024,
  "mes": 10,
  "imoveis": [
    {"id": 1, "nome": "Apto 101", "endereco": "Rua das Flores, 123"}
  ],
  "proprietarios": [
    {"id": 3, "nome": "João Silva"},
    {"id": 4, "nome": "Maria Souza"}
  ],
  "matriz": {
    "1": {
      "3": 1500.00,
      "4": null
    }
  }
}
```

### Exportar Relatório

```http
GET /api/relatorios/exportar?ano=2024&mes=10&formato=excel
Authorization: Bearer {token}

Response: [Excel file download]
```

---

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Com cobertura
pytest --cov=app tests/

# Testes específicos
pytest tests/test_auth.py
```

---

## 📝 Variáveis de Ambiente

Crie um arquivo `.env` com:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/alugueisv5

# Security
SECRET_KEY=sua-chave-secreta-super-segura-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Admin
ADMIN_EMAIL=admin@sistema.com
ADMIN_PASSWORD=admin123

# App
DEBUG=False
APP_NAME=AlugueisV5
```

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👨‍💻 Autor

**Manuel Loco**
- GitHub: [@Mlocoes](https://github.com/Mlocoes)
- Email: mcozzolinoes@gmail.com

---

## 🙏 Agradecimentos

- FastAPI pela incrível documentação
- Comunidade Python
- Google Material Symbols
- Handsontable
- Chart.js

---

## 📚 Documentação Adicional

- [Guia de Importação Excel](docs/IMPORT_GUIDE.md)
- [API Reference](docs/API.md)
- [Guia de Deploy](docs/DEPLOY.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

---

## 🗺️ Roadmap

- [x] Sistema de autenticação JWT
- [x] CRUD completo de Proprietários e Imóveis
- [x] Matriz de Participações
- [x] Dashboard com métricas
- [x] Importação de Excel
- [ ] **Matriz de Aluguéis (Em Desenvolvimento)**
- [ ] Dark theme completo com Material Symbols
- [ ] Bottom navigation bar responsiva
- [ ] Notificações por email
- [ ] Histórico de mudanças (audit log)
- [ ] App mobile (React Native)
- [ ] Integração com bancos (Open Banking)

---

**⭐ Se este projeto te ajudou, considere dar uma estrela no GitHub!**

