"""Rotas CRUD de Usuários/Proprietários"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.auth import get_current_user_from_cookie, require_admin, get_password_hash
from app.models.usuario import Usuario
from app.schemas.schemas import UsuarioCreate, UsuarioUpdate, UsuarioResponse


router = APIRouter(prefix="/api/usuarios", tags=["usuarios"])


@router.get("/", response_model=List[UsuarioResponse])
async def list_usuarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_admin: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    Lista usuários (apenas admins)
    """
    query = db.query(Usuario)
    
    # Filtro de busca
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Usuario.nome.ilike(search_filter),
                Usuario.email.ilike(search_filter),
                Usuario.cpf.ilike(search_filter)
            )
        )
    
    # Filtros
    if is_active is not None:
        query = query.filter(Usuario.is_active == is_active)
    
    if is_admin is not None:
        query = query.filter(Usuario.is_admin == is_admin)
    
    # Paginação
    usuarios = query.offset(skip).limit(limit).all()
    
    return [UsuarioResponse.model_validate(usuario) for usuario in usuarios]


@router.get("/proprietarios", response_model=List[UsuarioResponse])
async def list_proprietarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """
    Lista proprietários (usuários ativos)
    Todos os usuários autenticados podem ver a lista de proprietários
    """
    query = db.query(Usuario).filter(Usuario.is_active == True)
    
    # Filtro de busca
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Usuario.nome.ilike(search_filter),
                Usuario.email.ilike(search_filter)
            )
        )
    
    # Paginação
    proprietarios = query.offset(skip).limit(limit).all()
    
    return [UsuarioResponse.model_validate(p) for p in proprietarios]


@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def get_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """
    Obtém detalhes de um usuário
    - Admins podem ver qualquer usuário
    - Usuários normais só podem ver seu próprio perfil
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Verificar permissões
    if not current_user.is_admin and usuario.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para acessar este usuário"
        )
    
    return UsuarioResponse.model_validate(usuario)


@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def create_usuario(
    usuario_data: UsuarioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    Cria novo usuário (apenas admins)
    """
    # Verificar se email já existe
    existing_email = db.query(Usuario).filter(Usuario.email == usuario_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    # Verificar se CPF já existe
    if usuario_data.cpf:
        existing_cpf = db.query(Usuario).filter(Usuario.cpf == usuario_data.cpf).first()
        if existing_cpf:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF já cadastrado"
            )
    
    # Criar usuário
    user_dict = usuario_data.model_dump(exclude={'password'})
    user_dict['hashed_password'] = get_password_hash(usuario_data.password)
    
    new_usuario = Usuario(**user_dict)
    
    db.add(new_usuario)
    db.commit()
    db.refresh(new_usuario)
    
    return UsuarioResponse.model_validate(new_usuario)


@router.put("/{usuario_id}", response_model=UsuarioResponse)
async def update_usuario(
    usuario_id: int,
    usuario_data: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """
    Atualiza dados de um usuário
    - Admins podem atualizar qualquer usuário
    - Usuários normais só podem atualizar seu próprio perfil (exceto is_admin)
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Verificar permissões
    if not current_user.is_admin and usuario.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para editar este usuário"
        )
    
    # Usuários normais não podem alterar is_admin
    if not current_user.is_admin and usuario_data.is_admin is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para alterar status de administrador"
        )
    
    # Verificar email duplicado
    if usuario_data.email and usuario_data.email != usuario.email:
        existing = db.query(Usuario).filter(Usuario.email == usuario_data.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado"
            )
    
    # Verificar CPF duplicado
    if usuario_data.cpf and usuario_data.cpf != usuario.cpf:
        existing = db.query(Usuario).filter(Usuario.cpf == usuario_data.cpf).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF já cadastrado"
            )
    
    # Atualizar campos
    update_data = usuario_data.model_dump(exclude_unset=True, exclude={'password'})
    
    # Hash da nova senha se fornecida
    if usuario_data.password:
        update_data['hashed_password'] = get_password_hash(usuario_data.password)
    
    for field, value in update_data.items():
        setattr(usuario, field, value)
    
    db.commit()
    db.refresh(usuario)
    
    return UsuarioResponse.model_validate(usuario)


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    Desativa um usuário (soft delete)
    Apenas admins podem desativar usuários
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Não permitir desativar a si mesmo
    if usuario.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível desativar seu próprio usuário"
        )
    
    # Soft delete
    usuario.is_active = False
    db.commit()
    
    return None


@router.post("/{usuario_id}/reactivate", response_model=UsuarioResponse)
async def reactivate_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """Reativa um usuário desativado (apenas admins)"""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    usuario.is_active = True
    db.commit()
    db.refresh(usuario)
    
    return UsuarioResponse.model_validate(usuario)


@router.get("/stats/summary")
async def get_usuarios_stats(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """Retorna estatísticas dos usuários (apenas admins)"""
    total = db.query(Usuario).count()
    ativos = db.query(Usuario).filter(Usuario.is_active == True).count()
    inativos = db.query(Usuario).filter(Usuario.is_active == False).count()
    admins = db.query(Usuario).filter(Usuario.is_admin == True).count()
    
    return {
        "total": total,
        "ativos": ativos,
        "inativos": inativos,
        "admins": admins
    }
