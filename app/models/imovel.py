from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Imovel(Base):
    """Modelo de imóvel"""
    __tablename__ = "imoveis"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), nullable=False, index=True)
    endereco = Column(String(500), nullable=True)
    cidade = Column(String(100), nullable=True)
    estado = Column(String(2), nullable=True)
    cep = Column(String(10), nullable=True)
    
    # Características do imóvel
    tipo = Column(String(50), nullable=True)  # Comercial, Residencial, etc
    area_total = Column(Float, nullable=True)
    area_construida = Column(Float, nullable=True)
    
    # Dados financeiros
    valor_catastral = Column(Float, nullable=True)
    valor_mercado = Column(Float, nullable=True)
    valor_aluguel = Column(Float, nullable=True)
    valor_condominio = Column(Float, nullable=True)
    valor_iptu = Column(Float, nullable=True)
    
    # Status
    status = Column(String(20), nullable=False, default='disponivel')  # 'disponivel' ou 'alugado'
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    alugueis = relationship("AluguelMensal", back_populates="imovel", cascade="all, delete-orphan")
    participacoes = relationship("Participacao", back_populates="imovel", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Imovel(id={self.id}, nome='{self.nome}')>"
