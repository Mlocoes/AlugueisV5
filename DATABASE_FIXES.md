# Correções do Banco de Dados

## 06/11/2025 - Criação da tabela participacao_versoes

### Problema
A aplicação estava retornando erro 500 ao acessar `/api/participacoes-versoes/` porque a tabela `participacao_versoes` não existia no banco de dados, apesar do modelo estar definido.

### Solução
Criação manual da tabela no banco de dados:

```sql
CREATE TABLE IF NOT EXISTS participacao_versoes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    dados_json TEXT NOT NULL,
    observacoes VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES usuarios(id)
);

CREATE INDEX IF NOT EXISTS ix_participacao_versoes_id ON participacao_versoes(id);

UPDATE alembic_version SET version_num = 'add_participacao_versoes';
```

### Comandos executados
```bash
docker compose exec -T db psql -U alugueis_user -d alugueis_v5 -c "CREATE TABLE IF NOT EXISTS participacao_versoes (...)"
docker compose exec -T db psql -U alugueis_user -d alugueis_v5 -c "UPDATE alembic_version SET version_num = 'add_participacao_versoes';"
docker compose restart app
```

### Status
✅ Tabela criada com sucesso
✅ Endpoint funcionando (retorna 401 quando não autenticado, conforme esperado)
✅ Aplicação rodando normalmente

## 06/11/2025 - Correção do endpoint de proprietários

### Problema 1
Erro 500: `AttributeError: 'Proprietario' object has no attribute 'imoveis'`

### Solução 1
O modelo `Proprietario` não tem relacionamento direto com `Imovel`, apenas através de `Participacao`.
Mudança: `len(prop.imoveis)` → `len(set(p.imovel_id for p in prop.participacoes))`

### Problema 2
Erro 500: `AttributeError: 'Participacao' object has no attribute 'ativa'`

### Solução 2
O modelo `Participacao` não possui o campo `ativa` no schema atual.
Mudança: `len(set(p.imovel_id for p in prop.participacoes if p.ativa))` → `len(set(p.imovel_id for p in prop.participacoes))`

### Commits
- `1a12af2`: Primeira tentativa de correção
- `355d42a`: Correção definitiva removendo verificação do campo inexistente
