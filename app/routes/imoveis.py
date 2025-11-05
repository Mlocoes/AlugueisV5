"""Rotas CRUD de Imóveis"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.core.database import get_db
from app.core.auth import get_current_user_from_cookie, require_admin
from app.models.usuario import Usuario
from app.models.imovel import Imovel
from app.models.proprietario import Proprietario
from app.schemas.schemas import ImovelCreate, ImovelUpdate, ImovelResponse


router = APIRouter(prefix="/api/imoveis", tags=["imoveis"])


@router.get("/", response_model=List[ImovelResponse])
async def list_imoveis(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    proprietario_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """
    Lista imóveis com filtros opcionais
    - Admins veem todos os imóveis
    - Usuários normais não têm restrição (todos podem ver todos os imóveis)
    """
    query = db.query(Imovel)
    
    # Filtro por proprietário
    if proprietario_id:
        query = query.filter(Imovel.proprietario_id == proprietario_id)
    
    # Filtro de busca
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Imovel.nome.ilike(search_filter),
                Imovel.endereco.ilike(search_filter),
                Imovel.cidade.ilike(search_filter)
            )
        )
    
    # Filtro de status (is_active)
    if is_active is not None:
        query = query.filter(Imovel.is_active == is_active)
    
    # Filtro de status (alugado/disponivel)
    if status:
        query = query.filter(Imovel.status == status)
    
    # Paginação
    imoveis = query.offset(skip).limit(limit).all()
    
    return [ImovelResponse.model_validate(imovel) for imovel in imoveis]


@router.get("/{imovel_id}", response_model=ImovelResponse)
async def get_imovel(
    imovel_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """Obtém detalhes de um imóvel específico"""
    imovel = db.query(Imovel).filter(Imovel.id == imovel_id).first()
    
    if not imovel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Imóvel não encontrado"
        )
    
    return ImovelResponse.model_validate(imovel)


@router.post("/", response_model=ImovelResponse, status_code=status.HTTP_201_CREATED)
async def create_imovel(
    imovel_data: ImovelCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """
    Cria novo imóvel
    - Todos os usuários podem criar imóveis para qualquer proprietário
    """
    # Verificar se proprietário existe
    proprietario = db.query(Proprietario).filter(Proprietario.id == imovel_data.proprietario_id).first()
    if not proprietario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proprietário não encontrado"
        )
    
    # Criar imóvel
    new_imovel = Imovel(**imovel_data.model_dump())
    
    db.add(new_imovel)
    db.commit()
    db.refresh(new_imovel)
    
    return ImovelResponse.model_validate(new_imovel)


@router.put("/{imovel_id}", response_model=ImovelResponse)
async def update_imovel(
    imovel_id: int,
    imovel_data: ImovelUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """Atualiza dados de um imóvel"""
    imovel = db.query(Imovel).filter(Imovel.id == imovel_id).first()
    
    if not imovel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Imóvel não encontrado"
        )
    
    # Atualizar campos
    update_data = imovel_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(imovel, field, value)
    
    db.commit()
    db.refresh(imovel)
    
    return ImovelResponse.model_validate(imovel)


@router.delete("/{imovel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_imovel(
    imovel_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """
    Deleta um imóvel (soft delete - marca como inativo)
    Apenas admins podem deletar
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem deletar imóveis"
        )
    
    imovel = db.query(Imovel).filter(Imovel.id == imovel_id).first()
    
    if not imovel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Imóvel não encontrado"
        )
    
    # Soft delete
    imovel.is_active = False
    db.commit()
    
    return None


@router.get("/stats/summary")
async def get_imoveis_stats(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """Retorna estatísticas dos imóveis"""
    query = db.query(Imovel)
    
    total = query.count()
    ativos = query.filter(Imovel.is_active == True).count()
    inativos = query.filter(Imovel.is_active == False).count()
    
    # Valor total de aluguéis
    imoveis_ativos = query.filter(Imovel.is_active == True).all()
    valor_total_alugueis = sum(i.valor_aluguel or 0 for i in imoveis_ativos)
    
    return {
        "total": total,
        "ativos": ativos,
        "inativos": inativos,
        "valor_total_alugueis": valor_total_alugueis
    }


@router.get("/proprietarios/list")
async def list_proprietarios_for_select(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """Retorna lista simplificada de proprietários ativos para select"""
    proprietarios = db.query(Proprietario).filter(
        Proprietario.is_active == True
    ).order_by(Proprietario.nome).all()
    
    return [
        {
            "id": p.id,
            "nome": p.razao_social if p.tipo_pessoa == "juridica" else p.nome,
            "tipo_pessoa": p.tipo_pessoa,
            "cpf_cnpj": p.cnpj if p.tipo_pessoa == "juridica" else p.cpf
        }
        for p in proprietarios
    ]
