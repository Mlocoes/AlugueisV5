/**
 * JavaScript para gerenciamento de Transferências
 */

// Variáveis globais
let transferencias = [];
let usuarios = [];
let transferenciaAtual = null;
let acaoPendente = null;

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    carregarUsuarios();
    carregarTransferencias();
    carregarEstatisticas();
});

// ==================== CARREGAMENTO DE DADOS ====================

async function carregarUsuarios() {
    try {
        const data = await fetchWithAuth('/api/usuarios');
        usuarios = data.usuarios || [];
        
        // Preencher selects
        const origemSelect = document.getElementById('origem_id');
        const destinoSelect = document.getElementById('destino_id');
        const filtroOrigemSelect = document.getElementById('filtro-origem');
        const filtroDestinoSelect = document.getElementById('filtro-destino');
        
        // Limpar options existentes (exceto o primeiro)
        [origemSelect, destinoSelect, filtroOrigemSelect, filtroDestinoSelect].forEach(select => {
            while (select.options.length > 1) {
                select.remove(1);
            }
        });
        
        // Adicionar usuários
        usuarios.forEach(usuario => {
            const option1 = new Option(usuario.nome, usuario.id);
            const option2 = new Option(usuario.nome, usuario.id);
            const option3 = new Option(usuario.nome, usuario.id);
            const option4 = new Option(usuario.nome, usuario.id);
            
            origemSelect.add(option1);
            destinoSelect.add(option2);
            filtroOrigemSelect.add(option3);
            filtroDestinoSelect.add(option4);
        });
    } catch (error) {
        console.error('Erro ao carregar usuários:', error);
        showToast('Erro ao carregar usuários', 'error');
    }
}

async function carregarTransferencias() {
    try {
        const params = new URLSearchParams();
        
        // Aplicar filtros se existirem
        const mesRef = document.getElementById('filtro-mes')?.value;
        const origem = document.getElementById('filtro-origem')?.value;
        const destino = document.getElementById('filtro-destino')?.value;
        const status = document.getElementById('filtro-status')?.value;
        
        if (mesRef) params.append('mes_referencia', mesRef);
        if (origem) params.append('origem_id', origem);
        if (destino) params.append('destino_id', destino);
        if (status) params.append('confirmada', status);
        
        const url = `/api/transferencias${params.toString() ? '?' + params.toString() : ''}`;
        const data = await fetchWithAuth(url);
        
        transferencias = data.transferencias || [];
        renderizarTransferencias();
    } catch (error) {
        console.error('Erro ao carregar transferências:', error);
        showToast('Erro ao carregar transferências', 'error');
    }
}

async function carregarEstatisticas() {
    try {
        const mesRef = document.getElementById('filtro-mes')?.value;
        const url = `/api/transferencias/estatisticas/resumo${mesRef ? '?mes_referencia=' + mesRef : ''}`;
        const data = await fetchWithAuth(url);
        
        document.getElementById('stat-total').textContent = data.total_transferencias || 0;
        document.getElementById('stat-confirmadas').textContent = data.total_confirmadas || 0;
        document.getElementById('stat-pendentes').textContent = data.total_pendentes || 0;
        document.getElementById('stat-valor').textContent = formatarMoeda(data.valor_total || 0);
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
    }
}

// ==================== RENDERIZAÇÃO ====================

function renderizarTransferencias() {
    const tbody = document.getElementById('transferencias-tbody');
    const emptyState = document.getElementById('empty-state');
    
    if (transferencias.length === 0) {
        tbody.innerHTML = '';
        emptyState.classList.remove('hidden');
        return;
    }
    
    emptyState.classList.add('hidden');
    
    tbody.innerHTML = transferencias.map(t => `
        <tr class="hover:bg-gray-800/30 transition-colors">
            <td class="px-6 py-4 text-white">#${t.id}</td>
            <td class="px-6 py-4">
                <div class="flex items-center gap-2">
                    <span class="material-symbols-outlined text-sm text-blue-400">person</span>
                    <span class="text-white">${t.origem_nome || 'N/A'}</span>
                </div>
            </td>
            <td class="px-6 py-4">
                <div class="flex items-center gap-2">
                    <span class="material-symbols-outlined text-sm text-green-400">person</span>
                    <span class="text-white">${t.destino_nome || 'N/A'}</span>
                </div>
            </td>
            <td class="px-6 py-4">
                <span class="text-gray-300">${formatarMesReferencia(t.mes_referencia)}</span>
            </td>
            <td class="px-6 py-4">
                <span class="text-white font-semibold">${formatarMoeda(t.valor)}</span>
            </td>
            <td class="px-6 py-4">
                ${t.confirmada 
                    ? `<span class="badge badge-success">
                        <span class="material-symbols-outlined text-sm">check_circle</span>
                        Confirmada
                       </span>`
                    : `<span class="badge badge-warning">
                        <span class="material-symbols-outlined text-sm">pending</span>
                        Pendente
                       </span>`
                }
            </td>
            <td class="px-6 py-4">
                <div class="flex gap-2">
                    ${!t.confirmada ? `
                        <button onclick="confirmarTransferencia(${t.id})" 
                                class="text-green-400 hover:text-green-300 p-2 rounded hover:bg-green-500/10" 
                                title="Confirmar">
                            <span class="material-symbols-outlined text-sm">check_circle</span>
                        </button>
                    ` : ''}
                    <button onclick="editarTransferencia(${t.id})" 
                            class="text-blue-400 hover:text-blue-300 p-2 rounded hover:bg-blue-500/10" 
                            title="Editar">
                        <span class="material-symbols-outlined text-sm">edit</span>
                    </button>
                    <button onclick="excluirTransferencia(${t.id})" 
                            class="text-red-400 hover:text-red-300 p-2 rounded hover:bg-red-500/10" 
                            title="Excluir">
                        <span class="material-symbols-outlined text-sm">delete</span>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

// ==================== MODAL ====================

function openModal() {
    transferenciaAtual = null;
    document.getElementById('modal-title').textContent = 'Nova Transferência';
    document.getElementById('transferencia-form').reset();
    document.getElementById('transferencia-id').value = '';
    
    // Definir mês atual como padrão
    const hoje = new Date();
    const mesAtual = `${hoje.getFullYear()}-${String(hoje.getMonth() + 1).padStart(2, '0')}`;
    document.getElementById('mes_referencia').value = mesAtual;
    
    document.getElementById('modal').classList.remove('hidden');
}

function closeModal() {
    document.getElementById('modal').classList.add('hidden');
    transferenciaAtual = null;
}

async function editarTransferencia(id) {
    try {
        const transferencia = transferencias.find(t => t.id === id);
        if (!transferencia) {
            showToast('Transferência não encontrada', 'error');
            return;
        }
        
        transferenciaAtual = transferencia;
        
        document.getElementById('modal-title').textContent = 'Editar Transferência';
        document.getElementById('transferencia-id').value = transferencia.id;
        document.getElementById('origem_id').value = transferencia.origem_id;
        document.getElementById('destino_id').value = transferencia.destino_id;
        document.getElementById('mes_referencia').value = transferencia.mes_referencia;
        document.getElementById('valor').value = transferencia.valor;
        document.getElementById('descricao').value = transferencia.descricao || '';
        document.getElementById('confirmada').checked = transferencia.confirmada;
        
        document.getElementById('modal').classList.remove('hidden');
    } catch (error) {
        console.error('Erro ao editar transferência:', error);
        showToast('Erro ao carregar dados da transferência', 'error');
    }
}

// ==================== CRUD ====================

async function salvarTransferencia(event) {
    event.preventDefault();
    
    const id = document.getElementById('transferencia-id').value;
    const data = {
        origem_id: parseInt(document.getElementById('origem_id').value),
        destino_id: parseInt(document.getElementById('destino_id').value),
        mes_referencia: document.getElementById('mes_referencia').value,
        valor: parseFloat(document.getElementById('valor').value),
        descricao: document.getElementById('descricao').value,
        confirmada: document.getElementById('confirmada').checked
    };
    
    // Validações
    if (data.origem_id === data.destino_id) {
        showToast('Origem e destino não podem ser iguais', 'error');
        return;
    }
    
    if (data.valor <= 0) {
        showToast('Valor deve ser maior que zero', 'error');
        return;
    }
    
    try {
        if (id) {
            // Atualizar
            await fetchWithAuth(`/api/transferencias/${id}`, {
                method: 'PUT',
                body: JSON.stringify(data)
            });
            showToast('Transferência atualizada com sucesso', 'success');
        } else {
            // Criar
            await fetchWithAuth('/api/transferencias', {
                method: 'POST',
                body: JSON.stringify(data)
            });
            showToast('Transferência criada com sucesso', 'success');
        }
        
        closeModal();
        carregarTransferencias();
        carregarEstatisticas();
    } catch (error) {
        console.error('Erro ao salvar transferência:', error);
        showToast(error.message || 'Erro ao salvar transferência', 'error');
    }
}

function confirmarTransferencia(id) {
    acaoPendente = {
        tipo: 'confirmar',
        id: id
    };
    
    document.getElementById('confirm-message').textContent = 
        'Deseja realmente confirmar esta transferência? Esta ação não pode ser desfeita.';
    document.getElementById('confirm-modal').classList.remove('hidden');
}

function excluirTransferencia(id) {
    acaoPendente = {
        tipo: 'excluir',
        id: id
    };
    
    document.getElementById('confirm-message').textContent = 
        'Deseja realmente excluir esta transferência? Esta ação não pode ser desfeita.';
    document.getElementById('confirm-modal').classList.remove('hidden');
}

async function confirmarAcao() {
    if (!acaoPendente) return;
    
    try {
        if (acaoPendente.tipo === 'confirmar') {
            await fetchWithAuth(`/api/transferencias/${acaoPendente.id}/confirmar`, {
                method: 'POST'
            });
            showToast('Transferência confirmada com sucesso', 'success');
        } else if (acaoPendente.tipo === 'excluir') {
            await fetchWithAuth(`/api/transferencias/${acaoPendente.id}`, {
                method: 'DELETE'
            });
            showToast('Transferência excluída com sucesso', 'success');
        }
        
        closeConfirmModal();
        carregarTransferencias();
        carregarEstatisticas();
    } catch (error) {
        console.error('Erro ao executar ação:', error);
        showToast(error.message || 'Erro ao executar ação', 'error');
    }
}

function closeConfirmModal() {
    document.getElementById('confirm-modal').classList.add('hidden');
    acaoPendente = null;
}

// ==================== FILTROS ====================

function aplicarFiltros() {
    carregarTransferencias();
    carregarEstatisticas();
}

function limparFiltros() {
    document.getElementById('filtro-mes').value = '';
    document.getElementById('filtro-origem').value = '';
    document.getElementById('filtro-destino').value = '';
    document.getElementById('filtro-status').value = '';
    carregarTransferencias();
    carregarEstatisticas();
}

// ==================== UTILITÁRIOS ====================

function formatarMoeda(valor) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(valor || 0);
}

function formatarMesReferencia(mesRef) {
    if (!mesRef) return 'N/A';
    const [ano, mes] = mesRef.split('-');
    const meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
    return `${meses[parseInt(mes) - 1]}/${ano}`;
}
