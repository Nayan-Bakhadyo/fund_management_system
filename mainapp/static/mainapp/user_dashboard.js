document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');
    const toggleBtn = document.getElementById('sidebarToggle');
    const portfolioLink = document.getElementById('portfolio-link');
    const transactionHistoryLink = document.getElementById('transaction-history');
    const bankDetailLink = document.getElementById('bank-detail-link');
    const dashboardContent = document.getElementById('dashboard-content');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    const viewUserDashboardLink = document.getElementById('view-user-dashboard');

    function openSidebar() {
        sidebar.classList.add('open');
    }
    function closeSidebar() {
        sidebar.classList.remove('open');
    }

    toggleBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        if (sidebar.classList.contains('open')) {
            closeSidebar();
        } else {
            openSidebar();
        }
    });

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

    if (viewUserDashboardLink) {
        viewUserDashboardLink.addEventListener('click', function(e) {
            e.preventDefault();
            const email = prompt("Enter the user's email to view their portfolio:");
            if (email) {
                fetch(`/fundmanager/user_portfolio/?email=${encodeURIComponent(email)}`, {
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                })
                .then(response => response.text())
                .then(html => {
                    dashboardContent.innerHTML = html;
                    renderNavChart(); // <-- Call it right here!
                });
            }
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
  // Modal open on menu click
  const uploadMenu = document.getElementById('uploadTransactionMenu');
  if (uploadMenu) {
    uploadMenu.addEventListener('click', function(e) {
      e.preventDefault();
      const modal = new bootstrap.Modal(document.getElementById('uploadTransactionModal'));
      modal.show();
    });
  }

  // (Keep your AJAX form submission code here as before)
});

document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('transaction-upload-form');
  const messageDiv = document.getElementById('transaction-upload-message');
  if (form) {
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      const formData = new FormData(form);

      fetch('/user/upload_transaction/', {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          messageDiv.innerHTML = '<div class="alert alert-success">Upload successful!</div>';
          form.reset();
        } else {
          messageDiv.innerHTML = '<div class="alert alert-danger">' + (data.error || 'Upload failed.') + '</div>';
        }
      })
      .catch(() => {
        messageDiv.innerHTML = '<div class="alert alert-danger">An error occurred. Please try again.</div>';
      });
    });
  }
});

document.addEventListener('DOMContentLoaded', function() {
  // Show bank detail modal
  const bankMenu = document.getElementById('viewBankDetailMenu');
  if (bankMenu) {
    bankMenu.addEventListener('click', function(e) {
      e.preventDefault();
      const modal = new bootstrap.Modal(document.getElementById('bankDetailModal'));
      modal.show();
    });
  }

  // Copy to clipboard functionality for bank details
  document.querySelectorAll('.copy-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      const targetId = btn.getAttribute('data-copy');
      const text = document.getElementById(targetId).textContent;
      navigator.clipboard.writeText(text).then(function() {
        btn.textContent = 'Copied!';
        setTimeout(() => { btn.textContent = 'Copy'; }, 1200);
      });
    });
  });
});

document.addEventListener('DOMContentLoaded', function() {
  // Open modal and fetch current payment detail
  const modifyMenu = document.getElementById('modifyPaymentDetailMenu');
  if (modifyMenu) {
    modifyMenu.addEventListener('click', function(e) {
      e.preventDefault();
      fetch('/user/payment_detail/', {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      })
      .then(response => response.json())
      .then(data => {
        // Set values (or defaults)
        document.getElementById('recurring_payment_amount').value = data.recurring_payment_amount || '';
        document.getElementById('payment_date').value = data.payment_date || '';
        document.getElementById('modify-payment-detail-message').innerHTML = '';
        const modal = new bootstrap.Modal(document.getElementById('modifyPaymentDetailModal'));
        modal.show();
      });
    });
  }

  // Handle form submit
  const form = document.getElementById('modify-payment-detail-form');
  if (form) {
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      const formData = new FormData(form);
      fetch('/user/payment_detail/', {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        body: formData
      })
      .then(response => response.json())
      .then(data => {
        const msgDiv = document.getElementById('modify-payment-detail-message');
        if (data.success) {
          msgDiv.innerHTML = '<div class="alert alert-success">Payment detail updated!</div>';
        } else {
          msgDiv.innerHTML = '<div class="alert alert-danger">' + (data.error || 'Update failed.') + '</div>';
        }
      });
    });
  }
});

document.addEventListener('DOMContentLoaded', function() {
  const firmStatusMenu = document.getElementById('firmStatusMenu');
  if (firmStatusMenu) {
    firmStatusMenu.addEventListener('click', function(e) {
      e.preventDefault();
      // Show modal and loading spinner
      const modal = new bootstrap.Modal(document.getElementById('firmStatusModal'));
      document.getElementById('firm-status-dashboard').innerHTML =
        '<div class="text-center py-5"><div class="spinner-border text-success" role="status"></div></div>';
      modal.show();
      // Fetch dashboard content and render charts
      fetch('/firm_status_dashboard/')
        .then(response => response.json())
        .then(data => {
          document.getElementById('firm-status-dashboard').innerHTML = data.html;
          setTimeout(renderFirmStatusCharts, 100); // Give DOM time to update
        });
    });
  }
});

function renderFirmStatusCharts() {
    // Pie Chart
    const pieCanvas = document.getElementById('capitalPieChart');
    const lineCanvas = document.getElementById('capitalLineChart');
    if (!pieCanvas || !lineCanvas) return;

    // Get data from data attributes or hidden inputs if needed
    const invested = parseFloat(pieCanvas.getAttribute('data-invested')) || 0;
    const reserve = parseFloat(pieCanvas.getAttribute('data-reserve')) || 0;

    // For line chart, you can use data attributes or JSON embedded in the HTML
    const lineLabels = JSON.parse(lineCanvas.getAttribute('data-labels') || '[]');
    const lineData = JSON.parse(lineCanvas.getAttribute('data-data') || '[]');

    // Pie Chart
    new Chart(pieCanvas.getContext('2d'), {
        type: 'pie',
        data: {
            labels: ['Invested Capital', 'Reserve Cash'],
            datasets: [{
                data: [invested, reserve],
                backgroundColor: ['#0d6efd', '#ffc107'],
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { position: 'bottom' } }
        }
    });

    // Line Chart
    new Chart(lineCanvas.getContext('2d'), {
        type: 'line',
        data: {
            labels: lineLabels,
            datasets: [{
                label: 'Total Capital',
                data: lineData,
                borderColor: '#198754',
                backgroundColor: 'rgba(25,135,84,0.1)',
                fill: true,
                tension: 0.3,
                pointRadius: 3,
                pointBackgroundColor: '#198754'
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                x: { title: { display: true, text: 'Date' } },
                y: { title: { display: true, text: 'Total Capital' }, beginAtZero: false }
            }
        }
    });
}

// Close sidebar on menu click (for mobile)
document.querySelectorAll('.sidebar-menu .nav-link').forEach(function(link) {
    link.addEventListener('click', function() {
        if (window.innerWidth <= 767) {
            sidebar.classList.remove('open');
        }
    });
});


document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebar-overlay');

    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', function() {
            sidebar.classList.remove('open');
        });
    }
});