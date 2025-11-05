from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Participacao(Base):
    """Modelo de participação de proprietário em imóvel"""
    __tablename__ = "participacoes"

    id = Column(Integer, primary_key=True, index=True)
    
    # Referências
    imovel_id = Column(Integer, ForeignKey("imoveis.id"), nullable=False, index=True)
    proprietario_id = Column(Integer, ForeignKey("proprietarios.id"), nullable=False, index=True)
    
    # Período (formato: YYYY-MM)
    mes_referencia = Column(String(7), nullable=False, index=True)
    
    # Valores
    percentual = Column(Float, nullable=False)  # 0-100
    
    # Observações
    observacoes = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    imovel = relationship("Imovel", back_populates="participacoes")
    proprietario = relationship("Proprietario", back_populates="participacoes")

    def __repr__(self):
        return f"<Participacao(id={self.id}, imovel_id={self.imovel_id}, proprietario_id={self.proprietario_id}, percentual={self.percentual}%)>"
