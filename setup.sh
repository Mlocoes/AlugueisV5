#!/bin/bash

# Script de inicialização do AlugueisV5
# Executa setup completo do projeto

set -e  # Para em caso de erro

echo "🚀 AlugueisV5 - Setup Automático"
echo "================================"
echo ""

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Função de log
log_info() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# 1. Verificar Docker
echo "1. Verificando Docker..."
if ! command -v docker &> /dev/null; then
    log_error "Docker não encontrado. Instale: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose não encontrado. Instale: https://docs.docker.com/compose/install/"
    exit 1
fi
log_info "Docker OK"

# 2. Criar .env se não existir
echo ""
echo "2. Configurando variáveis de ambiente..."
if [ ! -f .env ]; then
    cp .env.example .env
    log_info "Arquivo .env criado"
else
    log_warn ".env já existe, mantendo configurações"
fi

# 3. Parar containers existentes
echo ""
echo "3. Limpando containers antigos..."
docker-compose down -v 2>/dev/null || true
log_info "Containers limpos"

# 4. Iniciar containers
echo ""
echo "4. Iniciando containers..."
docker-compose up -d
log_info "Containers iniciados"

# 5. Aguardar banco de dados
echo ""
echo "5. Aguardando banco de dados ficar pronto..."
sleep 5

MAX_RETRIES=30
RETRY_COUNT=0
while ! docker-compose exec -T db pg_isready -U alugueis_user &> /dev/null; do
    RETRY_COUNT=$((RETRY_COUNT+1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        log_error "Timeout aguardando banco de dados"
        docker-compose logs db
        exit 1
    fi
    echo -n "."
    sleep 1
done
echo ""
log_info "Banco de dados pronto"

# 6. Criar migração inicial
echo ""
echo "6. Criando migração inicial..."
docker-compose exec -T app alembic revision --autogenerate -m "initial migration" 2>/dev/null || {
    log_warn "Migração já existe ou erro ao criar"
}

# 7. Aplicar migrações
echo ""
echo "7. Aplicando migrações..."
docker-compose exec -T app alembic upgrade head
log_info "Migrações aplicadas"

# 8. Criar admin
echo ""
echo "8. Criando usuário administrador..."
docker-compose exec -T app python create_admin.py
log_info "Admin criado"

# 9. Verificar status
echo ""
echo "9. Verificando aplicação..."
sleep 2

if curl -s http://localhost:8000/health | grep -q "healthy"; then
    log_info "Aplicação está rodando!"
else
    log_error "Aplicação não está respondendo"
    echo ""
    echo "Logs do container:"
    docker-compose logs --tail=20 app
    exit 1
fi

# Sucesso!
echo ""
echo "================================"
echo -e "${GREEN}✅ Setup concluído com sucesso!${NC}"
echo ""
echo "📍 Acesse a aplicação:"
echo "   🌐 Interface: http://localhost:8000"
echo "   📚 API Docs:  http://localhost:8000/docs"
echo ""
echo "🔑 Credenciais padrão:"
echo "   Email: admin@sistema.com"
echo "   Senha: admin123"
echo ""
echo "📝 Comandos úteis:"
echo "   Ver logs:  docker-compose logs -f app"
echo "   Parar:     docker-compose down"
echo "   Reiniciar: docker-compose restart"
echo ""
echo "🎉 Bom desenvolvimento!"
echo "================================"
