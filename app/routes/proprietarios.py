"""
Rotas de Proprietários - CRUD completo
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Optional
from pydantic import BaseModel, Field, validator
import re

from app.core.database import get_db
from app.core.auth import get_current_user_from_cookie
from app.models.proprietario import Proprietario
from app.models.usuario import Usuario

router = APIRouter(prefix="/api/proprietarios", tags=["proprietarios"])


# ============= SCHEMAS =============

class ProprietarioBase(BaseModel):
    tipo_pessoa: str = Field(..., pattern=r'^(fisica|juridica)$')
    nome: str = Field(..., min_length=3, max_length=200)
    cpf: Optional[str] = Field(None, pattern=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$')
    rg: Optional[str] = None
    razao_social: Optional[str] = None
    nome_fantasia: Optional[str] = None
    cnpj: Optional[str] = Field(None, pattern=r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$')
    inscricao_estadual: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    celular: Optional[str] = None
    endereco: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = Field(None, pattern=r'^[A-Z]{2}$')
    cep: Optional[str] = Field(None, pattern=r'^\d{5}-\d{3}$')
    banco: Optional[str] = None
    agencia: Optional[str] = None
    conta: Optional[str] = None
    tipo_conta: Optional[str] = Field(None, pattern=r'^(corrente|poupanca)$')
    pix: Optional[str] = None
    observacoes: Optional[str] = None
    is_active: bool = True

    @validator('cpf', 'cnpj')
    def validar_documento(cls, v, values):
        if not v:
            return v
        tipo = values.get('tipo_pessoa')
        if tipo == 'fisica' and not values.get('cpf'):
            raise ValueError('CPF é obrigatório para pessoa física')
        if tipo == 'juridica' and not values.get('cnpj'):
            raise ValueError('CNPJ é obrigatório para pessoa jurídica')
        return v


class ProprietarioCreate(ProprietarioBase):
    pass


class ProprietarioUpdate(BaseModel):
    tipo_pessoa: Optional[str] = Field(None, pattern=r'^(fisica|juridica)$')
    nome: Optional[str] = Field(None, min_length=3, max_length=200)
    cpf: Optional[str] = Field(None, pattern=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$')
    rg: Optional[str] = None
    razao_social: Optional[str] = None
    nome_fantasia: Optional[str] = None
    cnpj: Optional[str] = Field(None, pattern=r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$')
    inscricao_estadual: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    celular: Optional[str] = None
    endereco: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = Field(None, pattern=r'^[A-Z]{2}$')
    cep: Optional[str] = Field(None, pattern=r'^\d{5}-\d{3}$')
    banco: Optional[str] = None
    agencia: Optional[str] = None
    conta: Optional[str] = None
    tipo_conta: Optional[str] = Field(None, pattern=r'^(corrente|poupanca)$')
    pix: Optional[str] = None
    observacoes: Optional[str] = None
    is_active: Optional[bool] = None


class ProprietarioResponse(ProprietarioBase):
    id: int
    created_at: str
    updated_at: str
    total_imoveis: int = 0

    class Config:
        from_attributes = True


# ============= ROTAS =============

@router.get("/", response_model=List[ProprietarioResponse])
async def listar_proprietarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = None,
    tipo_pessoa: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """Lista todos os proprietários com filtros opcionais"""
    
    query = db.query(Proprietario)
    
    # Filtro de busca (nome, CPF, CNPJ, email)
    if search:
        search_filter = or_(
            Proprietario.nome.ilike(f"%{search}%"),
            Proprietario.cpf.ilike(f"%{search}%"),
            Proprietario.cnpj.ilike(f"%{search}%"),
            Proprietario.email.ilike(f"%{search}%"),
            Proprietario.razao_social.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # Filtro por tipo de pessoa
    if tipo_pessoa:
        query = query.filter(Proprietario.tipo_pessoa == tipo_pessoa)
    
    # Filtro por status
    if is_active is not None:
        query = query.filter(Proprietario.is_active == is_active)
    
    # Ordenar por nome
    query = query.order_by(Proprietario.nome)
    
    # Paginação
    proprietarios = query.offset(skip).limit(limit).all()
    
    # Adicionar contagem de imóveis
    result = []
    for prop in proprietarios:
        prop_dict = {
            "id": prop.id,
            "tipo_pessoa": prop.tipo_pessoa,
            "nome": prop.nome,
            "cpf": prop.cpf,
            "rg": prop.rg,
            "razao_social": prop.razao_social,
            "nome_fantasia": prop.nome_fantasia,
            "cnpj": prop.cnpj,
            "inscricao_estadual": prop.inscricao_estadual,
            "email": prop.email,
            "telefone": prop.telefone,
            "celular": prop.celular,
            "endereco": prop.endereco,
            "numero": prop.numero,
            "complemento": prop.complemento,
            "bairro": prop.bairro,
            "cidade": prop.cidade,
            "estado": prop.estado,
            "cep": prop.cep,
            "banco": prop.banco,
            "agencia": prop.agencia,
            "conta": prop.conta,
            "tipo_conta": prop.tipo_conta,
            "pix": prop.pix,
            "observacoes": prop.observacoes,
            "is_active": prop.is_active,
            "created_at": prop.created_at.isoformat() if prop.created_at else None,
            "updated_at": prop.updated_at.isoformat() if prop.updated_at else None,
            "total_imoveis": len(prop.imoveis)
        }
        result.append(prop_dict)
    
    return result


@router.post("/", response_model=ProprietarioResponse, status_code=201)
async def criar_proprietario(
    proprietario: ProprietarioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """Cria um novo proprietário"""
    
    # Verificar se já existe proprietário com mesmo CPF ou CNPJ
    if proprietario.cpf:
        existing = db.query(Proprietario).filter(Proprietario.cpf == proprietario.cpf).first()
        if existing:
            raise HTTPException(status_code=400, detail="Já existe um proprietário com este CPF")
    
    if proprietario.cnpj:
        existing = db.query(Proprietario).filter(Proprietario.cnpj == proprietario.cnpj).first()
        if existing:
            raise HTTPException(status_code=400, detail="Já existe um proprietário com este CNPJ")
    
    # Criar proprietário
    db_proprietario = Proprietario(**proprietario.model_dump())
    db.add(db_proprietario)
    db.commit()
    db.refresh(db_proprietario)
    
    # Retornar com contagem de imóveis
    result = {
        **proprietario.model_dump(),
        "id": db_proprietario.id,
        "created_at": db_proprietario.created_at.isoformat(),
        "updated_at": db_proprietario.updated_at.isoformat(),
        "total_imoveis": 0
    }
    
    return result


@router.get("/{proprietario_id}", response_model=ProprietarioResponse)
async def obter_proprietario(
    proprietario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """Obtém um proprietário específico por ID"""
    
    proprietario = db.query(Proprietario).filter(Proprietario.id == proprietario_id).first()
    
    if not proprietario:
        raise HTTPException(status_code=404, detail="Proprietário não encontrado")
    
    # Retornar com contagem de imóveis
    result = {
        "id": proprietario.id,
        "tipo_pessoa": proprietario.tipo_pessoa,
        "nome": proprietario.nome,
        "cpf": proprietario.cpf,
        "rg": proprietario.rg,
        "razao_social": proprietario.razao_social,
        "nome_fantasia": proprietario.nome_fantasia,
        "cnpj": proprietario.cnpj,
        "inscricao_estadual": proprietario.inscricao_estadual,
        "email": proprietario.email,
        "telefone": proprietario.telefone,
        "celular": proprietario.celular,
        "endereco": proprietario.endereco,
        "numero": proprietario.numero,
        "complemento": proprietario.complemento,
        "bairro": proprietario.bairro,
        "cidade": proprietario.cidade,
        "estado": proprietario.estado,
        "cep": proprietario.cep,
        "banco": proprietario.banco,
        "agencia": proprietario.agencia,
        "conta": proprietario.conta,
        "tipo_conta": proprietario.tipo_conta,
        "pix": proprietario.pix,
        "observacoes": proprietario.observacoes,
        "is_active": proprietario.is_active,
        "created_at": proprietario.created_at.isoformat() if proprietario.created_at else None,
        "updated_at": proprietario.updated_at.isoformat() if proprietario.updated_at else None,
        "total_imoveis": len(proprietario.imoveis)
    }
    
    return result


@router.put("/{proprietario_id}", response_model=ProprietarioResponse)
async def atualizar_proprietario(
    proprietario_id: int,
    proprietario_update: ProprietarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """Atualiza um proprietário existente"""
    
    db_proprietario = db.query(Proprietario).filter(Proprietario.id == proprietario_id).first()
    
    if not db_proprietario:
        raise HTTPException(status_code=404, detail="Proprietário não encontrado")
    
    # Verificar duplicidade de CPF/CNPJ se foram alterados
    update_data = proprietario_update.model_dump(exclude_unset=True)
    
    if "cpf" in update_data and update_data["cpf"] != db_proprietario.cpf:
        existing = db.query(Proprietario).filter(
            Proprietario.cpf == update_data["cpf"],
            Proprietario.id != proprietario_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Já existe um proprietário com este CPF")
    
    if "cnpj" in update_data and update_data["cnpj"] != db_proprietario.cnpj:
        existing = db.query(Proprietario).filter(
            Proprietario.cnpj == update_data["cnpj"],
            Proprietario.id != proprietario_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Já existe um proprietário com este CNPJ")
    
    # Atualizar campos
    for key, value in update_data.items():
        setattr(db_proprietario, key, value)
    
    db.commit()
    db.refresh(db_proprietario)
    
    # Retornar com contagem de imóveis
    result = {
        "id": db_proprietario.id,
        "tipo_pessoa": db_proprietario.tipo_pessoa,
        "nome": db_proprietario.nome,
        "cpf": db_proprietario.cpf,
        "rg": db_proprietario.rg,
        "razao_social": db_proprietario.razao_social,
        "nome_fantasia": db_proprietario.nome_fantasia,
        "cnpj": db_proprietario.cnpj,
        "inscricao_estadual": db_proprietario.inscricao_estadual,
        "email": db_proprietario.email,
        "telefone": db_proprietario.telefone,
        "celular": db_proprietario.celular,
        "endereco": db_proprietario.endereco,
        "numero": db_proprietario.numero,
        "complemento": db_proprietario.complemento,
        "bairro": db_proprietario.bairro,
        "cidade": db_proprietario.cidade,
        "estado": db_proprietario.estado,
        "cep": db_proprietario.cep,
        "banco": db_proprietario.banco,
        "agencia": db_proprietario.agencia,
        "conta": db_proprietario.conta,
        "tipo_conta": db_proprietario.tipo_conta,
        "pix": db_proprietario.pix,
        "observacoes": db_proprietario.observacoes,
        "is_active": db_proprietario.is_active,
        "created_at": db_proprietario.created_at.isoformat() if db_proprietario.created_at else None,
        "updated_at": db_proprietario.updated_at.isoformat() if db_proprietario.updated_at else None,
        "total_imoveis": len(db_proprietario.imoveis)
    }
    
    return result


@router.delete("/{proprietario_id}", status_code=204)
async def deletar_proprietario(
    proprietario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """Deleta um proprietário (apenas admin)"""
    
    # Apenas admin pode deletar
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem deletar proprietários")
    
    db_proprietario = db.query(Proprietario).filter(Proprietario.id == proprietario_id).first()
    
    if not db_proprietario:
        raise HTTPException(status_code=404, detail="Proprietário não encontrado")
    
    # Verificar se tem imóveis vinculados
    if len(db_proprietario.imoveis) > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Não é possível deletar proprietário com {len(db_proprietario.imoveis)} imóvel(is) vinculado(s)"
        )
    
    db.delete(db_proprietario)
    db.commit()
    
    return None


@router.get("/stats/summary")
async def obter_estatisticas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """Retorna estatísticas gerais de proprietários"""
    
    total = db.query(func.count(Proprietario.id)).scalar()
    ativos = db.query(func.count(Proprietario.id)).filter(Proprietario.is_active == True).scalar()
    inativos = db.query(func.count(Proprietario.id)).filter(Proprietario.is_active == False).scalar()
    pessoas_fisicas = db.query(func.count(Proprietario.id)).filter(Proprietario.tipo_pessoa == "fisica").scalar()
    pessoas_juridicas = db.query(func.count(Proprietario.id)).filter(Proprietario.tipo_pessoa == "juridica").scalar()
    
    return {
        "total_proprietarios": total or 0,
        "ativos": ativos or 0,
        "inativos": inativos or 0,
        "pessoas_fisicas": pessoas_fisicas or 0,
        "pessoas_juridicas": pessoas_juridicas or 0
    }
