from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Proprietario(Base):
    """Modelo de Proprietário (pode ser pessoa física ou jurídica)"""
    __tablename__ = "proprietarios"

    id = Column(Integer, primary_key=True, index=True)
    
    # Tipo de pessoa
    tipo_pessoa = Column(String(20), nullable=False)  # "fisica" ou "juridica"
    
    # Dados pessoais (pessoa física)
    nome = Column(String(200), nullable=False, index=True)
    cpf = Column(String(14), nullable=True, unique=True, index=True)  # XXX.XXX.XXX-XX
    rg = Column(String(20), nullable=True)
    
    # Dados empresariais (pessoa jurídica)
    razao_social = Column(String(200), nullable=True)
    nome_fantasia = Column(String(200), nullable=True)
    cnpj = Column(String(18), nullable=True, unique=True, index=True)  # XX.XXX.XXX/XXXX-XX
    inscricao_estadual = Column(String(20), nullable=True)
    
    # Contato
    email = Column(String(100), nullable=True, index=True)
    telefone = Column(String(20), nullable=True)
    celular = Column(String(20), nullable=True)
    
    # Endereço
    endereco = Column(String(500), nullable=True)
    numero = Column(String(10), nullable=True)
    complemento = Column(String(100), nullable=True)
    bairro = Column(String(100), nullable=True)
    cidade = Column(String(100), nullable=True)
    estado = Column(String(2), nullable=True)
    cep = Column(String(10), nullable=True)
    
    # Dados bancários
    banco = Column(String(100), nullable=True)
    agencia = Column(String(20), nullable=True)
    conta = Column(String(20), nullable=True)
    tipo_conta = Column(String(20), nullable=True)  # "corrente" ou "poupanca"
    pix = Column(String(100), nullable=True)
    
    # Observações
    observacoes = Column(Text, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    imoveis = relationship("Imovel", back_populates="proprietario", cascade="all, delete-orphan")
    participacoes = relationship("Participacao", back_populates="proprietario", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Proprietario(id={self.id}, nome='{self.nome}', tipo='{self.tipo_pessoa}')>"
