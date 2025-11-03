"""Rotas de autenticação"""
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Form
from sqlalchemy.orm import Session
from typing import Optional
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.database import get_db
from app.core.auth import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user_from_cookie,
    require_admin,
    set_auth_cookie,
    set_refresh_cookie,
    clear_auth_cookies,
    get_password_hash
)
from app.core.rate_limiter import limiter, get_rate_limit, ip_blacklist, check_ip_blacklist, security_logger
from app.core.validators import validator
from app.models.usuario import Usuario
from app.schemas.schemas import LoginRequest, LoginResponse, TokenResponse, UsuarioResponse


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
@limiter.limit(get_rate_limit("auth_strict"))
async def login(
    request: Request,
    credentials: LoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Autentica usuário e retorna tokens JWT
    Define cookies httpOnly com access_token e refresh_token
    Rate limit: 5 requisições por minuto
    """
    # Verificar se IP está na blacklist
    await check_ip_blacklist(request)
    
    # Validar email
    email_clean = validator.validate_email_address(credentials.email)
    
    # Obter IP do cliente para logs
    client_ip = get_remote_address(request)
    
    # Autentica usuário
    usuario = authenticate_user(db, email_clean, credentials.password)
    
    if not usuario:
        # Registrar tentativa falha
        ip_blacklist.record_failed_attempt(client_ip, "/api/auth/login")
        
        security_logger.warning(
            f"Failed login attempt for email {email_clean} from IP {client_ip}"
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )
    
    # Login bem-sucedido - limpar tentativas falhas
    ip_blacklist.clear_attempts(client_ip)
    
    security_logger.info(
        f"Successful login for user {usuario.email} (ID: {usuario.id}) from IP {client_ip}"
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
async def logout(response: Response, current_user: Usuario = Depends(get_current_user_from_cookie)):
    """Remove cookies de autenticação"""
    security_logger.info(f"User {current_user.email} (ID: {current_user.id}) logged out")
    clear_auth_cookies(response)
    return {"message": "Logout realizado com sucesso"}


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit(get_rate_limit("auth_moderate"))
async def refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Renova access token usando refresh token do cookie
    Rate limit: 10 requisições por minuto
    """
    # Verificar se IP está na blacklist
    await check_ip_blacklist(request)
    
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


@router.post("/register", response_model=UsuarioResponse, status_code=201)
@limiter.limit(get_rate_limit("auth_strict"))
async def register_user(
    request: Request,
    nome: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    cpf: Optional[str] = Form(None),
    telefone: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """
    Registra novo usuário (restrito a administradores)
    Apenas usuários com is_admin=True podem criar novos usuários
    Rate limit: 5 requisições por minuto
    
    Validações aplicadas:
    - Email em formato válido
    - Senha forte (mínimo 8 caracteres, maiúsculas, minúsculas, números e especiais)
    - CPF válido (se fornecido)
    - Telefone válido (se fornecido)
    - Nome sanitizado contra XSS/SQL Injection
    """
    # Validações robustas
    email_clean = validator.validate_email_address(email)
    validator.validate_password(password)
    nome_clean = validator.validate_nome(nome)
    cpf_clean = validator.validate_cpf(cpf) if cpf else None
    telefone_clean = validator.validate_phone(telefone) if telefone else None
    
    # Obter IP do cliente para logs
    client_ip = get_remote_address(request)
    
    security_logger.info(
        f"Admin {current_user.email} attempting to register new user {email_clean} from IP {client_ip}"
    )
    
    # Verifica se email já existe
    existing_user = db.query(Usuario).filter(Usuario.email == email_clean).first()
    if existing_user:
        security_logger.warning(f"Registration failed: email {email_clean} already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    # Verifica CPF se fornecido
    if cpf_clean:
        existing_cpf = db.query(Usuario).filter(Usuario.cpf == cpf_clean).first()
        if existing_cpf:
            security_logger.warning(f"Registration failed: CPF {cpf_clean} already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF já cadastrado"
            )
    
    # Cria novo usuário com dados validados e sanitizados
    new_user = Usuario(
        nome=nome_clean,
        email=email_clean,
        hashed_password=get_password_hash(password),
        cpf=cpf_clean,
        telefone=telefone_clean,
        is_admin=False,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    security_logger.info(
        f"New user {email_clean} (ID: {new_user.id}) successfully registered by admin {current_user.email}"
    )
    
    return UsuarioResponse.model_validate(new_user)
