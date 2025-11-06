from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class ParticipacaoVersao(Base):
    """Modelo de versão de conjunto de participações"""
    __tablename__ = "participacao_versoes"

    id = Column(Integer, primary_key=True, index=True)
    
    # Nome/descrição da versão
    nome = Column(String(200), nullable=False)
    
    # JSON com os dados da tabela: {imovel_id: {proprietario_id: percentual}}
    dados_json = Column(Text, nullable=False)
    
    # Observações
    observacoes = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    # Relacionamentos
    usuario = relationship("Usuario")

    def __repr__(self):
        return f"<ParticipacaoVersao(id={self.id}, nome={self.nome})>"
