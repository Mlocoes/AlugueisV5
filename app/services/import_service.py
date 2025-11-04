"""
Serviço de importação de dados a partir de arquivos Excel
Adaptado para os templates específicos do sistema (excel/*.xlsx)

Estruturas esperadas:
- Proprietarios.xlsx: Nome, Sobrenome, Documento, Tipo Documento, Endereço, Telefone, Email
- Imoveis.xlsx: Nome, Endereço, Tipo, Área Total, Área Construida, Valor Catastral, Valor Mercado, IPTU Anual, Condominio
- Participacoes.xlsx: Nome, Endereço, VALOR, [nomes dos proprietários com percentuais]
- Alugueis.xlsx: Múltiplas abas/sheets (uma por mês), cada aba com [data], Valor Total, [nomes dos proprietários com valores], Taxa de Administração
- Transferencias.xlsx: formato matricial com datas e valores

IMPORTANTE: O importador de Alugueis agora processa TODAS as abas do arquivo Excel,
permitindo importar dados de todos os meses de uma só vez.
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
from sqlalchemy import func, or_

from app.models.usuario import Usuario
from app.models.imovel import Imovel
from app.models.aluguel import AluguelMensal
from app.models.participacao import Participacao
from app.models.proprietario import Proprietario
from app.models.transferencia import Transferencia


class ImportacaoService:
    """Serviço para importação de dados via Excel"""

    def __init__(self):
        if not PANDAS_AVAILABLE:
            raise RuntimeError(
                "Dependências necessárias não instaladas. Execute: pip install pandas openpyxl"
            )

    # ==================== UTILITÁRIOS ====================

    @staticmethod
    def limpar_documento(documento: str) -> str:
        """Remove formatação de CPF/CNPJ deixando apenas números"""
        if not documento:
            return ""
        return re.sub(r'[^\d]', '', str(documento))

    @staticmethod
    def parse_valor(valor) -> Optional[float]:
        """Converte valor monetário para float"""
        if valor is None or pd.isna(valor) or str(valor).strip() in ['', '-', 'nan', 'NaN']:
            return None

        if isinstance(valor, (int, float)):
            return float(valor)

        # Processar como string
        s = str(valor).strip()
        negativo = s.startswith('-')
        if negativo:
            s = s[1:].strip()

        # Remover símbolos de moeda e espaços
        s = re.sub(r'[R$\s]', '', s)

        # Converter vírgula para ponto
        s = s.replace(',', '.')

        try:
            valor_float = float(s)
            return -valor_float if negativo else valor_float
        except:
            return None

    @staticmethod
    def parse_data(data) -> Optional[datetime]:
        """Converte para datetime"""
        if data is None or pd.isna(data):
            return None

        if isinstance(data, datetime):
            return data
        
        if isinstance(data, date):
            return datetime.combine(data, datetime.min.time())

        # Tentar parsear string
        try:
            return pd.to_datetime(data)
        except:
            return None

    @staticmethod
    def mes_referencia_from_date(data: datetime) -> str:
        """Converte datetime para formato YYYY-MM"""
        if not data:
            return None
        return data.strftime('%Y-%m')

    # ==================== IMPORTAÇÃO DE PROPRIETÁRIOS ====================

    def importar_proprietarios(self, file_content: bytes, db: Session) -> Dict[str, Any]:
        """
        Importa proprietários do arquivo Proprietarios.xlsx
        
        Colunas esperadas:
        - Nome, Sobrenome, Documento, Tipo Documento, Endereço, Telefone, Email
        
        Retorna: {success, importados, erros, warnings, total_linhas}
        """
        try:
            df = pd.read_excel(BytesIO(file_content))
            
            importados = 0
            erros = []
            warnings = []
            
            for idx, row in df.iterrows():
                linha = idx + 2  # +2 porque Excel começa em 1 e tem cabeçalho
                
                try:
                    # Extrair dados
                    nome = str(row.get('Nome', '')).strip()
                    sobrenome = str(row.get('Sobrenome', '')).strip()
                    nome_completo = f"{nome} {sobrenome}".strip()
                    
                    documento = str(row.get('Documento', '')).strip()
                    tipo_doc = str(row.get('Tipo Documento', 'CPF')).strip().upper()
                    endereco = str(row.get('Endereço', '')) if not pd.isna(row.get('Endereço')) else None
                    telefone = str(row.get('Telefone', '')) if not pd.isna(row.get('Telefone')) else None
                    email = str(row.get('Email', '')).strip().lower() if not pd.isna(row.get('Email')) else None
                    
                    # Validações básicas
                    if not nome_completo:
                        erros.append(f"Linha {linha}: Nome é obrigatório")
                        continue
                    
                    if not email:
                        erros.append(f"Linha {linha}: Email é obrigatório")
                        continue
                    
                    # Validar email único
                    email_existe = db.query(Proprietario).filter(Proprietario.email == email).first()
                    if email_existe:
                        warnings.append(f"Linha {linha}: Email {email} já existe, pulando")
                        continue
                    
                    # Limpar documento
                    doc_limpo = self.limpar_documento(documento)
                    
                    # Determinar tipo de pessoa
                    tipo_pessoa = 'juridica' if tipo_doc == 'CNPJ' or len(doc_limpo) == 14 else 'fisica'
                    
                    # Criar proprietário
                    proprietario = Proprietario(
                        tipo_pessoa=tipo_pessoa,
                        nome=nome_completo,
                        cpf=doc_limpo if tipo_pessoa == 'fisica' and doc_limpo else None,
                        cnpj=doc_limpo if tipo_pessoa == 'juridica' and doc_limpo else None,
                        email=email,
                        telefone=telefone,
                        endereco=endereco,
                        is_active=True
                    )
                    
                    db.add(proprietario)
                    db.flush()  # Para obter o ID
                    importados += 1
                    
                except Exception as e:
                    erros.append(f"Linha {linha}: Erro ao processar - {str(e)}")
                    # Não fazer rollback aqui, apenas registrar o erro
                    continue
            
            if importados > 0:
                try:
                    db.commit()
                except Exception as e:
                    db.rollback()
                    return {
                        'success': False,
                        'importados': 0,
                        'erros': [f"Erro ao salvar dados: {str(e)}"] + erros,
                        'warnings': warnings,
                        'total_linhas': len(df)
                    }
            
            return {
                'success': True,
                'importados': importados,
                'erros': erros,
                'warnings': warnings,
                'total_linhas': len(df)
            }
            
        except Exception as e:
            db.rollback()
            return {
                'success': False,
                'importados': 0,
                'erros': [f"Erro ao processar arquivo: {str(e)}"],
                'warnings': [],
                'total_linhas': 0
            }

    # ==================== IMPORTAÇÃO DE IMÓVEIS ====================

    def importar_imoveis(self, file_content: bytes, db: Session) -> Dict[str, Any]:
        """
        Importa imóveis do arquivo Imoveis.xlsx
        
        Colunas esperadas:
        - Nome, Endereço, Tipo, Área Total, Área Construida, Valor Catastral, 
          Valor Mercado, IPTU Anual, Condominio
        
        Nota: Precisa ter pelo menos 1 proprietário cadastrado (será atribuído ao primeiro)
        
        Retorna: {success, importados, erros, warnings, total_linhas}
        """
        try:
            df = pd.read_excel(BytesIO(file_content))
            
            # Verificar se existe proprietário
            primeiro_proprietario = db.query(Proprietario).first()
            if not primeiro_proprietario:
                return {
                    'success': False,
                    'importados': 0,
                    'erros': ['Nenhum proprietário cadastrado. Importe proprietários primeiro.'],
                    'warnings': [],
                    'total_linhas': 0
                }
            
            importados = 0
            erros = []
            warnings = []
            
            for idx, row in df.iterrows():
                linha = idx + 2
                
                try:
                    # Extrair dados
                    nome = str(row.get('Nome', '')).strip()
                    endereco = str(row.get('Endereço', '')) if not pd.isna(row.get('Endereço')) else None
                    tipo = str(row.get('Tipo', 'Residencial')).strip()
                    area_total = self.parse_valor(row.get('Área Total'))
                    area_construida = self.parse_valor(row.get('Área Construida'))
                    valor_catastral = self.parse_valor(row.get('Valor Catastral'))
                    valor_mercado = self.parse_valor(row.get('Valor Mercado'))
                    iptu_anual = self.parse_valor(row.get('IPTU Anual'))
                    condominio = self.parse_valor(row.get('Condominio'))
                    
                    # Validações
                    if not nome:
                        erros.append(f"Linha {linha}: Nome do imóvel é obrigatório")
                        continue
                    
                    # Verificar se imóvel já existe (por nome)
                    imovel_existe = db.query(Imovel).filter(Imovel.nome == nome).first()
                    if imovel_existe:
                        warnings.append(f"Linha {linha}: Imóvel '{nome}' já existe, pulando")
                        continue
                    
                    # Criar imóvel
                    imovel = Imovel(
                        nome=nome,
                        endereco=endereco,
                        tipo=tipo,
                        area_total=area_total,
                        area_construida=area_construida,
                        valor_catastral=valor_catastral,
                        valor_mercado=valor_mercado,
                        iptu_anual=iptu_anual,
                        valor_condominio=condominio,
                        proprietario_id=primeiro_proprietario.id,
                        is_active=True
                    )
                    
                    db.add(imovel)
                    db.flush()
                    importados += 1
                    
                except Exception as e:
                    erros.append(f"Linha {linha}: Erro ao processar - {str(e)}")
                    continue
            
            if importados > 0:
                db.commit()
            
            return {
                'success': True,
                'importados': importados,
                'erros': erros,
                'warnings': warnings,
                'total_linhas': len(df)
            }
            
        except Exception as e:
            db.rollback()
            return {
                'success': False,
                'importados': 0,
                'erros': [f"Erro ao processar arquivo: {str(e)}"],
                'warnings': [],
                'total_linhas': 0
            }

    # ==================== IMPORTAÇÃO DE PARTICIPAÇÕES ====================

    def importar_participacoes(self, file_content: bytes, db: Session, mes_referencia: str = None) -> Dict[str, Any]:
        """
        Importa participações do arquivo Participacoes.xlsx
        
        Formato esperado:
        - Primeira coluna: Nome do imóvel
        - Segunda coluna: Endereço
        - Terceira coluna: VALOR (sempre 1.0, representa 100%)
        - Demais colunas: Nome dos proprietários com seus percentuais decimais
        
        Retorna: {success, importados, erros, warnings, total_linhas}
        """
        try:
            df = pd.read_excel(BytesIO(file_content))
            
            # Se não fornecido, usar mês atual
            if not mes_referencia:
                mes_referencia = datetime.now().strftime('%Y-%m')
            
            importados = 0
            erros = []
            warnings = []
            
            # Identificar colunas de proprietários (após as 3 primeiras colunas)
            colunas_proprietarios = df.columns[3:]  # Pula: Nome, Endereço, VALOR
            
            for idx, row in df.iterrows():
                linha = idx + 2
                
                try:
                    # Identificar imóvel
                    nome_imovel = str(row.iloc[0]).strip()  # Primeira coluna
                    endereco = str(row.iloc[1]) if not pd.isna(row.iloc[1]) else ''
                    
                    # Buscar imóvel por nome ou endereço
                    imovel = db.query(Imovel).filter(
                        or_(
                            Imovel.nome == nome_imovel,
                            Imovel.endereco == endereco
                        )
                    ).first()
                    
                    if not imovel:
                        erros.append(f"Linha {linha}: Imóvel '{nome_imovel}' não encontrado")
                        continue
                    
                    # Processar cada proprietário
                    for col_nome in colunas_proprietarios:
                        percentual_decimal = self.parse_valor(row[col_nome])
                        
                        if percentual_decimal is None or percentual_decimal == 0:
                            continue  # Pular se não tem participação
                        
                        # Buscar proprietário por nome (match parcial)
                        proprietario = db.query(Proprietario).filter(
                            Proprietario.nome.ilike(f"%{col_nome}%")
                        ).first()
                        
                        if not proprietario:
                            warnings.append(f"Linha {linha}: Proprietário '{col_nome}' não encontrado, pulando participação")
                            continue
                        
                        # Converter decimal para percentual (0.125 -> 12.5%)
                        percentual = percentual_decimal * 100
                        
                        # Verificar se já existe participação
                        part_existe = db.query(Participacao).filter(
                            Participacao.imovel_id == imovel.id,
                            Participacao.proprietario_id == proprietario.id,
                            Participacao.mes_referencia == mes_referencia
                        ).first()
                        
                        if part_existe:
                            warnings.append(
                                f"Linha {linha}: Participação de {col_nome} no imóvel '{nome_imovel}' "
                                f"já existe para {mes_referencia}, pulando"
                            )
                            continue
                        
                        # Criar participação
                        participacao = Participacao(
                            imovel_id=imovel.id,
                            proprietario_id=proprietario.id,
                            mes_referencia=mes_referencia,
                            percentual=percentual,
                            valor_participacao=0.0  # Será calculado quando houver aluguel
                        )
                        
                        db.add(participacao)
                        importados += 1
                    
                except Exception as e:
                    erros.append(f"Linha {linha}: Erro ao processar - {str(e)}")
                    continue
            
            if importados > 0:
                db.commit()
            
            return {
                'success': True,
                'importados': importados,
                'erros': erros,
                'warnings': warnings,
                'total_linhas': len(df)
            }
            
        except Exception as e:
            db.rollback()
            return {
                'success': False,
                'importados': 0,
                'erros': [f"Erro ao processar arquivo: {str(e)}"],
                'warnings': [],
                'total_linhas': 0
            }

    # ==================== IMPORTAÇÃO DE ALUGUÉIS ====================

    def importar_alugueis(self, file_content: bytes, db: Session) -> Dict[str, Any]:
        """
        Importa aluguéis mensais de planilha Excel com estrutura matricial.
        
        Lê TODAS as abas/sheets do arquivo Excel, processando cada mês separadamente.
        
        Estrutura esperada por aba:
        - Primeira coluna (cabeçalho): Data de referência (ex: 2025-01-25)
        - Segunda coluna: "Valor Total"
        - Colunas seguintes: Nomes dos proprietários
        - Última coluna: "Taxa de Administração"
        - Linhas: Nomes dos imóveis na primeira coluna, valores nas demais
        """
        try:
            # Ler todas as abas do Excel
            excel_file = pd.ExcelFile(BytesIO(file_content))
            sheet_names = excel_file.sheet_names
            
            if not sheet_names:
                return {
                    'success': False,
                    'importados': 0,
                    'erros': ['Arquivo não contém nenhuma aba/sheet'],
                    'warnings': [],
                    'sheets_processadas': []
                }
            
            # Variáveis globais para acumular resultados de todas as abas
            erros_globais = []
            warnings_globais = []
            importados_total = 0
            sheets_processadas = []
            total_linhas_global = 0
            
            # Processar cada aba/sheet
            for sheet_name in sheet_names:
                try:
                    # Ler a aba específica (usando o objeto excel_file já carregado)
                    df = excel_file.parse(sheet_name)
                    
                    if df.empty or len(df) < 1:
                        warnings_globais.append(f"Sheet '{sheet_name}': vazia ou sem dados suficientes")
                        continue
                    
                    erros = []
                    warnings = []
                    importados = 0
                    
                    # Extrair data de referência do nome da primeira coluna
                    primeira_coluna = df.columns[0]
                    try:
                        # A primeira coluna é um datetime
                        if isinstance(primeira_coluna, datetime):
                            data_referencia = primeira_coluna.date()
                        else:
                            # Tentar converter string para data
                            data_str = str(primeira_coluna).strip()
                            if '/' in data_str:
                                data_referencia = datetime.strptime(data_str, '%d/%m/%Y').date()
                            else:
                                data_referencia = datetime.strptime(data_str.split(' ')[0], '%Y-%m-%d').date()
                    except Exception as e:
                        erros_globais.append(f"Sheet '{sheet_name}': Não foi possível extrair data de referência do cabeçalho: {str(e)}")
                        continue
                    
                    # Mapear proprietários das colunas (ignorar primeira "Valor Total" e última "Taxa de Administração")
                    proprietarios_cols = []
                    for col_idx in range(2, len(df.columns) - 1):  # Pular "data", "Valor Total" e "Taxa Administração"
                        nome_col = str(df.columns[col_idx]).strip()
                        
                        if nome_col.lower() in ['nan', 'none', 'unnamed', 'taxa', 'administração']:
                            continue
                        
                        # Buscar proprietário no banco (busca parcial case-insensitive)
                        proprietario = db.query(Proprietario).filter(
                            Proprietario.nome.ilike(f'%{nome_col}%')
                        ).first()
                        
                        if proprietario:
                            proprietarios_cols.append((col_idx, nome_col, proprietario))
                        else:
                            warnings.append(f"Proprietário '{nome_col}' não encontrado no banco")
                    
                    if not proprietarios_cols:
                        warnings_globais.append(f"Sheet '{sheet_name}': Nenhum proprietário válido encontrado nos cabeçalhos")
                        continue
                    
                    # Processar cada linha (cada linha é um imóvel)
                    for idx, row in df.iterrows():
                        imovel_nome = "desconhecido"  # Inicializar para evitar NameError em exception handler
                        try:
                            # Primeira célula da linha é o nome do imóvel
                            imovel_nome = str(row.iloc[0]).strip()
                            if not imovel_nome or imovel_nome.lower() in ['nan', 'none', '']:
                                continue
                            
                            # Buscar imóvel no banco
                            imovel = db.query(Imovel).filter(
                                Imovel.nome.ilike(f'%{imovel_nome}%')
                            ).first()
                            
                            if not imovel:
                                # Tentar por endereço
                                imovel = db.query(Imovel).filter(
                                    Imovel.endereco.ilike(f'%{imovel_nome}%')
                                ).first()
                            
                            if not imovel:
                                warnings.append(f"Linha {idx+2}: Imóvel '{imovel_nome}' não encontrado")
                                continue
                            
                            # Valor total (segunda coluna)
                            valor_total_str = str(row.iloc[1]).strip()
                            valor_total = self.parse_valor(valor_total_str) or 0.0
                            
                            # Taxa de administração (última coluna)
                            taxa_admin_str = str(row.iloc[-1]).strip()
                            taxa_admin = self.parse_valor(taxa_admin_str) or 0.0
                            
                            # Processar valores para cada proprietário
                            for col_idx, nome_prop, proprietario in proprietarios_cols:
                                valor_str = str(row.iloc[col_idx]).strip()
                                if not valor_str or valor_str.lower() in ['nan', 'none', '', '-']:
                                    continue
                                
                                # Converter valor
                                valor_proprietario = self.parse_valor(valor_str)
                                if valor_proprietario is None or valor_proprietario == 0:
                                    continue
                                
                                # Verificar se já existe aluguel para este mês/proprietário/imóvel
                                existing = db.query(AluguelMensal).filter(
                                    AluguelMensal.imovel_id == imovel.id,
                                    AluguelMensal.proprietario_id == proprietario.id,
                                    AluguelMensal.data_referencia == data_referencia
                                ).first()
                                
                                if existing:
                                    # Atualizar valores
                                    existing.valor_total = valor_total
                                    existing.valor_proprietario = valor_proprietario
                                    existing.taxa_administracao = taxa_admin
                                    existing.atualizado_em = func.now()
                                else:
                                    # Criar novo registro
                                    # Gerar mes_referencia no formato YYYY-MM para compatibilidade
                                    mes_ref = data_referencia.strftime('%Y-%m')
                                    novo_aluguel = AluguelMensal(
                                        imovel_id=imovel.id,
                                        proprietario_id=proprietario.id,
                                        data_referencia=data_referencia,
                                        mes_referencia=mes_ref,
                                        valor_total=valor_total,
                                        valor_proprietario=valor_proprietario,
                                        taxa_administracao=taxa_admin
                                    )
                                    db.add(novo_aluguel)
                                
                                importados += 1
                        
                        except Exception as e:
                            erros.append(f"Linha {idx+2} (imóvel '{imovel_nome}'): {str(e)}")
                    
                    # Acumular resultados desta aba
                    importados_total += importados
                    total_linhas_global += len(df)
                    
                    # Adicionar erros e warnings desta aba aos globais (com prefixo do sheet)
                    for erro in erros:
                        erros_globais.append(f"Sheet '{sheet_name}': {erro}")
                    for warning in warnings:
                        warnings_globais.append(f"Sheet '{sheet_name}': {warning}")
                    
                    # Registrar informações da aba processada
                    sheets_processadas.append({
                        'nome': sheet_name,
                        'importados': importados,
                        'linhas': len(df),
                        'data_referencia': str(data_referencia)
                    })
                    
                except Exception as e:
                    erros_globais.append(f"Sheet '{sheet_name}': Erro ao processar - {str(e)}")
                    continue
            
            # Commit apenas uma vez, ao final de todas as abas
            if importados_total > 0:
                db.commit()
            
            return {
                'success': True,
                'importados': importados_total,
                'erros': erros_globais,
                'warnings': warnings_globais,
                'total_linhas': total_linhas_global,
                'sheets_processadas': sheets_processadas,
                'total_sheets': len(sheet_names)
            }
        
        except Exception as e:
            db.rollback()
            return {
                'success': False,
                'importados': 0,
                'erros': [f"Erro ao processar arquivo: {str(e)}"],
                'warnings': [],
                'total_linhas': 0,
                'sheets_processadas': []
            }

    # ==================== PREVIEW ====================

    def preview_arquivo(self, file_content: bytes) -> Dict[str, Any]:
        """
        Gera preview dos dados do arquivo
        Retorna: {success, colunas, preview, total_linhas_preview}
        """
        try:
            df = pd.read_excel(BytesIO(file_content))
            
            # Limitar preview a 10 linhas
            preview_df = df.head(10)
            
            # Converter para lista de dicionários
            preview_data = preview_df.fillna('').to_dict('records')
            
            return {
                'success': True,
                'colunas': list(df.columns),
                'preview': preview_data,
                'total_linhas_preview': len(preview_df),
                'total_linhas': len(df)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'colunas': [],
                'preview': [],
                'total_linhas_preview': 0
            }
