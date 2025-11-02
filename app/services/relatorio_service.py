from sqlalchemy.orm import Session
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any
import calendar

from app.models.aluguel import AluguelMensal
from app.models.imovel import Imovel
from app.models.proprietario import Proprietario
from app.models.participacao import Participacao


class RelatorioService:
    """Serviço para geração de relatórios financeiros"""
    
    @staticmethod
    def calcular_totais_aluguel(aluguel: AluguelMensal) -> Dict[str, Decimal]:
        """Calcula os totais de um aluguel"""
        valor_aluguel = Decimal(str(aluguel.valor_aluguel or 0))
        valor_condominio = Decimal(str(aluguel.valor_condominio or 0))
        valor_iptu = Decimal(str(aluguel.valor_iptu or 0))
        valor_luz = Decimal(str(aluguel.valor_luz or 0))
        valor_agua = Decimal(str(aluguel.valor_agua or 0))
        valor_gas = Decimal(str(aluguel.valor_gas or 0))
        valor_internet = Decimal(str(aluguel.valor_internet or 0))
        outros_valores = Decimal(str(aluguel.outros_valores or 0))
        
        total = valor_aluguel + valor_condominio + valor_iptu + valor_luz + valor_agua + valor_gas + valor_internet + outros_valores
        
        return {
            "valor_aluguel": valor_aluguel,
            "valor_condominio": valor_condominio,
            "valor_iptu": valor_iptu,
            "valor_luz": valor_luz,
            "valor_agua": valor_agua,
            "valor_gas": valor_gas,
            "valor_internet": valor_internet,
            "outros_valores": outros_valores,
            "valor_total": total
        }
    
    @staticmethod
    def gerar_relatorio_mensal(db: Session, ano: int, mes: int, proprietario_id: Optional[int] = None) -> Dict[str, Any]:
        """Gera relatório mensal consolidado"""
        mes_ref = f"{ano}-{mes:02d}"
        
        query = db.query(AluguelMensal).filter(AluguelMensal.mes_referencia == mes_ref)
        alugueis = query.all()
        
        total_esperado = Decimal('0')
        total_recebido = Decimal('0')
        total_pendente = Decimal('0')
        alugueis_pagos = 0
        alugueis_pendentes = 0
        detalhamento_imoveis = []
        
        for aluguel in alugueis:
            totais = RelatorioService.calcular_totais_aluguel(aluguel)
            valor_total = totais["valor_total"]
            
            total_esperado += valor_total
            
            if aluguel.pago:
                total_recebido += valor_total
                alugueis_pagos += 1
            else:
                total_pendente += valor_total
                alugueis_pendentes += 1
            
            detalhamento_imoveis.append({
                "aluguel_id": aluguel.id,
                "imovel_id": aluguel.imovel_id,
                "imovel_endereco": aluguel.imovel.endereco,
                "mes_referencia": aluguel.mes_referencia,
                "status_pagamento": "pago" if aluguel.pago else "pendente",
                "data_pagamento": aluguel.data_pagamento.isoformat() if aluguel.data_pagamento else None,
                "valores": {
                    "aluguel": float(totais["valor_aluguel"]),
                    "condominio": float(totais["valor_condominio"]),
                    "iptu": float(totais["valor_iptu"]),
                    "luz": float(totais["valor_luz"]),
                    "agua": float(totais["valor_agua"]),
                    "gas": float(totais["valor_gas"]),
                    "internet": float(totais["valor_internet"]),
                    "outros": float(totais["outros_valores"]),
                    "total": float(valor_total)
                },
                "participacoes": []
            })
        
        nome_mes = calendar.month_name[mes]
        
        return {
            "periodo": {"ano": ano, "mes": mes, "mes_nome": nome_mes, "mes_referencia": mes_ref},
            "resumo": {
                "total_alugueis": len(alugueis),
                "alugueis_pagos": alugueis_pagos,
                "alugueis_pendentes": alugueis_pendentes,
                "total_esperado": float(total_esperado),
                "total_recebido": float(total_recebido),
                "total_pendente": float(total_pendente),
                "taxa_recebimento": float((total_recebido / total_esperado * 100) if total_esperado > 0 else 0)
            },
            "detalhamento": detalhamento_imoveis
        }
    
    @staticmethod
    def gerar_relatorio_proprietario(db: Session, proprietario_id: int, ano: int, mes: Optional[int] = None) -> Dict[str, Any]:
        """Gera relatório de proprietário"""
        proprietario = db.query(Proprietario).filter(Proprietario.id == proprietario_id).first()
        
        if not proprietario:
            return {"erro": "Proprietário não encontrado"}
        
        return {
            "proprietario": {
                "id": proprietario.id,
                "nome": proprietario.nome,
                "cpf_cnpj": proprietario.cpf_cnpj,
                "tipo_pessoa": proprietario.tipo_pessoa
            },
            "periodo": {"ano": ano, "mes": mes},
            "resumo": {
                "total_imoveis": 0,
                "total_esperado": 0.0,
                "total_recebido": 0.0,
                "total_pendente": 0.0,
                "taxa_recebimento": 0.0
            },
            "receitas_por_mes": []
        }
    
    @staticmethod
    def gerar_relatorio_anual(db: Session, ano: int) -> Dict[str, Any]:
        """Gera relatório anual consolidado"""
        receitas_mensais = []
        total_anual_esperado = Decimal('0')
        total_anual_recebido = Decimal('0')
        total_anual_pendente = Decimal('0')
        
        for mes in range(1, 13):
            relatorio_mes = RelatorioService.gerar_relatorio_mensal(db, ano, mes)
            resumo = relatorio_mes["resumo"]
            
            total_anual_esperado += Decimal(str(resumo["total_esperado"]))
            total_anual_recebido += Decimal(str(resumo["total_recebido"]))
            total_anual_pendente += Decimal(str(resumo["total_pendente"]))
            
            receitas_mensais.append({
                "mes": mes,
                "mes_nome": relatorio_mes["periodo"]["mes_nome"],
                "total_alugueis": resumo["total_alugueis"],
                "alugueis_pagos": resumo["alugueis_pagos"],
                "alugueis_pendentes": resumo["alugueis_pendentes"],
                "total_esperado": resumo["total_esperado"],
                "total_recebido": resumo["total_recebido"],
                "total_pendente": resumo["total_pendente"]
            })
        
        return {
            "ano": ano,
            "resumo": {
                "total_esperado": float(total_anual_esperado),
                "total_recebido": float(total_anual_recebido),
                "total_pendente": float(total_anual_pendente),
                "taxa_recebimento": float((total_anual_recebido / total_anual_esperado * 100) if total_anual_esperado > 0 else 0)
            },
            "receitas_mensais": receitas_mensais
        }
    
    @staticmethod
    def gerar_relatorio_comparativo(db: Session, ano1: int, ano2: int) -> Dict[str, Any]:
        """Gera relatório comparativo entre dois anos"""
        relatorio_ano1 = RelatorioService.gerar_relatorio_anual(db, ano1)
        relatorio_ano2 = RelatorioService.gerar_relatorio_anual(db, ano2)
        
        total_ano1 = Decimal(str(relatorio_ano1["resumo"]["total_recebido"]))
        total_ano2 = Decimal(str(relatorio_ano2["resumo"]["total_recebido"]))
        
        variacao_absoluta = total_ano2 - total_ano1
        variacao_percentual = ((total_ano2 / total_ano1 - 1) * 100) if total_ano1 > 0 else Decimal('0')
        
        comparacao_mensal = []
        for mes in range(1, 13):
            dados_ano1 = relatorio_ano1["receitas_mensais"][mes - 1]
            dados_ano2 = relatorio_ano2["receitas_mensais"][mes - 1]
            
            receita_mes1 = Decimal(str(dados_ano1["total_recebido"]))
            receita_mes2 = Decimal(str(dados_ano2["total_recebido"]))
            
            var_mensal = receita_mes2 - receita_mes1
            var_perc_mensal = ((receita_mes2 / receita_mes1 - 1) * 100) if receita_mes1 > 0 else Decimal('0')
            
            comparacao_mensal.append({
                "mes": mes,
                "mes_nome": dados_ano1["mes_nome"],
                f"receita_{ano1}": float(receita_mes1),
                f"receita_{ano2}": float(receita_mes2),
                "variacao_absoluta": float(var_mensal),
                "variacao_percentual": float(var_perc_mensal)
            })
        
        return {
            "anos_comparados": [ano1, ano2],
            "resumo": {
                f"total_{ano1}": float(total_ano1),
                f"total_{ano2}": float(total_ano2),
                "variacao_absoluta": float(variacao_absoluta),
                "variacao_percentual": float(variacao_percentual)
            },
            "comparacao_mensal": comparacao_mensal
        }
