# CRUD de Participações - Documentação

## 📋 Visão Geral

Sistema completo de gestão de participações de proprietários em imóveis, permitindo o controle de percentuais e valores distribuídos mensalmente. Suporta múltiplos proprietários por imóvel e histórico mensal de participações.

---

## 🏗️ Arquitetura

### **Modelo de Dados** (`app/models/participacao.py`)

```python
class Participacao(Base):
    __tablename__ = "participacoes"
    
    # Identificação
    id: int (PK)
    
    # Referências
    imovel_id: int (FK → imoveis.id, required, indexed)
    proprietario_id: int (FK → proprietarios.id, required, indexed)
    
    # Período
    mes_referencia: str (required, indexed)  # Formato: YYYY-MM
    
    # Valores
    percentual: float (required)  # 0.00 - 100.00
    valor_participacao: float (required, default: 0.0)
    
    # Observações
    observacoes: str(500) (nullable)
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
```

**Relacionamentos:**
- `N:1` com **Imovel** (`imovel`)
- `N:1` com **Proprietario** (`proprietario`)

**Regras de Negócio:**
- Combinação `(imovel_id, proprietario_id, mes_referencia)` deve ser única
- Percentual entre 0 e 100
- Permite múltiplos proprietários no mesmo imóvel/mês (ex: 50% cada)
- Histórico mensal preservado

---

## 🔌 API Endpoints

Base URL: `/api/participacoes`

### 1. **Listar Participações**
```http
GET /api/participacoes/
```

**Query Parameters:**
- `skip` (int): Paginação - offset (default: 0)
- `limit` (int): Paginação - limit (default: 100, max: 1000)
- `search` (str): Busca em observações, nome do imóvel ou proprietário
- `imovel_id` (int): Filtrar por imóvel específico
- `proprietario_id` (int): Filtrar por proprietário específico
- `mes_referencia` (str): Filtrar por mês (formato: YYYY-MM)

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "imovel_id": 1,
    "proprietario_id": 2,
    "mes_referencia": "2025-11",
    "percentual": 100.0,
    "valor_participacao": 2500.0,
    "observacoes": "Participação integral",
    "created_at": "2025-11-02T10:00:00",
    "updated_at": "2025-11-02T10:00:00",
    "imovel_nome": "Apartamento Centro",
    "proprietario_nome": "João Silva"
  }
]
```

**Permissões:**
- ✅ Todos os usuários autenticados

---

### 2. **Criar Participação**
```http
POST /api/participacoes/
```

**Body:**
```json
{
  "imovel_id": 1,
  "proprietario_id": 2,
  "mes_referencia": "2025-11",
  "percentual": 100.0,
  "valor_participacao": 2500.0,
  "observacoes": "Participação integral do proprietário"
}
```

**Validações:**
- `imovel_id`: obrigatório, imóvel deve existir
- `proprietario_id`: obrigatório, proprietário deve existir
- `mes_referencia`: obrigatório, formato YYYY-MM
- `percentual`: obrigatório, entre 0 e 100
- `valor_participacao`: obrigatório, maior ou igual a 0
- `observacoes`: opcional, máximo 500 caracteres

**Regra de Unicidade:**
- Não pode existir duplicata para `(imovel_id, proprietario_id, mes_referencia)`

**Response:** `201 Created`
```json
{
  "id": 4,
  "imovel_id": 1,
  "proprietario_id": 2,
  "mes_referencia": "2025-11",
  "percentual": 100.0,
  "valor_participacao": 2500.0,
  "observacoes": "Participação integral do proprietário",
  "created_at": "2025-11-02T10:15:00",
  "updated_at": "2025-11-02T10:15:00",
  "imovel_nome": "Apartamento Centro",
  "proprietario_nome": "João Silva"
}
```

**Errors:**
- `400 Bad Request`: Duplicata encontrada
- `404 Not Found`: Imóvel ou proprietário não existe

---

### 3. **Obter Participação**
```http
GET /api/participacoes/{id}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "imovel_id": 1,
  "proprietario_id": 2,
  ...
}
```

**Errors:**
- `404 Not Found`: Participação não existe

---

### 4. **Atualizar Participação**
```http
PUT /api/participacoes/{id}
```

**Body:** (todos os campos opcionais)
```json
{
  "percentual": 50.0,
  "valor_participacao": 1250.0,
  "observacoes": "Divisão 50/50"
}
```

**Validações:**
- Se alterar `imovel_id`: imóvel deve existir
- Se alterar `proprietario_id`: proprietário deve existir
- Se alterar `mes_referencia`: formato YYYY-MM
- Se alterar `percentual`: entre 0 e 100
- Se alterar `valor_participacao`: >= 0
- Verifica duplicata se campos chave forem alterados

**Response:** `200 OK`

**Errors:**
- `400 Bad Request`: Duplicata ou validação falhou
- `404 Not Found`: Participação, imóvel ou proprietário não existe

---

### 5. **Deletar Participação**
```http
DELETE /api/participacoes/{id}
```

⚠️ **Apenas Administradores** | **Hard Delete**

**Response:** `204 No Content`

**Errors:**
- `403 Forbidden`: Usuário não é admin
- `404 Not Found`: Participação não existe

**Comportamento:**
- Remove permanentemente do banco (não é soft delete)
- Use com cuidado

---

### 6. **Estatísticas**
```http
GET /api/participacoes/stats/summary
```

**Response:** `200 OK`
```json
{
  "total": 3,
  "imoveis_com_participacao": 2,
  "proprietarios_participantes": 2,
  "valor_total": 6100.0
}
```

**Cálculos:**
- `total`: Total de registros de participação
- `imoveis_com_participacao`: Imóveis únicos com participações
- `proprietarios_participantes`: Proprietários únicos com participações
- `valor_total`: Soma de todos os valores_participacao

---

### 7. **Participações por Imóvel**
```http
GET /api/participacoes/imovel/{imovel_id}
```

**Query Parameters:**
- `mes_referencia` (str): Filtrar por mês (opcional)

**Response:** `200 OK`
```json
[
  {
    "id": 2,
    "imovel_id": 2,
    "proprietario_id": 2,
    "mes_referencia": "2025-11",
    "percentual": 50.0,
    "valor_participacao": 1800.0,
    "imovel_nome": "Casa Jardim América",
    "proprietario_nome": "João Silva"
  },
  {
    "id": 3,
    "imovel_id": 2,
    "proprietario_id": 3,
    "mes_referencia": "2025-11",
    "percentual": 50.0,
    "valor_participacao": 1800.0,
    "imovel_nome": "Casa Jardim América",
    "proprietario_nome": "Maria Santos"
  }
]
```

**Errors:**
- `404 Not Found`: Imóvel não existe

**Uso:**
- Visualizar todas as participações de um imóvel
- Útil para validar se percentuais somam 100%

---

## 🎨 Interface Web

Acesse: **`http://localhost:8000/participacoes`**

### **Funcionalidades:**

#### 📊 **Estatísticas (4 Cards)**
- Total de participações
- Imóveis com participação
- Proprietários participantes
- Valor total distribuído (R$)

#### 🔍 **Filtros**
- **Busca:** Nome do imóvel, proprietário, observações (debounce 500ms)
- **Imóvel:** Dropdown com todos os imóveis ativos
- **Proprietário:** Dropdown com todos os proprietários ativos
- **Mês de Referência:** Seletor tipo `month` (YYYY-MM)

#### 📝 **Tabela**
Colunas:
- Imóvel
- Proprietário
- Mês Referência (formato: Mês/Ano - ex: Nov/2025)
- Percentual (badge azul com %)
- Valor (R$)
- Ações (editar/deletar)

#### ➕ **Modal de Cadastro/Edição**

**Campos:**
1. **Imóvel** (select, obrigatório)
   - Lista apenas imóveis ativos
   - Carregado via `/api/imoveis/`

2. **Proprietário** (select, obrigatório)
   - Lista apenas proprietários ativos
   - Carregado via `/api/proprietarios/`

3. **Mês de Referência** (month input, obrigatório)
   - Formato: YYYY-MM
   - Permite seleção rápida via calendário

4. **Percentual** (number, obrigatório)
   - Min: 0, Max: 100
   - Step: 0.01 (permite decimais)
   - Hint: "Valor entre 0 e 100"

5. **Valor de Participação** (number, obrigatório)
   - Min: 0
   - Step: 0.01
   - Formato monetário na exibição

6. **Observações** (textarea, opcional)
   - Máximo 500 caracteres
   - Placeholder: "Observações adicionais..."

---

## 🧪 Testando

### **1. Via CURL**

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sistema.com","password":"admin123"}' \
  -c cookies.txt

# Listar participações
curl -X GET "http://localhost:8000/api/participacoes/" \
  -b cookies.txt

# Filtrar por imóvel
curl -X GET "http://localhost:8000/api/participacoes/?imovel_id=2" \
  -b cookies.txt

# Filtrar por proprietário
curl -X GET "http://localhost:8000/api/participacoes/?proprietario_id=2" \
  -b cookies.txt

# Filtrar por mês
curl -X GET "http://localhost:8000/api/participacoes/?mes_referencia=2025-11" \
  -b cookies.txt

# Criar participação (100% de um proprietário)
curl -X POST http://localhost:8000/api/participacoes/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "imovel_id": 1,
    "proprietario_id": 2,
    "mes_referencia": "2025-11",
    "percentual": 100.0,
    "valor_participacao": 2500.0,
    "observacoes": "Participação integral"
  }'

# Criar participação dividida (50/50)
curl -X POST http://localhost:8000/api/participacoes/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "imovel_id": 2,
    "proprietario_id": 2,
    "mes_referencia": "2025-11",
    "percentual": 50.0,
    "valor_participacao": 1800.0
  }'

curl -X POST http://localhost:8000/api/participacoes/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "imovel_id": 2,
    "proprietario_id": 3,
    "mes_referencia": "2025-11",
    "percentual": 50.0,
    "valor_participacao": 1800.0
  }'

# Atualizar percentual e valor
curl -X PUT http://localhost:8000/api/participacoes/1 \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "percentual": 60.0,
    "valor_participacao": 1500.0
  }'

# Obter participação específica
curl -X GET http://localhost:8000/api/participacoes/1 \
  -b cookies.txt

# Listar participações de um imóvel
curl -X GET http://localhost:8000/api/participacoes/imovel/2 \
  -b cookies.txt

# Deletar participação (apenas admin)
curl -X DELETE http://localhost:8000/api/participacoes/1 \
  -b cookies.txt

# Estatísticas
curl -X GET http://localhost:8000/api/participacoes/stats/summary \
  -b cookies.txt
```

### **2. Via Interface**

1. Acesse: `http://localhost:8000/login`
2. Login: `admin@sistema.com` / `admin123`
3. Navegue para: **Participações**
4. **Criar Participação:**
   - Clique em "Nova Participação"
   - Selecione imóvel
   - Selecione proprietário
   - Escolha mês/ano
   - Informe percentual (ex: 100 ou 50)
   - Informe valor (ex: 2500.00)
   - Adicione observações (opcional)
   - Clique em "Salvar"
5. **Editar Participação:**
   - Clique no ícone de editar (lápis)
   - Altere campos desejados
   - Clique em "Salvar"
6. **Deletar Participação:**
   - Clique no ícone de delete (lixeira)
   - Confirme a ação
7. **Filtrar:**
   - Use busca para encontrar por nome
   - Selecione imóvel no dropdown
   - Selecione proprietário no dropdown
   - Escolha mês de referência

---

## 📦 Estrutura de Arquivos

```
AlugueisV5/
├── app/
│   ├── models/
│   │   ├── participacao.py           # Modelo SQLAlchemy (FK para proprietarios)
│   │   ├── proprietario.py           # Relacionamento participacoes
│   │   └── usuario.py                # Relacionamento removido
│   ├── routes/
│   │   └── participacoes.py          # 7 endpoints REST + schemas
│   ├── templates/
│   │   └── participacoes.html        # Interface completa (600 linhas)
│   └── main.py                       # Rota /participacoes registrada
├── alembic/versions/
│   └── 2025_11_02_atualizar_participacoes_para_proprietarios.py
└── README_PARTICIPACOES.md           # Esta documentação
```

---

## 🔐 Permissões

### **Matriz de Permissões:**

| Ação | Admin | Usuário | Público |
|------|-------|---------|---------|
| Listar | ✅ | ✅ | ❌ |
| Criar | ✅ | ✅ | ❌ |
| Editar | ✅ | ✅ | ❌ |
| Ver Detalhes | ✅ | ✅ | ❌ |
| Deletar | ✅ | ❌ | ❌ |
| Estatísticas | ✅ | ✅ | ❌ |
| Por Imóvel | ✅ | ✅ | ❌ |

### **Regras:**
- Todos os usuários autenticados podem gerenciar participações
- Apenas admins podem deletar
- Não há soft delete (remoção permanente)

---

## 🔄 Integração com Outros Módulos

### **1. Imóveis**
```javascript
// Carregar imóveis ativos para select
const response = await fetchWithAuth('/api/imoveis/?limit=1000');
const imoveis = await response.json();
imoveis.filter(i => i.is_active).forEach(imovel => {
    // Preencher select
});
```

**Validação:**
- Participação só pode ser criada para imóveis existentes
- API retorna `404` se imóvel não existir

### **2. Proprietários**
```javascript
// Carregar proprietários ativos para select
const response = await fetchWithAuth('/api/proprietarios/?limit=1000');
const proprietarios = await response.json();
proprietarios.filter(p => p.is_active).forEach(prop => {
    // Preencher select
});
```

**Validação:**
- Participação só pode ser criada para proprietários existentes
- API retorna `404` se proprietário não existir

### **3. Migração de Dados**
- FK migrada de `usuarios.id` para `proprietarios.id`
- Comando: `alembic upgrade head`
- Arquivo: `2025_11_02_atualizar_participacoes_para_proprietarios.py`

---

## 💡 Funcionalidades Especiais

### **1. Lookup Maps (Performance)**

```javascript
// Criar maps para acesso O(1)
const imoveisMap = {};
imoveis.forEach(i => {
    imoveisMap[i.id] = i;
});

const proprietariosMap = {};
proprietarios.forEach(p => {
    proprietariosMap[p.id] = p;
});

// Uso rápido na renderização
const imovelNome = imoveisMap[participacao.imovel_id]?.nome;
const proprietarioNome = proprietariosMap[participacao.proprietario_id]?.nome;
```

**Benefício:** Evita loops aninhados, melhora performance com grandes volumes.

### **2. Formato de Mês Amigável**

```javascript
function formatMesReferencia(mesRef) {
    if (!mesRef) return 'N/A';
    const [ano, mes] = mesRef.split('-');
    const meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                   'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
    return `${meses[parseInt(mes) - 1]}/${ano}`;
}

// "2025-11" → "Nov/2025"
```

### **3. Validação de Duplicatas**

```python
# No backend (routes/participacoes.py)
existing = db.query(Participacao).filter(
    Participacao.imovel_id == data.imovel_id,
    Participacao.proprietario_id == data.proprietario_id,
    Participacao.mes_referencia == data.mes_referencia
).first()

if existing:
    raise HTTPException(
        status_code=400,
        detail="Já existe uma participação para este imóvel, proprietário e mês"
    )
```

**Comportamento:**
- Permite múltiplos proprietários no mesmo imóvel/mês
- NÃO permite mesmo proprietário duplicado no mesmo imóvel/mês

### **4. Histórico Mensal**

```sql
-- Exemplo de histórico de participações
SELECT 
    i.nome as imovel,
    p.nome as proprietario,
    pt.mes_referencia,
    pt.percentual,
    pt.valor_participacao
FROM participacoes pt
JOIN imoveis i ON pt.imovel_id = i.id
JOIN proprietarios p ON pt.proprietario_id = p.id
WHERE pt.imovel_id = 1
ORDER BY pt.mes_referencia DESC;
```

**Uso:** Rastreamento histórico de mudanças de participação ao longo do tempo.

---

## 🎯 Casos de Uso

### **Cenário 1: Proprietário Único**
```json
{
  "imovel_id": 1,
  "proprietario_id": 2,
  "mes_referencia": "2025-11",
  "percentual": 100.0,
  "valor_participacao": 2500.0
}
```
- 1 imóvel = 1 proprietário
- 100% dos rendimentos

### **Cenário 2: Co-propriedade 50/50**
```json
// Participação 1
{
  "imovel_id": 2,
  "proprietario_id": 2,
  "mes_referencia": "2025-11",
  "percentual": 50.0,
  "valor_participacao": 1800.0
}

// Participação 2
{
  "imovel_id": 2,
  "proprietario_id": 3,
  "mes_referencia": "2025-11",
  "percentual": 50.0,
  "valor_participacao": 1800.0
}
```
- 1 imóvel = 2 proprietários
- Cada um recebe 50%

### **Cenário 3: Participação Desigual**
```json
// 70% - Proprietário principal
{
  "imovel_id": 3,
  "proprietario_id": 2,
  "percentual": 70.0,
  "valor_participacao": 2800.0
}

// 30% - Proprietário secundário
{
  "imovel_id": 3,
  "proprietario_id": 3,
  "percentual": 30.0,
  "valor_participacao": 1200.0
}
```
- Divisão proporcional ao investimento

### **Cenário 4: Mudança de Participação ao Longo do Tempo**
```json
// Novembro/2025
{"mes_referencia": "2025-11", "percentual": 100.0, "proprietario_id": 2}

// Dezembro/2025 (venda de 50%)
{"mes_referencia": "2025-12", "percentual": 50.0, "proprietario_id": 2}
{"mes_referencia": "2025-12", "percentual": 50.0, "proprietario_id": 3}
```
- Histórico preservado mês a mês

---

## 🐛 Troubleshooting

### Erro: "Já existe uma participação para este imóvel, proprietário e mês"
**Causa:** Tentativa de criar duplicata.  
**Solução:**
1. Verifique se já existe participação:
```bash
curl "http://localhost:8000/api/participacoes/imovel/1?mes_referencia=2025-11" -b cookies.txt
```
2. Se quiser alterar, use `PUT` em vez de `POST`

### Erro: "Imóvel não encontrado"
**Solução:**
1. Liste imóveis disponíveis:
```bash
curl "http://localhost:8000/api/imoveis/" -b cookies.txt
```
2. Use um `imovel_id` válido da resposta

### Erro: "Proprietário não encontrado"
**Solução:**
1. Liste proprietários disponíveis:
```bash
curl "http://localhost:8000/api/proprietarios/" -b cookies.txt
```
2. Use um `proprietario_id` válido

### Erro: "mes_referencia deve estar no formato YYYY-MM"
**Solução:**
```json
// ❌ Errado
{"mes_referencia": "11/2025"}
{"mes_referencia": "2025-11-01"}

// ✅ Correto
{"mes_referencia": "2025-11"}
```

### Percentuais não somam 100%
**Nota:** Isso é permitido! O sistema não valida se os percentuais de um imóvel somam 100%.  
**Responsabilidade:** O usuário deve garantir a soma correta.  
**Verificação:**
```bash
# Listar todas as participações de um imóvel
curl "http://localhost:8000/api/participacoes/imovel/2?mes_referencia=2025-11" -b cookies.txt

# Somar percentuais manualmente
```

### Modal não carrega imóveis/proprietários
**Solução:**
1. Verifique se existem imóveis/proprietários ativos:
```sql
SELECT COUNT(*) FROM imoveis WHERE is_active = true;
SELECT COUNT(*) FROM proprietarios WHERE is_active = true;
```
2. Verifique console do navegador (F12) para erros JavaScript
3. Teste APIs manualmente:
```bash
curl "http://localhost:8000/api/imoveis/" -b cookies.txt
curl "http://localhost:8000/api/proprietarios/" -b cookies.txt
```

---

## 🎯 Próximos Passos

- [ ] Adicionar **validação automática** de soma de percentuais = 100%
- [ ] Implementar **gráficos** de distribuição de participações
- [ ] Criar **relatório de participações** por período
- [ ] Adicionar **exportação para Excel/PDF**
- [ ] Implementar **cálculo automático** baseado em aluguel recebido
- [ ] Criar **histórico de alterações** (audit log)
- [ ] Adicionar **notificações** quando participações mudarem
- [ ] Implementar **dashboard** de participações por proprietário
- [ ] Criar **previsão de pagamentos** futuros
- [ ] Adicionar **integração com pagamentos** (Pix, TED)

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs: `docker-compose logs app`
2. Consulte a documentação da API: `http://localhost:8000/docs`
3. Teste endpoints com curl ou Postman

**Endpoints Relacionados:**
- Imóveis: `/api/imoveis/` (ver README_IMOVEIS.md)
- Proprietários: `/api/proprietarios/` (ver README_PROPRIETARIOS.md)
- Autenticação: `/api/auth/login`, `/api/auth/logout`

---

## 📊 Exemplo de Uso Completo

```bash
# 1. Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sistema.com","password":"admin123"}' \
  -c cookies.txt

# 2. Criar imóvel (se necessário)
curl -X POST http://localhost:8000/api/imoveis/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "nome": "Apartamento Vila Mariana",
    "proprietario_id": 2,
    "endereco": "Rua Domingos de Morais, 1234",
    "valor_aluguel": 3000.0
  }'

# 3. Criar participação única (100%)
curl -X POST http://localhost:8000/api/participacoes/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "imovel_id": 7,
    "proprietario_id": 2,
    "mes_referencia": "2025-11",
    "percentual": 100.0,
    "valor_participacao": 3000.0,
    "observacoes": "Aluguel novembro - proprietário único"
  }'

# 4. Verificar estatísticas
curl -X GET "http://localhost:8000/api/participacoes/stats/summary" \
  -b cookies.txt

# 5. Listar participações do imóvel
curl -X GET "http://localhost:8000/api/participacoes/imovel/7" \
  -b cookies.txt
```

---

**Versão:** 1.0  
**Última Atualização:** 02/11/2025  
**Autor:** Sistema AlugueisV5
