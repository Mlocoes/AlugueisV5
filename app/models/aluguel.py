from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class AluguelMensal(Base):
    """Modelo de aluguel mensal de imóvel"""
    __tablename__ = "alugueis_mensais"

    id = Column(Integer, primary_key=True, index=True)
    
    # Referências
    imovel_id = Column(Integer, ForeignKey("imoveis.id"), nullable=False, index=True)
    proprietario_id = Column(Integer, ForeignKey("proprietarios.id"), nullable=True, index=True)  # Novo campo
    
    # Data de referência (date completo)
    data_referencia = Column(Date, nullable=True, index=True)  # Novo campo
    
    # Valor específico do proprietário (quando aplicável)
    valor_proprietario = Column(Float, nullable=True)  # Novo campo
    taxa_administracao = Column(Float, nullable=True, default=0.0)  # Novo campo
    
    # Período (formato: YYYY-MM) - mantido para compatibilidade
    mes_referencia = Column(String(7), nullable=False, index=True)
    
    # Valores
    valor_total = Column(Float, nullable=False, default=0.0)
    
    # Status de pagamento
    pago = Column(Boolean, default=False)
    data_pagamento = Column(Date, nullable=True)
    
    # Observações
    observacoes = Column(String(1000), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Alias para compatibilidade

    # Relacionamentos
    imovel = relationship("Imovel", back_populates="alugueis")

    def __repr__(self):
        return f"<AluguelMensal(id={self.id}, imovel_id={self.imovel_id}, mes='{self.mes_referencia}', total={self.valor_total})>"
