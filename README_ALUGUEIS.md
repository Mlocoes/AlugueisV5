# CRUD de Aluguéis Mensais - Documentação

## 📋 Visão Geral

Sistema completo de gestão de aluguéis mensais, permitindo registro, acompanhamento de pagamentos, controle de valores (aluguel + condomínio + taxas) e geração de relatórios financeiros. Suporta múltiplos imóveis com histórico mensal completo.

---

## 🏗️ Arquitetura

### **Modelo de Dados** (`app/models/aluguel.py`)

```python
class AluguelMensal(Base):
    __tablename__ = "alugueis_mensais"
    
    # Identificação
    id: int (PK)
    
    # Referência
    imovel_id: int (FK → imoveis.id, required, indexed)
    
    # Período
    mes_referencia: str (required, indexed)  # Formato: YYYY-MM
    
    # Valores Individuais
    valor_aluguel: float (required, default: 0.0)
    valor_condominio: float (required, default: 0.0)
    valor_iptu: float (required, default: 0.0)
    valor_luz: float (required, default: 0.0)
    valor_agua: float (required, default: 0.0)
    valor_gas: float (required, default: 0.0)
    valor_internet: float (required, default: 0.0)
    outros_valores: float (required, default: 0.0)
    
    # Total Calculado
    valor_total: float (required, default: 0.0)  # Soma de todos os valores
    
    # Status de Pagamento
    pago: bool (default: false)
    data_pagamento: date (nullable)
    
    # Observações
    observacoes: str(1000) (nullable)
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
```

**Relacionamentos:**
- `N:1` com **Imovel** (`imovel`)

**Regras de Negócio:**
- Combinação `(imovel_id, mes_referencia)` deve ser única
- `valor_total` é calculado automaticamente (soma de todos os valores)
- Permite apenas 1 aluguel por imóvel por mês
- Histórico mensal preservado

---

## 🔌 API Endpoints

Base URL: `/api/alugueis`

### 1. **Listar Aluguéis**
```http
GET /api/alugueis/
```

**Query Parameters:**
- `skip` (int): Paginação - offset (default: 0)
- `limit` (int): Paginação - limit (default: 100)
- `mes_referencia` (str): Filtrar por mês específico (YYYY-MM)
- `imovel_id` (int): Filtrar por imóvel
- `ano` (int): Filtrar por ano (ex: 2025)
- `pago` (bool): Filtrar por status de pagamento (true | false)

**Permissões:**
- Admin: vê todos os aluguéis
- Usuário: vê apenas aluguéis de seus imóveis

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "imovel_id": 1,
    "mes_referencia": "2025-11",
    "valor_aluguel": 2500.0,
    "valor_condominio": 450.0,
    "valor_iptu": 120.0,
    "valor_luz": 0.0,
    "valor_agua": 0.0,
    "valor_gas": 0.0,
    "valor_internet": 0.0,
    "outros_valores": 0.0,
    "valor_total": 3070.0,
    "pago": true,
    "data_pagamento": "2025-11-05",
    "observacoes": "Pagamento em dia",
    "created_at": "2025-11-02T10:15:07",
    "updated_at": "2025-11-02T10:15:07",
    "imovel_nome": "Apartamento Centro",
    "imovel_endereco": "Rua das Flores, 123 - Apto 501"
  }
]
```

---

### 2. **Criar Aluguel**
```http
POST /api/alugueis/
```

**Body:**
```json
{
  "imovel_id": 1,
  "mes_referencia": "2025-11",
  "valor_aluguel": 2500.0,
  "valor_condominio": 450.0,
  "valor_iptu": 120.0,
  "valor_luz": 180.0,
  "valor_agua": 85.0,
  "valor_gas": 0.0,
  "valor_internet": 0.0,
  "outros_valores": 0.0,
  "pago": false,
  "data_pagamento": null,
  "observacoes": "Aguardando pagamento"
}
```

**Validações:**
- `imovel_id`: obrigatório, imóvel deve existir
- `mes_referencia`: obrigatório, formato YYYY-MM
- Todos os valores: opcional, default 0.0
- `pago`: opcional, default false
- `data_pagamento`: opcional, obrigatório se `pago=true`
- Não pode existir duplicata para `(imovel_id, mes_referencia)`

**Permissões:**
- Admin: pode criar para qualquer imóvel
- Usuário: apenas para seus próprios imóveis

**Response:** `201 Created`
```json
{
  "id": 5,
  "imovel_id": 1,
  "mes_referencia": "2025-11",
  "valor_aluguel": 2500.0,
  "valor_condominio": 450.0,
  "valor_iptu": 120.0,
  "valor_luz": 180.0,
  "valor_agua": 85.0,
  "valor_gas": 0.0,
  "valor_internet": 0.0,
  "outros_valores": 0.0,
  "valor_total": 3335.0,
  "pago": false,
  "data_pagamento": null,
  "observacoes": "Aguardando pagamento",
  "created_at": "2025-11-02T10:30:00",
  "updated_at": "2025-11-02T10:30:00",
  "imovel_nome": "Apartamento Centro",
  "imovel_endereco": "Rua das Flores, 123 - Apto 501"
}
```

**Errors:**
- `400 Bad Request`: Já existe aluguel para este imóvel neste mês
- `403 Forbidden`: Usuário não tem permissão para este imóvel
- `404 Not Found`: Imóvel não existe

---

### 3. **Obter Aluguel**
```http
GET /api/alugueis/{id}
```

**Permissões:**
- Admin: pode visualizar qualquer aluguel
- Usuário: apenas aluguéis de seus imóveis

**Response:** `200 OK`

**Errors:**
- `403 Forbidden`: Sem permissão
- `404 Not Found`: Aluguel não existe

---

### 4. **Atualizar Aluguel**
```http
PUT /api/alugueis/{id}
```

**Body:** (todos os campos opcionais)
```json
{
  "valor_aluguel": 2600.0,
  "pago": true,
  "data_pagamento": "2025-11-05",
  "observacoes": "Pago via PIX"
}
```

**Validações:**
- Campos não fornecidos permanecem inalterados
- `valor_total` é recalculado automaticamente

**Permissões:**
- Admin: pode atualizar qualquer aluguel
- Usuário: apenas aluguéis de seus imóveis

**Response:** `200 OK`

**Errors:**
- `403 Forbidden`: Sem permissão
- `404 Not Found`: Aluguel não existe

**Caso de Uso Comum:** Marcar como pago
```json
{
  "pago": true,
  "data_pagamento": "2025-11-05"
}
```

---

### 5. **Deletar Aluguel**
```http
DELETE /api/alugueis/{id}
```

⚠️ **Apenas Administradores** | **Hard Delete**

**Response:** `204 No Content`

**Errors:**
- `403 Forbidden`: Usuário não é admin
- `404 Not Found`: Aluguel não existe

**Comportamento:**
- Remove permanentemente do banco
- Use com cuidado (sem confirmação adicional)

---

### 6. **Estatísticas**
```http
GET /api/alugueis/stats/summary
```

**Query Parameters:**
- `ano` (int): Filtrar estatísticas por ano (opcional)

**Permissões:**
- Admin: estatísticas de todos os aluguéis
- Usuário: apenas de seus imóveis

**Response:** `200 OK`
```json
{
  "total_alugueis": 5,
  "pagos": 4,
  "pendentes": 1,
  "valor_total_recebido": 15500.0,
  "valor_total_pendente": 6685.0,
  "valor_total": 22185.0
}
```

**Cálculos:**
- `total_alugueis`: Total de registros
- `pagos`: Aluguéis com `pago = true`
- `pendentes`: Aluguéis com `pago = false`
- `valor_total_recebido`: Soma dos `valor_total` pagos
- `valor_total_pendente`: Soma dos `valor_total` pendentes
- `valor_total`: Soma de todos os valores

---

## 🎨 Interface Web

Acesse: **`http://localhost:8000/alugueis`**

### **Funcionalidades:**

#### 📊 **Estatísticas (5 Cards)**
- Total de aluguéis
- Pagos (verde)
- Pendentes (amarelo)
- Total recebido (azul)
- Total pendente (vermelho)

#### 🔍 **Filtros**
- **Ano:** Dropdown com anos disponíveis
- **Mês:** Seletor tipo `month` (YYYY-MM)
- **Imóvel:** Dropdown com todos os imóveis do usuário
- **Status:** Todos / Pagos / Pendentes

#### 📝 **Tabela**
Colunas:
- Imóvel (nome + endereço)
- Mês/Ano (formato: Nov/2025)
- Aluguel (R$)
- Condomínio (R$)
- IPTU (R$)
- Outros (soma de luz, água, gás, internet, outros)
- Total (R$, em negrito)
- Status (badge verde "PAGO" ou amarelo "PENDENTE")
- Ações (ver detalhes, editar, deletar)

#### ➕ **Modal de Cadastro/Edição**

**Abas:**

**1. Dados Básicos**
- Imóvel (select, obrigatório)
- Mês de Referência (month input, obrigatório)
- Status de Pagamento (checkbox "Pagamento Recebido")
- Data de Pagamento (date, condicional - aparece se marcado como pago)

**2. Valores**
Grid com 8 campos:
- Valor do Aluguel (R$)
- Condomínio (R$)
- IPTU (R$)
- Luz (R$)
- Água (R$)
- Gás (R$)
- Internet (R$)
- Outros Valores (R$)

**Preview do Total:** Exibido em tempo real (soma automática)

**3. Observações**
- Textarea para observações (máximo 1000 caracteres)

---

## 🧪 Testando

### **1. Via CURL**

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sistema.com","password":"admin123"}' \
  -c cookies.txt

# Listar aluguéis
curl -X GET "http://localhost:8000/api/alugueis/" \
  -b cookies.txt

# Filtrar apenas pendentes
curl -X GET "http://localhost:8000/api/alugueis/?pago=false" \
  -b cookies.txt

# Filtrar por ano
curl -X GET "http://localhost:8000/api/alugueis/?ano=2025" \
  -b cookies.txt

# Filtrar por mês específico
curl -X GET "http://localhost:8000/api/alugueis/?mes_referencia=2025-11" \
  -b cookies.txt

# Filtrar por imóvel
curl -X GET "http://localhost:8000/api/alugueis/?imovel_id=1" \
  -b cookies.txt

# Criar aluguel completo
curl -X POST http://localhost:8000/api/alugueis/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "imovel_id": 1,
    "mes_referencia": "2025-12",
    "valor_aluguel": 2500.0,
    "valor_condominio": 450.0,
    "valor_iptu": 120.0,
    "valor_luz": 180.0,
    "valor_agua": 85.0,
    "valor_gas": 60.0,
    "valor_internet": 100.0,
    "outros_valores": 50.0,
    "pago": false,
    "observacoes": "Dezembro 2025"
  }'

# Criar aluguel simples (apenas aluguel + condomínio)
curl -X POST http://localhost:8000/api/alugueis/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "imovel_id": 2,
    "mes_referencia": "2025-12",
    "valor_aluguel": 3600.0,
    "valor_condominio": 580.0,
    "pago": false
  }'

# Marcar como pago
curl -X PUT http://localhost:8000/api/alugueis/1 \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "pago": true,
    "data_pagamento": "2025-11-05",
    "observacoes": "Pago via PIX"
  }'

# Atualizar valores
curl -X PUT http://localhost:8000/api/alugueis/2 \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "valor_luz": 200.0,
    "valor_agua": 95.0
  }'

# Obter aluguel específico
curl -X GET http://localhost:8000/api/alugueis/1 \
  -b cookies.txt

# Deletar aluguel (apenas admin)
curl -X DELETE http://localhost:8000/api/alugueis/5 \
  -b cookies.txt

# Estatísticas gerais
curl -X GET http://localhost:8000/api/alugueis/stats/summary \
  -b cookies.txt

# Estatísticas de 2025
curl -X GET "http://localhost:8000/api/alugueis/stats/summary?ano=2025" \
  -b cookies.txt
```

### **2. Via Interface**

1. Acesse: `http://localhost:8000/login`
2. Login: `admin@sistema.com` / `admin123`
3. Navegue para: **Aluguéis**
4. **Criar Aluguel:**
   - Clique em "Novo Aluguel"
   - Selecione imóvel
   - Escolha mês/ano
   - Preencha valores (aluguel, condomínio, etc.)
   - Marque "Pagamento Recebido" se pago
   - Selecione data de pagamento (se pago)
   - Adicione observações (opcional)
   - Visualize o total calculado
   - Clique em "Salvar"
5. **Marcar como Pago:**
   - Localize aluguel pendente na tabela
   - Clique em "Editar"
   - Marque checkbox "Pagamento Recebido"
   - Selecione data de pagamento
   - Clique em "Salvar"
6. **Filtrar:**
   - Use filtros de Ano, Mês, Imóvel, Status
   - Resultados são atualizados automaticamente
7. **Ver Detalhes:**
   - Clique no ícone de "visualizar" (olho)
   - Modal exibe todos os detalhes do aluguel

---

## 📦 Estrutura de Arquivos

```
AlugueisV5/
├── app/
│   ├── models/
│   │   └── aluguel.py                # Modelo SQLAlchemy
│   ├── routes/
│   │   └── alugueis.py               # 6 endpoints REST + schemas
│   ├── templates/
│   │   └── alugueis.html             # Interface completa (640 linhas)
│   └── main.py                       # Rota /alugueis registrada
└── README_ALUGUEIS.md                # Esta documentação
```

---

## 🔐 Permissões

### **Matriz de Permissões:**

| Ação | Admin | Usuário | Público |
|------|-------|---------|---------|
| Listar | ✅ Todos | ✅ Seus imóveis | ❌ |
| Criar | ✅ Qualquer imóvel | ✅ Seus imóveis | ❌ |
| Editar | ✅ Qualquer | ✅ Seus imóveis | ❌ |
| Ver Detalhes | ✅ Qualquer | ✅ Seus imóveis | ❌ |
| Deletar | ✅ | ❌ | ❌ |
| Estatísticas | ✅ Todos | ✅ Seus imóveis | ❌ |

### **Regras:**
- Usuários veem apenas aluguéis de imóveis onde são proprietários
- Admins têm acesso completo a todos os aluguéis
- Validação de propriedade é feita via join com tabela `imoveis`

---

## 🔄 Integração com Outros Módulos

### **1. Imóveis**
```javascript
// Carregar imóveis do usuário para select
const response = await fetchWithAuth('/api/imoveis/');
const imoveis = await response.json();
imoveis.filter(i => i.is_active).forEach(imovel => {
    // Preencher select
});
```

**Validação:**
- Aluguel só pode ser criado para imóveis existentes
- Usuário só pode criar aluguel para seus imóveis
- API retorna `404` se imóvel não existir ou `403` se sem permissão

### **2. Participações**
**Integração futura sugerida:**
- Ao marcar aluguel como pago, calcular automaticamente participações
- Distribuir `valor_total` entre proprietários baseado em percentuais
- Criar registros em `participacoes` automaticamente

```python
# Exemplo de integração futura
if aluguel.pago and not participacoes_criadas:
    participacoes = db.query(Participacao).filter(
        Participacao.imovel_id == aluguel.imovel_id,
        Participacao.mes_referencia == aluguel.mes_referencia
    ).all()
    
    for participacao in participacoes:
        # Calcular valor_participacao baseado em percentual
        participacao.valor_participacao = aluguel.valor_total * (participacao.percentual / 100)
```

---

## 💡 Funcionalidades Especiais

### **1. Cálculo Automático do Total**

```python
def calcular_valor_total(aluguel_data: dict) -> float:
    """Calcula o valor total do aluguel"""
    return (
        aluguel_data.get('valor_aluguel', 0) +
        aluguel_data.get('valor_condominio', 0) +
        aluguel_data.get('valor_iptu', 0) +
        aluguel_data.get('valor_luz', 0) +
        aluguel_data.get('valor_agua', 0) +
        aluguel_data.get('valor_gas', 0) +
        aluguel_data.get('valor_internet', 0) +
        aluguel_data.get('outros_valores', 0)
    )
```

**Benefício:** 
- Elimina erros de cálculo manual
- Total sempre consistente
- Atualizado automaticamente em edições

### **2. Formato de Mês Amigável**

```javascript
function formatMesReferencia(mesRef) {
    const [ano, mes] = mesRef.split('-');
    const meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                   'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
    return `${meses[parseInt(mes) - 1]}/${ano}`;
}

// "2025-11" → "Nov/2025"
```

### **3. Badge de Status Dinâmico**

```html
${aluguel.pago ? 
    '<span class="px-2 py-1 bg-green-500/20 text-green-400 rounded text-xs font-semibold">PAGO</span>' : 
    '<span class="px-2 py-1 bg-yellow-500/20 text-yellow-400 rounded text-xs font-semibold">PENDENTE</span>'
}
```

### **4. Preview de Total no Modal**

```javascript
// Recalcula total em tempo real
function calcularTotal() {
    const valores = [
        'valor_aluguel', 'valor_condominio', 'valor_iptu',
        'valor_luz', 'valor_agua', 'valor_gas', 
        'valor_internet', 'outros_valores'
    ];
    
    let total = 0;
    valores.forEach(campo => {
        total += parseFloat(document.getElementById(campo).value || 0);
    });
    
    document.getElementById('preview-total').textContent = formatCurrency(total);
}

// Adiciona listener em todos os campos de valor
valores.forEach(campo => {
    document.getElementById(campo).addEventListener('input', calcularTotal);
});
```

**Benefício:** Usuário vê o total antes de salvar.

### **5. Validação de Duplicatas**

```python
# No backend (routes/alugueis.py)
aluguel_existente = db.query(AluguelMensal).filter(
    and_(
        AluguelMensal.imovel_id == aluguel_data.imovel_id,
        AluguelMensal.mes_referencia == aluguel_data.mes_referencia
    )
).first()

if aluguel_existente:
    raise HTTPException(
        status_code=400,
        detail=f"Já existe um aluguel cadastrado para este imóvel em {mes_referencia}"
    )
```

**Comportamento:**
- Impede cadastro duplicado para mesmo imóvel/mês
- 1 aluguel por imóvel por mês

---

## 🎯 Casos de Uso

### **Cenário 1: Aluguel Simples (apenas aluguel)**
```json
{
  "imovel_id": 1,
  "mes_referencia": "2025-11",
  "valor_aluguel": 2500.0,
  "pago": false
}
// Total: R$ 2.500,00
```

### **Cenário 2: Aluguel + Condomínio + IPTU**
```json
{
  "imovel_id": 2,
  "mes_referencia": "2025-11",
  "valor_aluguel": 3600.0,
  "valor_condominio": 580.0,
  "valor_iptu": 150.0,
  "pago": true,
  "data_pagamento": "2025-11-05"
}
// Total: R$ 4.330,00
```

### **Cenário 3: Todos os Valores Inclusos**
```json
{
  "imovel_id": 3,
  "mes_referencia": "2025-11",
  "valor_aluguel": 5500.0,
  "valor_condominio": 720.0,
  "valor_iptu": 200.0,
  "valor_luz": 180.0,
  "valor_agua": 85.0,
  "valor_gas": 60.0,
  "valor_internet": 100.0,
  "outros_valores": 50.0,
  "pago": false
}
// Total: R$ 6.895,00
```

### **Cenário 4: Fluxo de Pagamento**
```bash
# 1. Criar aluguel pendente
POST /api/alugueis/ 
{"imovel_id": 1, "mes_referencia": "2025-11", "valor_aluguel": 2500.0, "pago": false}

# 2. Aguardar pagamento do inquilino
# (dias se passam...)

# 3. Recebimento confirmado - marcar como pago
PUT /api/alugueis/1
{"pago": true, "data_pagamento": "2025-11-15", "observacoes": "Pago via TED"}

# 4. Verificar estatísticas atualizadas
GET /api/alugueis/stats/summary
```

---

## 📊 Relatórios e Análises

### **1. Relatório Mensal**
```bash
# Todos os aluguéis de novembro/2025
curl "http://localhost:8000/api/alugueis/?mes_referencia=2025-11" -b cookies.txt

# Resultado: Lista com todos os aluguéis do mês
# Use para: Fechar mês, conferir recebimentos
```

### **2. Relatório Anual**
```bash
# Todos os aluguéis de 2025
curl "http://localhost:8000/api/alugueis/?ano=2025" -b cookies.txt

# Estatísticas do ano
curl "http://localhost:8000/api/alugueis/stats/summary?ano=2025" -b cookies.txt

# Use para: Declaração de IR, balanço anual
```

### **3. Pendências por Imóvel**
```bash
# Aluguéis pendentes do imóvel 1
curl "http://localhost:8000/api/alugueis/?imovel_id=1&pago=false" -b cookies.txt

# Use para: Cobranças, follow-up de pagamentos
```

### **4. Histórico de Imóvel**
```bash
# Todos os aluguéis do imóvel 1 (histórico completo)
curl "http://localhost:8000/api/alugueis/?imovel_id=1" -b cookies.txt

# Use para: Análise de rentabilidade, vacância
```

---

## 🐛 Troubleshooting

### Erro: "Já existe um aluguel cadastrado para este imóvel neste mês"
**Causa:** Tentativa de criar duplicata.  
**Solução:**
1. Verifique se já existe:
```bash
curl "http://localhost:8000/api/alugueis/?imovel_id=1&mes_referencia=2025-11" -b cookies.txt
```
2. Se quiser alterar, use `PUT` no ID existente
3. Se quiser criar para outro mês, altere `mes_referencia`

### Erro: "Imóvel não encontrado"
**Solução:**
```bash
# Liste imóveis disponíveis
curl "http://localhost:8000/api/imoveis/" -b cookies.txt
# Use um imovel_id válido da resposta
```

### Erro: "Você não tem permissão para criar aluguel neste imóvel"
**Causa:** Usuário não-admin tentando criar aluguel em imóvel de outro proprietário.  
**Solução:**
1. Verifique propriedade do imóvel:
```sql
SELECT id, nome, proprietario_id FROM imoveis WHERE id = 1;
```
2. Se for admin, verifique token/cookie
3. Se for usuário, crie apenas para seus imóveis

### Total calculado está incorreto
**Causa:** Provavelmente não é erro - o total é calculado no backend.  
**Verificação:**
```bash
# Obtenha o aluguel
curl "http://localhost:8000/api/alugueis/1" -b cookies.txt

# Soma manual:
# valor_total = aluguel + condominio + iptu + luz + agua + gas + internet + outros
```

### Data de pagamento obrigatória quando marcar como pago
**Solução:**
```json
// ❌ Errado
{"pago": true}

// ✅ Correto
{"pago": true, "data_pagamento": "2025-11-05"}
```

### Estatísticas não batem
**Solução:**
1. Verifique filtros aplicados (ano, imóvel)
2. Usuários não-admin veem apenas seus imóveis:
```bash
# Como admin (vê tudo)
curl "http://localhost:8000/api/alugueis/stats/summary" -b admin_cookies.txt

# Como usuário (vê apenas seus)
curl "http://localhost:8000/api/alugueis/stats/summary" -b user_cookies.txt
```

---

## 🎯 Próximos Passos

- [ ] Adicionar **gráficos** de inadimplência ao longo do tempo
- [ ] Implementar **alertas automáticos** para aluguéis atrasados
- [ ] Criar **relatório de vacância** (meses sem aluguel cadastrado)
- [ ] Adicionar **exportação para Excel/PDF** de relatórios
- [ ] Implementar **cálculo automático de participações** ao marcar como pago
- [ ] Criar **dashboard financeiro** com receitas vs despesas
- [ ] Adicionar **previsão de recebimentos** futuros
- [ ] Implementar **integração com bancos** (OFX import)
- [ ] Criar **envio de recibos** por email automaticamente
- [ ] Adicionar **multas e juros** para atrasos
- [ ] Implementar **contratos** vinculados a aluguéis
- [ ] Criar **índice de reajuste** automático (IGPM, IPCA)

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs: `docker-compose logs app`
2. Consulte a documentação da API: `http://localhost:8000/docs`
3. Teste endpoints com curl ou Postman

**Endpoints Relacionados:**
- Imóveis: `/api/imoveis/` (ver README_IMOVEIS.md)
- Proprietários: `/api/proprietarios/` (ver README_PROPRIETARIOS.md)
- Participações: `/api/participacoes/` (ver README_PARTICIPACOES.md)
- Autenticação: `/api/auth/login`, `/api/auth/logout`

---

## 📊 Exemplo de Workflow Completo

```bash
# ========================================
# WORKFLOW: Gestão Mensal de Aluguéis
# ========================================

# 1. Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sistema.com","password":"admin123"}' \
  -c cookies.txt

# 2. Início do mês - Criar aluguéis para dezembro/2025
curl -X POST http://localhost:8000/api/alugueis/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "imovel_id": 1,
    "mes_referencia": "2025-12",
    "valor_aluguel": 2500.0,
    "valor_condominio": 450.0,
    "valor_iptu": 120.0,
    "pago": false
  }'

curl -X POST http://localhost:8000/api/alugueis/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "imovel_id": 2,
    "mes_referencia": "2025-12",
    "valor_aluguel": 3600.0,
    "valor_condominio": 580.0,
    "valor_iptu": 150.0,
    "pago": false
  }'

# 3. Acompanhar pendências
curl -X GET "http://localhost:8000/api/alugueis/?mes_referencia=2025-12&pago=false" \
  -b cookies.txt

# 4. Recebimento do primeiro aluguel (dia 05/12)
curl -X PUT http://localhost:8000/api/alugueis/1 \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "pago": true,
    "data_pagamento": "2025-12-05",
    "observacoes": "Pago via TED"
  }'

# 5. Recebimento do segundo aluguel (dia 10/12)
curl -X PUT http://localhost:8000/api/alugueis/2 \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "pago": true,
    "data_pagamento": "2025-12-10",
    "observacoes": "Pago via PIX"
  }'

# 6. Verificar estatísticas do mês
curl -X GET "http://localhost:8000/api/alugueis/stats/summary?ano=2025" \
  -b cookies.txt

# 7. Gerar relatório para contabilidade
curl -X GET "http://localhost:8000/api/alugueis/?mes_referencia=2025-12" \
  -b cookies.txt > relatorio_dezembro_2025.json

# 8. Fim do ano - Relatório anual para IR
curl -X GET "http://localhost:8000/api/alugueis/?ano=2025" \
  -b cookies.txt > relatorio_anual_2025.json
```

---

**Versão:** 1.0  
**Última Atualização:** 02/11/2025  
**Autor:** Sistema AlugueisV5  
**Status:** Testado e Documentado ✅

**Testes Realizados:**
- ✅ 5 aluguéis criados com sucesso
- ✅ Filtros funcionando (ano, mês, imóvel, status)
- ✅ Atualização testada (marcar como pago)
- ✅ Estatísticas calculadas corretamente
- ✅ Validação de duplicatas funcionando
- ✅ Permissões verificadas
- ✅ Cálculo automático de total validado

**Estatísticas Atuais do Sistema:**
- Total: 5 aluguéis
- Pagos: 4 (R$ 15.500,00)
- Pendentes: 1 (R$ 6.685,00)
- Total geral: R$ 22.185,00
