// static/js/dashboard.js

document.addEventListener('DOMContentLoaded', () => {
    // 1) Referências principais
    const sidebar      = document.getElementById('sidebar');
    const mobileToggle = document.getElementById('mobile-menu-toggle');
    const collapseBtn  = document.getElementById('sidebar-collapse-btn');

    // --------------------------------------------------
    // 2) MOBILE MENU: mostra / oculta sidebar em telas pequenas
    // --------------------------------------------------
    if (mobileToggle) {
        mobileToggle.addEventListener('click', () => {
            sidebar.classList.toggle('mobile-open');
        });
    }

    // Fecha sidebar mobile ao clicar fora dela
    document.addEventListener('click', (e) => {
        if (
            sidebar.classList.contains('mobile-open') &&
            !sidebar.contains(e.target) &&
            mobileToggle &&
            !mobileToggle.contains(e.target) &&
            !e.target.closest('#sidebar')
        ) {
            sidebar.classList.remove('mobile-open');
        }
    });

    // --------------------------------------------------
    // 3) ATIVA ITEM DE MENU ATUAL
    // --------------------------------------------------
    const currentPath = window.location.pathname;
    document.querySelectorAll('#sidebar nav li a').forEach(item => {
        if (item.getAttribute('href') === currentPath) {
            item.classList.add('bg-gray-700', 'text-white');
            item.classList.remove('hover:bg-gray-700', 'text-gray-300');
        }
    });

    // --------------------------------------------------
    // 4) ANIMAÇÃO DAS SETAS DOS SUBMENUS (toggle rotate)
    // --------------------------------------------------
    document.querySelectorAll('[data-bs-toggle="collapse"]').forEach(btn => {
        btn.addEventListener('click', function() {
            const icon = this.querySelector('.fa-chevron-down');
            if (icon) {
                icon.classList.toggle('rotate-180');
            }
        });
    });

    // --------------------------------------------------
    // 5) TOOLTIP (opcional) quando sidebar colapsado
    // --------------------------------------------------
    if (sidebar.classList.contains('collapsed')) {
        document.querySelectorAll('#sidebar nav li > a:not([data-bs-toggle])').forEach(item => {
            const spanText = item.querySelector('span');
            if (spanText) {
                item.setAttribute('data-tooltip', spanText.textContent.trim());
            }
        });
    }

    // --------------------------------------------------
    // 6) TOGGLE DE COLAPSO DO SIDEBAR - CORRIGIDO
    // --------------------------------------------------
    if (collapseBtn) {
        collapseBtn.addEventListener('click', () => {
            // 6.1) Alterna a classe 'collapsed'
            sidebar.classList.toggle('collapsed');

            // 6.2) Animação do ícone (rotação)
            const icon = collapseBtn.querySelector('i');
            if (icon) {
                icon.style.transform = sidebar.classList.contains('collapsed') 
                    ? 'rotate(180deg)' 
                    : 'rotate(0deg)';
            }

            // 6.3) Adiciona ou remove tooltips
            document.querySelectorAll('#sidebar nav li > a:not([data-bs-toggle])').forEach(item => {
                if (sidebar.classList.contains('collapsed')) {
                    const textSpan = item.querySelector('span');
                    if (textSpan) {
                        item.setAttribute('data-tooltip', textSpan.textContent.trim());
                    }
                } else {
                    item.removeAttribute('data-tooltip');
                }
            });
        });
    }

    // Garante que o sidebar inicie no estado correto
    if (localStorage.getItem('sidebar-collapsed') === 'true') {
        sidebar.classList.add('collapsed');
        const icon = collapseBtn.querySelector('i');
        if (icon) icon.style.transform = 'rotate(180deg)';
    }

    // Salva o estado do sidebar
    collapseBtn.addEventListener('click', () => {
        localStorage.setItem('sidebar-collapsed', sidebar.classList.contains('collapsed'));
    });
});
