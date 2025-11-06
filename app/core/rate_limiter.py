"""
Sistema de Rate Limiting e Proteção contra Força Bruta
Implementa limitação de taxa para proteger endpoints sensíveis
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
from typing import Dict, Optional
import time
import logging
from collections import defaultdict

# Logger específico para segurança
security_logger = logging.getLogger("security")
security_logger.setLevel(logging.INFO)

# Handler para salvar logs de segurança em arquivo
# security_handler = logging.FileHandler("logs/security.log")
# security_handler.setFormatter(
#     logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# )
# security_logger.addHandler(security_handler)


# Configuração do Limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],  # Limite padrão global
    storage_uri="memory://",  # Usar memória (para produção, usar Redis)
)


# Sistema de Blacklist Temporária
class IPBlacklist:
    """Gerencia blacklist temporária de IPs suspeitos"""
    
    def __init__(self):
        self.failed_attempts: Dict[str, list] = defaultdict(list)
        self.blacklist: Dict[str, float] = {}  # IP -> timestamp de desbloqueio
        
        # Configurações
        self.MAX_ATTEMPTS = 5  # Tentativas antes de bloquear
        self.ATTEMPT_WINDOW = 300  # Janela de tempo (5 minutos)
        self.BLACKLIST_DURATION = 900  # Duração do bloqueio (15 minutos)
    
    def record_failed_attempt(self, ip: str, endpoint: str) -> None:
        """Registra tentativa falha de autenticação"""
        current_time = time.time()
        
        # Limpar tentativas antigas (fora da janela)
        self.failed_attempts[ip] = [
            t for t in self.failed_attempts[ip]
            if current_time - t < self.ATTEMPT_WINDOW
        ]
        
        # Adicionar nova tentativa
        self.failed_attempts[ip].append(current_time)
        
        # Log de segurança
        security_logger.warning(
            f"Failed authentication attempt from {ip} on {endpoint}. "
            f"Total attempts: {len(self.failed_attempts[ip])}"
        )
        
        # Verificar se deve bloquear
        if len(self.failed_attempts[ip]) >= self.MAX_ATTEMPTS:
            self.block_ip(ip)
    
    def block_ip(self, ip: str) -> None:
        """Bloqueia IP temporariamente"""
        unblock_time = time.time() + self.BLACKLIST_DURATION
        self.blacklist[ip] = unblock_time
        
        security_logger.error(
            f"IP {ip} has been BLOCKED for {self.BLACKLIST_DURATION}s "
            f"due to excessive failed attempts"
        )
    
    def is_blocked(self, ip: str) -> bool:
        """Verifica se IP está bloqueado"""
        if ip not in self.blacklist:
            return False
        
        # Verificar se ainda está bloqueado
        current_time = time.time()
        if current_time < self.blacklist[ip]:
            return True
        
        # Tempo de bloqueio expirou, remover da blacklist
        del self.blacklist[ip]
        self.failed_attempts[ip] = []
        security_logger.info(f"IP {ip} has been unblocked")
        return False
    
    def clear_attempts(self, ip: str) -> None:
        """Limpa tentativas falhas após sucesso"""
        if ip in self.failed_attempts:
            del self.failed_attempts[ip]
        if ip in self.blacklist:
            del self.blacklist[ip]


# Instância global da blacklist
ip_blacklist = IPBlacklist()


async def check_ip_blacklist(request: Request) -> None:
    """
    Middleware para verificar se IP está na blacklist
    Deve ser chamado antes de processar requisição
    """
    client_ip = get_remote_address(request)
    
    if ip_blacklist.is_blocked(client_ip):
        security_logger.warning(f"Blocked request from blacklisted IP: {client_ip}")
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Too many failed attempts",
                "message": "Your IP has been temporarily blocked due to excessive failed login attempts. Please try again later.",
                "retry_after": int(ip_blacklist.blacklist[client_ip] - time.time())
            }
        )


# Limites específicos para diferentes tipos de endpoints
RATE_LIMITS = {
    "auth_strict": "5/minute",      # Login, registro (muito restritivo)
    "auth_moderate": "10/minute",   # Refresh token (moderado)
    "api_standard": "30/minute",    # Endpoints normais de API
    "api_read": "60/minute",        # Apenas leitura (mais permissivo)
    "public": "20/minute",          # Endpoints públicos
}


def get_rate_limit(limit_type: str = "api_standard") -> str:
    """Retorna o limite configurado para o tipo especificado"""
    return RATE_LIMITS.get(limit_type, "30/minute")


# Handler customizado para rate limit exceeded
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handler customizado quando rate limit é excedido"""
    client_ip = get_remote_address(request)
    
    security_logger.warning(
        f"Rate limit exceeded for IP {client_ip} on {request.url.path}"
    )
    
    return HTTPException(
        status_code=429,
        detail={
            "error": "Rate limit exceeded",
            "message": "Too many requests. Please slow down and try again later.",
            "retry_after": exc.detail
        }
    )
