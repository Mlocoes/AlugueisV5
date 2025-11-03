"""
Sistema de Validação Robusta de Entrada
Implementa validações de segurança para todos os inputs
"""
import re
from typing import Optional
from email_validator import validate_email, EmailNotValidError
from fastapi import HTTPException
import html
import logging

logger = logging.getLogger(__name__)


class InputValidator:
    """Classe para validações de entrada de dados"""
    
    # Padrões de validação
    CPF_PATTERN = re.compile(r'^\d{11}$')
    CNPJ_PATTERN = re.compile(r'^\d{14}$')
    PHONE_PATTERN = re.compile(r'^\d{10,11}$')
    
    # Padrões perigosos (XSS, SQL Injection)
    XSS_PATTERNS = [
        re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
        re.compile(r'javascript:', re.IGNORECASE),
        re.compile(r'on\w+\s*=', re.IGNORECASE),  # onclick, onerror, etc
        re.compile(r'<iframe', re.IGNORECASE),
        re.compile(r'<object', re.IGNORECASE),
        re.compile(r'<embed', re.IGNORECASE),
    ]
    
    SQL_INJECTION_PATTERNS = [
        re.compile(r"(\bUNION\b|\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|\bDROP\b)", re.IGNORECASE),
        re.compile(r"(-{2}|;|\*/|/\*)", re.IGNORECASE),  # Comentários SQL
        re.compile(r"(\bOR\b|\bAND\b)\s+\d+\s*=\s*\d+", re.IGNORECASE),  # OR 1=1
    ]
    
    @staticmethod
    def validate_email_address(email: str) -> str:
        """
        Valida formato de email
        Retorna email normalizado ou levanta exceção
        """
        if not email or len(email) > 254:
            raise HTTPException(
                status_code=400,
                detail="Email inválido ou muito longo"
            )
        
        try:
            # Usa email-validator para validação robusta
            validation = validate_email(email, check_deliverability=False)
            return validation.normalized
        except EmailNotValidError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Email inválido: {str(e)}"
            )
    
    @staticmethod
    def validate_password(password: str) -> bool:
        """
        Valida senha forte:
        - Mínimo 8 caracteres
        - Pelo menos 1 letra maiúscula
        - Pelo menos 1 letra minúscula
        - Pelo menos 1 número
        - Pelo menos 1 caractere especial
        """
        if not password or len(password) < 8:
            raise HTTPException(
                status_code=400,
                detail="Senha deve ter no mínimo 8 caracteres"
            )
        
        if len(password) > 128:
            raise HTTPException(
                status_code=400,
                detail="Senha muito longa (máximo 128 caracteres)"
            )
        
        if not re.search(r'[A-Z]', password):
            raise HTTPException(
                status_code=400,
                detail="Senha deve conter pelo menos uma letra maiúscula"
            )
        
        if not re.search(r'[a-z]', password):
            raise HTTPException(
                status_code=400,
                detail="Senha deve conter pelo menos uma letra minúscula"
            )
        
        if not re.search(r'\d', password):
            raise HTTPException(
                status_code=400,
                detail="Senha deve conter pelo menos um número"
            )
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise HTTPException(
                status_code=400,
                detail="Senha deve conter pelo menos um caractere especial (!@#$%^&*...)"
            )
        
        return True
    
    @staticmethod
    def validate_cpf(cpf: Optional[str]) -> Optional[str]:
        """
        Valida CPF brasileiro
        Remove caracteres não numéricos e valida dígitos verificadores
        """
        if not cpf:
            return None
        
        # Remove caracteres não numéricos
        cpf_clean = re.sub(r'\D', '', cpf)
        
        if not InputValidator.CPF_PATTERN.match(cpf_clean):
            raise HTTPException(
                status_code=400,
                detail="CPF deve conter exatamente 11 dígitos"
            )
        
        # Verifica se não é uma sequência repetida (111.111.111-11)
        if cpf_clean == cpf_clean[0] * 11:
            raise HTTPException(
                status_code=400,
                detail="CPF inválido"
            )
        
        # Validação dos dígitos verificadores
        def calculate_digit(cpf_partial: str, weights: list) -> int:
            total = sum(int(digit) * weight for digit, weight in zip(cpf_partial, weights))
            remainder = total % 11
            return 0 if remainder < 2 else 11 - remainder
        
        # Primeiro dígito verificador
        first_digit = calculate_digit(cpf_clean[:9], range(10, 1, -1))
        if first_digit != int(cpf_clean[9]):
            raise HTTPException(status_code=400, detail="CPF inválido")
        
        # Segundo dígito verificador
        second_digit = calculate_digit(cpf_clean[:10], range(11, 1, -1))
        if second_digit != int(cpf_clean[10]):
            raise HTTPException(status_code=400, detail="CPF inválido")
        
        return cpf_clean
    
    @staticmethod
    def validate_cnpj(cnpj: Optional[str]) -> Optional[str]:
        """Valida CNPJ brasileiro"""
        if not cnpj:
            return None
        
        # Remove caracteres não numéricos
        cnpj_clean = re.sub(r'\D', '', cnpj)
        
        if not InputValidator.CNPJ_PATTERN.match(cnpj_clean):
            raise HTTPException(
                status_code=400,
                detail="CNPJ deve conter exatamente 14 dígitos"
            )
        
        # Verifica se não é uma sequência repetida
        if cnpj_clean == cnpj_clean[0] * 14:
            raise HTTPException(status_code=400, detail="CNPJ inválido")
        
        return cnpj_clean
    
    @staticmethod
    def validate_phone(phone: Optional[str]) -> Optional[str]:
        """Valida telefone brasileiro (10 ou 11 dígitos)"""
        if not phone:
            return None
        
        # Remove caracteres não numéricos
        phone_clean = re.sub(r'\D', '', phone)
        
        if not InputValidator.PHONE_PATTERN.match(phone_clean):
            raise HTTPException(
                status_code=400,
                detail="Telefone deve conter 10 ou 11 dígitos"
            )
        
        return phone_clean
    
    @staticmethod
    def sanitize_string(text: Optional[str], max_length: int = 500) -> Optional[str]:
        """
        Sanitiza string para prevenir XSS e SQL Injection
        - Remove tags HTML
        - Escapa caracteres especiais
        - Limita comprimento
        - Detecta padrões suspeitos
        """
        if not text:
            return None
        
        # Limitar comprimento
        if len(text) > max_length:
            raise HTTPException(
                status_code=400,
                detail=f"Texto muito longo (máximo {max_length} caracteres)"
            )
        
        # Verificar padrões XSS
        for pattern in InputValidator.XSS_PATTERNS:
            if pattern.search(text):
                logger.warning(f"XSS attempt detected: {text[:100]}")
                raise HTTPException(
                    status_code=400,
                    detail="Conteúdo potencialmente perigoso detectado"
                )
        
        # Verificar padrões SQL Injection
        for pattern in InputValidator.SQL_INJECTION_PATTERNS:
            if pattern.search(text):
                logger.warning(f"SQL Injection attempt detected: {text[:100]}")
                raise HTTPException(
                    status_code=400,
                    detail="Conteúdo potencialmente perigoso detectado"
                )
        
        # Escapar HTML
        sanitized = html.escape(text.strip())
        
        return sanitized
    
    @staticmethod
    def validate_nome(nome: str) -> str:
        """Valida nome de pessoa/empresa"""
        if not nome or len(nome) < 2:
            raise HTTPException(
                status_code=400,
                detail="Nome deve ter no mínimo 2 caracteres"
            )
        
        nome_clean = InputValidator.sanitize_string(nome, max_length=200)
        
        # Verificar se contém pelo menos algumas letras
        if not re.search(r'[a-zA-ZÀ-ÿ]', nome_clean):
            raise HTTPException(
                status_code=400,
                detail="Nome deve conter letras"
            )
        
        return nome_clean
    
    @staticmethod
    def validate_numeric_range(
        value: float,
        min_value: float = 0,
        max_value: float = 999999999,
        field_name: str = "Valor"
    ) -> float:
        """Valida que número está dentro de um range aceitável"""
        if value < min_value:
            raise HTTPException(
                status_code=400,
                detail=f"{field_name} não pode ser menor que {min_value}"
            )
        
        if value > max_value:
            raise HTTPException(
                status_code=400,
                detail=f"{field_name} não pode ser maior que {max_value}"
            )
        
        return value


# Instância global para uso fácil
validator = InputValidator()
