"""Sistema de autenticação JWT"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings
from app.core.database import get_db
from app.models.usuario import Usuario


# Configuração de hashing de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security para Bearer token
security = HTTPBearer(auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha está correta"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Gera hash da senha"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Cria token JWT de acesso"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Cria token JWT de refresh (7 dias)"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decodifica token JWT"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )


def authenticate_user(db: Session, email: str, password: str) -> Optional[Usuario]:
    """Autentica usuário por email e senha"""
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    
    if not usuario:
        return None
    
    if not verify_password(password, usuario.hashed_password):
        return None
    
    if not usuario.is_active:
        return None
    
    return usuario


async def get_current_user_from_cookie(
    request: Request,
    db: Session = Depends(get_db)
) -> Usuario:
    """Obtém usuário atual do cookie JWT"""
    token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado"
        )
    
    try:
        payload = decode_token(token)
        user_id: int = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado"
        )
    
    if not usuario.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )
    
    return usuario


async def get_current_user_from_bearer(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Usuario:
    """Obtém usuário atual do Bearer token (para API)"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado"
        )
    
    token = credentials.credentials
    
    try:
        payload = decode_token(token)
        user_id: int = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado"
        )
    
    if not usuario.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )
    
    return usuario


def require_admin(current_user: Usuario = Depends(get_current_user_from_cookie)) -> Usuario:
    """Verifica se usuário é admin"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada: requer privilégios de administrador"
        )
    return current_user


def set_auth_cookie(response: Response, token: str):
    """Define cookie de autenticação"""
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=not settings.DEBUG,  # HTTPS em produção
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


def set_refresh_cookie(response: Response, refresh_token: str):
    """Define cookie de refresh token"""
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
        max_age=7 * 24 * 60 * 60  # 7 dias
    )


def clear_auth_cookies(response: Response):
    """Remove cookies de autenticação"""
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
