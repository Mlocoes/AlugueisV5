#!/usr/bin/env python3
"""
Script para corrigir o uso de fetchWithAuth nos templates
Agora fetchWithAuth retorna diretamente o JSON, não o response
"""

import re
from pathlib import Path

def fix_template(filepath):
    """Corrige padrões de uso do fetchWithAuth em um template"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    changes = []
    
    # Padrão 1: const response = await fetchWithAuth(...); if (response && response.ok) { const data = await response.json();
    # Substituir por: const data = await fetchWithAuth(...); if (data) {
    pattern1 = r'const (\w+) = await fetchWithAuth\(([^)]+)\);\s*if \(\1 && \1\.ok\) \{\s*const (\w+) = await \1\.json\(\);'
    replacement1 = r'const \3 = await fetchWithAuth(\2);\n        if (\3) {'
    
    if re.search(pattern1, content):
        content = re.sub(pattern1, replacement1, content)
        changes.append(f"Padrão 1: response && response.ok com .json()")
    
    # Padrão 2: const response = await fetchWithAuth(...); if (response.ok) { const data = await response.json();
    pattern2 = r'const response = await fetchWithAuth\(([^)]+)\);\s*if \(response\.ok\) \{\s*(\w+) = await response\.json\(\);'
    replacement2 = r'\2 = await fetchWithAuth(\1);\n        if (\2) {'
    
    if re.search(pattern2, content):
        content = re.sub(pattern2, replacement2, content)
        changes.append(f"Padrão 2: response.ok com .json()")
    
    # Padrão 3: const data = await response.json(); (sem if antes)
    # Este padrão precisa ser tratado manualmente, então vamos apenas reportar
    pattern3 = r'const (\w+) = await (\w+)\.json\(\);'
    matches3 = re.findall(pattern3, content)
    if matches3:
        for match in matches3:
            if 'response' in match[1].lower():
                changes.append(f"MANUAL: const {match[0]} = await {match[1]}.json(); (linha precisa ser verificada)")
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n✅ {filepath.name}:")
        for change in changes:
            print(f"   - {change}")
        return True
    else:
        print(f"⏭️  {filepath.name}: Nenhuma alteração necessária")
        return False

def main():
    templates_dir = Path(__file__).parent / 'app' / 'templates'
    
    print("🔧 Corrigindo uso de fetchWithAuth nos templates...\n")
    
    templates = [
        'alugueis.html',
        'participacoes.html',
        'relatorios.html',
    ]
    
    fixed_count = 0
    for template_name in templates:
        template_path = templates_dir / template_name
        if template_path.exists():
            if fix_template(template_path):
                fixed_count += 1
        else:
            print(f"❌ {template_name}: Arquivo não encontrado")
    
    print(f"\n📊 Resumo: {fixed_count} arquivo(s) modificado(s)")
    print("\n⚠️  ATENÇÃO: Alguns padrões precisam de revisão manual!")
    print("   Procure por 'await response.json()' nos templates e substitua conforme necessário.")

if __name__ == '__main__':
    main()
