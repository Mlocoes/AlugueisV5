# CRUD de Proprietários - Documentação

## 📋 Visão Geral

Sistema completo de gestão de proprietários (pessoas físicas e jurídicas) com interface web, API REST e migração automática de dados.

---

## 🏗️ Arquitetura

### **Modelo de Dados** (`app/models/proprietario.py`)

```python
class Proprietario(Base):
    __tablename__ = "proprietarios"
    
    # Identificação
    id: int (PK)
    tipo_pessoa: str  # "fisica" ou "juridica"
    
    # Pessoa Física
    nome: str (required)
    cpf: str (unique, masked: XXX.XXX.XXX-XX)
    rg: str
    
    # Pessoa Jurídica
    razao_social: str
    nome_fantasia: str
    cnpj: str (unique, masked: XX.XXX.XXX/XXXX-XX)
    inscricao_estadual: str
    
    # Contato
    email: str (indexed)
    telefone: str
    celular: str
    
    # Endereço
    endereco, numero, complemento, bairro
    cidade, estado (UF), cep (XXXXX-XXX)
    
    # Dados Bancários
    banco, agencia, conta
    tipo_conta: str  # "corrente" ou "poupanca"
    pix: str
    
    # Outros
    observacoes: text
    is_active: bool (default: true)
    created_at, updated_at: datetime
```

**Relacionamentos:**
- `1:N` com **Imovel** (`proprietario_id`)

---

## 🔌 API Endpoints

Base URL: `/api/proprietarios`

### 1. **Listar Proprietários**
```http
GET /api/proprietarios/
```

**Query Parameters:**
- `skip` (int): Paginação - offset (default: 0)
- `limit` (int): Paginação - limit (default: 100, max: 100)
- `search` (str): Busca em nome, CPF, CNPJ, email, razão social
- `tipo_pessoa` (str): Filtro por tipo ("fisica" | "juridica")
- `is_active` (bool): Filtro por status (true | false)

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "tipo_pessoa": "fisica",
    "nome": "João Silva",
    "cpf": "123.456.789-00",
    "email": "joao@email.com",
    "telefone": "(11) 1234-5678",
    "celular": "(11) 98765-4321",
    "cidade": "São Paulo",
    "estado": "SP",
    "banco": "Banco do Brasil",
    "pix": "joao@email.com",
    "is_active": true,
    "total_imoveis": 5,
    "created_at": "2025-11-02T10:30:00",
    "updated_at": "2025-11-02T10:30:00"
  }
]
```

---

### 2. **Criar Proprietário**
```http
POST /api/proprietarios/
```

**Body:**
```json
{
  "tipo_pessoa": "fisica",
  "nome": "Maria Santos",
  "cpf": "987.654.321-00",
  "rg": "12.345.678-9",
  "email": "maria@email.com",
  "telefone": "(11) 1111-2222",
  "celular": "(11) 91111-2222",
  "endereco": "Rua das Flores",
  "numero": "123",
  "complemento": "Apto 45",
  "bairro": "Centro",
  "cidade": "São Paulo",
  "estado": "SP",
  "cep": "01234-567",
  "banco": "Itaú",
  "agencia": "1234",
  "conta": "56789-0",
  "tipo_conta": "corrente",
  "pix": "11911112222",
  "observacoes": "Cliente VIP",
  "is_active": true
}
```

**Validações:**
- `tipo_pessoa`: obrigatório, deve ser "fisica" ou "juridica"
- `nome`: obrigatório para PF, 3-200 caracteres
- `razao_social`: obrigatório para PJ
- `cpf`: padrão XXX.XXX.XXX-XX, obrigatório para PF, único
- `cnpj`: padrão XX.XXX.XXX/XXXX-XX, obrigatório para PJ, único
- `estado`: padrão UF (2 letras maiúsculas)
- `cep`: padrão XXXXX-XXX
- `tipo_conta`: "corrente" ou "poupanca"

**Response:** `201 Created`
```json
{
  "id": 4,
  "tipo_pessoa": "fisica",
  "nome": "Maria Santos",
  ...
  "total_imoveis": 0
}
```

**Errors:**
- `400 Bad Request`: CPF/CNPJ duplicado ou validação falhou
- `401 Unauthorized`: Não autenticado

---

### 3. **Obter Proprietário**
```http
GET /api/proprietarios/{id}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  ...
  "total_imoveis": 5
}
```

**Errors:**
- `404 Not Found`: Proprietário não existe

---

### 4. **Atualizar Proprietário**
```http
PUT /api/proprietarios/{id}
```

**Body:** (todos os campos opcionais)
```json
{
  "nome": "João Silva Santos",
  "email": "joao.novo@email.com",
  "is_active": false
}
```

**Response:** `200 OK`

**Errors:**
- `400 Bad Request`: CPF/CNPJ duplicado
- `404 Not Found`: Proprietário não existe

---

### 5. **Deletar Proprietário**
```http
DELETE /api/proprietarios/{id}
```

⚠️ **Apenas Administradores**

**Response:** `204 No Content`

**Errors:**
- `400 Bad Request`: Proprietário possui imóveis vinculados
- `403 Forbidden`: Usuário não é admin
- `404 Not Found`: Proprietário não existe

---

### 6. **Estatísticas**
```http
GET /api/proprietarios/stats/summary
```

**Response:** `200 OK`
```json
{
  "total_proprietarios": 10,
  "ativos": 8,
  "inativos": 2,
  "pessoas_fisicas": 7,
  "pessoas_juridicas": 3
}
```

---

## 🎨 Interface Web

Acesse: **`http://localhost:8000/proprietarios`**

### **Funcionalidades:**

#### 📊 **Estatísticas (5 Cards)**
- Total de proprietários
- Ativos
- Inativos
- Pessoas Físicas
- Pessoas Jurídicas

#### 🔍 **Filtros**
- **Busca:** Nome, CPF, CNPJ, Email, Razão Social
- **Tipo:** Todos / P. Física / P. Jurídica
- **Status:** Todos / Ativos / Inativos

#### 📝 **Tabela**
Colunas:
- Nome/Razão Social (+ nome fantasia para PJ)
- CPF/CNPJ
- Tipo (badge azul/roxo)
- Contato (email, celular ou telefone)
- Nº de Imóveis (badge azul)
- Status (badge verde/cinza)
- Ações (editar/excluir)

#### ➕ **Modal de Cadastro/Edição**

**Seções:**
1. **Tipo de Pessoa** (toggle radio)
   - Pessoa Física → mostra campos: Nome, CPF, RG
   - Pessoa Jurídica → mostra campos: Razão Social, Nome Fantasia, CNPJ, IE

2. **Contato**
   - Email
   - Telefone
   - Celular

3. **Endereço**
   - Endereço
   - Número, Complemento, Bairro
   - Cidade, Estado (UF), CEP

4. **Dados Bancários**
   - Banco, Agência, Conta
   - Tipo de Conta (select)
   - Chave PIX

5. **Observações**
   - Textarea para notas

6. **Status**
   - Checkbox "Proprietário Ativo"

#### ⚙️ **Comportamento Dinâmico**
- **Toggle PF/PJ:** Mostra/esconde campos automaticamente
- **Validação:** Padrões regex para CPF, CNPJ, CEP, UF
- **Máscaras:** Campos formatados (CPF, CNPJ, telefone, CEP)
- **Preview:** Contador de imóveis na tabela
- **Debounce:** Busca com 500ms de delay

---

## 🗄️ Migração de Banco

### **Arquivo:** `alembic/versions/56b513dc45c9_adicionar_tabela_proprietarios.py`

**O que faz:**
1. ✅ Cria tabela `proprietarios`
2. ✅ Cria 5 índices (id, nome, cpf, cnpj, email)
3. ✅ Migra dados de `usuarios` → `proprietarios`
   - Converte usuários não-admin com imóveis em proprietários PF
   - Mantém o mesmo ID para preservar FKs
4. ✅ Atualiza FK `imoveis.proprietario_id`:
   - **Antes:** `usuarios.id`
   - **Depois:** `proprietarios.id`

**Comandos:**
```bash
# Aplicar migração
docker-compose exec app alembic upgrade head

# Reverter (cuidado!)
docker-compose exec app alembic downgrade -1
```

---

## 🧪 Testando

### **1. Via CURL**

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sistema.com","password":"admin123"}' \
  -c cookies.txt

# Listar proprietários
curl -X GET "http://localhost:8000/api/proprietarios/" \
  -b cookies.txt

# Buscar por nome
curl -X GET "http://localhost:8000/api/proprietarios/?search=João" \
  -b cookies.txt

# Filtrar PF ativos
curl -X GET "http://localhost:8000/api/proprietarios/?tipo_pessoa=fisica&is_active=true" \
  -b cookies.txt

# Criar proprietário
curl -X POST http://localhost:8000/api/proprietarios/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "tipo_pessoa": "juridica",
    "nome": "Empresa XYZ",
    "razao_social": "Empresa XYZ Ltda",
    "cnpj": "12.345.678/0001-90",
    "email": "contato@xyz.com",
    "is_active": true
  }'

# Estatísticas
curl -X GET http://localhost:8000/api/proprietarios/stats/summary \
  -b cookies.txt
```

### **2. Via Interface**

1. Acesse: `http://localhost:8000/login`
2. Login: `admin@sistema.com` / `admin123`
3. Navegue para: **Proprietários**
4. Clique em **"Novo Proprietário"**
5. Preencha o formulário:
   - Selecione **Pessoa Física** ou **Jurídica**
   - Preencha campos obrigatórios (*)
   - Opcional: Contato, Endereço, Dados Bancários
6. Clique em **"Salvar"**
7. Teste filtros e busca

---

## 📦 Estrutura de Arquivos

```
AlugueisV5/
├── alembic/
│   └── versions/
│       └── 56b513dc45c9_adicionar_tabela_proprietarios.py  # Migração
├── app/
│   ├── models/
│   │   ├── __init__.py               # Export Proprietario
│   │   └── proprietario.py           # Modelo SQLAlchemy
│   ├── routes/
│   │   └── proprietarios.py          # 7 endpoints REST
│   ├── templates/
│   │   └── proprietarios.html        # Interface completa (920 linhas)
│   └── main.py                       # Registro da rota /proprietarios
└── README_PROPRIETARIOS.md           # Esta documentação
```

---

## 🔐 Permissões

| Ação | Admin | Usuário |
|------|-------|---------|
| Listar | ✅ Todos | ✅ Todos |
| Criar | ✅ | ✅ |
| Editar | ✅ | ✅ |
| Ver Detalhes | ✅ | ✅ |
| Deletar | ✅ | ❌ |
| Estatísticas | ✅ | ✅ |

> **Nota:** Apenas administradores podem deletar proprietários, e apenas se não houver imóveis vinculados.

---

## 🎯 Próximos Passos

- [ ] Atualizar CRUD de **Imóveis** para usar `Proprietario` em vez de `Usuario`
- [ ] Implementar **validação de CPF/CNPJ** (algoritmo dígito verificador)
- [ ] Adicionar **máscaras automáticas** nos inputs (JavaScript)
- [ ] Criar **relatório de proprietários** (PDF/Excel export)
- [ ] Implementar **importação em massa** via CSV/Excel
- [ ] Adicionar **foto/logo** do proprietário
- [ ] Criar **histórico de alterações** (audit log)

---

## 🐛 Troubleshooting

### Erro: "CPF/CNPJ já cadastrado"
**Solução:** Verifique se não há duplicatas no banco.
```sql
SELECT cpf, COUNT(*) FROM proprietarios GROUP BY cpf HAVING COUNT(*) > 1;
SELECT cnpj, COUNT(*) FROM proprietarios GROUP BY cnpj HAVING COUNT(*) > 1;
```

### Erro: "Não é possível deletar proprietário com X imóvel(is)"
**Solução:** Primeiro delete ou reatribua os imóveis vinculados.

### Erro: "Internal Server Error" após migração
**Solução:** Restart o container app:
```bash
docker-compose restart app
```

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs: `docker-compose logs app`
2. Consulte a documentação da API: `http://localhost:8000/docs`
3. Teste endpoints com curl ou Postman

---

**Versão:** 1.0  
**Última Atualização:** 02/11/2025  
**Autor:** Sistema AlugueisV5
