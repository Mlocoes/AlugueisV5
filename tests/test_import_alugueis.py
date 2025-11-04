"""
Test for import service - verify all sheets are imported from Alugueis.xlsx
"""
import pytest
from pathlib import Path
from app.services.import_service import ImportacaoService
from app.models.proprietario import Proprietario
from app.models.imovel import Imovel
from app.models.aluguel import AluguelMensal


def test_importar_alugueis_all_sheets(db_session):
    """
    Test that importar_alugueis reads all sheets from Excel file,
    not just the first one
    """
    # Setup: Create test proprietarios and imoveis first
    # (These need to exist for the import to work)
    
    # Create test proprietarios matching the Excel file
    proprietarios_nomes = ['Jandira', 'Manoel', 'Fabio', 'Carla', 'Armando', 
                          'Suely', 'Felipe', 'Adriana', 'Regina', 'Mario Angelo']
    
    for nome in proprietarios_nomes:
        prop = Proprietario(
            tipo_pessoa='fisica',
            nome=nome,
            email=f"{nome.lower()}@test.com",
            is_active=True
        )
        db_session.add(prop)
    
    # Create test imoveis matching the Excel file
    imoveis_nomes = ['Cunha Gago 223', 'Teodoro Sampaio 1779', 'Dep. Lacerda']
    
    # Get first proprietario as owner
    db_session.commit()
    primeiro_proprietario = db_session.query(Proprietario).first()
    
    for nome in imoveis_nomes:
        imovel = Imovel(
            nome=nome,
            endereco=nome,
            tipo='Residencial',
            proprietario_id=primeiro_proprietario.id,
            is_active=True
        )
        db_session.add(imovel)
    
    db_session.commit()
    
    # Load the actual Excel file
    excel_path = Path('/home/runner/work/AlugueisV5/AlugueisV5/excel/Alugueis.xlsx')
    
    if not excel_path.exists():
        pytest.skip(f"Excel file not found: {excel_path}")
    
    with open(excel_path, 'rb') as f:
        file_content = f.read()
    
    # Execute import
    service = ImportacaoService()
    resultado = service.importar_alugueis(file_content, db_session)
    
    # Assertions
    assert resultado['success'] is True, f"Import failed: {resultado.get('erros', [])}"
    
    # Verify multiple sheets were processed
    assert 'sheets_processadas' in resultado, "Result should include sheets_processadas"
    assert 'total_sheets' in resultado, "Result should include total_sheets"
    
    sheets_processadas = resultado['sheets_processadas']
    total_sheets = resultado['total_sheets']
    
    print(f"\n✅ Total sheets in file: {total_sheets}")
    print(f"✅ Sheets successfully processed: {len(sheets_processadas)}")
    
    # The file should have 10 sheets (Jan2025 through Out25)
    assert total_sheets == 10, f"Expected 10 sheets, but found {total_sheets}"
    
    # At least some sheets should have been processed successfully
    # (some might fail due to missing proprietarios/imoveis in test DB)
    assert len(sheets_processadas) > 1, "Should process more than 1 sheet"
    
    # Verify that records were imported
    assert resultado['importados'] > 0, "Should have imported some records"
    
    # Verify data in database
    count_alugueis = db_session.query(AluguelMensal).count()
    assert count_alugueis > 0, "Should have created AluguelMensal records"
    
    # Verify multiple months were imported
    distinct_months = db_session.query(AluguelMensal.mes_referencia).distinct().all()
    distinct_months_list = [m[0] for m in distinct_months]
    
    print(f"✅ Distinct months imported: {distinct_months_list}")
    print(f"✅ Total records imported: {resultado['importados']}")
    print(f"✅ Total alugueis in DB: {count_alugueis}")
    
    # Should have more than 1 distinct month
    assert len(distinct_months_list) > 1, \
        f"Should have multiple months, but only found: {distinct_months_list}"
    
    # Print details of each sheet processed
    print("\n📊 Details of processed sheets:")
    for sheet_info in sheets_processadas:
        print(f"  - {sheet_info['nome']:15s}: {sheet_info['importados']:3d} records "
              f"(from {sheet_info['linhas']} rows, date: {sheet_info['data_referencia']})")
    
    # Show warnings if any
    if resultado.get('warnings'):
        print(f"\n⚠️  Warnings ({len(resultado['warnings'])}):")
        for warning in resultado['warnings'][:5]:  # Show first 5
            print(f"  - {warning}")
    
    print(f"\n✅ TEST PASSED: All sheets are being processed!")


def test_importar_alugueis_empty_file(db_session):
    """Test that empty file is handled gracefully"""
    service = ImportacaoService()
    
    # Create a minimal empty Excel file
    import pandas as pd
    from io import BytesIO
    
    # Create empty workbook
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        pd.DataFrame().to_excel(writer, index=False, sheet_name='Empty')
    
    content = output.getvalue()
    
    resultado = service.importar_alugueis(content, db_session)
    
    # Should handle gracefully
    assert resultado['success'] is True  # Technically successful, just no data
    assert resultado['importados'] == 0
    assert 'sheets_processadas' in resultado


if __name__ == '__main__':
    # Run with: python -m pytest tests/test_import_alugueis.py -v -s
    pytest.main([__file__, '-v', '-s'])
