#!/usr/bin/env python3
"""
Script de migração para corrigir valores monetários incorretos no banco de dados.

Este script identifica e corrige valores que podem ter sido incorretamente
importados devido ao bug de formatação de números brasileiros no parse_valor.

IMPORTANTE: Faça backup do banco de dados antes de executar este script!

Uso:
    python fix_incorrect_values.py --dry-run  # Apenas mostra o que seria corrigido
    python fix_incorrect_values.py            # Aplica as correções

Cenários detectados e corrigidos:
1. Valores muito pequenos (< 10) que deveriam ser maiores (multiplicados por 1000)
   Exemplo: valor_total = 2.8 deveria ser 2800.0
   
2. Detecção baseada em padrões típicos de aluguéis brasileiros
   - Valores típicos de aluguel: R$ 500 - R$ 50.000
   - Se valor_aluguel < 10 e outros encargos também < 10, provável erro de importação
"""

import sys
import os
from decimal import Decimal

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import SessionLocal
from app.models.aluguel import AluguelMensal
from datetime import datetime


def detectar_valores_suspeitos(db: Session, dry_run: bool = True):
    """
    Detecta aluguéis com valores suspeitos que podem estar incorretos
    """
    print("=" * 80)
    print("ANÁLISE DE VALORES SUSPEITOS")
    print("=" * 80)
    
    # Buscar aluguéis com valores muito baixos (suspeito de divisão por 1000)
    # Assumimos que aluguéis legítimos são raramente menores que R$ 100
    alugueis_suspeitos = db.query(AluguelMensal).filter(
        AluguelMensal.valor_total < 100.0,
        AluguelMensal.valor_total > 0.0
    ).all()
    
    print(f"\nEncontrados {len(alugueis_suspeitos)} aluguéis com valor_total < R$ 100")
    
    correcoes = []
    
    for aluguel in alugueis_suspeitos:
        # Calcular o que seria o valor se multiplicado por 1000
        valor_corrigido = aluguel.valor_total * 1000
        
        # Verificar se o valor corrigido está em um range mais razoável
        if 100 <= valor_corrigido <= 50000:  # Range típico de aluguéis
            correcoes.append({
                'id': aluguel.id,
                'imovel_id': aluguel.imovel_id,
                'mes_referencia': aluguel.mes_referencia,
                'valor_atual': float(aluguel.valor_total),
                'valor_corrigido': float(valor_corrigido),
                'valor_aluguel_atual': float(aluguel.valor_aluguel),
                'valor_aluguel_corrigido': float(aluguel.valor_aluguel * 1000)
            })
    
    print(f"\nIdentificadas {len(correcoes)} correções potenciais:")
    print("-" * 80)
    
    for i, corr in enumerate(correcoes, 1):
        print(f"\n{i}. Aluguel ID {corr['id']} - {corr['mes_referencia']}")
        print(f"   Imóvel ID: {corr['imovel_id']}")
        print(f"   Valor Total: R$ {corr['valor_atual']:.2f} → R$ {corr['valor_corrigido']:.2f}")
        print(f"   Valor Aluguel: R$ {corr['valor_aluguel_atual']:.2f} → R$ {corr['valor_aluguel_corrigido']:.2f}")
    
    return correcoes


def aplicar_correcoes(db: Session, correcoes: list, dry_run: bool = True):
    """
    Aplica as correções identificadas
    """
    if not correcoes:
        print("\nNenhuma correção a ser aplicada.")
        return
    
    print("\n" + "=" * 80)
    if dry_run:
        print("MODO DRY-RUN: As seguintes correções SERIAM aplicadas:")
    else:
        print("APLICANDO CORREÇÕES:")
    print("=" * 80)
    
    total_corrigido = 0
    
    for corr in correcoes:
        aluguel = db.query(AluguelMensal).filter(AluguelMensal.id == corr['id']).first()
        
        if not aluguel:
            print(f"❌ Aluguel ID {corr['id']} não encontrado")
            continue
        
        if not dry_run:
            # Multiplicar todos os valores monetários por 1000
            aluguel.valor_aluguel *= 1000
            aluguel.valor_condominio *= 1000
            aluguel.valor_iptu *= 1000
            aluguel.valor_luz *= 1000
            aluguel.valor_agua *= 1000
            aluguel.valor_gas *= 1000
            aluguel.valor_internet *= 1000
            aluguel.outros_valores *= 1000
            aluguel.valor_total *= 1000
            
            total_corrigido += 1
            print(f"✅ Aluguel ID {corr['id']} corrigido: R$ {corr['valor_atual']:.2f} → R$ {corr['valor_corrigido']:.2f}")
        else:
            print(f"   Aluguel ID {corr['id']}: R$ {corr['valor_atual']:.2f} → R$ {corr['valor_corrigido']:.2f}")
    
    if not dry_run:
        db.commit()
        print(f"\n✅ {total_corrigido} aluguéis corrigidos com sucesso!")
    else:
        print(f"\n   {len(correcoes)} correções seriam aplicadas")
        print("\n   Execute sem --dry-run para aplicar as correções")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Corrige valores monetários incorretos no banco de dados')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Apenas mostra o que seria corrigido sem fazer alterações')
    parser.add_argument('--force', action='store_true',
                       help='Aplica correções sem confirmação')
    
    args = parser.parse_args()
    
    db: Session = SessionLocal()
    
    try:
        # Detectar valores suspeitos
        correcoes = detectar_valores_suspeitos(db, args.dry_run)
        
        if not correcoes:
            print("\n✅ Nenhum valor suspeito encontrado!")
            return
        
        if not args.dry_run:
            if not args.force:
                print("\n" + "=" * 80)
                resposta = input(f"\n⚠️  Deseja aplicar {len(correcoes)} correções? (sim/não): ")
                if resposta.lower() not in ['sim', 's', 'yes', 'y']:
                    print("❌ Operação cancelada pelo usuário")
                    return
            
            print("\n⚠️  ATENÇÃO: Aplicando correções...")
            
        # Aplicar correções
        aplicar_correcoes(db, correcoes, args.dry_run)
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Erro: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
