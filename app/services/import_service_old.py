"""
Serviço de importação de dados a partir de arquivos Excel
Adaptado para os templates específicos do sistema
"""
from typing import List, Dict, Any, Optional, Tuple
import re
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from io import BytesIO

try:
    import pandas as pd
    import openpyxl
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.usuario import Usuario
from app.models.imovel import Imovel
from app.models.aluguel import AluguelMensal
from app.models.participacao import Participacao
from app.models.proprietario import Proprietario
from app.models.transferencia import Transferencia


class ImportacaoService:
    """Serviço para importação de dados via Excel/CSV"""

    def __init__(self):
        if not PANDAS_AVAILABLE:
            raise RuntimeError(
                "Dependências necessárias não instaladas. Execute: pip install pandas openpyxl"
            )

    # ==================== UTILITÁRIOS ====================

    @staticmethod
    def limpar_cpf_cnpj(documento: str) -> str:
        """Remove formatação de CPF/CNPJ deixando apenas números"""
        if not documento:
            return ""
        return re.sub(r'[^\d]', '', str(documento))

    @staticmethod
    def validar_cpf_cnpj(documento: str) -> bool:
        """Valida formato básico de CPF (11 dígitos) ou CNPJ (14 dígitos)"""
        doc = ImportacaoService.limpar_cpf_cnpj(documento)
        return len(doc) in [11, 14]

    @staticmethod
    def parse_valor_monetario(valor) -> Optional[Decimal]:
        """Converte valor monetário para Decimal"""
        if valor is None or str(valor).strip() in ['', '-', 'nan', 'NaN']:
            return None

        # Se já é número
        if isinstance(valor, (int, float, Decimal)):
            try:
                return Decimal(str(valor))
            except:
                return None

        # Processar como string
        s = str(valor).strip()
        negativo = s.startswith('-')
        if negativo:
            s = s[1:].strip()

        # Remover símbolos de moeda e espaços
        s = re.sub(r'[R$\s]', '', s)

        # Detectar formato: brasileiro (1.234,56) vs americano (1,234.56)
        if ',' in s and '.' in s:
            last_dot = s.rfind('.')
            last_comma = s.rfind(',')
            
            if last_dot > last_comma:
                # Formato americano: vírgula é milhares
                s = s.replace(',', '')
            else:
                # Formato brasileiro: ponto é milhares
                s = s.replace('.', '').replace(',', '.')
        elif ',' in s:
            # Apenas vírgula: assumir decimal brasileiro
            s = s.replace(',', '.')

        try:
            valor_decimal = Decimal(s)
            return -valor_decimal if negativo else valor_decimal
        except:
            return None

    @staticmethod
    def parse_data(data_str) -> Optional[date]:
        """Converte string ou datetime para date"""
        if data_str is None or str(data_str).strip() in ['', '-', 'nan', 'NaN']:
            return None

        # Se já é datetime/date
        if isinstance(data_str, datetime):
            return data_str.date()
        if isinstance(data_str, date):
            return data_str

        # Processar como string
        formatos = [
            '%d/%m/%Y',
            '%Y-%m-%d',
            '%d-%m-%Y',
            '%m/%d/%Y',
            '%d/%m/%y',
            '%Y/%m/%d'
        ]

        s = str(data_str).strip()
        for fmt in formatos:
            try:
                return datetime.strptime(s, fmt).date()
            except ValueError:
                continue

        return None

    @staticmethod
    def parse_mes_referencia(mes_str) -> Optional[str]:
        """Converte string para formato YYYY-MM"""
        if not mes_str or str(mes_str).strip() in ['', '-', 'nan', 'NaN']:
            return None

        s = str(mes_str).strip()

        # Se já está no formato correto
        if re.match(r'^\d{4}-\d{2}$', s):
            return s

        # Tentar formatos comuns
        formatos = [
            '%m/%Y',  # 11/2025
            '%Y-%m',  # 2025-11
            '%Y/%m',  # 2025/11
            '%m-%Y',  # 11-2025
        ]

        for fmt in formatos:
            try:
                dt = datetime.strptime(s, fmt)
                return dt.strftime('%Y-%m')
            except ValueError:
                continue

        return None

    @staticmethod
    def parse_boolean(valor) -> bool:
        """Converte valor para booleano"""
        if isinstance(valor, bool):
            return valor
        
        s = str(valor).strip().lower()
        return s in ['sim', 'yes', 'true', '1', 's', 'y', 't']

    # ==================== IMPORTAÇÃO DE PROPRIETÁRIOS ====================

    def importar_proprietarios(self, file_content: bytes, db: Session) -> Dict[str, Any]:
        """Importa proprietários/usuários do Excel/CSV"""
        try:
            # Tentar ler como Excel primeiro, depois CSV
            try:
                df = pd.read_excel(BytesIO(file_content), sheet_name=0)
            except:
                df = pd.read_csv(BytesIO(file_content))

            # Normalizar nomes das colunas
            df.columns = df.columns.str.strip()

            # Validar colunas obrigatórias
            colunas_obrigatorias = ['nome', 'email']
            colunas_encontradas = [col.lower() for col in df.columns]
            
            faltando = [col for col in colunas_obrigatorias if col not in colunas_encontradas]
            if faltando:
                return {
                    'success': False,
                    'message': f'Colunas obrigatórias faltando: {", ".join(faltando)}',
                    'colunas_encontradas': list(df.columns)
                }

            sucesso = 0
            erros = []
            warnings = []

            for idx, row in df.iterrows():
                linha_num = idx + 2  # +2 porque começa em 1 e tem cabeçalho
                
                try:
                    # Extrair dados (case-insensitive)
                    row_dict = {k.lower(): v for k, v in row.items()}
                    
                    nome = str(row_dict.get('nome', '')).strip()
                    email = str(row_dict.get('email', '')).strip().lower()
                    
                    if not nome or not email:
                        erros.append(f"Linha {linha_num}: Nome e email são obrigatórios")
                        continue

                    # Verificar se usuário já existe
                    usuario_existe = db.query(Usuario).filter(
                        func.lower(Usuario.email) == email
                    ).first()

                    if usuario_existe:
                        warnings.append(f"Linha {linha_num}: Usuário {email} já existe, pulando")
                        continue

                    # Criar usuário
                    usuario = Usuario(
                        nome=nome,
                        email=email,
                        senha_hash="$2b$12$default",  # Senha padrão, deve ser alterada
                        ativo=self.parse_boolean(row_dict.get('ativo', True)),
                        tipo=str(row_dict.get('tipo', 'proprietario')).lower()
                    )

                    db.add(usuario)
                    sucesso += 1

                except Exception as e:
                    erros.append(f"Linha {linha_num}: {str(e)}")

            if sucesso > 0:
                db.commit()

            return {
                'success': True,
                'importados': sucesso,
                'erros': erros,
                'warnings': warnings,
                'total_linhas': len(df)
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao processar arquivo: {str(e)}'
            }

    # ==================== IMPORTAÇÃO DE IMÓVEIS ====================

    def importar_imoveis(self, file_content: bytes, db: Session) -> Dict[str, Any]:
        """Importa imóveis do Excel/CSV"""
        try:
            try:
                df = pd.read_excel(BytesIO(file_content), sheet_name=0)
            except:
                df = pd.read_csv(BytesIO(file_content))

            df.columns = df.columns.str.strip()
            colunas_encontradas = [col.lower() for col in df.columns]

            # Colunas obrigatórias
            if 'codigo' not in colunas_encontradas:
                return {
                    'success': False,
                    'message': 'Coluna "codigo" é obrigatória',
                    'colunas_encontradas': list(df.columns)
                }

            sucesso = 0
            erros = []
            warnings = []

            for idx, row in df.iterrows():
                linha_num = idx + 2
                
                try:
                    row_dict = {k.lower(): v for k, v in row.items()}
                    
                    codigo = str(row_dict.get('codigo', '')).strip()
                    if not codigo:
                        erros.append(f"Linha {linha_num}: Código é obrigatório")
                        continue

                    # Verificar se imóvel já existe
                    imovel_existe = db.query(Imovel).filter(
                        Imovel.codigo == codigo
                    ).first()

                    if imovel_existe:
                        warnings.append(f"Linha {linha_num}: Imóvel {codigo} já existe, pulando")
                        continue

                    # Criar imóvel
                    imovel = Imovel(
                        codigo=codigo,
                        endereco=str(row_dict.get('endereco', '')).strip(),
                        tipo=str(row_dict.get('tipo', 'residencial')).lower(),
                        ativo=self.parse_boolean(row_dict.get('ativo', True))
                    )

                    db.add(imovel)
                    sucesso += 1

                except Exception as e:
                    erros.append(f"Linha {linha_num}: {str(e)}")

            if sucesso > 0:
                db.commit()

            return {
                'success': True,
                'importados': sucesso,
                'erros': erros,
                'warnings': warnings,
                'total_linhas': len(df)
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao processar arquivo: {str(e)}'
            }

    # ==================== IMPORTAÇÃO DE ALUGUÉIS ====================

    def importar_alugueis(self, file_content: bytes, db: Session) -> Dict[str, Any]:
        """Importa aluguéis do Excel/CSV"""
        try:
            try:
                df = pd.read_excel(BytesIO(file_content), sheet_name=0)
            except:
                df = pd.read_csv(BytesIO(file_content))

            df.columns = df.columns.str.strip()
            colunas_encontradas = [col.lower() for col in df.columns]

            # Colunas obrigatórias
            obrigatorias = ['codigo_imovel', 'mes_referencia', 'valor_aluguel']
            faltando = [col for col in obrigatorias if col not in colunas_encontradas]
            
            if faltando:
                return {
                    'success': False,
                    'message': f'Colunas obrigatórias faltando: {", ".join(faltando)}',
                    'colunas_encontradas': list(df.columns)
                }

            sucesso = 0
            erros = []
            warnings = []

            for idx, row in df.iterrows():
                linha_num = idx + 2
                
                try:
                    row_dict = {k.lower(): v for k, v in row.items()}
                    
                    codigo_imovel = str(row_dict.get('codigo_imovel', '')).strip()
                    mes_ref = self.parse_mes_referencia(row_dict.get('mes_referencia'))
                    valor_aluguel = self.parse_valor_monetario(row_dict.get('valor_aluguel'))

                    if not codigo_imovel or not mes_ref or valor_aluguel is None:
                        erros.append(f"Linha {linha_num}: Dados obrigatórios faltando")
                        continue

                    # Buscar imóvel
                    imovel = db.query(Imovel).filter(Imovel.codigo == codigo_imovel).first()
                    if not imovel:
                        erros.append(f"Linha {linha_num}: Imóvel {codigo_imovel} não encontrado")
                        continue

                    # Verificar se aluguel já existe
                    aluguel_existe = db.query(AluguelMensal).filter(
                        AluguelMensal.imovel_id == imovel.id,
                        AluguelMensal.mes_referencia == mes_ref
                    ).first()

                    if aluguel_existe:
                        warnings.append(f"Linha {linha_num}: Aluguel já existe para {codigo_imovel} em {mes_ref}")
                        continue

                    # Criar aluguel
                    aluguel = AluguelMensal(
                        imovel_id=imovel.id,
                        mes_referencia=mes_ref,
                        valor_aluguel=float(valor_aluguel),
                        valor_condominio=float(self.parse_valor_monetario(row_dict.get('valor_condominio', 0)) or 0),
                        valor_iptu=float(self.parse_valor_monetario(row_dict.get('valor_iptu', 0)) or 0),
                        valor_luz=float(self.parse_valor_monetario(row_dict.get('valor_luz', 0)) or 0),
                        valor_agua=float(self.parse_valor_monetario(row_dict.get('valor_agua', 0)) or 0),
                        valor_gas=float(self.parse_valor_monetario(row_dict.get('valor_gas', 0)) or 0),
                        outras_despesas=float(self.parse_valor_monetario(row_dict.get('outras_despesas', 0)) or 0),
                        data_pagamento=self.parse_data(row_dict.get('data_pagamento')),
                        pago=self.parse_boolean(row_dict.get('pago', False)),
                        observacoes=str(row_dict.get('observacoes', '')).strip()
                    )

                    db.add(aluguel)
                    sucesso += 1

                except Exception as e:
                    erros.append(f"Linha {linha_num}: {str(e)}")

            if sucesso > 0:
                db.commit()

            return {
                'success': True,
                'importados': sucesso,
                'erros': erros,
                'warnings': warnings,
                'total_linhas': len(df)
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao processar arquivo: {str(e)}'
            }

    # ==================== PREVIEW ====================

    def preview_arquivo(self, file_content: bytes, tipo: str = 'excel') -> Dict[str, Any]:
        """Gera preview do arquivo antes da importação"""
        try:
            try:
                df = pd.read_excel(BytesIO(file_content), sheet_name=0, nrows=10)
            except:
                df = pd.read_csv(BytesIO(file_content), nrows=10)

            # Converter para formato JSON-serializable
            preview_data = []
            for idx, row in df.iterrows():
                preview_data.append({col: str(val) for col, val in row.items()})

            return {
                'success': True,
                'colunas': list(df.columns),
                'preview': preview_data,
                'total_linhas_preview': len(preview_data)
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao gerar preview: {str(e)}'
            }
