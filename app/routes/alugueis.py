"""Rotas para gestão de aluguéis mensais"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, extract
from typing import Optional, List, Dict
from collections import defaultdict
from datetime import datetime, date

from app.core.database import get_db
from app.core.auth import get_current_user_from_cookie, require_admin
from app.models.usuario import Usuario
from app.models.aluguel import AluguelMensal
from app.models.imovel import Imovel
from app.models.participacao import Participacao
from app.models.proprietario import Proprietario
from pydantic import BaseModel, Field


router = APIRouter(prefix="/api/alugueis", tags=["alugueis"])


# Schemas Pydantic
class AluguelBase(BaseModel):
    imovel_id: int
    mes_referencia: str = Field(..., pattern=r'^\d{4}-\d{2}$')  # YYYY-MM
    valor_total: float = 0.0
    pago: bool = False


class AluguelCreate(AluguelBase):
    pass


class AluguelUpdate(BaseModel):
    valor_total: Optional[float] = None
    pago: Optional[bool] = None


class AluguelResponse(AluguelBase):
    id: int
    created_at: datetime
    imovel_nome: Optional[str] = None
    imovel_endereco: Optional[str] = None

    class Config:
        from_attributes = True


class AluguelDistribuicaoRow(BaseModel):
    aluguel_id: int
    imovel_id: int
    imovel_nome: str
    mes_referencia: str
    valor_total: float
    distribuicao: Dict[int, float]

    class Config:
        from_attributes = True


class AluguelGridResponse(BaseModel):
    mes_referencia: Optional[str]
    mes_label: str
    col_headers: List[str]
    proprietarios: List[Dict[str, str]]
    rows: List[AluguelDistribuicaoRow]


def calcular_valor_total(aluguel_data: dict) -> float:
    """Calcula o valor total do aluguel - agora apenas retorna o valor_total fornecido"""
    return aluguel_data.get('valor_total', 0.0)


def _format_mes_header(mes_referencia: Optional[str]) -> str:
    """Formata o cabeçalho da primeira coluna para o padrão brasileiro (DD/MM/AAAA)."""
    if not mes_referencia:
        return "Imóvel"
    try:
        mes_dt = datetime.strptime(mes_referencia, "%Y-%m")
        mes_dt = mes_dt.replace(day=1)
        return mes_dt.strftime("%d/%m/%Y")
    except ValueError:
        return "Imóvel"


@router.get("/", response_model=List[AluguelResponse])
async def listar_alugueis(
    mes_referencia: Optional[str] = None,
    imovel_id: Optional[int] = None,
    ano: Optional[int] = None,
    pago: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: Usuario = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    """
    Lista aluguéis com filtros
    - Admins veem todos
    - Usuários veem apenas seus imóveis
    """
    # Usar joinedload para prevenir N+1 ao acessar aluguel.imovel.nome e aluguel.imovel.endereco
    query = db.query(AluguelMensal).join(Imovel).options(joinedload(AluguelMensal.imovel))
    
    # Filtro de permissão
    if not current_user.is_admin:
        query = query.filter(Imovel.proprietario_id == current_user.id)
    
    # Filtros
    if mes_referencia:
        query = query.filter(AluguelMensal.mes_referencia == mes_referencia)
    
    if imovel_id:
        query = query.filter(AluguelMensal.imovel_id == imovel_id)
    
    if ano:
        query = query.filter(AluguelMensal.mes_referencia.like(f"{ano}%"))
    
    if pago is not None:
        query = query.filter(AluguelMensal.pago == pago)
    
    # Ordenar por mês mais recente primeiro
    query = query.order_by(AluguelMensal.mes_referencia.desc())
    
    alugueis = query.offset(skip).limit(limit).all()
    
    # Adicionar informações do imóvel
    result = []
    for aluguel in alugueis:
        aluguel_dict = {
            "id": aluguel.id,
            "imovel_id": aluguel.imovel_id,
            "mes_referencia": aluguel.mes_referencia,
            "valor_total": aluguel.valor_total,
            "pago": aluguel.pago,
            "created_at": aluguel.created_at,
            "imovel_nome": aluguel.imovel.nome if aluguel.imovel else None,
            "imovel_endereco": aluguel.imovel.endereco if aluguel.imovel else None
        }
        result.append(aluguel_dict)
    
    return result


@router.get("/grid-data", response_model=AluguelGridResponse)
async def obter_grid_alugueis(
    mes_referencia: Optional[str] = None,
    imovel_id: Optional[int] = None,
    ano: Optional[int] = None,
    mes_like: Optional[str] = None,
    pago: Optional[bool] = None,
    current_user: Usuario = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    """Retorna dados agregados para exibição dos aluguéis em formato de planilha."""

    query = db.query(AluguelMensal).join(Imovel).options(joinedload(AluguelMensal.imovel))

    if not current_user.is_admin:
        query = query.filter(Imovel.proprietario_id == current_user.id)

    if mes_referencia:
        query = query.filter(AluguelMensal.mes_referencia == mes_referencia)

    if imovel_id:
        query = query.filter(AluguelMensal.imovel_id == imovel_id)

    if ano:
        query = query.filter(AluguelMensal.mes_referencia.like(f"{ano}%"))

    if mes_like:
        query = query.filter(AluguelMensal.mes_referencia.like(f"%{mes_like}"))

    if pago is not None:
        query = query.filter(AluguelMensal.pago == pago)

    alugueis = query.order_by(AluguelMensal.mes_referencia.desc(), Imovel.nome.asc()).all()

    # Agrupar aluguéis por imóvel, pegando o mais recente de cada um
    alugueis_por_imovel: Dict[int, AluguelMensal] = {}
    for aluguel in alugueis:
        if aluguel.imovel_id not in alugueis_por_imovel:
            alugueis_por_imovel[aluguel.imovel_id] = aluguel

    # Usar apenas um aluguel por imóvel (o mais recente filtrado)
    alugueis_unicos = list(alugueis_por_imovel.values())

    mes_ref_para_header = mes_referencia or (alugueis_unicos[0].mes_referencia if alugueis_unicos else None)
    mes_label = _format_mes_header(mes_ref_para_header)

    if not alugueis_unicos:
        return AluguelGridResponse(
            mes_referencia=mes_referencia,
            mes_label=mes_label,
            col_headers=[mes_label, "Valor Total"],
            proprietarios=[],
            rows=[]
        )

    imovel_ids = {aluguel.imovel_id for aluguel in alugueis_unicos if aluguel.imovel_id}
    participacoes_por_imovel = defaultdict(list)
    proprietarios_dict: Dict[int, str] = {}

    if imovel_ids:
        participacoes = (
            db.query(Participacao)
            .options(joinedload(Participacao.proprietario))
            .filter(Participacao.imovel_id.in_(imovel_ids))
            .all()
        )

        for participacao in participacoes:
            participacoes_por_imovel[participacao.imovel_id].append(participacao)
            if participacao.proprietario and participacao.proprietario_id:
                proprietarios_dict[participacao.proprietario_id] = participacao.proprietario.nome

    proprietarios_ordenados = sorted(
        (
            {"id": str(prop_id), "nome": nome}
            for prop_id, nome in proprietarios_dict.items()
        ),
        key=lambda item: item["nome"].lower()
    )

    linhas: List[AluguelDistribuicaoRow] = []

    for aluguel in alugueis_unicos:
        valor_total = float(aluguel.valor_total or 0)
        distribuicao: Dict[int, float] = {}

        for participacao in participacoes_por_imovel.get(aluguel.imovel_id, []):
            percentual = participacao.percentual or 0
            distribuicao[participacao.proprietario_id] = round(valor_total * (percentual / 100), 2)

        linhas.append(
            AluguelDistribuicaoRow(
                aluguel_id=aluguel.id,
                imovel_id=aluguel.imovel_id,
                imovel_nome=aluguel.imovel.nome if aluguel.imovel else "Imóvel não cadastrado",
                mes_referencia=aluguel.mes_referencia,
                valor_total=valor_total,
                distribuicao=distribuicao
            )
        )

    col_headers = [mes_label, "Valor Total"] + [prop["nome"] for prop in proprietarios_ordenados]

    return AluguelGridResponse(
        mes_referencia=mes_referencia,
        mes_label=mes_label,
        col_headers=col_headers,
        proprietarios=proprietarios_ordenados,
        rows=linhas
    )


@router.post("/", response_model=AluguelResponse, status_code=status.HTTP_201_CREATED)
async def criar_aluguel(
    aluguel_data: AluguelCreate,
    current_user: Usuario = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    """
    Cria novo aluguel mensal
    - Admins podem criar para qualquer imóvel
    - Usuários apenas para seus imóveis
    """
    # Verificar se imóvel existe
    imovel = db.query(Imovel).filter(Imovel.id == aluguel_data.imovel_id).first()
    if not imovel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Imóvel não encontrado"
        )
    
    # Verificar permissão
    if not current_user.is_admin and imovel.proprietario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para criar aluguel neste imóvel"
        )
    
    # Verificar se já existe aluguel para este imóvel neste mês
    aluguel_existente = db.query(AluguelMensal).filter(
        and_(
            AluguelMensal.imovel_id == aluguel_data.imovel_id,
            AluguelMensal.mes_referencia == aluguel_data.mes_referencia
        )
    ).first()
    
    if aluguel_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Já existe um aluguel cadastrado para este imóvel em {aluguel_data.mes_referencia}"
        )
    
    # Calcular valor total
    aluguel_dict = aluguel_data.model_dump()
    aluguel_dict['valor_total'] = calcular_valor_total(aluguel_dict)
    
    # Criar aluguel
    novo_aluguel = AluguelMensal(**aluguel_dict)
    db.add(novo_aluguel)
    db.commit()
    db.refresh(novo_aluguel)
    
    # Retornar com dados do imóvel
    return AluguelResponse(
        **{
            "id": novo_aluguel.id,
            "imovel_id": novo_aluguel.imovel_id,
            "mes_referencia": novo_aluguel.mes_referencia,
            "valor_total": novo_aluguel.valor_total,
            "pago": novo_aluguel.pago,
            "created_at": novo_aluguel.created_at,
            "imovel_nome": imovel.nome,
            "imovel_endereco": imovel.endereco
        }
    )


@router.get("/{aluguel_id}", response_model=AluguelResponse)
async def obter_aluguel(
    aluguel_id: int,
    current_user: Usuario = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    """Obtém aluguel específico"""
    aluguel = db.query(AluguelMensal).options(joinedload(AluguelMensal.imovel)).filter(AluguelMensal.id == aluguel_id).first()
    
    if not aluguel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aluguel não encontrado"
        )
    
    # Verificar permissão
    if not current_user.is_admin:
        imovel = db.query(Imovel).filter(Imovel.id == aluguel.imovel_id).first()
        if imovel.proprietario_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para acessar este aluguel"
            )
    
    return AluguelResponse(
        **{
            "id": aluguel.id,
            "imovel_id": aluguel.imovel_id,
            "mes_referencia": aluguel.mes_referencia,
            "valor_total": aluguel.valor_total,
            "pago": aluguel.pago,
            "created_at": aluguel.created_at,
            "imovel_nome": aluguel.imovel.nome if aluguel.imovel else None,
            "imovel_endereco": aluguel.imovel.endereco if aluguel.imovel else None
        }
    )


@router.put("/{aluguel_id}", response_model=AluguelResponse)
async def atualizar_aluguel(
    aluguel_id: int,
    aluguel_data: AluguelUpdate,
    current_user: Usuario = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    """Atualiza aluguel existente"""
    aluguel = db.query(AluguelMensal).options(joinedload(AluguelMensal.imovel)).filter(AluguelMensal.id == aluguel_id).first()
    
    if not aluguel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aluguel não encontrado"
        )
    
    # Verificar permissão
    if not current_user.is_admin:
        imovel = db.query(Imovel).filter(Imovel.id == aluguel.imovel_id).first()
        if imovel.proprietario_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para editar este aluguel"
            )
    
    # Atualizar campos
    update_data = aluguel_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(aluguel, field, value)
    
    # O valor_total é fornecido diretamente, não precisa recalcular
    db.commit()
    db.refresh(aluguel)
    
    return AluguelResponse(
        **{
            "id": aluguel.id,
            "imovel_id": aluguel.imovel_id,
            "mes_referencia": aluguel.mes_referencia,
            "valor_total": aluguel.valor_total,
            "pago": aluguel.pago,
            "created_at": aluguel.created_at,
            "imovel_nome": aluguel.imovel.nome if aluguel.imovel else None,
            "imovel_endereco": aluguel.imovel.endereco if aluguel.imovel else None
        }
    )


@router.delete("/{aluguel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_aluguel(
    aluguel_id: int,
    current_user: Usuario = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    """Deleta aluguel (apenas admins)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem deletar aluguéis"
        )
    
    aluguel = db.query(AluguelMensal).filter(AluguelMensal.id == aluguel_id).first()
    
    if not aluguel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aluguel não encontrado"
        )
    
    db.delete(aluguel)
    db.commit()


@router.get("/stats/summary")
async def obter_estatisticas(
    ano: Optional[int] = None,
    current_user: Usuario = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    """Retorna estatísticas de aluguéis"""
    query = db.query(AluguelMensal).join(Imovel)
    
    # Filtro de permissão
    if not current_user.is_admin:
        query = query.filter(Imovel.proprietario_id == current_user.id)
    
    # Filtro de ano
    if ano:
        query = query.filter(AluguelMensal.mes_referencia.like(f"{ano}%"))
    
    alugueis = query.all()
    
    total_alugueis = len(alugueis)
    alugueis_pagos = sum(1 for a in alugueis if a.pago)
    alugueis_pendentes = total_alugueis - alugueis_pagos
    valor_total_recebido = sum(a.valor_total for a in alugueis if a.pago)
    valor_total_pendente = sum(a.valor_total for a in alugueis if not a.pago)
    
    return {
        "total_alugueis": total_alugueis,
        "pagos": alugueis_pagos,
        "pendentes": alugueis_pendentes,
        "valor_total_recebido": valor_total_recebido,
        "valor_total_pendente": valor_total_pendente,
        "valor_total": valor_total_recebido + valor_total_pendente
    }
