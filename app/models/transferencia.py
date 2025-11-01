from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Transferencia(Base):
    """Modelo de transferência entre proprietários"""
    __tablename__ = "transferencias"

    id = Column(Integer, primary_key=True, index=True)
    
    # Referências de usuários
    origem_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    destino_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    
    # Período (formato: YYYY-MM)
    mes_referencia = Column(String(7), nullable=False, index=True)
    
    # Valor da transferência
    valor = Column(Float, nullable=False)
    
    # Status
    confirmada = Column(Boolean, default=False)
    data_confirmacao = Column(Date, nullable=True)
    
    # Descrição
    descricao = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    origem = relationship("Usuario", foreign_keys=[origem_id])
    destino = relationship("Usuario", foreign_keys=[destino_id])

    def __repr__(self):
        return f"<Transferencia(id={self.id}, origem_id={self.origem_id}, destino_id={self.destino_id}, valor={self.valor})>"
