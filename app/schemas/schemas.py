"""Schemas Pydantic para validação de dados"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime, date


# ===== USUARIO SCHEMAS =====

class UsuarioBase(BaseModel):
    nome: str = Field(..., min_length=3, max_length=200)
    email: EmailStr
    cpf: Optional[str] = None
    telefone: Optional[str] = None


class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=6)


class UsuarioUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=3, max_length=200)
    email: Optional[EmailStr] = None
    cpf: Optional[str] = None
    telefone: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None


class UsuarioResponse(UsuarioBase):
    id: int
    is_admin: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== IMOVEL SCHEMAS =====

class ImovelBase(BaseModel):
    nome: str = Field(..., min_length=3, max_length=200)
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = Field(None, max_length=2)
    cep: Optional[str] = None
    valor_aluguel: Optional[float] = Field(None, ge=0)
    valor_condominio: Optional[float] = Field(None, ge=0)
    valor_iptu: Optional[float] = Field(None, ge=0)
    status: Optional[str] = Field('disponivel', pattern=r'^(disponivel|alugado)$')


class ImovelCreate(ImovelBase):
    proprietario_id: Optional[int] = None  # Opcional: proprietários definidos em participacoes


class ImovelUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=3, max_length=200)
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = Field(None, max_length=2)
    cep: Optional[str] = None
    valor_aluguel: Optional[float] = Field(None, ge=0)
    valor_condominio: Optional[float] = Field(None, ge=0)
    valor_iptu: Optional[float] = Field(None, ge=0)
    status: Optional[str] = Field(None, pattern=r'^(disponivel|alugado)$')
    is_active: Optional[bool] = None


class ImovelResponse(ImovelBase):
    id: int
    proprietario_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== ALUGUEL SCHEMAS =====

class AluguelBase(BaseModel):
    mes_referencia: str = Field(..., pattern=r"^\d{4}-(0[1-9]|1[0-2])$")
    valor_aluguel: float = Field(0.0, ge=0)
    valor_condominio: float = Field(0.0, ge=0)
    valor_iptu: float = Field(0.0, ge=0)
    valor_luz: float = Field(0.0, ge=0)
    valor_agua: float = Field(0.0, ge=0)
    valor_gas: float = Field(0.0, ge=0)
    valor_internet: float = Field(0.0, ge=0)
    outros_valores: float = Field(0.0, ge=0)
    observacoes: Optional[str] = None


class AluguelCreate(AluguelBase):
    imovel_id: int


class AluguelUpdate(BaseModel):
    valor_aluguel: Optional[float] = Field(None, ge=0)
    valor_condominio: Optional[float] = Field(None, ge=0)
    valor_iptu: Optional[float] = Field(None, ge=0)
    valor_luz: Optional[float] = Field(None, ge=0)
    valor_agua: Optional[float] = Field(None, ge=0)
    valor_gas: Optional[float] = Field(None, ge=0)
    valor_internet: Optional[float] = Field(None, ge=0)
    outros_valores: Optional[float] = Field(None, ge=0)
    pago: Optional[bool] = None
    data_pagamento: Optional[date] = None
    observacoes: Optional[str] = None


class AluguelResponse(AluguelBase):
    id: int
    imovel_id: int
    valor_total: float
    pago: bool
    data_pagamento: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== PARTICIPACAO SCHEMAS =====

class ParticipaçãoBase(BaseModel):
    mes_referencia: str = Field(..., pattern=r"^\d{4}-(0[1-9]|1[0-2])$")
    percentual: float = Field(..., ge=0, le=100)
    observacoes: Optional[str] = None


class ParticipaçãoCreate(ParticipaçãoBase):
    imovel_id: int
    proprietario_id: int


class ParticipaçãoUpdate(BaseModel):
    percentual: Optional[float] = Field(None, ge=0, le=100)
    observacoes: Optional[str] = None


class ParticipaçãoResponse(ParticipaçãoBase):
    id: int
    imovel_id: int
    proprietario_id: int
    valor_participacao: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== AUTH SCHEMAS =====

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UsuarioResponse


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ===== ALIAS SCHEMAS =====

class AliasCreate(BaseModel):
    nome_alias: str = Field(..., min_length=3, max_length=200)
    usuario_id: int


class AliasResponse(BaseModel):
    id: int
    nome_alias: str
    usuario_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ===== TRANSFERENCIA SCHEMAS =====

class TransferenciaCreate(BaseModel):
    origem_id: int
    destino_id: int
    mes_referencia: str = Field(..., pattern=r"^\d{4}-(0[1-9]|1[0-2])$")
    valor: float = Field(..., gt=0)
    descricao: Optional[str] = None


class TransferenciaUpdate(BaseModel):
    confirmada: Optional[bool] = None
    data_confirmacao: Optional[date] = None
    descricao: Optional[str] = None


class TransferenciaResponse(BaseModel):
    id: int
    origem_id: int
    destino_id: int
    mes_referencia: str
    valor: float
    confirmada: bool
    data_confirmacao: Optional[date] = None
    descricao: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ===== PERMISSAO SCHEMAS =====

class PermissaoCreate(BaseModel):
    usuario_id: int
    tipo_permissao: str = Field(..., pattern=r"^(visualizar_proprios|visualizar_todos|editar_todos)$")
    descricao: Optional[str] = None


class PermissaoUpdate(BaseModel):
    ativa: Optional[bool] = None
    descricao: Optional[str] = None


class PermissaoResponse(BaseModel):
    id: int
    usuario_id: int
    tipo_permissao: str
    ativa: bool
    descricao: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
