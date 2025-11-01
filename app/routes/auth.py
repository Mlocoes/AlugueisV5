"""Rotas de autenticação"""
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user_from_cookie,
    set_auth_cookie,
    set_refresh_cookie,
    clear_auth_cookies,
    get_password_hash
)
from app.models.usuario import Usuario
from app.schemas.schemas import LoginRequest, LoginResponse, TokenResponse, UsuarioResponse


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: LoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Autentica usuário e retorna tokens JWT
    Define cookies httpOnly com access_token e refresh_token
    """
    # Autentica usuário
    usuario = authenticate_user(db, credentials.email, credentials.password)
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )
    
    # Cria tokens
    access_token = create_access_token(data={"sub": str(usuario.id)})
    refresh_token = create_refresh_token(data={"sub": str(usuario.id)})
    
    # Define cookies
    set_auth_cookie(response, access_token)
    set_refresh_cookie(response, refresh_token)
    
    # Retorna response
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UsuarioResponse.model_validate(usuario)
    )


@router.post("/logout")
async def logout(response: Response):
    """Remove cookies de autenticação"""
    clear_auth_cookies(response)
    return {"message": "Logout realizado com sucesso"}


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Renova access token usando refresh token do cookie
    """
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token não encontrado"
        )
    
    try:
        payload = decode_token(refresh_token)
        
        # Verifica se é refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        # Converter string para int
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado"
        )
    
    # Verifica se usuário existe
    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    
    if not usuario or not usuario.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo"
        )
    
    # Cria novo access token
    new_access_token = create_access_token(data={"sub": str(usuario.id)})
    
    # Atualiza cookie
    set_auth_cookie(response, new_access_token)
    
    return TokenResponse(access_token=new_access_token)


@router.get("/me", response_model=UsuarioResponse)
async def get_current_user_info(
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """Retorna informações do usuário autenticado"""
    return UsuarioResponse.model_validate(current_user)


@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    nome: str,
    email: str,
    password: str,
    cpf: str = None,
    telefone: str = None,
    db: Session = Depends(get_db)
):
    """
    Registra novo usuário (apenas para desenvolvimento)
    Em produção, isso deve ser restrito a admins
    """
    # Verifica se email já existe
    existing_user = db.query(Usuario).filter(Usuario.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    # Verifica CPF se fornecido
    if cpf:
        existing_cpf = db.query(Usuario).filter(Usuario.cpf == cpf).first()
        if existing_cpf:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF já cadastrado"
            )
    
    # Cria novo usuário
    new_user = Usuario(
        nome=nome,
        email=email,
        hashed_password=get_password_hash(password),
        cpf=cpf,
        telefone=telefone,
        is_admin=False,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UsuarioResponse.model_validate(new_user)
