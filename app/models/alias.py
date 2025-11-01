from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Alias(Base):
    """Modelo de alias/apelido para nomes de proprietários"""
    __tablename__ = "aliases"

    id = Column(Integer, primary_key=True, index=True)
    
    # Nome alternativo encontrado no Excel
    nome_alias = Column(String(200), nullable=False, unique=True, index=True)
    
    # Usuário correspondente
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    usuario = relationship("Usuario", back_populates="aliases")

    def __repr__(self):
        return f"<Alias(id={self.id}, alias='{self.nome_alias}', usuario_id={self.usuario_id})>"
