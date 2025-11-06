# Participações - Handsontable Implementation

## Overview

This implementation replaces the traditional participation table with an Excel-like editable grid using Handsontable. The new interface provides:

- **Matrix View**: Properties (rows) × Owners (columns) showing percentage participations
- **Real-time Validation**: Ensures each property's total equals 100% (±0.05%)
- **Version Control**: Save and restore different participation configurations
- **Visual Feedback**: Color-coded validation (red for errors, yellow for warnings)

## Features Implemented

### 1. Database Layer
- **Model**: `ParticipacaoVersao` - Stores historical versions of participation configurations
- **Migration**: Automatically creates the `participacao_versoes` table
- **Transaction Safety**: All database operations use transactions with rollback on errors

### 2. API Endpoints

Base path: `/api/participacoes-versoes`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/grid-data` | GET | Returns data for the grid (imoveis, proprietarios, current participacoes) |
| `/` | GET | Lists all saved versions |
| `/` | POST | Creates and applies a new version |
| `/{id}` | GET | Gets a specific version |
| `/{id}/aplicar` | POST | Applies a saved version |
| `/{id}` | DELETE | Deletes a version (admin only) |

### 3. Frontend Features

#### Handsontable Grid
- **Read-only columns**:
  - Column 1: Property names
  - Column 2: Total percentage (auto-calculated)
- **Editable columns**: One per owner showing their participation percentage
- **Dark theme**: Styled to match the application's design

#### Validation
- **Acceptable range**: 99.95% - 100.05% per property
- **Warning range**: 99.98% - 100.02% per property
- **Visual feedback**:
  - ❌ Red: Total outside acceptable range
  - ⚠️ Yellow: Total in acceptable range but outside recommended range
  - ✅ Green (hidden): All validations pass

#### Version Management
- **Save**: Validates and saves current configuration with a name
- **Load**: Select from dropdown to view/restore previous versions
- **Dropdown**: Shows version name and creation date

## Usage

### For Developers

1. **Run migration**:
   ```bash
   alembic upgrade head
   ```

2. **Start application**:
   ```bash
   uvicorn app.main:app --reload
   ```

3. **Access interface**:
   Navigate to `/participacoes` in your browser

### For Users

1. **View Current Participations**:
   - Grid shows all properties and their ownership distribution
   - Total column shows sum of all owner percentages

2. **Edit Participations**:
   - Click any percentage cell to edit
   - Enter new percentage value
   - Total automatically recalculates
   - Validation runs in real-time

3. **Save New Version**:
   - Ensure all properties have valid totals (100% ±0.05%)
   - Click "Salvar Versão" button
   - Enter version name and optional notes
   - Click "Salvar" in modal

4. **Load Previous Version**:
   - Select version from dropdown
   - Grid updates to show that version's data
   - Can be edited and saved as a new version

## Data Structure

Participation data is stored in JSON format:
```json
{
  "imovel_id": {
    "proprietario_id": percentage_value
  }
}
```

Example:
```json
{
  "1": {
    "1": 50.0,
    "2": 30.0,
    "3": 20.0
  },
  "2": {
    "1": 100.0
  }
}
```

## Validation Rules

1. **Sum Check**: For each property, the sum of all owner percentages must be between 99.95% and 100.05%
2. **Recommended Range**: Ideally between 99.98% and 100.02% (shows warning otherwise)
3. **Tolerance Reason**: Accounts for floating-point arithmetic and rounding

## Security

- ✅ No SQL injection vulnerabilities (CodeQL verified)
- ✅ Transaction safety with rollback on errors
- ✅ Authentication required for all endpoints
- ✅ Admin-only deletion of versions

## Technical Stack

- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Frontend**: Handsontable 13.1.0 + Vanilla JavaScript
- **Styling**: TailwindCSS + Custom dark theme

## Files Modified/Created

### Created
1. `app/models/participacao_versao.py` - Database model
2. `app/routes/participacoes_versoes.py` - API endpoints
3. `alembic/versions/20251106_add_participacao_versoes.py` - Migration
4. `app/templates/participacoes.html` - New UI (replaced)

### Modified
1. `app/main.py` - Router registration
2. `app/models/__init__.py` - Model export
3. `app/templates/base.html` - Added head block support

### Backed Up
1. `app/templates/participacoes_old.html` - Original template

## Testing

Run the validation tests:
```bash
python3 /tmp/test_participacoes_versoes.py
```

Expected output:
```
✅ Model structure validated
✅ Pydantic schemas validated
✅ Validation logic tested
✅ Router configuration verified
```

## Known Limitations

1. **License**: Handsontable uses "non-commercial-and-evaluation" license
   - For commercial use, purchase a license from handsontable.com
2. **Browser Support**: Requires modern browser with ES6+ support
3. **Network**: External CDN resources (may be blocked in restricted environments)

## Future Enhancements

- [ ] Export to Excel
- [ ] Import from Excel
- [ ] Audit log for version changes
- [ ] Batch edit operations
- [ ] Comparison between versions
- [ ] Undo/redo functionality

## Support

For issues or questions:
1. Check API documentation at `/docs`
2. Review console for JavaScript errors
3. Check server logs for backend errors
4. Verify database migration completed successfully

## License

This implementation is part of the AlugueisV5 system and follows the same license terms.
