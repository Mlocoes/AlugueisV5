# Fix para Valores Incorretos no Dashboard

## Problema

Os cards de "Valor Recebido" no Dashboard estavam mostrando valores multiplicados por 1000 devido a um problema de formatação de números brasileiros.

### Causa Raiz

O problema estava na função `parse_valor` em `app/services/import_service.py`. A função original apenas substituía vírgulas por pontos sem considerar o contexto completo da formatação brasileira de números:

**Formato Brasileiro vs Internacional:**
- 🇧🇷 Brasil: `2.800,50` (ponto para milhares, vírgula para decimal)
- 🇺🇸 Internacional: `2,800.50` (vírgula para milhares, ponto para decimal)

**Exemplo do Bug:**
```
Entrada: "2.800,50" (dois mil e oitocentos reais e cinquenta centavos)
Função antiga: replace(',', '.') → "2.800.50"
Resultado: float("2.800.50") → ERRO ou valor incorreto
```

## Solução Implementada

A função `parse_valor` foi reescrita para:

1. **Detectar automaticamente** o formato do número baseado nos separadores presentes
2. **Tratar corretamente** ambos os formatos (brasileiro e internacional)
3. **Distinguir** entre separadores de milhares e decimais

### Exemplos de Casos Tratados

| Entrada | Formato | Resultado |
|---------|---------|-----------|
| `2,8` | BR decimal | 2.8 |
| `2.8` | INT decimal | 2.8 |
| `2.800` | BR milhares | 2800.0 |
| `2,800` | INT milhares | 2800.0 |
| `2.800,50` | BR completo | 2800.5 |
| `2,800.50` | INT completo | 2800.5 |
| `R$ 2.800,50` | BR com moeda | 2800.5 |
| `1.234.567,89` | BR grande | 1234567.89 |
| `1,234,567.89` | INT grande | 1234567.89 |

## O que foi Corrigido

### ✅ Arquivo: `app/services/import_service.py`

- Função `parse_valor` completamente reescrita
- Suporta detecção automática de formato
- Trata casos ambíguos usando contexto (ex: número de dígitos após separador)
- Todos os testes passando

### ✅ Script de Migração: `fix_incorrect_values.py`

Um script foi criado para corrigir dados já existentes no banco que possam ter sido importados com o bug anterior:

```bash
# Ver o que seria corrigido (sem fazer alterações)
python fix_incorrect_values.py --dry-run

# Aplicar correções (com confirmação)
python fix_incorrect_values.py

# Aplicar correções sem confirmação
python fix_incorrect_values.py --force
```

## Como Usar

### Para Novas Importações

As novas importações via Excel/CSV já usarão a função corrigida automaticamente. Nenhuma ação necessária.

### Para Dados Existentes

Se você tem dados no banco que foram importados antes desta correção e estão com valores incorretos:

1. **Faça backup do banco de dados**
2. Execute o script de análise:
   ```bash
   python fix_incorrect_values.py --dry-run
   ```
3. Revise as correções sugeridas
4. Se estiver tudo correto, aplique:
   ```bash
   python fix_incorrect_values.py
   ```

### Reimportar Dados

Alternativamente, você pode reimportar os dados do Excel usando a funcionalidade de importação do sistema, que agora usa a função corrigida.

## Prevenção

Para evitar problemas futuros:

1. **Use os campos de entrada do sistema** que já validam e formatam corretamente
2. **Ao importar Excel**, use o formato brasileiro consistentemente (2.800,50)
3. **Evite misturar formatos** no mesmo arquivo Excel

## Testes

A função `parse_valor` foi testada com 11 casos de teste cobrindo:
- ✅ Formato brasileiro com decimais
- ✅ Formato internacional com decimais  
- ✅ Formato brasileiro com milhares
- ✅ Formato internacional com milhares
- ✅ Formato completo (milhares + decimais) em ambos os formatos
- ✅ Valores com símbolo de moeda
- ✅ Números grandes com múltiplos separadores
- ✅ Valores pequenos (centavos)

Todos os testes passaram com 100% de sucesso.

## Suporte

Se você encontrar valores ainda incorretos após seguir este guia, verifique:

1. Os valores foram importados antes ou depois da correção?
2. O script de migração foi executado?
3. Os logs de importação mostram algum erro?

Para suporte adicional, abra uma issue no GitHub com:
- Exemplo de valor incorreto (esperado vs atual)
- Como o valor foi inserido (manual, importação, etc.)
- Logs relevantes se disponíveis
