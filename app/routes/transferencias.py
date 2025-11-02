"""
Rotas para gerenciamento de transferências entre proprietários
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from app.core.database import get_db
from app.core.auth import get_current_user_from_cookie
from app.models.usuario import Usuario
from app.models.transferencia import Transferencia
from app.models.aluguel import AluguelMensal

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# ==================== PÁGINA WEB ====================

@router.get("/transferencias", response_class=HTMLResponse)
async def transferencias_page(
    request: Request,
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """Renderiza a página de transferências"""
    return templates.TemplateResponse(
        "transferencias.html",
        {"request": request, "user": current_user}
    )


# ==================== API REST ====================

@router.get("/api/transferencias")
async def listar_transferencias(
    mes_referencia: Optional[str] = None,
    origem_id: Optional[int] = None,
    destino_id: Optional[int] = None,
    confirmada: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """Lista todas as transferências com filtros opcionais"""
    query = db.query(Transferencia)
    
    # Aplicar filtros
    if mes_referencia:
        query = query.filter(Transferencia.mes_referencia == mes_referencia)
    if origem_id:
        query = query.filter(Transferencia.origem_id == origem_id)
    if destino_id:
        query = query.filter(Transferencia.destino_id == destino_id)
    if confirmada is not None:
        query = query.filter(Transferencia.confirmada == confirmada)
    
    # Ordenar por data de criação (mais recente primeiro)
    transferencias = query.order_by(Transferencia.created_at.desc()).all()
    
    # Montar resposta com dados completos
    resultado = []
    for t in transferencias:
        resultado.append({
            "id": t.id,
            "origem_id": t.origem_id,
            "origem_nome": t.origem.nome if t.origem else "N/A",
            "destino_id": t.destino_id,
            "destino_nome": t.destino.nome if t.destino else "N/A",
            "mes_referencia": t.mes_referencia,
            "valor": t.valor,
            "confirmada": t.confirmada,
            "data_confirmacao": t.data_confirmacao.isoformat() if t.data_confirmacao else None,
            "descricao": t.descricao,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "updated_at": t.updated_at.isoformat() if t.updated_at else None
        })
    
    return {"transferencias": resultado, "total": len(resultado)}


@router.get("/api/transferencias/{transferencia_id}")
async def obter_transferencia(
    transferencia_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """Obtém detalhes de uma transferência específica"""
    transferencia = db.query(Transferencia).filter(
        Transferencia.id == transferencia_id
    ).first()
    
    if not transferencia:
        raise HTTPException(status_code=404, detail="Transferência não encontrada")
    
    return {
        "id": transferencia.id,
        "origem_id": transferencia.origem_id,
        "origem_nome": transferencia.origem.nome if transferencia.origem else "N/A",
        "destino_id": transferencia.destino_id,
        "destino_nome": transferencia.destino.nome if transferencia.destino else "N/A",
        "mes_referencia": transferencia.mes_referencia,
        "valor": transferencia.valor,
        "confirmada": transferencia.confirmada,
        "data_confirmacao": transferencia.data_confirmacao.isoformat() if transferencia.data_confirmacao else None,
        "descricao": transferencia.descricao,
        "created_at": transferencia.created_at.isoformat() if transferencia.created_at else None,
        "updated_at": transferencia.updated_at.isoformat() if transferencia.updated_at else None
    }


@router.post("/api/transferencias")
async def criar_transferencia(
    data: dict,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """Cria uma nova transferência"""
    
    # Validações
    if not data.get("origem_id") or not data.get("destino_id"):
        raise HTTPException(status_code=400, detail="Origem e destino são obrigatórios")
    
    if data["origem_id"] == data["destino_id"]:
        raise HTTPException(status_code=400, detail="Origem e destino não podem ser iguais")
    
    if not data.get("mes_referencia"):
        raise HTTPException(status_code=400, detail="Mês de referência é obrigatório")
    
    if not data.get("valor") or data["valor"] <= 0:
        raise HTTPException(status_code=400, detail="Valor deve ser maior que zero")
    
    # Verificar se usuários existem
    origem = db.query(Usuario).filter(Usuario.id == data["origem_id"]).first()
    destino = db.query(Usuario).filter(Usuario.id == data["destino_id"]).first()
    
    if not origem:
        raise HTTPException(status_code=404, detail="Usuário de origem não encontrado")
    if not destino:
        raise HTTPException(status_code=404, detail="Usuário de destino não encontrado")
    
    # Criar transferência
    transferencia = Transferencia(
        origem_id=data["origem_id"],
        destino_id=data["destino_id"],
        mes_referencia=data["mes_referencia"],
        valor=float(data["valor"]),
        descricao=data.get("descricao", ""),
        confirmada=data.get("confirmada", False),
        data_confirmacao=date.today() if data.get("confirmada") else None
    )
    
    db.add(transferencia)
    db.commit()
    db.refresh(transferencia)
    
    return {
        "message": "Transferência criada com sucesso",
        "id": transferencia.id,
        "transferencia": {
            "id": transferencia.id,
            "origem_id": transferencia.origem_id,
            "origem_nome": origem.nome,
            "destino_id": transferencia.destino_id,
            "destino_nome": destino.nome,
            "mes_referencia": transferencia.mes_referencia,
            "valor": transferencia.valor,
            "confirmada": transferencia.confirmada,
            "descricao": transferencia.descricao
        }
    }


@router.put("/api/transferencias/{transferencia_id}")
async def atualizar_transferencia(
    transferencia_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """Atualiza uma transferência existente"""
    
    transferencia = db.query(Transferencia).filter(
        Transferencia.id == transferencia_id
    ).first()
    
    if not transferencia:
        raise HTTPException(status_code=404, detail="Transferência não encontrada")
    
    # Validações
    if "origem_id" in data and "destino_id" in data:
        if data["origem_id"] == data["destino_id"]:
            raise HTTPException(status_code=400, detail="Origem e destino não podem ser iguais")
    
    if "valor" in data and data["valor"] <= 0:
        raise HTTPException(status_code=400, detail="Valor deve ser maior que zero")
    
    # Atualizar campos
    if "origem_id" in data:
        origem = db.query(Usuario).filter(Usuario.id == data["origem_id"]).first()
        if not origem:
            raise HTTPException(status_code=404, detail="Usuário de origem não encontrado")
        transferencia.origem_id = data["origem_id"]
    
    if "destino_id" in data:
        destino = db.query(Usuario).filter(Usuario.id == data["destino_id"]).first()
        if not destino:
            raise HTTPException(status_code=404, detail="Usuário de destino não encontrado")
        transferencia.destino_id = data["destino_id"]
    
    if "mes_referencia" in data:
        transferencia.mes_referencia = data["mes_referencia"]
    
    if "valor" in data:
        transferencia.valor = float(data["valor"])
    
    if "descricao" in data:
        transferencia.descricao = data["descricao"]
    
    if "confirmada" in data:
        transferencia.confirmada = data["confirmada"]
        if data["confirmada"] and not transferencia.data_confirmacao:
            transferencia.data_confirmacao = date.today()
        elif not data["confirmada"]:
            transferencia.data_confirmacao = None
    
    transferencia.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(transferencia)
    
    return {
        "message": "Transferência atualizada com sucesso",
        "transferencia": {
            "id": transferencia.id,
            "origem_id": transferencia.origem_id,
            "origem_nome": transferencia.origem.nome,
            "destino_id": transferencia.destino_id,
            "destino_nome": transferencia.destino.nome,
            "mes_referencia": transferencia.mes_referencia,
            "valor": transferencia.valor,
            "confirmada": transferencia.confirmada,
            "descricao": transferencia.descricao
        }
    }


@router.delete("/api/transferencias/{transferencia_id}")
async def excluir_transferencia(
    transferencia_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """Exclui uma transferência"""
    
    transferencia = db.query(Transferencia).filter(
        Transferencia.id == transferencia_id
    ).first()
    
    if not transferencia:
        raise HTTPException(status_code=404, detail="Transferência não encontrada")
    
    db.delete(transferencia)
    db.commit()
    
    return {"message": "Transferência excluída com sucesso"}


@router.post("/api/transferencias/{transferencia_id}/confirmar")
async def confirmar_transferencia(
    transferencia_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """Confirma uma transferência pendente"""
    
    transferencia = db.query(Transferencia).filter(
        Transferencia.id == transferencia_id
    ).first()
    
    if not transferencia:
        raise HTTPException(status_code=404, detail="Transferência não encontrada")
    
    if transferencia.confirmada:
        raise HTTPException(status_code=400, detail="Transferência já confirmada")
    
    transferencia.confirmada = True
    transferencia.data_confirmacao = date.today()
    transferencia.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(transferencia)
    
    return {
        "message": "Transferência confirmada com sucesso",
        "transferencia": {
            "id": transferencia.id,
            "confirmada": transferencia.confirmada,
            "data_confirmacao": transferencia.data_confirmacao.isoformat()
        }
    }


@router.get("/api/transferencias/estatisticas/resumo")
async def obter_estatisticas(
    mes_referencia: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """Obtém estatísticas de transferências"""
    
    query = db.query(Transferencia)
    
    if mes_referencia:
        query = query.filter(Transferencia.mes_referencia == mes_referencia)
    
    transferencias = query.all()
    
    total_transferencias = len(transferencias)
    total_confirmadas = sum(1 for t in transferencias if t.confirmada)
    total_pendentes = total_transferencias - total_confirmadas
    valor_total = sum(t.valor for t in transferencias)
    valor_confirmado = sum(t.valor for t in transferencias if t.confirmada)
    valor_pendente = valor_total - valor_confirmado
    
    return {
        "total_transferencias": total_transferencias,
        "total_confirmadas": total_confirmadas,
        "total_pendentes": total_pendentes,
        "valor_total": valor_total,
        "valor_confirmado": valor_confirmado,
        "valor_pendente": valor_pendente
    }
