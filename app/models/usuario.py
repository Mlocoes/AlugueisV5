from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Usuario(Base):
    """Modelo de usuário do sistema"""
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), nullable=False)
    email = Column(String(200), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    cpf = Column(String(14), unique=True, nullable=True, index=True)
    telefone = Column(String(20), nullable=True)
    
    # Controle de acesso
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    imoveis = relationship("Imovel", back_populates="proprietario")
    participacoes = relationship("Participacao", back_populates="proprietario")
    permissoes_financeiras = relationship("PermissaoFinanceira", back_populates="usuario")
    aliases = relationship("Alias", back_populates="usuario")

    def __repr__(self):
        return f"<Usuario(id={self.id}, nome='{self.nome}', email='{self.email}')>"
