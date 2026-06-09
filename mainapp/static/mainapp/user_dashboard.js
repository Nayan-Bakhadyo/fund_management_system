document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');
    const toggleBtn = document.getElementById('sidebarToggle');
    const portfolioLink = document.getElementById('portfolio-link');
    const transactionHistoryLink = document.getElementById('transaction-history');
    const bankDetailLink = document.getElementById('bank-detail-link');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    const viewUserDashboardLink = document.getElementById('view-user-dashboard');
    const dynamicContent = document.getElementById('dynamic-content');
    const portfolioSection = document.getElementById('portfolio-section');
    const transactionSection = document.getElementById('transaction-history-section');
    const bankDetailSection = document.getElementById('bank-detail-section');

    function openSidebar() {
        sidebar.classList.add('open');
        document.body.classList.add('sidebar-open');
    }
    
    function closeSidebar() {
        sidebar.classList.remove('open');
        document.body.classList.remove('sidebar-open');
    }

    // Toggle sidebar on button click
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            if (sidebar.classList.contains('open')) {
                closeSidebar();
            } else {
                openSidebar();
            }
        });
    }

    // Enhanced sidebar functionality for modern UI
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', function() {
            closeSidebar();
        });
    }

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768 && 
            sidebar.classList.contains('open') && 
            !sidebar.contains(e.target) && 
            toggleBtn && !toggleBtn.contains(e.target)) {
            closeSidebar();
        }
    });

    // Close sidebar on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && sidebar.classList.contains('open')) {
            closeSidebar();
        }
    });

    // Close sidebar when resizing to desktop
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

    // Helper function to hide all sections and show specific one
    function showSection(sectionToShow) {
        const allSections = document.querySelectorAll('.content-section');
        allSections.forEach(section => section.style.display = 'none');
        if (sectionToShow) {
            sectionToShow.style.display = 'block';
        }
    }

    // When the user clicks "My Portfolio"
    if (portfolioLink) {
        portfolioLink.addEventListener('click', function(e) {
            e.preventDefault();
            fetch('/user/portfolio/', { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
                .then(response => response.text())
                .then(html => {
                    portfolioSection.innerHTML = html;
                    showSection(portfolioSection);
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
                transactionSection.innerHTML = html;
                showSection(transactionSection);
            });
        });
    }

    if (bankDetailLink) {
        bankDetailLink.addEventListener('click', function(e) {
            e.preventDefault();
            fetch('/user/bank_detail/', { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
                .then(response => response.json())
                .then(data => {
                    bankDetailSection.innerHTML = data.html;
                    showSection(bankDetailSection);
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
                showSection(null); // Hide all sections to show the main dashboard
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

    // Action card click handlers
    document.addEventListener('click', function(e) {
        const actionCard = e.target.closest('.action-card');
        if (actionCard) {
            const action = actionCard.dataset.action;
            handleActionCardClick(action);
        }
    });

    function handleActionCardClick(action) {
        switch(action) {
            case 'upload-transaction':
                const uploadModal = new bootstrap.Modal(document.getElementById('uploadTransactionModal'));
                uploadModal.show();
                break;
            case 'bank-details':
                window.location.href = '/user/firm_bank_detail/';
                break;
            case 'payment-settings':
                const paymentModal = new bootstrap.Modal(document.getElementById('modifyPaymentDetailModal'));
                paymentModal.show();
                break;
            case 'firm-portfolio':
                const firmModal = new bootstrap.Modal(document.getElementById('firmStatusModal'));
                firmModal.show();
                // Load firm status data
                loadFirmStatus();
                break;
        }
    }

    function loadFirmStatus() {
        const modalBody = document.getElementById('firm-status-dashboard');
        modalBody.innerHTML = '<div class="text-center py-5"><div class="spinner-border text-primary" role="status"></div></div>';
        
        fetch('/user/firm_status/', {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(response => response.text())
        .then(html => {
            modalBody.innerHTML = html;
        })
        .catch(error => {
            modalBody.innerHTML = '<div class="alert alert-danger">Failed to load firm status.</div>';
        });
    }

}); // End of main DOMContentLoaded block

    // Modal menu items event handlers
    const uploadTransactionMenu = document.getElementById('uploadTransactionMenu');
    const viewBankDetailMenu = document.getElementById('viewBankDetailMenu');
    const modifyPaymentDetailMenu = document.getElementById('modifyPaymentDetailMenu');
    const firmStatusMenu = document.getElementById('firmStatusMenu');

    if (uploadTransactionMenu) {
        uploadTransactionMenu.addEventListener('click', function(e) {
            e.preventDefault();
            const uploadModal = new bootstrap.Modal(document.getElementById('uploadTransactionModal'));
            uploadModal.show();
            if (window.innerWidth <= 767) closeSidebar();
        });
    }

    if (viewBankDetailMenu) {
        viewBankDetailMenu.addEventListener('click', function(e) {
            e.preventDefault();
            window.location.href = '/user/firm_bank_detail/';
        });
    }

    if (modifyPaymentDetailMenu) {
        modifyPaymentDetailMenu.addEventListener('click', function(e) {
            e.preventDefault();
            const paymentModal = new bootstrap.Modal(document.getElementById('modifyPaymentDetailModal'));
            paymentModal.show();
            if (window.innerWidth <= 767) closeSidebar();
        });
    }

    if (firmStatusMenu) {
        firmStatusMenu.addEventListener('click', function(e) {
            e.preventDefault();
            const firmModal = new bootstrap.Modal(document.getElementById('firmStatusModal'));
            firmModal.show();
            loadFirmStatus();
            if (window.innerWidth <= 767) closeSidebar();
        });
    }

    // Close sidebar on menu click for content sections (mobile)
    if (portfolioLink) {
        portfolioLink.addEventListener('click', function() {
            if (window.innerWidth <= 767) closeSidebar();
        });
    }
    if (transactionHistoryLink) {
        transactionHistoryLink.addEventListener('click', function() {
            if (window.innerWidth <= 767) closeSidebar();
        });
    }
    if (bankDetailLink) {
        bankDetailLink.addEventListener('click', function() {
            if (window.innerWidth <= 767) closeSidebar();
        });
    }
});

// Transaction upload form handler
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
    }
  });

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

// Close sidebar on menu click (for mobile) - outside DOMContentLoaded
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('nav-link') && window.innerWidth <= 767) {
        const sidebar = document.getElementById('sidebar');
        if (sidebar) {
            sidebar.classList.remove('open');
        }
    }
});

// Action Card Event Handlers for new modern UI - outside DOMContentLoaded  
document.addEventListener('click', function(e) {
    const actionCard = e.target.closest('.action-card');
    if (actionCard) {
        const action = actionCard.dataset.action;
        handleActionCardClick(action);
    }
});

function handleActionCardClick(action) {
    switch(action) {
        case 'upload-transaction':
            const uploadModal = new bootstrap.Modal(document.getElementById('uploadTransactionModal'));
            uploadModal.show();
            break;
        case 'bank-details':
            window.location.href = '/user/firm_bank_detail/';
            break;
        case 'payment-settings':
            const paymentModal = new bootstrap.Modal(document.getElementById('modifyPaymentDetailModal'));
            paymentModal.show();
            break;
        case 'firm-portfolio':
            const firmModal = new bootstrap.Modal(document.getElementById('firmStatusModal'));
            firmModal.show();
            // Load firm status data
            loadFirmStatusExternal();
            break;
    }
}

function loadFirmStatusExternal() {
    const modalBody = document.getElementById('firm-status-dashboard');
    modalBody.innerHTML = '<div class="text-center py-5"><div class="spinner-border text-primary" role="status"></div></div>';
    
    fetch('/user/firm_status/', {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => response.text())
    .then(html => {
        modalBody.innerHTML = html;
    })
    .catch(error => {
        modalBody.innerHTML = '<div class="alert alert-danger">Failed to load firm status.</div>';
    });
}
