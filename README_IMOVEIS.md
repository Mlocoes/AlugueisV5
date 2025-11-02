# CRUD de Imóveis - Documentação

## 📋 Visão Geral

Sistema completo de gestão de imóveis com interface web, API REST e integração com Proprietários. Permite cadastrar, editar e gerenciar propriedades com informações de endereço, valores e status.

---

## 🏗️ Arquitetura

### **Modelo de Dados** (`app/models/imovel.py`)

```python
class Imovel(Base):
    __tablename__ = "imoveis"
    
    # Identificação
    id: int (PK)
    nome: str (required, indexed)  # Ex: "Apartamento Centro"
    
    # Endereço
    endereco: str
    cidade: str
    estado: str (UF - 2 caracteres)
    cep: str (XXXXX-XXX)
    
    # Dados Financeiros
    valor_aluguel: float
    valor_condominio: float
    valor_iptu: float
    
    # Relacionamento
    proprietario_id: int (FK -> proprietarios.id, required, indexed)
    
    # Status
    is_active: bool (default: true)
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
```

**Relacionamentos:**
- `N:1` com **Proprietario** (`proprietario_id`)
- `1:N` com **AluguelMensal** (`alugueis`)
- `1:N` com **Participacao** (`participacoes`)

---

## 🔌 API Endpoints

Base URL: `/api/imoveis`

### 1. **Listar Imóveis**
```http
GET /api/imoveis/
```

**Query Parameters:**
- `skip` (int): Paginação - offset (default: 0)
- `limit` (int): Paginação - limit (default: 100, max: 1000)
- `search` (str): Busca em nome, endereço, cidade
- `proprietario_id` (int): Filtro por proprietário
- `is_active` (bool): Filtro por status (true | false)

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "nome": "Apartamento Centro",
    "endereco": "Rua Principal, 123",
    "cidade": "São Paulo",
    "estado": "SP",
    "cep": "01234-567",
    "valor_aluguel": 2500.00,
    "valor_condominio": 450.00,
    "valor_iptu": 150.00,
    "proprietario_id": 2,
    "is_active": true,
    "created_at": "2025-11-01T10:30:00",
    "updated_at": "2025-11-01T10:30:00"
  }
]
```

**Permissões:**
- ✅ Todos os usuários autenticados podem ver todos os imóveis

---

### 2. **Criar Imóvel**
```http
POST /api/imoveis/
```

**Body:**
```json
{
  "nome": "Casa Jardim Europa",
  "proprietario_id": 2,
  "endereco": "Av. Europa, 456",
  "cidade": "São Paulo",
  "estado": "SP",
  "cep": "05432-100",
  "valor_aluguel": 5000.00,
  "valor_condominio": 800.00,
  "valor_iptu": 300.00,
  "is_active": true
}
```

**Validações:**
- `nome`: obrigatório, 3-200 caracteres
- `proprietario_id`: obrigatório, deve existir na tabela `proprietarios`
- `estado`: opcional, padrão UF (2 letras maiúsculas)
- `cep`: opcional, padrão XXXXX-XXX
- `valor_aluguel`, `valor_condominio`, `valor_iptu`: opcional, números >= 0

**Response:** `201 Created`
```json
{
  "id": 7,
  "nome": "Casa Jardim Europa",
  ...
}
```

**Errors:**
- `404 Not Found`: Proprietário não encontrado
- `401 Unauthorized`: Não autenticado

**Permissões:**
- ✅ Todos os usuários autenticados podem criar imóveis

---

### 3. **Obter Imóvel**
```http
GET /api/imoveis/{id}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "nome": "Apartamento Centro",
  ...
}
```

**Errors:**
- `404 Not Found`: Imóvel não existe

**Permissões:**
- ✅ Todos os usuários autenticados podem ver qualquer imóvel

---

### 4. **Atualizar Imóvel**
```http
PUT /api/imoveis/{id}
```

**Body:** (todos os campos opcionais)
```json
{
  "nome": "Apartamento Centro - Renovado",
  "valor_aluguel": 2800.00,
  "is_active": true
}
```

**Response:** `200 OK`

**Errors:**
- `404 Not Found`: Imóvel não existe

**Permissões:**
- ✅ Todos os usuários autenticados podem editar qualquer imóvel

---

### 5. **Deletar Imóvel**
```http
DELETE /api/imoveis/{id}
```

⚠️ **Apenas Administradores** | **Soft Delete** (marca como inativo)

**Response:** `204 No Content`

**Errors:**
- `403 Forbidden`: Usuário não é admin
- `404 Not Found`: Imóvel não existe

**Permissões:**
- ❌ Apenas administradores podem deletar imóveis

---

### 6. **Estatísticas**
```http
GET /api/imoveis/stats/summary
```

**Response:** `200 OK`
```json
{
  "total": 6,
  "ativos": 5,
  "inativos": 1,
  "valor_total_alugueis": 24900.00
}
```

**Cálculos:**
- `total`: Total de imóveis no banco
- `ativos`: Imóveis com `is_active = true`
- `inativos`: Imóveis com `is_active = false`
- `valor_total_alugueis`: Soma dos `valor_aluguel` de imóveis ativos

---

### 7. **Listar Proprietários (para Select)**
```http
GET /api/imoveis/proprietarios/list
```

**Response:** `200 OK`
```json
[
  {
    "id": 2,
    "nome": "João Silva",
    "tipo_pessoa": "fisica",
    "cpf_cnpj": "123.456.789-00"
  },
  {
    "id": 3,
    "nome": "Empresa XYZ Ltda",
    "tipo_pessoa": "juridica",
    "cpf_cnpj": "12.345.678/0001-90"
  }
]
```

**Filtros:**
- Apenas proprietários ativos (`is_active = true`)
- Ordenados por nome

**Uso:**
- Endpoint auxiliar para popular select de proprietários na interface

---

## 🎨 Interface Web

Acesse: **`http://localhost:8000/imoveis`**

### **Funcionalidades:**

#### 📊 **Estatísticas (4 Cards)**
- Total de imóveis
- Ativos
- Inativos
- Valor Total de Aluguéis (R$)

#### 🔍 **Filtros**
- **Busca:** Nome, endereço, cidade
- **Proprietário:** Select dinâmico (carregado via API)
- **Status:** Todos / Ativos / Inativos

#### 📝 **Tabela**
Colunas:
- Nome do imóvel
- Endereço completo (endereço, cidade, estado)
- Proprietário (lookup via mapa)
- Aluguel (formatado em R$)
- Status (badge verde/cinza)
- Ações (editar/excluir)

#### ➕ **Modal de Cadastro/Edição**

**Seções:**
1. **Dados Básicos**
   - Nome do imóvel *
   - Proprietário * (select dinâmico)

2. **Endereço**
   - Endereço
   - Cidade
   - Estado (UF, uppercase automático)
   - CEP (máscara XXXXX-XXX)

3. **Valores Mensais**
   - Aluguel (R$)
   - Condomínio (R$)
   - IPTU (R$)

4. **Status**
   - Checkbox "Imóvel Ativo"

#### ⚙️ **Comportamento Dinâmico**
- **Lookup de Proprietários:** Carregamento único no início, armazenado em `proprietariosMap{}` para performance
- **Debounce:** Busca com 500ms de delay
- **Formatação:** Valores em R$ com 2 casas decimais
- **Validação:** Estado em maiúsculas automaticamente

---

## 🧪 Testando

### **1. Via CURL**

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sistema.com","password":"admin123"}' \
  -c cookies.txt

# Listar imóveis
curl -X GET "http://localhost:8000/api/imoveis/" \
  -b cookies.txt

# Buscar por cidade
curl -X GET "http://localhost:8000/api/imoveis/?search=São Paulo" \
  -b cookies.txt

# Filtrar por proprietário
curl -X GET "http://localhost:8000/api/imoveis/?proprietario_id=2" \
  -b cookies.txt

# Listar proprietários para select
curl -X GET "http://localhost:8000/api/imoveis/proprietarios/list" \
  -b cookies.txt

# Criar imóvel
curl -X POST http://localhost:8000/api/imoveis/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "nome": "Cobertura Morumbi",
    "proprietario_id": 2,
    "endereco": "Av. Morumbi, 789",
    "cidade": "São Paulo",
    "estado": "SP",
    "cep": "05650-000",
    "valor_aluguel": 8000.00,
    "valor_condominio": 1500.00,
    "valor_iptu": 600.00,
    "is_active": true
  }'

# Atualizar imóvel
curl -X PUT http://localhost:8000/api/imoveis/1 \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "valor_aluguel": 2800.00
  }'

# Estatísticas
curl -X GET http://localhost:8000/api/imoveis/stats/summary \
  -b cookies.txt
```

### **2. Via Interface**

1. Acesse: `http://localhost:8000/login`
2. Login: `admin@sistema.com` / `admin123`
3. Navegue para: **Imóveis**
4. Clique em **"Novo Imóvel"**
5. Preencha o formulário:
   - Nome: "Apartamento Vila Madalena"
   - Proprietário: Selecione da lista
   - Endereço completo (opcional)
   - Valores (aluguel obrigatório)
6. Clique em **"Salvar"**
7. Teste filtros:
   - Busque por "Vila"
   - Filtre por proprietário específico
   - Filtre apenas ativos

---

## 📦 Estrutura de Arquivos

```
AlugueisV5/
├── app/
│   ├── models/
│   │   └── imovel.py                 # Modelo SQLAlchemy
│   ├── routes/
│   │   └── imoveis.py                # 8 endpoints REST
│   ├── templates/
│   │   └── imoveis.html              # Interface completa (560 linhas)
│   └── main.py                       # Registro da rota /imoveis
└── README_IMOVEIS.md                 # Esta documentação
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

> **Nota:** Sistema tem permissões abertas para facilitar colaboração. Apenas a exclusão (soft delete) é restrita a administradores.

---

## 🔄 Integração com Proprietários

### **Mudanças de Relacionamento:**
- ✅ Imóveis agora referenciam tabela `proprietarios` (não mais `usuarios`)
- ✅ Foreign key: `imoveis.proprietario_id` → `proprietarios.id`
- ✅ Endpoint auxiliar: `GET /api/imoveis/proprietarios/list`
- ✅ Select dinâmico na interface carrega apenas proprietários ativos

### **Migração de Dados:**
```sql
-- Executado automaticamente na migração 56b513dc45c9
-- Dados de usuarios foram migrados para proprietarios
-- FK atualizada de usuarios.id para proprietarios.id
```

---

## 💡 Funcionalidades Especiais

### **1. Lookup de Proprietários (Performance)**
```javascript
// Carregamento único no início
const proprietarios = await fetchWithAuth('/api/imoveis/proprietarios/list');

// Criar mapa para lookup O(1)
const proprietariosMap = {};
proprietarios.forEach(p => {
    proprietariosMap[p.id] = p.nome;
});

// Uso na tabela (sem queries adicionais)
const proprietarioNome = proprietariosMap[imovel.proprietario_id];
```

### **2. Soft Delete**
- Imóveis nunca são deletados fisicamente
- `DELETE /api/imoveis/{id}` marca `is_active = false`
- Mantém histórico de aluguéis e participações
- Admin pode reativar editando o imóvel

### **3. Cálculo Automático de Total**
```javascript
// Valor total mensal do imóvel
const total = (imovel.valor_aluguel || 0) + 
              (imovel.valor_condominio || 0) + 
              (imovel.valor_iptu || 0);
```

---

## 🎯 Próximos Passos

- [ ] Adicionar **foto/imagem** do imóvel
- [ ] Implementar **galeria de fotos**
- [ ] Criar **histórico de valores** (rastreio de mudanças)
- [ ] Adicionar **campos adicionais**: quartos, banheiros, área (m²), tipo
- [ ] Implementar **geolocalização** via CEP (API ViaCEP)
- [ ] Criar **mapa de imóveis** (Google Maps/Leaflet)
- [ ] Relatório de **imóveis por proprietário**
- [ ] Exportar lista para **PDF/Excel**
- [ ] Implementar **importação em massa** via CSV

---

## 🐛 Troubleshooting

### Erro: "Proprietário não encontrado"
**Solução:** Verifique se o `proprietario_id` existe e está ativo:
```sql
SELECT id, nome, is_active FROM proprietarios WHERE id = X;
```

### Erro: Select de proprietários vazio
**Solução:** 
1. Verifique se há proprietários ativos: `SELECT * FROM proprietarios WHERE is_active = true;`
2. Verifique console do navegador para erros de API
3. Teste endpoint: `curl http://localhost:8000/api/imoveis/proprietarios/list -b cookies.txt`

### Estatísticas não atualizam
**Solução:** Força reload da página ou limpe cache do navegador (Ctrl+F5)

### Erro: "Apenas administradores podem deletar imóveis"
**Solução:** Faça login como admin ou peça para um admin desativar o imóvel.

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs: `docker-compose logs app`
2. Consulte a documentação da API: `http://localhost:8000/docs`
3. Teste endpoints com curl ou Postman

**Endpoints Relacionados:**
- Proprietários: `/api/proprietarios/` (ver README_PROPRIETARIOS.md)
- Aluguéis: `/api/alugueis/`
- Participações: `/api/participacoes/` (em desenvolvimento)

---

**Versão:** 1.0  
**Última Atualização:** 02/11/2025  
**Autor:** Sistema AlugueisV5
