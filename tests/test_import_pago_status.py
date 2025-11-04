"""
Test to verify that imported rentals (alugueis) have pago=True status
"""
import pytest
from pathlib import Path
from app.services.import_service import ImportacaoService
from app.models.proprietario import Proprietario
from app.models.imovel import Imovel
from app.models.aluguel import AluguelMensal

# Get the project root directory and construct the path to the Excel file
PROJECT_ROOT = Path(__file__).parent.parent
EXCEL_FILE_PATH = PROJECT_ROOT / 'excel' / 'Alugueis.xlsx'


def test_imported_alugueis_are_marked_as_paid(db_session):
    """
    Test that alugueis imported from Excel are marked as paid (pago=True)
    
    This is the core requirement: imported rentals should be saved with
    paid status, not pending status.
    """
    # Setup: Create test proprietarios and imoveis first
    proprietarios_nomes = ['Jandira', 'Manoel', 'Fabio']
    
    for nome in proprietarios_nomes:
        prop = Proprietario(
            tipo_pessoa='fisica',
            nome=nome,
            email=f"{nome.lower()}@test.com",
            is_active=True
        )
        db_session.add(prop)
    
    # Create test imoveis
    imoveis_nomes = ['Cunha Gago 223', 'Teodoro Sampaio 1779']
    
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
    if not EXCEL_FILE_PATH.exists():
        pytest.skip(f"Excel file not found: {EXCEL_FILE_PATH}")
    
    with open(EXCEL_FILE_PATH, 'rb') as f:
        file_content = f.read()
    
    # Execute import
    service = ImportacaoService()
    resultado = service.importar_alugueis(file_content, db_session)
    
    # Verify import was successful
    assert resultado['success'] is True, f"Import failed: {resultado.get('erros', [])}"
    assert resultado['importados'] > 0, "Should have imported some records"
    
    # MAIN ASSERTION: All imported alugueis should have pago=True
    all_alugueis = db_session.query(AluguelMensal).all()
    
    assert len(all_alugueis) > 0, "Should have created some AluguelMensal records"
    
    # Check that ALL imported rentals are marked as paid
    for aluguel in all_alugueis:
        assert aluguel.pago is True, (
            f"AluguelMensal (id={aluguel.id}, imovel_id={aluguel.imovel_id}, "
            f"mes={aluguel.mes_referencia}) should be marked as paid (pago=True), "
            f"but pago={aluguel.pago}"
        )
    
    print(f"\n✅ SUCCESS: All {len(all_alugueis)} imported rentals are marked as paid!")
    print(f"   - Verified {len(all_alugueis)} AluguelMensal records")
    print(f"   - All have pago=True status")


def test_reimporting_alugueis_keeps_paid_status(db_session):
    """
    Test that re-importing alugueis (updating existing records) also sets pago=True
    """
    # Setup
    proprietarios_nomes = ['Jandira', 'Manoel']
    
    for nome in proprietarios_nomes:
        prop = Proprietario(
            tipo_pessoa='fisica',
            nome=nome,
            email=f"{nome.lower()}@test.com",
            is_active=True
        )
        db_session.add(prop)
    
    imoveis_nomes = ['Cunha Gago 223']
    
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
    
    # Load Excel file
    if not EXCEL_FILE_PATH.exists():
        pytest.skip(f"Excel file not found: {EXCEL_FILE_PATH}")
    
    with open(EXCEL_FILE_PATH, 'rb') as f:
        file_content = f.read()
    
    service = ImportacaoService()
    
    # Import first time
    resultado1 = service.importar_alugueis(file_content, db_session)
    assert resultado1['success'] is True
    count_first_import = resultado1['importados']
    
    # All should be marked as paid
    all_alugueis = db_session.query(AluguelMensal).all()
    for aluguel in all_alugueis:
        assert aluguel.pago is True
    
    # Now manually set some to unpaid to simulate user changing status
    if len(all_alugueis) > 0:
        all_alugueis[0].pago = False
        db_session.commit()
    
    # Import again (this will update existing records)
    resultado2 = service.importar_alugueis(file_content, db_session)
    assert resultado2['success'] is True
    
    # After re-import, ALL should be marked as paid again (including the one we set to False)
    all_alugueis = db_session.query(AluguelMensal).all()
    for aluguel in all_alugueis:
        assert aluguel.pago is True, (
            f"Re-imported aluguel (id={aluguel.id}) should be marked as paid"
        )
    
    print(f"\n✅ SUCCESS: Re-importing also sets pago=True for existing records!")
    print(f"   - First import: {count_first_import} records")
    print(f"   - All {len(all_alugueis)} records have pago=True after re-import")


if __name__ == '__main__':
    # Run with: python -m pytest tests/test_import_pago_status.py -v -s
    pytest.main([__file__, '-v', '-s'])
