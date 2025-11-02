"""
Rotas para importação de dados via Excel/CSV
"""
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
import io
from pathlib import Path

from app.core.database import get_db
from app.core.auth import get_current_user_from_cookie
from app.models.usuario import Usuario
from app.services.import_service import ImportacaoService

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# ==================== PÁGINA WEB ====================

@router.get("/importacao", response_class=HTMLResponse)
async def importacao_page(
    request: Request,
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """Renderiza a página de importação"""
    return templates.TemplateResponse(
        "importacao.html",
        {"request": request, "user": current_user}
    )


# ==================== API - PREVIEW ====================

@router.post("/api/importacao/preview")
async def preview_importacao(
    file: UploadFile = File(...),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """Gera preview do arquivo antes da importação"""
    try:
        # Validar extensão do arquivo
        if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(
                status_code=400,
                detail="Formato de arquivo inválido. Use .xlsx, .xls ou .csv"
            )

        # Ler conteúdo do arquivo
        content = await file.read()
        
        # Gerar preview
        service = ImportacaoService()
        resultado = service.preview_arquivo(content)
        
        if not resultado['success']:
            error_msg = resultado.get('error', 'Erro desconhecido')
            raise HTTPException(status_code=400, detail=error_msg)
        
        return resultado

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")


# ==================== API - IMPORTAÇÃO ====================

@router.post("/api/importacao/proprietarios")
async def importar_proprietarios(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """Importa proprietários de um arquivo Excel/CSV"""
    try:
        if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(
                status_code=400,
                detail="Formato de arquivo inválido. Use .xlsx, .xls ou .csv"
            )

        content = await file.read()
        
        service = ImportacaoService()
        resultado = service.importar_proprietarios(content, db)
        
        if not resultado['success']:
            erros_msg = '\n'.join(resultado.get('erros', ['Erro desconhecido']))
            raise HTTPException(status_code=400, detail=erros_msg)
        
        return resultado

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao importar: {str(e)}")


@router.post("/api/importacao/imoveis")
async def importar_imoveis(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """Importa imóveis de um arquivo Excel/CSV"""
    try:
        if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(
                status_code=400,
                detail="Formato de arquivo inválido. Use .xlsx, .xls ou .csv"
            )

        content = await file.read()
        
        service = ImportacaoService()
        resultado = service.importar_imoveis(content, db)
        
        if not resultado['success']:
            erros_msg = ' | '.join(resultado.get('erros', ['Erro desconhecido']))
            raise HTTPException(status_code=400, detail=erros_msg)
        
        return resultado

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao importar: {str(e)}")


@router.post("/api/importacao/alugueis")
async def importar_alugueis(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """Importa aluguéis de um arquivo Excel/CSV"""
    try:
        if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(
                status_code=400,
                detail="Formato de arquivo inválido. Use .xlsx, .xls ou .csv"
            )

        content = await file.read()
        
        service = ImportacaoService()
        resultado = service.importar_alugueis(content, db)
        
        if not resultado['success']:
            erros_msg = ' | '.join(resultado.get('erros', ['Erro desconhecido']))
            raise HTTPException(status_code=400, detail=erros_msg)
        
        return resultado

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao importar: {str(e)}")


@router.post("/api/importacao/participacoes")
async def importar_participacoes(
    file: UploadFile = File(...),
    mes_referencia: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """Importa participações de um arquivo Excel/CSV"""
    try:
        if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(
                status_code=400,
                detail="Formato de arquivo inválido. Use .xlsx, .xls ou .csv"
            )

        content = await file.read()
        
        service = ImportacaoService()
        resultado = service.importar_participacoes(content, db, mes_referencia)
        
        if not resultado['success']:
            erros_msg = ' | '.join(resultado.get('erros', ['Erro desconhecido']))
            raise HTTPException(status_code=400, detail=erros_msg)
        
        return resultado

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao importar: {str(e)}")


# ==================== DOWNLOAD DE TEMPLATES ====================

@router.get("/api/importacao/template/{tipo}")
async def download_template(
    tipo: str,
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """Baixa template Excel para importação"""
    
    try:
        import pandas as pd
        import io
        
        # Definir estrutura dos templates
        templates_estrutura = {
            'proprietarios': {
                'colunas': ['nome', 'email', 'tipo', 'ativo'],
                'exemplo': [
                    ['João Silva', 'joao@email.com', 'proprietario', 'sim'],
                    ['Maria Santos', 'maria@email.com', 'proprietario', 'sim'],
                ]
            },
            'imoveis': {
                'colunas': ['codigo', 'endereco', 'tipo', 'ativo'],
                'exemplo': [
                    ['APT101', 'Rua das Flores, 123 - Apto 101', 'apartamento', 'sim'],
                    ['CASA202', 'Av. Principal, 456', 'casa', 'sim'],
                ]
            },
            'alugueis': {
                'colunas': [
                    'codigo_imovel', 'mes_referencia', 'valor_aluguel',
                    'valor_condominio', 'valor_iptu', 'valor_luz',
                    'valor_agua', 'valor_gas', 'outras_despesas',
                    'data_pagamento', 'pago', 'observacoes'
                ],
                'exemplo': [
                    ['APT101', '2025-11', 1500.00, 350.00, 120.00, 80.00, 50.00, 30.00, 0, '05/11/2025', 'sim', ''],
                    ['CASA202', '2025-11', 2000.00, 0, 200.00, 120.00, 70.00, 40.00, 0, '', 'nao', 'Aguardando pagamento'],
                ]
            }
        }
        
        if tipo not in templates_estrutura:
            raise HTTPException(status_code=404, detail="Template não encontrado")
        
        # Criar DataFrame
        estrutura = templates_estrutura[tipo]
        df = pd.DataFrame(estrutura['exemplo'], columns=estrutura['colunas'])
        
        # Gerar arquivo Excel em memória
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Dados')
            
            # Formatar planilha
            workbook = writer.book
            worksheet = writer.sheets['Dados']
            
            # Ajustar largura das colunas
            for idx, col in enumerate(df.columns, 1):
                worksheet.column_dimensions[chr(64 + idx)].width = 20
        
        output.seek(0)
        
        # Retornar arquivo
        return StreamingResponse(
            io.BytesIO(output.read()),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={
                'Content-Disposition': f'attachment; filename=template_{tipo}.xlsx'
            }
        )
        
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="Biblioteca pandas ou openpyxl não instalada"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar template: {str(e)}")


# ==================== VERIFICAÇÃO DE DEPENDÊNCIAS ====================

@router.get("/api/importacao/check-dependencies")
async def check_dependencies(
    current_user: Usuario = Depends(get_current_user_from_cookie)
):
    """Verifica se as dependências necessárias estão instaladas"""
    try:
        import pandas
        import openpyxl
        return {
            'success': True,
            'pandas_version': pandas.__version__,
            'openpyxl_version': openpyxl.__version__
        }
    except ImportError as e:
        return {
            'success': False,
            'message': 'Dependências não instaladas. Execute: pip install pandas openpyxl',
            'error': str(e)
        }
