# 📊 Módulo de Relatórios Financeiros

## Visão Geral

O módulo de Relatórios oferece análise completa dos dados financeiros do sistema, permitindo visualizar receitas, despesas, participações e comparações temporais de forma consolidada.

## 🎯 Funcionalidades

### Tipos de Relatórios

1. **Relatório Mensal**: Consolidação de todos os aluguéis de um mês específico
2. **Relatório de Proprietário**: Receitas específicas de um proprietário em período determinado
3. **Relatório Anual**: Visão consolidada de 12 meses com totais e métricas
4. **Relatório Comparativo**: Comparação entre dois anos com variação percentual

### Recursos

- ✅ Cards de resumo com KPIs principais
- ✅ Tabelas detalhadas por imóvel
- ✅ Cálculo automático de participações
- ✅ Exportação para PDF e Excel
- ✅ Filtros avançados por período e proprietário
- ✅ Indicadores visuais (taxas de recebimento, variações)
- ✅ Dark mode completo
- ✅ Interface responsiva

---

## 📡 API Endpoints

### Base URL
```
/api/relatorios
```

### 1. Relatório Mensal

Gera consolidação de um mês específico com todos os aluguéis.

**Endpoint:** `GET /api/relatorios/mensal`

**Parâmetros:**
- `ano` (int, obrigatório): Ano de referência
- `mes` (int, obrigatório): Mês de 1 a 12
- `proprietario_id` (int, opcional): Filtrar por proprietário

**Exemplo de Requisição:**
```bash
curl -X GET "http://localhost:8000/api/relatorios/mensal?ano=2025&mes=11" \
  -H "Cookie: session_token=SEU_TOKEN"
```

**Resposta de Sucesso (200):**
```json
{
  "periodo": {
    "ano": 2025,
    "mes": 11,
    "mes_nome": "November",
    "mes_referencia": "2025-11"
  },
  "resumo": {
    "total_alugueis": 5,
    "alugueis_pagos": 4,
    "alugueis_pendentes": 1,
    "total_esperado": 18300.00,
    "total_recebido": 12800.00,
    "total_pendente": 5500.00,
    "taxa_recebimento": 69.9
  },
  "detalhamento": [
    {
      "aluguel_id": 1,
      "imovel_id": 1,
      "imovel_endereco": "Rua das Flores, 123",
      "mes_referencia": "2025-11",
      "status_pagamento": "pago",
      "data_pagamento": "2025-11-05",
      "valores": {
        "aluguel": 2500.00,
        "condominio": 300.00,
        "iptu": 150.00,
        "luz": 120.00,
        "agua": 80.00,
        "gas": 50.00,
        "internet": 100.00,
        "outros": 0.00,
        "total": 3300.00
      },
      "participacoes": [
        {
          "proprietario_id": 1,
          "proprietario_nome": "João Silva",
          "percentual": 100.0,
          "valor": 3300.00
        }
      ]
    }
  ]
}
```

---

### 2. Relatório de Proprietário

Gera relatório específico para um proprietário, mostrando suas receitas em imóveis onde possui participação.

**Endpoint:** `GET /api/relatorios/proprietario/{proprietario_id}`

**Parâmetros de Path:**
- `proprietario_id` (int, obrigatório): ID do proprietário

**Parâmetros de Query:**
- `ano` (int, obrigatório): Ano de referência
- `mes` (int, opcional): Mês específico (se omitido, gera anual)

**Exemplo de Requisição:**
```bash
# Relatório anual do proprietário
curl -X GET "http://localhost:8000/api/relatorios/proprietario/1?ano=2025" \
  -H "Cookie: session_token=SEU_TOKEN"

# Relatório mensal do proprietário
curl -X GET "http://localhost:8000/api/relatorios/proprietario/1?ano=2025&mes=11" \
  -H "Cookie: session_token=SEU_TOKEN"
```

**Resposta de Sucesso (200):**
```json
{
  "proprietario": {
    "id": 1,
    "nome": "João Silva",
    "cpf_cnpj": "123.456.789-00",
    "tipo_pessoa": "fisica"
  },
  "periodo": {
    "ano": 2025,
    "mes": null
  },
  "resumo": {
    "total_imoveis": 3,
    "total_esperado": 45600.00,
    "total_recebido": 42300.00,
    "total_pendente": 3300.00,
    "taxa_recebimento": 92.8
  },
  "receitas_por_mes": [
    {
      "mes_referencia": "2025-11",
      "total_esperado": 3800.00,
      "total_recebido": 3800.00,
      "total_pendente": 0.00,
      "detalhes": [
        {
          "imovel_id": 1,
          "imovel_endereco": "Rua das Flores, 123",
          "percentual": 100.0,
          "valor_aluguel_total": 3300.00,
          "valor_proprietario": 3300.00,
          "status_pagamento": "pago",
          "mes_referencia": "2025-11",
          "data_pagamento": "2025-11-05"
        }
      ]
    }
  ]
}
```

---

### 3. Relatório Anual

Gera consolidação anual com dados mensais aggregados.

**Endpoint:** `GET /api/relatorios/anual`

**Parâmetros:**
- `ano` (int, obrigatório): Ano de referência

**Exemplo de Requisição:**
```bash
curl -X GET "http://localhost:8000/api/relatorios/anual?ano=2025" \
  -H "Cookie: session_token=SEU_TOKEN"
```

**Resposta de Sucesso (200):**
```json
{
  "ano": 2025,
  "resumo": {
    "total_esperado": 219600.00,
    "total_recebido": 198400.00,
    "total_pendente": 21200.00,
    "taxa_recebimento": 90.3
  },
  "receitas_mensais": [
    {
      "mes": 1,
      "mes_nome": "January",
      "total_alugueis": 5,
      "alugueis_pagos": 5,
      "alugueis_pendentes": 0,
      "total_esperado": 18300.00,
      "total_recebido": 18300.00,
      "total_pendente": 0.00
    },
    {
      "mes": 2,
      "mes_nome": "February",
      "total_alugueis": 5,
      "alugueis_pagos": 4,
      "alugueis_pendentes": 1,
      "total_esperado": 18300.00,
      "total_recebido": 16500.00,
      "total_pendente": 1800.00
    }
  ]
}
```

---

### 4. Relatório Comparativo

Compara receitas entre dois anos, mês a mês.

**Endpoint:** `GET /api/relatorios/comparativo`

**Parâmetros:**
- `ano1` (int, obrigatório): Primeiro ano
- `ano2` (int, obrigatório): Segundo ano

**Exemplo de Requisição:**
```bash
curl -X GET "http://localhost:8000/api/relatorios/comparativo?ano1=2024&ano2=2025" \
  -H "Cookie: session_token=SEU_TOKEN"
```

**Resposta de Sucesso (200):**
```json
{
  "anos_comparados": [2024, 2025],
  "resumo": {
    "total_2024": 185600.00,
    "total_2025": 198400.00,
    "variacao_absoluta": 12800.00,
    "variacao_percentual": 6.9
  },
  "comparacao_mensal": [
    {
      "mes": 1,
      "mes_nome": "January",
      "receita_2024": 15200.00,
      "receita_2025": 18300.00,
      "variacao_absoluta": 3100.00,
      "variacao_percentual": 20.4
    },
    {
      "mes": 2,
      "mes_nome": "February",
      "receita_2024": 15800.00,
      "receita_2025": 16500.00,
      "variacao_absoluta": 700.00,
      "variacao_percentual": 4.4
    }
  ]
}
```

---

### 5. Dados do Dashboard

Retorna dados agregados para dashboard principal.

**Endpoint:** `GET /api/relatorios/dashboard`

**Exemplo de Requisição:**
```bash
curl -X GET "http://localhost:8000/api/relatorios/dashboard" \
  -H "Cookie: session_token=SEU_TOKEN"
```

**Resposta de Sucesso (200):**
```json
{
  "mes_atual": {
    "periodo": {
      "ano": 2025,
      "mes": 11,
      "mes_nome": "November"
    },
    "resumo": {
      "total_alugueis": 5,
      "total_esperado": 18300.00,
      "total_recebido": 12800.00,
      "taxa_recebimento": 69.9
    }
  },
  "comparacao_mensal": {
    "variacao_absoluta": 1200.00,
    "variacao_percentual": 10.3,
    "mes_anterior": {
      "ano": 2025,
      "mes": 10,
      "total_recebido": 11600.00
    }
  },
  "anual": {
    "ano": 2025,
    "resumo": {
      "total_esperado": 219600.00,
      "total_recebido": 198400.00,
      "taxa_recebimento": 90.3
    }
  },
  "top_imoveis": [
    {
      "imovel_endereco": "Av. Paulista, 1000",
      "valores": {
        "total": 5500.00
      }
    }
  ]
}
```

---

### 6. Exportar PDF (Mensal)

Exporta relatório mensal em formato PDF com formatação profissional.

**Endpoint:** `GET /api/relatorios/exportar/pdf/mensal`

**Parâmetros:**
- `ano` (int, obrigatório): Ano de referência
- `mes` (int, obrigatório): Mês de 1 a 12
- `proprietario_id` (int, opcional): Filtrar por proprietário

**Exemplo de Requisição:**
```bash
curl -X GET "http://localhost:8000/api/relatorios/exportar/pdf/mensal?ano=2025&mes=11" \
  -H "Cookie: session_token=SEU_TOKEN" \
  --output relatorio_novembro_2025.pdf
```

**Resposta de Sucesso (200):**
- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename=relatorio_mensal_2025_11.pdf`

**Formato do PDF:**
- Título com período
- Tabela de resumo (totais, taxa de recebimento)
- Tabela detalhada por imóvel
- Cores corporativas (azul #135bec)
- Paginação automática

---

### 7. Exportar Excel (Mensal)

Exporta relatório mensal em formato Excel com múltiplas abas.

**Endpoint:** `GET /api/relatorios/exportar/excel/mensal`

**Parâmetros:**
- `ano` (int, obrigatório): Ano de referência
- `mes` (int, obrigatório): Mês de 1 a 12
- `proprietario_id` (int, opcional): Filtrar por proprietário

**Exemplo de Requisição:**
```bash
curl -X GET "http://localhost:8000/api/relatorios/exportar/excel/mensal?ano=2025&mes=11" \
  -H "Cookie: session_token=SEU_TOKEN" \
  --output relatorio_novembro_2025.xlsx
```

**Resposta de Sucesso (200):**
- Content-Type: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- Content-Disposition: `attachment; filename=relatorio_mensal_2025_11.xlsx`

**Estrutura do Excel:**
- **Aba "Resumo"**: KPIs e totais gerais
- **Aba "Detalhamento"**: Todos os aluguéis com valores discriminados
- Células com bordas e formatação de cores
- Larguras de coluna ajustadas automaticamente

---

## 💻 Interface Web

### Acesso

```
http://localhost:8000/relatorios
```

### Funcionalidades da Interface

#### 1. Tabs de Tipos de Relatório

- **Mensal**: Selecionar ano, mês e proprietário (opcional)
- **Por Proprietário**: Selecionar proprietário, ano e mês (opcional)
- **Anual**: Selecionar apenas o ano
- **Comparativo**: Selecionar dois anos para comparação

#### 2. Cards de Resumo

Exibição visual com cores diferentes:
- 🔵 **Total de Aluguéis** (azul): Quantidade total
- 🟢 **Total Esperado** (verde): Valor total previsto
- 🟢 **Total Recebido** (verde escuro): Valor efetivamente pago
- 🟠 **Total Pendente** (laranja): Valor ainda não recebido

#### 3. Barra de Progresso

Taxa de recebimento visual com indicador percentual animado.

#### 4. Tabela Detalhada

Colunas:
- Imóvel (endereço)
- Status (badge pago/pendente)
- Vencimento
- Valores discriminados (aluguel, condomínio, IPTU, despesas)
- Total

#### 5. Botões de Exportação

- **PDF**: Botão vermelho, ícone de documento
- **Excel**: Botão verde, ícone de planilha

---

## 🔍 Casos de Uso

### Caso 1: Relatório Mensal para Prestação de Contas

**Objetivo:** Gerar relatório mensal completo para enviar aos proprietários.

**Passos:**
1. Acessar `/relatorios`
2. Selecionar tab "Mensal"
3. Escolher ano e mês
4. Clicar em "Gerar"
5. Revisar dados na tela
6. Clicar em "Excel" para exportar
7. Abrir arquivo Excel gerado
8. Enviar por email aos proprietários

**Resultado:**
- Relatório completo com todos os valores
- Arquivo Excel pronto para compartilhamento
- Dados consolidados por imóvel

---

### Caso 2: Acompanhamento de Inadimplência

**Objetivo:** Identificar aluguéis pendentes do mês.

**Passos:**
1. Gerar relatório mensal do mês atual
2. Observar campo "Aluguéis Pendentes" no card laranja
3. Ver taxa de recebimento na barra de progresso
4. Consultar tabela detalhada
5. Filtrar visualmente linhas com badge "PENDENTE"
6. Anotar imóveis inadimplentes

**Resultado:**
- Lista de imóveis com pagamento pendente
- Valor total em atraso
- Percentual de inadimplência

---

### Caso 3: Relatório Individual de Proprietário

**Objetivo:** Mostrar ao proprietário apenas suas receitas.

**Passos:**
1. Acessar `/relatorios`
2. Selecionar tab "Por Proprietário"
3. Escolher proprietário no dropdown
4. Selecionar ano (e mês se desejar)
5. Clicar em "Gerar"
6. Exportar para PDF com botão vermelho

**Resultado:**
- Relatório personalizado com nome do proprietário
- Apenas imóveis onde ele possui participação
- Valores calculados conforme sua porcentagem
- PDF profissional pronto para envio

---

### Caso 4: Análise Anual e Tendências

**Objetivo:** Avaliar desempenho financeiro do ano.

**Passos:**
1. Acessar `/relatorios`
2. Selecionar tab "Anual"
3. Escolher o ano
4. Clicar em "Gerar"
5. Analisar gráfico mensal
6. Identificar meses com melhor/pior desempenho
7. Exportar para Excel para análises adicionais

**Resultado:**
- Visão consolidada de 12 meses
- Total anual recebido
- Taxa média de recebimento
- Identificação de sazonalidades

---

### Caso 5: Comparação entre Anos

**Objetivo:** Verificar crescimento ou queda de receitas.

**Passos:**
1. Acessar `/relatorios`
2. Selecionar tab "Comparativo"
3. Escolher ano anterior (ex: 2024) em "Ano 1"
4. Escolher ano atual (ex: 2025) em "Ano 2"
5. Clicar em "Gerar"
6. Observar cards de variação
7. Analisar tabela mês a mês

**Resultado:**
- Variação percentual entre anos
- Variação absoluta em reais
- Comparação mensal detalhada
- Identificação de meses com maior crescimento/queda

---

## 🔗 Integrações

### Módulos Relacionados

#### Aluguéis Mensais
- **Usado para:** Obter valores mensais de cada imóvel
- **Campos utilizados:** mes_referencia, pago, valor_aluguel, valor_condominio, etc.
- **Relacionamento:** 1:N com Imóveis

#### Imóveis
- **Usado para:** Informações de endereço e identificação
- **Campos utilizados:** id, endereco
- **Relacionamento:** N:1 com Proprietários (via Participações)

#### Proprietários
- **Usado para:** Identificação e dados cadastrais
- **Campos utilizados:** id, nome, cpf_cnpj, tipo_pessoa
- **Relacionamento:** N:M com Imóveis (via Participações)

#### Participações
- **Usado para:** Calcular valor proporcional de cada proprietário
- **Campos utilizados:** imovel_id, proprietario_id, percentual, mes_referencia
- **Relacionamento:** Tabela de associação entre Proprietários e Imóveis

---

## ⚙️ Configuração

### Dependências Necessárias

```txt
reportlab==4.0.7     # Para exportação PDF
openpyxl==3.1.2      # Para exportação Excel (já instalado)
```

### Instalação

```bash
pip install reportlab==4.0.7
```

### Verificação

```bash
python -c "import reportlab; print('ReportLab:', reportlab.Version)"
python -c "import openpyxl; print('OpenPyXL:', openpyxl.__version__)"
```

---

## 🎨 Personalização

### Cores do Tema

Definidas em CSS variables:
```css
--primary: #135bec        /* Azul principal */
--bg-dark: #101622        /* Fundo escuro */
--card-dark: #1e293b      /* Card escuro */
```

### Modificar Cor dos PDFs

Em `app/routes/relatorios.py`, linha ~230:
```python
header_fill = PatternFill(
    start_color="135bec",  # Alterar esta cor
    end_color="135bec",
    fill_type="solid"
)
```

### Adicionar Novos Tipos de Relatório

1. Criar método em `RelatorioService`
2. Adicionar endpoint em `app/routes/relatorios.py`
3. Adicionar tab na interface `app/templates/relatorios.html`
4. Implementar função JavaScript de geração
5. Criar função de renderização específica

---

## 🐛 Troubleshooting

### Problema: "Biblioteca reportlab não instalada"

**Solução:**
```bash
pip install reportlab==4.0.7
# ou dentro do container:
docker-compose exec app pip install reportlab==4.0.7
```

### Problema: Relatório vazio mesmo com aluguéis cadastrados

**Causa:** Formato de `mes_referencia` incorreto

**Verificação:**
```sql
SELECT DISTINCT mes_referencia FROM alugueis_mensais;
```

**Solução:** Garantir formato `YYYY-MM` (ex: `2025-11`)

### Problema: Valores de participação não aparecem

**Causa:** Participações não cadastradas para o mês

**Verificação:**
```sql
SELECT * FROM participacoes 
WHERE mes_referencia = '2025-11';
```

**Solução:** Cadastrar participações para o mês desejado

### Problema: Taxa de recebimento sempre 0%

**Causa:** Campo `pago` como `false` para todos os aluguéis

**Verificação:**
```sql
SELECT COUNT(*), pago FROM alugueis_mensais 
WHERE mes_referencia = '2025-11'
GROUP BY pago;
```

**Solução:** Marcar aluguéis pagos com `pago = true`

### Problema: Exportação PDF com erros de encoding

**Causa:** Caracteres especiais em nomes

**Solução:** ReportLab 4.0+ suporta UTF-8 automaticamente. Verificar versão:
```python
import reportlab
print(reportlab.Version)  # Deve ser >= 4.0
```

---

## 📈 Performance

### Otimizações Implementadas

1. **Consultas SQL otimizadas**
   - Uso de `filter()` ao invés de loops Python
   - Joins apenas quando necessário
   - Índices em `mes_referencia`, `imovel_id`

2. **Cálculos em lote**
   - Agregações feitas no banco quando possível
   - Cache de participações por mês

3. **Renderização condicional**
   - Carregamento sob demanda (só gera quando solicitado)
   - JavaScript assíncrono para não bloquear UI

### Benchmarks Esperados

- Relatório mensal (5 aluguéis): ~50ms
- Relatório anual (60 aluguéis): ~600ms
- Exportação PDF: ~200ms
- Exportação Excel: ~150ms

---

## 🔐 Segurança

### Autenticação

Todos os endpoints exigem autenticação via cookie:
```python
current_user: Usuario = Depends(get_current_user_from_cookie)
```

### Autorização

- ✅ Qualquer usuário autenticado pode visualizar relatórios
- ❌ Não há restrição por proprietário (todos veem tudo)
- 💡 **Sugestão futura:** Filtrar automaticamente por proprietário do usuário logado

### Dados Sensíveis

- CPF/CNPJ exibidos apenas em relatórios de proprietário
- Valores financeiros visíveis para todos os usuários autenticados

---

## 📊 Métricas e KPIs

### KPIs Calculados

1. **Total Esperado**: Soma de todos os valores de aluguel do período
2. **Total Recebido**: Soma dos aluguéis marcados como `pago = true`
3. **Total Pendente**: `Total Esperado - Total Recebido`
4. **Taxa de Recebimento**: `(Total Recebido / Total Esperado) * 100`
5. **Variação Percentual**: `((Ano2 - Ano1) / Ano1) * 100`

### Fórmulas

```python
# Taxa de recebimento
taxa = (total_recebido / total_esperado * 100) if total_esperado > 0 else 0

# Variação percentual
variacao = ((valor_novo - valor_antigo) / valor_antigo * 100) if valor_antigo > 0 else 0

# Valor por proprietário
valor_prop = valor_total_imovel * (percentual_participacao / 100)
```

---

## 🚀 Roadmap Futuro

### Funcionalidades Planejadas

- [ ] **Gráficos interativos** (Chart.js)
  - Gráfico de barras mensal
  - Gráfico de pizza por imóvel
  - Linha temporal de receitas

- [ ] **Relatório de Despesas**
  - Consolidar gastos com condomínio, IPTU, etc.
  - Calcular margem líquida

- [ ] **Previsões**
  - Projeção de receitas futuras
  - Análise de tendências

- [ ] **Relatórios Personalizados**
  - Query builder visual
  - Salvar relatórios favoritos

- [ ] **Notificações**
  - Alertas de baixa taxa de recebimento
  - Lembretes de aluguéis pendentes

- [ ] **Agendamento**
  - Envio automático de relatórios por email
  - Geração periódica (diária, semanal, mensal)

---

## 📝 Changelog

### v1.0.0 (2025-11-02)

**Funcionalidades Iniciais:**
- ✅ Relatório Mensal com detalhamento por imóvel
- ✅ Relatório de Proprietário com cálculo de participações
- ✅ Relatório Anual com consolidação de 12 meses
- ✅ Relatório Comparativo entre anos
- ✅ Dados agregados para Dashboard
- ✅ Exportação para PDF (reportlab)
- ✅ Exportação para Excel (openpyxl)
- ✅ Interface web responsiva com dark mode
- ✅ Cards de resumo com KPIs
- ✅ Tabelas detalhadas
- ✅ Filtros por período e proprietário
- ✅ Integração completa com módulos existentes

---

## 📞 Suporte

### Problemas Comuns

Consultar seção [Troubleshooting](#-troubleshooting) acima.

### Documentação Relacionada

- [README_ALUGUEIS.md](./README_ALUGUEIS.md): Módulo de Aluguéis Mensais
- [README_PARTICIPACOES.md](./README_PARTICIPACOES.md): Módulo de Participações
- [README_PROPRIETARIOS.md](./README_PROPRIETARIOS.md): Módulo de Proprietários
- [README_IMOVEIS.md](./README_IMOVEIS.md): Módulo de Imóveis

### Contato

Para dúvidas ou sugestões, abra uma issue no repositório do projeto.

---

## ✅ Checklist de Implementação

- [x] Serviço de geração de relatórios (`RelatorioService`)
- [x] Endpoints da API (7 endpoints)
- [x] Interface web com tabs e filtros
- [x] Cards de resumo com estatísticas
- [x] Tabelas detalhadas
- [x] Exportação para PDF
- [x] Exportação para Excel
- [x] Integração com Aluguéis
- [x] Integração com Imóveis
- [x] Integração com Proprietários
- [x] Integração com Participações
- [x] Cálculo de participações
- [x] Dark mode
- [x] Responsividade mobile
- [x] Documentação completa

---

## 🎓 Exemplos Adicionais

### Exemplo 1: Consulta SQL Manual

```sql
-- Relatório mensal manual (novembro/2025)
SELECT 
    i.endereco,
    a.mes_referencia,
    a.pago,
    a.valor_aluguel + a.valor_condominio + a.valor_iptu + 
    a.valor_luz + a.valor_agua + a.valor_gas + 
    a.valor_internet + a.outros_valores AS valor_total
FROM alugueis_mensais a
JOIN imoveis i ON a.imovel_id = i.id
WHERE a.mes_referencia = '2025-11'
ORDER BY i.endereco;
```

### Exemplo 2: Relatório por Proprietário (SQL)

```sql
-- Receitas de um proprietário específico
SELECT 
    p.nome AS proprietario,
    i.endereco AS imovel,
    part.percentual,
    a.mes_referencia,
    (a.valor_aluguel + a.valor_condominio + a.valor_iptu + 
     a.valor_luz + a.valor_agua + a.valor_gas + 
     a.valor_internet + a.outros_valores) AS valor_total,
    ((a.valor_aluguel + a.valor_condominio + a.valor_iptu + 
      a.valor_luz + a.valor_agua + a.valor_gas + 
      a.valor_internet + a.outros_valores) * part.percentual / 100) AS valor_proprietario,
    a.pago
FROM proprietarios p
JOIN participacoes part ON p.id = part.proprietario_id
JOIN imoveis i ON part.imovel_id = i.id
JOIN alugueis_mensais a ON a.imovel_id = i.id AND a.mes_referencia = part.mes_referencia
WHERE p.id = 1 AND a.mes_referencia LIKE '2025%'
ORDER BY a.mes_referencia, i.endereco;
```

### Exemplo 3: Taxa de Recebimento Geral (SQL)

```sql
-- Taxa de recebimento do sistema
SELECT 
    COUNT(*) AS total_alugueis,
    SUM(CASE WHEN pago = TRUE THEN 1 ELSE 0 END) AS pagos,
    SUM(CASE WHEN pago = FALSE THEN 1 ELSE 0 END) AS pendentes,
    ROUND(
        SUM(CASE WHEN pago = TRUE THEN 1 ELSE 0 END)::NUMERIC / 
        COUNT(*)::NUMERIC * 100, 
        2
    ) AS taxa_recebimento
FROM alugueis_mensais
WHERE mes_referencia LIKE '2025%';
```

---

**Documentação gerada em:** 02/11/2025  
**Versão do sistema:** AlugueisV5  
**Módulo:** Relatórios Financeiros v1.0.0
