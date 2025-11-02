# CRUD de Usuários - Documentação

## 📋 Visão Geral

Sistema completo de gestão de usuários do sistema com interface web, API REST e controle de permissões. Permite cadastrar, editar e gerenciar contas de usuários com diferentes níveis de acesso (admin/usuário).

---

## 🏗️ Arquitetura

### **Modelo de Dados** (`app/models/usuario.py`)

```python
class Usuario(Base):
    __tablename__ = "usuarios"
    
    # Identificação
    id: int (PK)
    nome: str (required)
    email: str (unique, required, indexed)
    hashed_password: str (required)
    
    # Dados Pessoais
    cpf: str (unique, nullable, indexed)  # XXX.XXX.XXX-XX
    telefone: str
    
    # Controle de Acesso
    is_admin: bool (default: false)
    is_active: bool (default: true)
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
```

**Relacionamentos:**
- `1:N` com **Participacao** (`participacoes`)
- `1:N` com **PermissaoFinanceira** (`permissoes_financeiras`)
- `1:N` com **Alias** (`aliases`)

> **Nota:** Usuários NÃO têm relacionamento direto com Imóveis. Use a tabela `proprietarios` para gestão de propriedades.

---

## 🔌 API Endpoints

Base URL: `/api/usuarios`

### 1. **Listar Usuários**
```http
GET /api/usuarios/
```

⚠️ **Apenas Administradores**

**Query Parameters:**
- `skip` (int): Paginação - offset (default: 0)
- `limit` (int): Paginação - limit (default: 100, max: 1000)
- `search` (str): Busca em nome, email, CPF
- `is_active` (bool): Filtro por status (true | false)
- `is_admin` (bool): Filtro por tipo (true | false)

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "nome": "Administrador",
    "email": "admin@sistema.com",
    "cpf": null,
    "telefone": null,
    "is_admin": true,
    "is_active": true,
    "created_at": "2025-11-01T10:00:00",
    "updated_at": "2025-11-01T10:00:00"
  }
]
```

**Permissões:**
- ❌ Apenas administradores podem listar usuários

---

### 2. **Criar Usuário**
```http
POST /api/usuarios/
```

⚠️ **Apenas Administradores**

**Body:**
```json
{
  "nome": "João Silva",
  "email": "joao@email.com",
  "password": "senha123",
  "cpf": "123.456.789-00",
  "telefone": "(11) 98765-4321",
  "is_admin": false,
  "is_active": true
}
```

**Validações:**
- `nome`: obrigatório, 3-200 caracteres
- `email`: obrigatório, único, formato válido
- `password`: obrigatório, mínimo 6 caracteres
- `cpf`: opcional, único se fornecido, padrão XXX.XXX.XXX-XX
- `telefone`: opcional
- `is_admin`: opcional, default false
- `is_active`: opcional, default true

**Response:** `201 Created`
```json
{
  "id": 5,
  "nome": "João Silva",
  "email": "joao@email.com",
  "cpf": "123.456.789-00",
  "telefone": "(11) 98765-4321",
  "is_admin": false,
  "is_active": true,
  "created_at": "2025-11-02T14:30:00",
  "updated_at": "2025-11-02T14:30:00"
}
```

**Errors:**
- `400 Bad Request`: Email ou CPF já cadastrado, validação falhou
- `401 Unauthorized`: Não autenticado
- `403 Forbidden`: Usuário não é admin

---

### 3. **Obter Usuário**
```http
GET /api/usuarios/{id}
```

⚠️ **Apenas Administradores**

**Response:** `200 OK`
```json
{
  "id": 5,
  "nome": "João Silva",
  ...
}
```

**Errors:**
- `404 Not Found`: Usuário não existe
- `403 Forbidden`: Usuário não é admin

---

### 4. **Atualizar Usuário**
```http
PUT /api/usuarios/{id}
```

⚠️ **Apenas Administradores**

**Body:** (todos os campos opcionais)
```json
{
  "nome": "João Silva Santos",
  "email": "joao.novo@email.com",
  "password": "novasenha123",
  "cpf": "987.654.321-00",
  "telefone": "(11) 91234-5678",
  "is_admin": true,
  "is_active": true
}
```

**Validações:**
- `password`: se fornecida, mínimo 6 caracteres
- `email`: se alterado, deve ser único
- `cpf`: se alterado, deve ser único
- Campos não fornecidos permanecem inalterados

**Response:** `200 OK`

**Errors:**
- `400 Bad Request`: Email/CPF duplicado, validação falhou
- `404 Not Found`: Usuário não existe
- `403 Forbidden`: Usuário não é admin

**Casos Especiais:**
- ⚠️ Admin não pode remover seu próprio status de admin (segurança)
- ⚠️ Alteração de senha só afeta o usuário editado (não requer senha antiga)

---

### 5. **Deletar Usuário**
```http
DELETE /api/usuarios/{id}
```

⚠️ **Apenas Administradores** | **Soft Delete** (marca como inativo)

**Response:** `204 No Content`

**Errors:**
- `400 Bad Request`: Não pode desativar a si mesmo
- `404 Not Found`: Usuário não existe
- `403 Forbidden`: Usuário não é admin

**Comportamento:**
- Marca `is_active = false`
- Usuário não pode fazer login
- Dados permanecem no banco (histórico preservado)
- Admin pode reativar posteriormente

---

### 6. **Reativar Usuário**
```http
POST /api/usuarios/{id}/reactivate
```

⚠️ **Apenas Administradores**

**Response:** `200 OK`
```json
{
  "id": 5,
  "nome": "João Silva",
  "is_active": true,
  ...
}
```

**Errors:**
- `400 Bad Request`: Usuário já está ativo
- `404 Not Found`: Usuário não existe
- `403 Forbidden`: Usuário não é admin

---

### 7. **Estatísticas**
```http
GET /api/usuarios/stats/summary
```

⚠️ **Apenas Administradores**

**Response:** `200 OK`
```json
{
  "total": 5,
  "ativos": 4,
  "inativos": 1,
  "admins": 1
}
```

**Cálculos:**
- `total`: Total de usuários no banco
- `ativos`: Usuários com `is_active = true`
- `inativos`: Usuários com `is_active = false`
- `admins`: Usuários com `is_admin = true`

---

### 8. **Listar Proprietários (Legacy)**
```http
GET /api/usuarios/proprietarios
```

⚠️ **Endpoint Legado** - Use `/api/proprietarios/` em vez disso

**Nota:** Este endpoint lista usuários que eram proprietários antes da migração para a tabela `proprietarios`. Mantido por compatibilidade.

---

## 🎨 Interface Web

Acesse: **`http://localhost:8000/usuarios`**

⚠️ **Acesso Restrito:** Apenas administradores podem acessar esta página.

### **Funcionalidades:**

#### 📊 **Estatísticas (4 Cards)**
- Total de usuários
- Ativos
- Inativos
- Administradores

#### 🔍 **Filtros**
- **Busca:** Nome, email, CPF (debounce 500ms)
- **Tipo:** Todos / Administradores / Usuários
- **Status:** Todos / Ativos / Inativos

#### 📝 **Tabela**
Colunas:
- Nome
- Email
- CPF
- Tipo (badge roxo=admin, azul=usuário)
- Status (badge verde=ativo, cinza=inativo)
- Ações (editar/desativar/reativar)

#### ➕ **Modal de Cadastro/Edição**

**Modo Criação:**
1. **Dados Básicos**
   - Nome Completo *
   - Email *
   - CPF
   - Telefone

2. **Senha** (obrigatória)
   - Senha * (mínimo 6 caracteres)
   - Confirmar Senha *
   - Validação de igualdade

3. **Permissões**
   - Checkbox "Administrador do Sistema"
   - Checkbox "Usuário Ativo"

**Modo Edição:**
1. **Dados Básicos**
   - Nome Completo *
   - Email *
   - CPF
   - Telefone

2. **Alterar Senha** (opcional)
   - Checkbox "Alterar senha do usuário"
   - Nova Senha * (condicional)
   - Confirmar Nova Senha * (condicional)
   - Campos aparecem/escondem dinamicamente

3. **Permissões**
   - Checkbox "Administrador do Sistema"
   - Checkbox "Usuário Ativo"

#### ⚙️ **Comportamento Dinâmico**
- **Validação de Senha:**
  - Mínimo 6 caracteres
  - Senhas devem ser iguais
  - Mensagem de erro via toast
- **Toggle Alterar Senha:**
  - Checkbox controla visibilidade dos campos
  - Campos obrigatórios quando visíveis
- **Botão Reativar:**
  - Aparece apenas para usuários inativos
  - Cor verde (check_circle icon)
- **Confirmações:**
  - Desativar usuário: "Deseja realmente desativar..."
  - Reativar usuário: "Deseja realmente reativar..."

---

## 🧪 Testando

### **1. Via CURL**

```bash
# Login como admin
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sistema.com","password":"admin123"}' \
  -c cookies.txt

# Listar usuários
curl -X GET "http://localhost:8000/api/usuarios/" \
  -b cookies.txt

# Buscar por nome
curl -X GET "http://localhost:8000/api/usuarios/?search=João" \
  -b cookies.txt

# Filtrar apenas admins
curl -X GET "http://localhost:8000/api/usuarios/?is_admin=true" \
  -b cookies.txt

# Criar usuário
curl -X POST http://localhost:8000/api/usuarios/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "nome": "Maria Santos",
    "email": "maria@email.com",
    "password": "senha123",
    "cpf": "987.654.321-00",
    "telefone": "(11) 91234-5678",
    "is_admin": false,
    "is_active": true
  }'

# Atualizar usuário (alterar email e tornar admin)
curl -X PUT http://localhost:8000/api/usuarios/5 \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "email": "maria.santos@email.com",
    "is_admin": true
  }'

# Alterar senha de usuário
curl -X PUT http://localhost:8000/api/usuarios/5 \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "password": "novasenha456"
  }'

# Desativar usuário
curl -X DELETE http://localhost:8000/api/usuarios/5 \
  -b cookies.txt

# Reativar usuário
curl -X POST http://localhost:8000/api/usuarios/5/reactivate \
  -b cookies.txt

# Estatísticas
curl -X GET http://localhost:8000/api/usuarios/stats/summary \
  -b cookies.txt
```

### **2. Via Interface**

1. Acesse: `http://localhost:8000/login`
2. Login: `admin@sistema.com` / `admin123`
3. Navegue para: **Usuários**
4. **Criar Usuário:**
   - Clique em "Novo Usuário"
   - Preencha: Nome, Email, Senha (obrigatórios)
   - Opcional: CPF, Telefone
   - Marque "Administrador" se necessário
   - Clique em "Salvar"
5. **Editar Usuário:**
   - Clique no ícone de editar (lápis)
   - Altere campos desejados
   - Para alterar senha: marque checkbox e preencha campos
   - Clique em "Salvar"
6. **Desativar Usuário:**
   - Clique no ícone de delete (lixeira)
   - Confirme a ação
   - Usuário fica inativo (cinza)
7. **Reativar Usuário:**
   - Para usuários inativos, aparece ícone verde
   - Clique e confirme
   - Usuário volta a ser ativo

---

## 📦 Estrutura de Arquivos

```
AlugueisV5/
├── app/
│   ├── models/
│   │   └── usuario.py                # Modelo SQLAlchemy
│   ├── routes/
│   │   └── usuarios.py               # 8 endpoints REST
│   ├── templates/
│   │   └── usuarios.html             # Interface completa (550 linhas)
│   └── main.py                       # Rota /usuarios com proteção admin
└── README_USUARIOS.md                # Esta documentação
```

---

## 🔐 Permissões e Segurança

### **Matriz de Permissões:**

| Ação | Admin | Usuário | Público |
|------|-------|---------|---------|
| Listar | ✅ | ❌ | ❌ |
| Criar | ✅ | ❌ | ❌ |
| Editar | ✅ | ❌ | ❌ |
| Ver Detalhes | ✅ | ❌ | ❌ |
| Deletar | ✅ | ❌ | ❌ |
| Reativar | ✅ | ❌ | ❌ |
| Estatísticas | ✅ | ❌ | ❌ |

### **Regras de Segurança:**

1. **Proteção de Senha:**
   - Senhas são hasheadas com bcrypt
   - Nunca retornadas na API (campo `hashed_password` não exposto)
   - Validação mínimo 6 caracteres

2. **Proteção de Admin:**
   - Admin não pode remover seu próprio status de admin
   - Admin não pode desativar a si mesmo
   - Apenas admins podem criar outros admins

3. **Unicidade:**
   - Email deve ser único no sistema
   - CPF (se fornecido) deve ser único

4. **Soft Delete:**
   - Usuários nunca são deletados fisicamente
   - `DELETE` marca `is_active = false`
   - Preserva histórico de ações no sistema

5. **Proteção de Rota:**
   - `/usuarios` redireciona para `/dashboard` se não for admin
   - API retorna `403 Forbidden` para não-admins

---

## 💡 Funcionalidades Especiais

### **1. Duplo Modo do Modal (Criar/Editar)**

```javascript
// Modo Criação
function openModal() {
    // Mostra seção de senha obrigatória
    document.getElementById('password-section').classList.remove('hidden');
    document.getElementById('change-password-section').classList.add('hidden');
    document.getElementById('password').required = true;
}

// Modo Edição
async function editarUsuario(id) {
    // Esconde senha obrigatória, mostra alterar senha (opcional)
    document.getElementById('password-section').classList.add('hidden');
    document.getElementById('change-password-section').classList.remove('hidden');
    document.getElementById('password').required = false;
}
```

### **2. Toggle Alterar Senha**

```javascript
function togglePasswordChange() {
    const checkbox = document.getElementById('change-password-toggle');
    const fields = document.getElementById('password-fields');
    
    if (checkbox.checked) {
        // Mostrar campos e tornar obrigatórios
        fields.classList.remove('hidden');
        document.getElementById('new-password').required = true;
    } else {
        // Esconder e limpar
        fields.classList.add('hidden');
        document.getElementById('new-password').required = false;
        document.getElementById('new-password').value = '';
    }
}
```

### **3. Validação de Senha**

```javascript
// Na criação
const password = document.getElementById('password').value;
const passwordConfirm = document.getElementById('password-confirm').value;

if (password.length < 6) {
    showToast('A senha deve ter no mínimo 6 caracteres', 'error');
    return;
}

if (password !== passwordConfirm) {
    showToast('As senhas não conferem', 'error');
    return;
}
```

### **4. Botão Reativar Condicional**

```html
<!-- Aparece apenas para usuários inativos -->
${!usuario.is_active ? `
    <button onclick="reativarUsuario(${usuario.id}, '${usuario.nome}')" 
        class="text-green-400 hover:text-green-300" title="Reativar">
        <span class="material-symbols-outlined">check_circle</span>
    </button>
` : ''}
```

---

## 🎯 Próximos Passos

- [ ] Adicionar **foto de perfil** do usuário
- [ ] Implementar **alteração de senha própria** (sem admin)
- [ ] Criar **perfil do usuário** (página /perfil)
- [ ] Adicionar **logs de ações** (audit trail)
- [ ] Implementar **2FA** (autenticação em dois fatores)
- [ ] Criar **roles** personalizadas (além de admin/usuário)
- [ ] Adicionar **permissões granulares** por módulo
- [ ] Implementar **sessões ativas** (ver logins ativos)
- [ ] Criar **recuperação de senha** via email
- [ ] Adicionar **histórico de logins**

---

## 🐛 Troubleshooting

### Erro: "Email já cadastrado"
**Solução:** Verifique se o email já existe no banco:
```sql
SELECT id, nome, email, is_active FROM usuarios WHERE email = 'email@exemplo.com';
```

### Erro: "CPF já cadastrado"
**Solução:** Verifique duplicatas:
```sql
SELECT id, nome, cpf FROM usuarios WHERE cpf = '123.456.789-00';
```

### Não consigo acessar /usuarios
**Solução:**
1. Verifique se está logado como admin
2. Consulte no banco: `SELECT is_admin FROM usuarios WHERE email = 'seu@email.com';`
3. Se não for admin, peça para um admin alterar suas permissões

### Admin removeu próprio status de admin
**Solução:**
```sql
-- Restaurar status de admin via SQL
UPDATE usuarios SET is_admin = true WHERE email = 'admin@sistema.com';
```

### Esqueci a senha do admin
**Solução:**
```python
# Script Python para resetar senha
from app.core.auth import get_password_hash
from app.core.database import get_db
from app.models.usuario import Usuario

db = next(get_db())
admin = db.query(Usuario).filter(Usuario.email == "admin@sistema.com").first()
admin.hashed_password = get_password_hash("novasenha123")
db.commit()
```

### Modal não abre/fecha
**Solução:**
1. Verifique console do navegador (F12) para erros JavaScript
2. Limpe cache (Ctrl+F5)
3. Verifique se utils.js está carregando corretamente

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs: `docker-compose logs app`
2. Consulte a documentação da API: `http://localhost:8000/docs`
3. Teste endpoints com curl ou Postman

**Endpoints Relacionados:**
- Autenticação: `/api/auth/login`, `/api/auth/logout`
- Proprietários: `/api/proprietarios/` (ver README_PROPRIETARIOS.md)
- Imóveis: `/api/imoveis/` (ver README_IMOVEIS.md)

---

## 🔒 Boas Práticas de Segurança

1. **Senhas:**
   - Use senhas fortes (mínimo 6 caracteres, recomendado 12+)
   - Não reutilize senhas de outros sistemas
   - Altere senhas periodicamente

2. **Administradores:**
   - Mantenha o mínimo de admins necessário
   - Revise periodicamente quem tem acesso admin
   - Desative usuários que saíram da empresa

3. **Auditoria:**
   - Monitore criações/alterações de usuários admin
   - Revise logs de acesso periodicamente
   - Investigue acessos não autorizados

4. **Dados:**
   - Não compartilhe credenciais
   - Use HTTPS em produção
   - Backup regular do banco de dados

---

**Versão:** 1.0  
**Última Atualização:** 02/11/2025  
**Autor:** Sistema AlugueisV5
