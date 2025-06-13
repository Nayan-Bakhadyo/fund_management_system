document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');
    const toggleBtn = document.getElementById('sidebarToggle');
    const portfolioLink = document.getElementById('portfolio-link');
    const transactionHistoryLink = document.getElementById('transaction-history');
    const bankDetailLink = document.getElementById('bank-detail-link');
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

    // Function to render the NAV chart after loading portfolio.html
    function renderNavChart() {
        const canvas = document.getElementById('navLineChart');
        if (!canvas) return;
        const navDates = JSON.parse(canvas.dataset.dates);
        const navUnitCosts = JSON.parse(canvas.dataset.costs);

        if (!navDates.length || !navUnitCosts.length) return;

        // Destroy previous chart instance if needed
        if (window.navChartInstance) {
            window.navChartInstance.destroy();
        }

        const ctx = canvas.getContext('2d');
        window.navChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: navDates,
                datasets: [{
                    label: 'Unit Cost (NAV)',
                    data: navUnitCosts,
                    borderColor: '#bfa14a',
                    backgroundColor: 'rgba(191,161,74,0.1)',
                    tension: 0.3,
                    fill: true,
                    pointRadius: 3,
                    pointBackgroundColor: '#bfa14a'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        title: { display: true, text: 'Date' }
                    },
                    y: {
                        title: { display: true, text: 'Unit Cost' },
                        beginAtZero: false
                    }
                }
            }
        });
    }

    // When the user clicks "Portfolio Performance"
    if (portfolioLink) {
        portfolioLink.addEventListener('click', function(e) {
            e.preventDefault();
            fetch('/user/portfolio/', { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
                .then(response => response.text())
                .then(html => {
                    dashboardContent.innerHTML = html;
                    renderNavChart(); // Call this after injecting the HTML
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

    if (bankDetailLink) {
        bankDetailLink.addEventListener('click', function(e) {
            e.preventDefault();
            fetch('/user/bank_detail/', { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
                .then(response => response.json())
                .then(data => {
                    dashboardContent.innerHTML = data.html;
                    attachBankDetailFormHandler();
                });
        });
    }

    function attachBankDetailFormHandler() {
        const form = document.getElementById('bank-detail-form');
        const cancelBtn = document.getElementById('cancel-bank-detail');
        const messageDiv = document.getElementById('bank-detail-message');
        if (form) {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                const formData = new FormData(form);
                fetch('/user/bank_detail/', {
                    method: 'POST',
                    headers: { 'X-Requested-With': 'XMLHttpRequest' },
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        messageDiv.textContent = data.message;
                        messageDiv.className = 'alert alert-success mt-2';
                    } else {
                        messageDiv.textContent = 'Failed to save bank details.';
                        messageDiv.className = 'alert alert-danger mt-2';
                    }
                });
            });
        }
        if (cancelBtn) {
            cancelBtn.addEventListener('click', function() {
                dashboardContent.innerHTML = `
                    <div class="dashboard-title">Welcome to Your Dashboard</div>
                    <div class="dashboard-message">
                        Hello, ${document.querySelector('.user-name').textContent}!<br>
                        This is your user dashboard.
                    </div>
                `;
            });
        }
    }

    // Call renderNavChart on page load
    renderNavChart();
});

