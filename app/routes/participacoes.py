from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator
import re

from app.core.database import get_db
from app.core.auth import get_current_user_from_cookie
from app.models.usuario import Usuario
from app.models.participacao import Participacao
from app.models.imovel import Imovel
from app.models.proprietario import Proprietario

router = APIRouter(prefix="/api/participacoes", tags=["participacoes"])


# Schemas Pydantic
class ParticipacaoBase(BaseModel):
    imovel_id: int
    proprietario_id: int
    percentual: float = Field(..., ge=0, le=100, description="Percentual de participação (0-100)")
    observacoes: Optional[str] = None

    class Config:
        from_attributes = True


class ParticipacaoCreate(ParticipacaoBase):
    pass


class ParticipacaoUpdate(BaseModel):
    imovel_id: Optional[int] = None
    proprietario_id: Optional[int] = None
    percentual: Optional[float] = Field(None, ge=0, le=100)
    observacoes: Optional[str] = None

    class Config:
        from_attributes = True


class ParticipacaoResponse(ParticipacaoBase):
    id: int
    created_at: datetime
    updated_at: datetime

    # Dados relacionados
    imovel_nome: Optional[str] = None
    proprietario_nome: Optional[str] = None

    class Config:
        from_attributes = True


# Endpoints
@router.get("/", response_model=List[ParticipacaoResponse])
async def listar_participacoes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, description="Buscar em observações, nome do imóvel ou proprietário"),
    imovel_id: Optional[int] = Query(None, description="Filtrar por imóvel"),
    proprietario_id: Optional[int] = Query(None, description="Filtrar por proprietário"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """
    Lista todas as participações com filtros opcionais
    """
    # Usar joinedload para prevenir N+1 ao acessar p.imovel.nome e p.proprietario.nome
    query = db.query(Participacao).options(joinedload(Participacao.imovel), joinedload(Participacao.proprietario))
    
    # Aplicar filtros
    if imovel_id:
        query = query.filter(Participacao.imovel_id == imovel_id)
    
    if proprietario_id:
        query = query.filter(Participacao.proprietario_id == proprietario_id)
    
    if search:
        search_filter = f"%{search}%"
        query = query.join(Imovel).join(Proprietario).filter(
            (Participacao.observacoes.ilike(search_filter)) |
            (Imovel.nome.ilike(search_filter)) |
            (Proprietario.nome.ilike(search_filter))
        )
    
    # Paginação
    participacoes = query.order_by(Participacao.id.desc()).offset(skip).limit(limit).all()
    
    # Enriquecer com dados relacionados
    result = []
    for p in participacoes:
        data = ParticipacaoResponse.from_orm(p)
        data.imovel_nome = p.imovel.nome if p.imovel else None
        data.proprietario_nome = p.proprietario.nome if p.proprietario else None
        result.append(data)
    
    return result


@router.post("/", response_model=ParticipacaoResponse, status_code=201)
async def criar_participacao(
    participacao: ParticipacaoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """
    Cria uma nova participação
    """
    # Validar se o imóvel existe
    imovel = db.query(Imovel).filter(Imovel.id == participacao.imovel_id).first()
    if not imovel:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    
    # Validar se o proprietário existe
    proprietario = db.query(Proprietario).filter(Proprietario.id == participacao.proprietario_id).first()
    if not proprietario:
        raise HTTPException(status_code=404, detail="Proprietário não encontrado")
    
    # Verificar se já existe participação para este imóvel e proprietário
    existing = db.query(Participacao).filter(
        Participacao.imovel_id == participacao.imovel_id,
        Participacao.proprietario_id == participacao.proprietario_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400, 
            detail="Já existe uma participação para este imóvel e proprietário"
        )
    
    # Criar participação
    db_participacao = Participacao(**participacao.dict())
    db.add(db_participacao)
    db.commit()
    db.refresh(db_participacao)
    
    # Retornar com dados relacionados
    response = ParticipacaoResponse.from_orm(db_participacao)
    response.imovel_nome = imovel.nome
    response.proprietario_nome = proprietario.nome
    
    return response


@router.get("/{participacao_id}", response_model=ParticipacaoResponse)
async def obter_participacao(
    participacao_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """
    Obtém uma participação específica
    """
    participacao = db.query(Participacao).options(joinedload(Participacao.imovel), joinedload(Participacao.proprietario)).filter(Participacao.id == participacao_id).first()
    
    if not participacao:
        raise HTTPException(status_code=404, detail="Participação não encontrada")
    
    # Enriquecer com dados relacionados
    response = ParticipacaoResponse.from_orm(participacao)
    response.imovel_nome = participacao.imovel.nome if participacao.imovel else None
    response.proprietario_nome = participacao.proprietario.nome if participacao.proprietario else None
    
    return response


@router.put("/{participacao_id}", response_model=ParticipacaoResponse)
async def atualizar_participacao(
    participacao_id: int,
    participacao_update: ParticipacaoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """
    Atualiza uma participação existente
    """
    db_participacao = db.query(Participacao).options(joinedload(Participacao.imovel), joinedload(Participacao.proprietario)).filter(Participacao.id == participacao_id).first()
    
    if not db_participacao:
        raise HTTPException(status_code=404, detail="Participação não encontrada")
    
    # Validar imóvel se foi alterado
    if participacao_update.imovel_id and participacao_update.imovel_id != db_participacao.imovel_id:
        imovel = db.query(Imovel).filter(Imovel.id == participacao_update.imovel_id).first()
        if not imovel:
            raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    
    # Validar proprietário se foi alterado
    if participacao_update.proprietario_id and participacao_update.proprietario_id != db_participacao.proprietario_id:
        proprietario = db.query(Proprietario).filter(Proprietario.id == participacao_update.proprietario_id).first()
        if not proprietario:
            raise HTTPException(status_code=404, detail="Proprietário não encontrado")
    
    # Verificar duplicata se campos chave foram alterados
    if any([participacao_update.imovel_id, participacao_update.proprietario_id]):
        new_imovel_id = participacao_update.imovel_id or db_participacao.imovel_id
        new_proprietario_id = participacao_update.proprietario_id or db_participacao.proprietario_id
        
        existing = db.query(Participacao).filter(
            Participacao.id != participacao_id,
            Participacao.imovel_id == new_imovel_id,
            Participacao.proprietario_id == new_proprietario_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Já existe uma participação para este imóvel e proprietário"
            )
    
    # Atualizar campos fornecidos
    update_data = participacao_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_participacao, field, value)
    
    db_participacao.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_participacao)
    
    # Retornar com dados relacionados
    response = ParticipacaoResponse.from_orm(db_participacao)
    response.imovel_nome = db_participacao.imovel.nome if db_participacao.imovel else None
    response.proprietario_nome = db_participacao.proprietario.nome if db_participacao.proprietario else None
    
    return response


@router.delete("/{participacao_id}", status_code=204)
async def deletar_participacao(
    participacao_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """
    Deleta uma participação (hard delete)
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem deletar participações")
    
    db_participacao = db.query(Participacao).filter(Participacao.id == participacao_id).first()
    
    if not db_participacao:
        raise HTTPException(status_code=404, detail="Participação não encontrada")
    
    db.delete(db_participacao)
    db.commit()
    
    return None


@router.get("/stats/summary")
async def obter_estatisticas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """
    Retorna estatísticas gerais de participações
    """
    total = db.query(Participacao).count()
    
    # Contar participações únicas por imóvel
    imoveis_distintos = db.query(Participacao.imovel_id).distinct().count()
    
    # Contar participações únicas por proprietário
    proprietarios_distintos = db.query(Participacao.proprietario_id).distinct().count()
    
    return {
        "total": total,
        "imoveis_com_participacao": imoveis_distintos,
        "proprietarios_participantes": proprietarios_distintos
    }


@router.get("/imovel/{imovel_id}", response_model=List[ParticipacaoResponse])
async def listar_participacoes_por_imovel(
    imovel_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """
    Lista todas as participações de um imóvel específico
    """
    # Validar se o imóvel existe
    imovel = db.query(Imovel).filter(Imovel.id == imovel_id).first()
    if not imovel:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    
    query = db.query(Participacao).filter(Participacao.imovel_id == imovel_id)
    
    participacoes = query.order_by(Participacao.id.desc()).all()
    
    # Enriquecer com dados relacionados
    result = []
    for p in participacoes:
        data = ParticipacaoResponse.from_orm(p)
        data.imovel_nome = imovel.nome
        data.proprietario_nome = p.proprietario.nome if p.proprietario else None
        result.append(data)
    
    return result
