"""
Models package - Modelos SQLAlchemy do banco de dados
"""
# Imports dos modelos
from app.models.usuario import Usuario
from app.models.proprietario import Proprietario
from app.models.imovel import Imovel
from app.models.aluguel import AluguelMensal
from app.models.participacao import Participacao
from app.models.alias import Alias
from app.models.transferencia import Transferencia
from app.models.permissao_financeira import PermissaoFinanceira

__all__ = [
    "Usuario",
    "Proprietario",
    "Imovel",
    "AluguelMensal",
    "Participacao",
    "Alias",
    "Transferencia",
    "PermissaoFinanceira"
]
# from app.models.imovel import Imovel
# from app.models.participacao import Participacao
# from app.models.aluguel import AluguelMensal
# from app.models.alias import Alias, AliasProprietario
# from app.models.transferencia import Transferencia
# from app.models.permissao_financeira import PermissaoFinanceira

__all__ = []
