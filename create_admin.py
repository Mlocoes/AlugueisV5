#!/usr/bin/env python3
"""
Script para criar usuário administrador inicial
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.core.auth import get_password_hash
from app.core.config import settings
from app.models.usuario import Usuario


def create_admin():
    """Cria usuário administrador"""
    # Cria todas as tabelas
    print("Criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    
    # Abre sessão
    db: Session = SessionLocal()
    
    try:
        # Verifica se admin já existe
        existing_admin = db.query(Usuario).filter(Usuario.email == settings.ADMIN_EMAIL).first()
        
        if existing_admin:
            print(f"✅ Admin já existe: {existing_admin.email}")
            return
        
        # Cria admin
        admin = Usuario(
            nome="Administrador",
            email=settings.ADMIN_EMAIL,
            hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
            is_admin=True,
            is_active=True
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print("✅ Usuário administrador criado com sucesso!")
        print(f"   Email: {admin.email}")
        print(f"   ID: {admin.id}")
        
    except Exception as e:
        print(f"❌ Erro ao criar admin: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
