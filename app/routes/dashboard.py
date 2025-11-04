"""
Rotas do Dashboard com métricas e gráficos
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, case
from typing import Optional
from datetime import datetime, date, timedelta
from decimal import Decimal

from app.core.database import get_db
from app.core.auth import get_current_user_from_cookie
from app.models.usuario import Usuario
from app.models.imovel import Imovel
from app.models.aluguel import AluguelMensal
from app.models.proprietario import Proprietario
from pydantic import BaseModel


router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


# Schemas
class DashboardStats(BaseModel):
    total_imoveis: int
    imoveis_ativos: int
    total_proprietarios: int
    total_alugueis: int
    valor_total_esperado: float
    valor_total_recebido: float
    taxa_recebimento: float
    mes_atual: str
    ano_atual: int


class EvolutionData(BaseModel):
    mes: int
    mes_nome: str
    valor_esperado: float
    valor_recebido: float
    taxa_recebimento: float


class DistributionData(BaseModel):
    imovel_nome: str
    valor_total: float
    percentual: float


# Helper function
def _build_base_query(db: Session, current_user: Usuario, ano_filtro: int, mes_filtro: Optional[int] = None):
    """
    Constrói query base de aluguéis com filtros de permissão, ano e mês (opcional)
    
    Args:
        db: Sessão do banco
        current_user: Usuário atual
        ano_filtro: Ano para filtrar
        mes_filtro: Mês para filtrar (opcional)
    
    Returns:
        Query configurada com os filtros
    """
    query = db.query(AluguelMensal)
    
    # Filtro de permissões
    if not current_user.is_admin:
        query = query.join(Imovel).filter(Imovel.proprietario_id == current_user.id)
    
    # Filtrar por ano
    query = query.filter(AluguelMensal.mes_referencia.like(f"{ano_filtro}%"))
    
    # Filtrar por mês se especificado
    if mes_filtro:
        mes_ref = f"{ano_filtro}-{mes_filtro:02d}"
        query = query.filter(AluguelMensal.mes_referencia == mes_ref)
    
    return query


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    ano: Optional[int] = Query(None, description="Ano para filtrar (padrão: ano atual)"),
    mes: Optional[int] = Query(None, description="Mês para filtrar (padrão: todos os meses do ano)"),
    current_user: Usuario = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    """
    Retorna estatísticas agregadas do dashboard
    Query otimizada com agregações SQL
    
    IMPORTANTE: 
    - Valor Esperado: usa filtro de mês quando especificado (valor do mês selecionado)
    - Valor Recebido: sempre usa dados acumulados do ano inteiro
    """
    # Determinar período
    ano_filtro = ano or datetime.now().year
    mes_atual = datetime.now().month
    
    # Query para Valor Esperado (filtrado por mês se especificado)
    query_esperado = _build_base_query(db, current_user, ano_filtro, mes)
    
    # Calcular Valor Esperado (do mês ou ano conforme filtro)
    stats_esperado = query_esperado.with_entities(
        func.count(AluguelMensal.id).label('total_alugueis'),
        func.sum(AluguelMensal.valor_total).label('valor_esperado')
    ).first()
    
    # Query para Valor Recebido (SEMPRE acumulado do ano inteiro - sem filtro de mês)
    query_recebido = _build_base_query(db, current_user, ano_filtro, mes_filtro=None)
    
    # Calcular Valor Recebido (acumulado do ano)
    stats_recebido = query_recebido.with_entities(
        func.sum(
            case(
                (AluguelMensal.pago == True, AluguelMensal.valor_total),
                else_=0
            )
        ).label('valor_recebido')
    ).first()
    
    # Estatísticas de imóveis
    query_imoveis = db.query(Imovel)
    if not current_user.is_admin:
        query_imoveis = query_imoveis.filter(Imovel.proprietario_id == current_user.id)
    
    total_imoveis = query_imoveis.count()
    imoveis_ativos = query_imoveis.filter(Imovel.is_active == True).count()
    
    # Total de proprietários
    total_proprietarios = db.query(Proprietario).count()
    
    # Calcular valores
    valor_esperado = float(stats_esperado.valor_esperado or 0)
    valor_recebido = float(stats_recebido.valor_recebido or 0)
    
    # Taxa de recebimento é calculada sobre o total do ano (usar mesma query que valor_recebido)
    query_esperado_ano = _build_base_query(db, current_user, ano_filtro, mes_filtro=None)
    stats_esperado_ano = query_esperado_ano.with_entities(
        func.sum(AluguelMensal.valor_total).label('valor_esperado_ano')
    ).first()
    valor_esperado_ano = float(stats_esperado_ano.valor_esperado_ano or 0)
    
    taxa_recebimento = (valor_recebido / valor_esperado_ano * 100) if valor_esperado_ano > 0 else 0
    
    return DashboardStats(
        total_imoveis=total_imoveis,
        imoveis_ativos=imoveis_ativos,
        total_proprietarios=total_proprietarios,
        total_alugueis=stats_esperado.total_alugueis or 0,
        valor_total_esperado=valor_esperado,
        valor_total_recebido=valor_recebido,
        taxa_recebimento=round(taxa_recebimento, 2),
        mes_atual=f"{mes_atual:02d}",
        ano_atual=ano_filtro
    )


@router.get("/evolution", response_model=list[EvolutionData])
async def get_evolution_data(
    ano: Optional[int] = Query(None, description="Ano para análise (padrão: ano atual)"),
    current_user: Usuario = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    """
    Retorna evolução mensal de receitas para gráfico de linha
    """
    ano_filtro = ano or datetime.now().year
    
    # Query agregada por mês usando valor_total
    query = db.query(
        func.substr(AluguelMensal.mes_referencia, 6, 2).label('mes'),
        func.sum(AluguelMensal.valor_total).label('valor_esperado'),
        func.sum(
            case(
                (AluguelMensal.pago == True, AluguelMensal.valor_total),
                else_=0
            )
        ).label('valor_recebido')
    )
    
    # Filtro de permissões
    if not current_user.is_admin:
        query = query.join(Imovel).filter(Imovel.proprietario_id == current_user.id)
    
    query = query.filter(
        AluguelMensal.mes_referencia.like(f"{ano_filtro}%")
    ).group_by(
        func.substr(AluguelMensal.mes_referencia, 6, 2)
    ).order_by('mes')
    
    resultados = query.all()
    
    # Mapear nomes dos meses
    meses_nomes = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    
    # Criar dados para todos os 12 meses
    evolution = []
    resultados_dict = {int(r.mes): r for r in resultados}
    
    for mes_num in range(1, 13):
        if mes_num in resultados_dict:
            r = resultados_dict[mes_num]
            valor_esperado = float(r.valor_esperado or 0)
            valor_recebido = float(r.valor_recebido or 0)
            taxa = (valor_recebido / valor_esperado * 100) if valor_esperado > 0 else 0
        else:
            valor_esperado = 0.0
            valor_recebido = 0.0
            taxa = 0.0
        
        evolution.append(EvolutionData(
            mes=mes_num,
            mes_nome=meses_nomes[mes_num - 1],
            valor_esperado=valor_esperado,
            valor_recebido=valor_recebido,
            taxa_recebimento=round(taxa, 2)
        ))
    
    return evolution


@router.get("/distribution", response_model=list[DistributionData])
async def get_distribution_data(
    ano: Optional[int] = Query(None, description="Ano para análise (padrão: ano atual)"),
    limit: int = Query(10, description="Número máximo de imóveis"),
    current_user: Usuario = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    """
    Retorna distribuição de receitas por imóvel para gráfico de pizza
    """
    ano_filtro = ano or datetime.now().year
    
    # Query agregada por imóvel usando valor_total
    query = db.query(
        Imovel.nome.label('imovel_nome'),
        func.sum(AluguelMensal.valor_total).label('valor_total')
    ).join(
        AluguelMensal, AluguelMensal.imovel_id == Imovel.id
    )
    
    # Filtro de permissões
    if not current_user.is_admin:
        query = query.filter(Imovel.proprietario_id == current_user.id)
    
    query = query.filter(
        AluguelMensal.mes_referencia.like(f"{ano_filtro}%")
    ).group_by(
        Imovel.id, Imovel.nome
    ).order_by(
        func.sum(AluguelMensal.valor_total).desc()
    ).limit(limit)
    
    resultados = query.all()
    
    # Calcular total para percentuais
    total_geral = sum(float(r.valor_total or 0) for r in resultados)
    
    # Criar lista de distribuição
    distribution = []
    for r in resultados:
        valor = float(r.valor_total or 0)
        percentual = (valor / total_geral * 100) if total_geral > 0 else 0
        
        distribution.append(DistributionData(
            imovel_nome=r.imovel_nome or "Sem nome",
            valor_total=valor,
            percentual=round(percentual, 2)
        ))
    
    return distribution
