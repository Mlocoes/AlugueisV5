"""
Configurações da aplicação
Carrega variáveis de ambiente e define configurações globais
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Database
    DATABASE_URL: str = "postgresql://alugueisv5:alugueisv5_password@db:5432/alugueisv5_db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Admin
    ADMIN_EMAIL: str = "admin@sistema.com"
    ADMIN_PASSWORD: str = "admin123"
    
    # App
    APP_NAME: str = "AlugueisV5"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instância global de configurações
settings = Settings()
