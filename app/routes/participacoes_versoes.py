from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
import json

from app.core.database import get_db
from app.core.auth import get_current_user_from_cookie
from app.models.usuario import Usuario
from app.models.participacao_versao import ParticipacaoVersao
from app.models.participacao import Participacao
from app.models.imovel import Imovel
from app.models.proprietario import Proprietario

router = APIRouter(prefix="/api/participacoes-versoes", tags=["participacoes-versoes"])


# Schemas Pydantic
class ParticipacaoVersaoCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=200)
    dados_json: Dict[str, Dict[str, float]]  # {imovel_id: {proprietario_id: percentual}}
    observacoes: Optional[str] = None

    class Config:
        from_attributes = True


class ParticipacaoVersaoResponse(BaseModel):
    id: int
    nome: str
    dados_json: str
    observacoes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    created_by_nome: Optional[str] = None

    class Config:
        from_attributes = True


class ParticipacaoGridData(BaseModel):
    """Dados formatados para a grid de participações"""
    imoveis: List[Dict[str, Any]]  # [{id, nome}]
    proprietarios: List[Dict[str, Any]]  # [{id, nome}]
    dados: Dict[str, Dict[str, float]]  # {imovel_id: {proprietario_id: percentual}}


# Endpoints
@router.get("/grid-data", response_model=ParticipacaoGridData)
async def obter_dados_grid(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """
    Retorna os dados necessários para montar a grid de participações
    """
    # Buscar imóveis ativos
    imoveis = db.query(Imovel).filter(Imovel.is_active == True).order_by(Imovel.nome).all()
    
    # Buscar proprietários ativos
    proprietarios = db.query(Proprietario).filter(Proprietario.is_active == True).order_by(Proprietario.nome).all()
    
    # Buscar participações atuais
    participacoes = db.query(Participacao).all()
    
    # Construir dicionário de dados
    dados = {}
    for p in participacoes:
        imovel_id = str(p.imovel_id)
        proprietario_id = str(p.proprietario_id)
        
        if imovel_id not in dados:
            dados[imovel_id] = {}
        
        dados[imovel_id][proprietario_id] = p.percentual
    
    return {
        "imoveis": [{"id": i.id, "nome": i.nome} for i in imoveis],
        "proprietarios": [{"id": p.id, "nome": p.nome} for p in proprietarios],
        "dados": dados
    }


@router.get("/", response_model=List[ParticipacaoVersaoResponse])
async def listar_versoes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """
    Lista todas as versões de participações
    """
    query = db.query(ParticipacaoVersao).order_by(ParticipacaoVersao.created_at.desc())
    versoes = query.offset(skip).limit(limit).all()
    
    # Enriquecer com dados do usuário
    result = []
    for v in versoes:
        data = ParticipacaoVersaoResponse.from_orm(v)
        if v.usuario:
            data.created_by_nome = v.usuario.nome
        result.append(data)
    
    return result


@router.post("/", response_model=ParticipacaoVersaoResponse, status_code=201)
async def criar_versao(
    versao: ParticipacaoVersaoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """
    Cria uma nova versão de participações e aplica ao banco
    """
    # Validar que a soma dos percentuais de cada imóvel está entre 99.95% e 100.05%
    for imovel_id, proprietarios_dict in versao.dados_json.items():
        total = sum(proprietarios_dict.values())
        if not (99.95 <= total <= 100.05):
            raise HTTPException(
                status_code=400,
                detail=f"Imóvel ID {imovel_id}: soma dos percentuais ({total:.2f}%) deve estar entre 99.95% e 100.05%"
            )
    
    # Converter dados para JSON string
    dados_json_str = json.dumps(versao.dados_json)
    
    # Criar versão
    db_versao = ParticipacaoVersao(
        nome=versao.nome,
        dados_json=dados_json_str,
        observacoes=versao.observacoes,
        created_by=current_user.id
    )
    db.add(db_versao)
    db.flush()
    
    # Aplicar as participações ao banco
    # Use a transaction to ensure atomicity
    try:
        # Remove existing participacoes
        db.query(Participacao).delete()
        
        # Create new participacoes
        for imovel_id, proprietarios_dict in versao.dados_json.items():
            for proprietario_id, percentual in proprietarios_dict.items():
                if percentual > 0:  # Only create if there's a percentage
                    participacao = Participacao(
                        imovel_id=int(imovel_id),
                        proprietario_id=int(proprietario_id),
                        percentual=percentual
                    )
                    db.add(participacao)
        
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao aplicar participações: {str(e)}")
    
    db.refresh(db_versao)
    
    # Retornar resposta
    response = ParticipacaoVersaoResponse.from_orm(db_versao)
    response.created_by_nome = current_user.nome
    
    return response


@router.get("/{versao_id}", response_model=ParticipacaoVersaoResponse)
async def obter_versao(
    versao_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """
    Obtém uma versão específica de participações
    """
    versao = db.query(ParticipacaoVersao).filter(ParticipacaoVersao.id == versao_id).first()
    
    if not versao:
        raise HTTPException(status_code=404, detail="Versão não encontrada")
    
    response = ParticipacaoVersaoResponse.from_orm(versao)
    if versao.usuario:
        response.created_by_nome = versao.usuario.nome
    
    return response


@router.post("/{versao_id}/aplicar", response_model=Dict[str, str])
async def aplicar_versao(
    versao_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """
    Aplica uma versão existente ao banco de dados
    """
    versao = db.query(ParticipacaoVersao).filter(ParticipacaoVersao.id == versao_id).first()
    
    if not versao:
        raise HTTPException(status_code=404, detail="Versão não encontrada")
    
    # Parse JSON
    dados_json = json.loads(versao.dados_json)
    
    # Apply participacoes in a transaction
    try:
        # Remove existing participacoes
        db.query(Participacao).delete()
        
        # Create new participacoes
        for imovel_id, proprietarios_dict in dados_json.items():
            for proprietario_id, percentual in proprietarios_dict.items():
                if percentual > 0:
                    participacao = Participacao(
                        imovel_id=int(imovel_id),
                        proprietario_id=int(proprietario_id),
                        percentual=percentual
                    )
                    db.add(participacao)
        
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao aplicar versão: {str(e)}")
    
    return {"message": "Versão aplicada com sucesso"}


@router.delete("/{versao_id}", status_code=204)
async def deletar_versao(
    versao_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """
    Deleta uma versão de participações
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem deletar versões")
    
    versao = db.query(ParticipacaoVersao).filter(ParticipacaoVersao.id == versao_id).first()
    
    if not versao:
        raise HTTPException(status_code=404, detail="Versão não encontrada")
    
    db.delete(versao)
    db.commit()
    
    return None
