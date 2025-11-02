// Utilidades gerais do AlugueisV5

// Configuração de timeout de inatividade (30 minutos)
const INACTIVITY_TIMEOUT = 30 * 60 * 1000; // 30 minutos em milissegundos
let inactivityTimer = null;

// Sistema de detecção de reload (F5/Ctrl+R)
// Detecta quando a página é recarregada e força logout
(function() {
    const navigationType = performance.getEntriesByType('navigation')[0]?.type;
    const currentPath = window.location.pathname;
    
    // Se foi reload (F5, Ctrl+R) e não está na página de login
    if (navigationType === 'reload' && !currentPath.includes('/login')) {
        // Fazer logout imediatamente
        fetch('/api/auth/logout', {
            method: 'POST',
            credentials: 'include'
        }).finally(() => {
            window.location.href = '/login';
        });
        
        // Prevenir que o resto da página carregue
        throw new Error('Reload detected - redirecting to login');
    }
})();

// Resetar timer de inatividade
function resetInactivityTimer() {
    // Não fazer nada se estiver na página de login
    if (window.location.pathname.includes('/login')) {
        return;
    }
    
    clearTimeout(inactivityTimer);
    
    inactivityTimer = setTimeout(() => {
        showToast('Sessão expirada por inatividade', 'warning');
        setTimeout(() => logout(), 2000);
    }, INACTIVITY_TIMEOUT);
}

// Inicializar monitoramento apenas se não estiver no login
if (!window.location.pathname.includes('/login')) {
    // Eventos que resetam o timer
    const activityEvents = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
    
    activityEvents.forEach(event => {
        document.addEventListener(event, resetInactivityTimer, { passive: true, capture: true });
    });
    
    // Iniciar timer quando página carregar
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', resetInactivityTimer);
    } else {
        resetInactivityTimer();
    }
}

// Função de logout
async function logout() {
    try {
        await fetch('/api/auth/logout', {
            method: 'POST',
            credentials: 'include'
        });
    } catch (error) {
        console.error('Erro ao fazer logout:', error);
    } finally {
        window.location.href = '/login';
    }
}

// Função para fazer requisições com token JWT
async function fetchWithAuth(url, options = {}) {
    // Resetar timer de inatividade em cada requisição
    resetInactivityTimer();
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
        credentials: 'include', // Inclui cookies (JWT)
        ...options
    };

    try {
        const response = await fetch(url, defaultOptions);
        
        // Se não autorizado, redireciona para login
        if (response.status === 401) {
            window.location.href = '/login';
            return null;
        }

        // Se não for sucesso, lançar erro
        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Erro desconhecido' }));
            throw new Error(error.detail || `HTTP error! status: ${response.status}`);
        }

        // Retornar o JSON parseado
        return await response.json();
    } catch (error) {
        console.error('Erro na requisição:', error);
        throw error;
    }
}

// Sistema de notificações toast
function showToast(message, type = 'info') {
    // Remove toast anterior se existir
    const oldToast = document.querySelector('.toast');
    if (oldToast) {
        oldToast.remove();
    }

    const colors = {
        success: 'bg-green-500',
        error: 'bg-red-500',
        warning: 'bg-yellow-500',
        info: 'bg-blue-500'
    };

    const toast = document.createElement('div');
    toast.className = `toast fixed top-4 right-4 ${colors[type]} text-white px-6 py-3 rounded-lg shadow-lg z-50 fade-in`;
    toast.textContent = message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Formatar valor monetário (BRL)
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

// Formatar data no padrão brasileiro
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
}

// Formatar mês/ano (MM/YYYY)
function formatMonthYear(monthStr) {
    if (!monthStr) return '-';
    const [year, month] = monthStr.split('-');
    return `${month}/${year}`;
}

// Debounce para otimizar buscas
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Confirmar ação crítica
function confirmAction(message) {
    return new Promise((resolve) => {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="bg-[#1e293b] rounded-lg p-6 max-w-md mx-4">
                <h3 class="text-xl font-semibold mb-4">Confirmação</h3>
                <p class="text-gray-300 mb-6">${message}</p>
                <div class="flex gap-3 justify-end">
                    <button class="btn-cancel px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded-lg">
                        Cancelar
                    </button>
                    <button class="btn-confirm px-4 py-2 bg-red-500 hover:bg-red-600 rounded-lg">
                        Confirmar
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        modal.querySelector('.btn-cancel').onclick = () => {
            modal.remove();
            resolve(false);
        };

        modal.querySelector('.btn-confirm').onclick = () => {
            modal.remove();
            resolve(true);
        };

        // Fechar ao clicar fora
        modal.onclick = (e) => {
            if (e.target === modal) {
                modal.remove();
                resolve(false);
            }
        };
    });
}

// Loading overlay
function showLoading() {
    const loading = document.createElement('div');
    loading.id = 'loading-overlay';
    loading.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    loading.innerHTML = '<div class="spinner"></div>';
    document.body.appendChild(loading);
}

function hideLoading() {
    const loading = document.getElementById('loading-overlay');
    if (loading) loading.remove();
}

// Validação de email
function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// Validação de CPF
function isValidCPF(cpf) {
    cpf = cpf.replace(/[^\d]/g, '');
    if (cpf.length !== 11 || /^(\d)\1+$/.test(cpf)) return false;

    let sum = 0;
    let remainder;

    for (let i = 1; i <= 9; i++) {
        sum += parseInt(cpf.substring(i - 1, i)) * (11 - i);
    }
    remainder = (sum * 10) % 11;
    if (remainder === 10 || remainder === 11) remainder = 0;
    if (remainder !== parseInt(cpf.substring(9, 10))) return false;

    sum = 0;
    for (let i = 1; i <= 10; i++) {
        sum += parseInt(cpf.substring(i - 1, i)) * (12 - i);
    }
    remainder = (sum * 10) % 11;
    if (remainder === 10 || remainder === 11) remainder = 0;
    if (remainder !== parseInt(cpf.substring(10, 11))) return false;

    return true;
}

// Exportar para CSV
function exportToCSV(data, filename) {
    const csv = data.map(row => Object.values(row).join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
}

// Event listener para logout
document.addEventListener('DOMContentLoaded', () => {
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            const response = await fetchWithAuth('/api/auth/logout', { method: 'POST' });
            if (response && response.ok) {
                window.location.href = '/login';
            }
        });
    }
});
