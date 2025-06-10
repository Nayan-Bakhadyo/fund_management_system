document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');
    const toggleBtn = document.getElementById('sidebarToggle');
    const portfolioLink = document.getElementById('portfolio-link');
    const transactionHistoryLink = document.getElementById('transaction-history');
    const dashboardContent = document.getElementById('dashboard-content');
    const sidebarOverlay = document.getElementById('sidebar-overlay');

    function openSidebar() {
        sidebar.classList.add('open');
        sidebarOverlay.style.display = 'block';
    }
    function closeSidebar() {
        sidebar.classList.remove('open');
        sidebarOverlay.style.display = 'none';
    }

    toggleBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        if (sidebar.classList.contains('open')) {
            closeSidebar();
        } else {
            openSidebar();
        }
    });

    sidebarOverlay.addEventListener('click', closeSidebar);

    // Optional: close sidebar when resizing to desktop
    window.addEventListener('resize', function() {
        if (window.innerWidth > 767) {
            closeSidebar();
        }
    });

    if (portfolioLink) {
        portfolioLink.addEventListener('click', function(e) {
            e.preventDefault();
            fetch('/user/portfolio/', {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.text())
            .then(html => {
                dashboardContent.innerHTML = html;
            });
        });
    }

    if (transactionHistoryLink) {
        transactionHistoryLink.addEventListener('click', function(e) {
            e.preventDefault();
            fetch('/user/transactions/', {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.text())
            .then(html => {
                dashboardContent.innerHTML = html;
            });
        });
    }
});