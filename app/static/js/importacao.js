/**
 * JavaScript para módulo de Importação
 */

let tipoImportacao = null;
let arquivoAtual = null;

// ==================== SELEÇÃO DE TIPO ====================

function selecionarTipo(tipo) {
    tipoImportacao = tipo;
    
    // Mostrar área de upload
    document.getElementById('upload-area').classList.remove('hidden');
    document.getElementById('tipo-selecionado').textContent = `(${tipo.charAt(0).toUpperCase() + tipo.slice(1)})`;
    
    // Scroll suave para a área de upload
    document.getElementById('upload-area').scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    // Baixar template automaticamente
    baixarTemplate(tipo);
}

async function baixarTemplate(tipo) {
    try {
        const response = await fetch(`/api/importacao/template/${tipo}`);
        
        if (!response.ok) {
            throw new Error('Erro ao baixar template');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `template_${tipo}.xlsx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showToast(`Template de ${tipo} baixado com sucesso!`, 'success');
    } catch (error) {
        console.error('Erro ao baixar template:', error);
        showToast('Erro ao baixar template', 'error');
    }
}

// ==================== UPLOAD DE ARQUIVO ====================

// Configurar dropzone
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('file-input');

dropzone.addEventListener('click', () => {
    fileInput.click();
});

dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('border-[var(--primary)]');
});

dropzone.addEventListener('dragleave', () => {
    dropzone.classList.remove('border-[var(--primary)]');
});

dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('border-[var(--primary)]');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

function handleFile(file) {
    // Validar tamanho (10MB)
    if (file.size > 10 * 1024 * 1024) {
        showToast('Arquivo muito grande. Máximo: 10MB', 'error');
        return;
    }
    
    // Validar extensão
    const extensao = file.name.split('.').pop().toLowerCase();
    if (!['xlsx', 'xls', 'csv'].includes(extensao)) {
        showToast('Formato inválido. Use .xlsx, .xls ou .csv', 'error');
        return;
    }
    
    arquivoAtual = file;
    
    // Mostrar informações do arquivo
    document.getElementById('file-selected').classList.remove('hidden');
    document.getElementById('file-name').textContent = file.name;
    document.getElementById('file-size').textContent = formatarTamanho(file.size);
    
    showToast('Arquivo carregado com sucesso', 'success');
}

function limparArquivo() {
    arquivoAtual = null;
    fileInput.value = '';
    document.getElementById('file-selected').classList.add('hidden');
    document.getElementById('preview-area').classList.add('hidden');
}

function formatarTamanho(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
}

// ==================== PREVIEW ====================

async function gerarPreview() {
    if (!arquivoAtual) {
        showToast('Nenhum arquivo selecionado', 'error');
        return;
    }
    
    showLoading('Gerando preview...');
    
    try {
        const formData = new FormData();
        formData.append('file', arquivoAtual);
        
        const response = await fetch('/api/importacao/preview', {
            method: 'POST',
            body: formData,
            credentials: 'include'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao gerar preview');
        }
        
        const data = await response.json();
        
        // Mostrar preview
        mostrarPreview(data);
        
        hideLoading();
    } catch (error) {
        console.error('Erro ao gerar preview:', error);
        showToast(error.message, 'error');
        hideLoading();
    }
}

function mostrarPreview(data) {
    const previewArea = document.getElementById('preview-area');
    const previewInfo = document.getElementById('preview-info');
    const previewHeader = document.getElementById('preview-header');
    const previewBody = document.getElementById('preview-body');
    
    // Informações
    previewInfo.innerHTML = `
        <div class="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4 mb-4">
            <p class="text-gray-300">
                <strong>${data.colunas.length}</strong> colunas encontradas • 
                <strong>${data.total_linhas_preview}</strong> primeiras linhas exibidas
            </p>
            <p class="text-gray-400 text-sm mt-1">
                Colunas: ${data.colunas.join(', ')}
            </p>
        </div>
    `;
    
    // Cabeçalho
    previewHeader.innerHTML = data.colunas.map(col => 
        `<th class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">${col}</th>`
    ).join('');
    
    // Corpo
    previewBody.innerHTML = data.preview.map(row => `
        <tr class="hover:bg-gray-800/30 border-t border-gray-700">
            ${data.colunas.map(col => `
                <td class="px-4 py-3 text-gray-300 text-sm">${row[col] || '-'}</td>
            `).join('')}
        </tr>
    `).join('');
    
    // Mostrar
    previewArea.classList.remove('hidden');
    previewArea.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function fecharPreview() {
    document.getElementById('preview-area').classList.add('hidden');
}

// ==================== IMPORTAÇÃO ====================

async function iniciarImportacao() {
    if (!arquivoAtual || !tipoImportacao) {
        showToast('Selecione um arquivo e tipo de importação', 'error');
        return;
    }
    
    // Confirmar
    if (!confirm(`Deseja importar ${tipoImportacao}? Esta ação não pode ser desfeita.`)) {
        return;
    }
    
    showLoading(`Importando ${tipoImportacao}...`);
    
    try {
        const formData = new FormData();
        formData.append('file', arquivoAtual);
        
        const response = await fetch(`/api/importacao/${tipoImportacao}`, {
            method: 'POST',
            body: formData,
            credentials: 'include'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao importar');
        }
        
        const resultado = await response.json();
        
        // Mostrar resultado
        mostrarResultado(resultado);
        
        hideLoading();
    } catch (error) {
        console.error('Erro ao importar:', error);
        showToast(error.message, 'error');
        hideLoading();
    }
}

function mostrarResultado(resultado) {
    const resultadoArea = document.getElementById('resultado-area');
    const resultadoConteudo = document.getElementById('resultado-conteudo');
    
    let html = `
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div class="card p-6 bg-green-500/10 border border-green-500/30">
                <div class="flex items-center gap-3">
                    <span class="material-symbols-outlined text-green-400 text-4xl">check_circle</span>
                    <div>
                        <p class="text-gray-400 text-sm">Importados</p>
                        <p class="text-2xl font-bold text-white">${resultado.importados}</p>
                    </div>
                </div>
            </div>
            
            <div class="card p-6 bg-red-500/10 border border-red-500/30">
                <div class="flex items-center gap-3">
                    <span class="material-symbols-outlined text-red-400 text-4xl">error</span>
                    <div>
                        <p class="text-gray-400 text-sm">Erros</p>
                        <p class="text-2xl font-bold text-white">${resultado.erros?.length || 0}</p>
                    </div>
                </div>
            </div>
            
            <div class="card p-6 bg-yellow-500/10 border border-yellow-500/30">
                <div class="flex items-center gap-3">
                    <span class="material-symbols-outlined text-yellow-400 text-4xl">warning</span>
                    <div>
                        <p class="text-gray-400 text-sm">Avisos</p>
                        <p class="text-2xl font-bold text-white">${resultado.warnings?.length || 0}</p>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Erros
    if (resultado.erros && resultado.erros.length > 0) {
        html += `
            <div class="card p-6 bg-red-500/10 border border-red-500/30 mb-6">
                <h3 class="text-lg font-bold text-white mb-4 flex items-center gap-2">
                    <span class="material-symbols-outlined">error</span>
                    Erros Encontrados
                </h3>
                <div class="space-y-2 max-h-64 overflow-y-auto">
                    ${resultado.erros.map(erro => `
                        <div class="bg-gray-800 rounded p-3 text-sm text-gray-300">${erro}</div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    // Avisos
    if (resultado.warnings && resultado.warnings.length > 0) {
        html += `
            <div class="card p-6 bg-yellow-500/10 border border-yellow-500/30">
                <h3 class="text-lg font-bold text-white mb-4 flex items-center gap-2">
                    <span class="material-symbols-outlined">warning</span>
                    Avisos
                </h3>
                <div class="space-y-2 max-h-64 overflow-y-auto">
                    ${resultado.warnings.map(aviso => `
                        <div class="bg-gray-800 rounded p-3 text-sm text-gray-300">${aviso}</div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    resultadoConteudo.innerHTML = html;
    
    // Ocultar outras áreas
    document.getElementById('upload-area').classList.add('hidden');
    document.getElementById('preview-area').classList.add('hidden');
    
    // Mostrar resultado
    resultadoArea.classList.remove('hidden');
    resultadoArea.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    showToast(`Importação concluída! ${resultado.importados} registro(s) importado(s)`, 'success');
}

function resetarImportacao() {
    // Limpar tudo
    tipoImportacao = null;
    arquivoAtual = null;
    fileInput.value = '';
    
    // Ocultar áreas
    document.getElementById('upload-area').classList.add('hidden');
    document.getElementById('file-selected').classList.add('hidden');
    document.getElementById('preview-area').classList.add('hidden');
    document.getElementById('resultado-area').classList.add('hidden');
    
    // Scroll para o topo
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ==================== LOADING ====================

function showLoading(message) {
    document.getElementById('loading-message').textContent = message;
    const overlay = document.getElementById('loading-overlay');
    overlay.classList.remove('hidden');
    overlay.classList.add('flex');
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    overlay.classList.add('hidden');
    overlay.classList.remove('flex');
}

// ==================== INICIALIZAÇÃO ====================

document.addEventListener('DOMContentLoaded', () => {
    // Verificar dependências
    verificarDependencias();
});

async function verificarDependencias() {
    try {
        const response = await fetchWithAuth('/api/importacao/check-dependencies');
        
        if (!response.success) {
            showToast('Aviso: Dependências de importação não instaladas completamente', 'warning');
            console.warn(response.message);
        }
    } catch (error) {
        console.error('Erro ao verificar dependências:', error);
    }
}
