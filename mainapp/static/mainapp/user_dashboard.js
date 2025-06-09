document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');
    const toggleBtn = document.getElementById('sidebarToggle');
    const portfolioLink = document.getElementById('portfolio-link');
    const dashboardContent = document.getElementById('dashboard-content');

    toggleBtn.addEventListener('click', function() {
        sidebar.classList.toggle('collapsed');
        mainContent.classList.toggle('collapsed');
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
});