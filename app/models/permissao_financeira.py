from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class PermissaoFinanceira(Base):
    """Modelo de permissão financeira para visualização de dados"""
    __tablename__ = "permissoes_financeiras"

    id = Column(Integer, primary_key=True, index=True)
    
    # Usuário que recebe a permissão
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    
    # Tipo de permissão
    tipo_permissao = Column(String(50), nullable=False)  # 'visualizar_proprios', 'visualizar_todos', 'editar_todos'
    
    # Status
    ativa = Column(Boolean, default=True)
    
    # Descrição opcional
    descricao = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    usuario = relationship("Usuario", back_populates="permissoes_financeiras")

    def __repr__(self):
        return f"<PermissaoFinanceira(id={self.id}, usuario_id={self.usuario_id}, tipo='{self.tipo_permissao}')>"
