document.addEventListener('DOMContentLoaded', function() {
    // DOM element references
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');
    const toggleBtn = document.getElementById('sidebarToggle');
    const portfolioLink = document.getElementById('portfolio-link');
    const transactionHistoryLink = document.getElementById('transaction-history');
    const bankDetailLink = document.getElementById('bank-detail-link');
    const withdrawRequestLink = document.getElementById('withdrawRequestMenu');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    const dynamicContent = document.getElementById('dynamic-content');
    const portfolioSection = document.getElementById('portfolio-section');
    const transactionSection = document.getElementById('transaction-history-section');
    const bankDetailSection = document.getElementById('bank-detail-section');
    const withdrawRequestSection = document.getElementById('withdraw-request-section');

    // Sidebar functionality
    function openSidebar() {
        if (sidebar) {
            sidebar.classList.add('open');
            document.body.classList.add('sidebar-open');
        }
    }
    
    function closeSidebar() {
        if (sidebar) {
            sidebar.classList.remove('open');
            document.body.classList.remove('sidebar-open');
        }
    }

    // Toggle sidebar on button click
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            if (sidebar && sidebar.classList.contains('open')) {
                closeSidebar();
            } else {
                openSidebar();
            }
        });
    }

    // Sidebar overlay click
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', function() {
            closeSidebar();
        });
    }

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768 && 
            sidebar && sidebar.classList.contains('open') && 
            !sidebar.contains(e.target) && 
            toggleBtn && !toggleBtn.contains(e.target)) {
            closeSidebar();
        }
    });

    // Close sidebar on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && sidebar && sidebar.classList.contains('open')) {
            closeSidebar();
        }
    });

    // Close sidebar when resizing to desktop
    window.addEventListener('resize', function() {
        if (window.innerWidth > 767) {
            closeSidebar();
        }
    });

    // Helper function to hide all sections and show specific one
    function showSection(sectionToShow) {
        console.log('showSection called with:', sectionToShow);
        
        // Hide the main dashboard content wrapper (contains NAV chart)
        const mainDashboardContent = document.getElementById('main-dashboard-content');
        if (mainDashboardContent) {
            mainDashboardContent.style.display = 'none';
        }
        
        // Hide all content sections
        const allSections = document.querySelectorAll('.content-section');
        allSections.forEach(section => section.style.display = 'none');
        
        if (sectionToShow) {
            sectionToShow.style.display = 'block';
        } else {
            // Show the main dashboard content again (this includes NAV chart)
            if (mainDashboardContent) {
                mainDashboardContent.style.display = 'block';
            }
        }
    }

    // Show main dashboard content (including NAV chart)
    function showMainDashboard() {
        console.log('Showing main dashboard');
        showSection(null); // null means show main dashboard
    }

    // Portfolio link handler - Show main dashboard content
    if (portfolioLink) {
        portfolioLink.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Portfolio link clicked - showing main dashboard');
            showMainDashboard(); // Show main dashboard content with NAV chart
            // Close sidebar on mobile
            if (window.innerWidth <= 767) closeSidebar();
        });
    }

    // Transaction history link handler
    if (transactionHistoryLink) {
        transactionHistoryLink.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Transaction history link clicked');
            
            if (!transactionSection) {
                console.error('Transaction section not found');
                return;
            }
            
            transactionSection.innerHTML = '<div class="text-center py-5"><div class="spinner-border text-primary" role="status"></div><p class="mt-2">Loading transactions...</p></div>';
            showSection(transactionSection);
            
            fetch('/user/transactions/', {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => {
                console.log('Transactions response status:', response.status);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.text();
            })
            .then(html => {
                console.log('Transactions HTML received, length:', html.length);
                transactionSection.innerHTML = html;
            })
            .catch(error => {
                console.error('Error loading transactions:', error);
                transactionSection.innerHTML = '<div class="alert alert-danger">Failed to load transaction data. Please try again.</div>';
            });
            
            // Close sidebar on mobile
            if (window.innerWidth <= 767) closeSidebar();
        });
    }

    // Bank detail link handler
    if (bankDetailLink) {
        bankDetailLink.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Bank detail link clicked');
            
            if (!bankDetailSection) {
                console.error('Bank detail section not found');
                return;
            }
            
            bankDetailSection.innerHTML = '<div class="text-center py-5"><div class="spinner-border text-primary" role="status"></div><p class="mt-2">Loading bank details...</p></div>';
            showSection(bankDetailSection);
            
            fetch('/user/bank_detail/', { 
                headers: { 'X-Requested-With': 'XMLHttpRequest' } 
            })
            .then(response => {
                console.log('Bank detail response status:', response.status);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Bank detail data received:', data);
                if (data.html) {
                    bankDetailSection.innerHTML = data.html;
                    attachBankDetailFormHandler();
                } else {
                    bankDetailSection.innerHTML = '<div class="alert alert-warning">No bank detail form available.</div>';
                }
            })
            .catch(error => {
                console.error('Error loading bank details:', error);
                bankDetailSection.innerHTML = '<div class="alert alert-danger">Failed to load bank detail form. Please try again.</div>';
            });
            
            // Close sidebar on mobile
            if (window.innerWidth <= 767) closeSidebar();
        });
    }

    // Withdraw Request link handler
    if (withdrawRequestLink) {
        withdrawRequestLink.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Withdraw request link clicked');
            
            if (!withdrawRequestSection) {
                console.error('Withdraw request section not found');
                return;
            }
            
            showSection(withdrawRequestSection);
            
            // Show loading state
            withdrawRequestSection.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';
            
            // Fetch withdraw request form
            fetch('/user/withdraw_request/', {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                console.log('Withdraw request response status:', response.status);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Withdraw request data received:', data);
                if (data.html) {
                    withdrawRequestSection.innerHTML = data.html;
                    attachWithdrawRequestFormHandler();
                } else {
                    withdrawRequestSection.innerHTML = '<div class="alert alert-warning">No withdraw request form available.</div>';
                }
            })
            .catch(error => {
                console.error('Error loading withdraw request:', error);
                withdrawRequestSection.innerHTML = '<div class="alert alert-danger">Failed to load withdraw request form. Please try again.</div>';
            });
            
            // Close sidebar on mobile
            if (window.innerWidth <= 767) closeSidebar();
        });
    }

    // Bank detail form handler
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
                    if (messageDiv) {
                        if (data.success) {
                            messageDiv.textContent = data.message;
                            messageDiv.className = 'alert alert-success mt-2';
                        } else {
                            messageDiv.textContent = 'Failed to save bank details.';
                            messageDiv.className = 'alert alert-danger mt-2';
                        }
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

    // Withdraw request form handler
    function attachWithdrawRequestFormHandler() {
        const form = document.getElementById('withdraw-request-form');
        if (!form) return;

        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            
            // Show loading state
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Processing...';
            
            fetch('/user/withdraw_request/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    withdrawRequestSection.innerHTML = `
                        <div class="alert alert-success">
                            <h4>Withdrawal Request Submitted Successfully!</h4>
                            <p>Your withdrawal request ID: <strong>${data.withdrawal_id}</strong></p>
                            <p>Amount: <strong>NRs. ${data.requested_amount}</strong></p>
                            <p>Status: <strong>Pending Review</strong></p>
                            <p>You will be notified once the fund manager reviews your request.</p>
                        </div>
                    `;
                } else if (data.html) {
                    // Form has errors, reload with error messages
                    withdrawRequestSection.innerHTML = data.html;
                    attachWithdrawRequestFormHandler(); // Re-attach handler
                } else {
                    withdrawRequestSection.innerHTML = '<div class="alert alert-danger">An error occurred. Please try again.</div>';
                }
            })
            .catch(error => {
                console.error('Error submitting withdraw request:', error);
                withdrawRequestSection.innerHTML = '<div class="alert alert-danger">Failed to submit withdraw request. Please try again.</div>';
            })
            .finally(() => {
                // Reset button
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            });
        });
    }

    // Modal menu items event handlers
    const uploadTransactionMenu = document.getElementById('uploadTransactionMenu');
    const viewBankDetailMenu = document.getElementById('viewBankDetailMenu');
    const modifyPaymentDetailMenu = document.getElementById('modifyPaymentDetailMenu');
    const firmStatusMenu = document.getElementById('firmStatusMenu');

    // Upload transaction modal
    if (uploadTransactionMenu) {
        uploadTransactionMenu.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Upload transaction menu clicked');
            const uploadModal = new bootstrap.Modal(document.getElementById('uploadTransactionModal'));
            uploadModal.show();
            if (window.innerWidth <= 767) closeSidebar();
        });
    }

    // View bank detail modal
    if (viewBankDetailMenu) {
        viewBankDetailMenu.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('View bank detail menu clicked');
            const bankModal = new bootstrap.Modal(document.getElementById('bankDetailModal'));
            bankModal.show();
            if (window.innerWidth <= 767) closeSidebar();
        });
    }

    // Modify payment detail modal
    if (modifyPaymentDetailMenu) {
        modifyPaymentDetailMenu.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Modify payment detail menu clicked');
            
            // Fetch current payment details first
            fetch('/user/payment_detail/', {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.json())
            .then(data => {
                // Set values
                const amountInput = document.getElementById('recurring_payment_amount');
                const dateInput = document.getElementById('payment_date');
                const messageDiv = document.getElementById('modify-payment-detail-message');
                
                if (amountInput) amountInput.value = data.recurring_payment_amount || '';
                if (dateInput) dateInput.value = data.payment_date || '';
                if (messageDiv) messageDiv.innerHTML = '';
                
                const paymentModal = new bootstrap.Modal(document.getElementById('modifyPaymentDetailModal'));
                paymentModal.show();
            })
            .catch(error => {
                console.error('Error loading payment details:', error);
                const paymentModal = new bootstrap.Modal(document.getElementById('modifyPaymentDetailModal'));
                paymentModal.show();
            });
            
            if (window.innerWidth <= 767) closeSidebar();
        });
    }

    // Firm status modal
    if (firmStatusMenu) {
        firmStatusMenu.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Firm status menu clicked');
            const firmModal = new bootstrap.Modal(document.getElementById('firmStatusModal'));
            firmModal.show();
            loadFirmStatus();
            if (window.innerWidth <= 767) closeSidebar();
        });
    }

    // Load firm status function
    function loadFirmStatus() {
        const modalBody = document.getElementById('firm-status-dashboard');
        if (modalBody) {
            modalBody.innerHTML = '<div class="text-center py-5"><div class="spinner-border text-primary" role="status"></div></div>';
            
            fetch('/firm_status_dashboard/', {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.html) {
                    modalBody.innerHTML = data.html;
                    // Initialize charts after content is loaded
                    setTimeout(() => {
                        initializeFirmStatusCharts();
                    }, 100);
                } else {
                    throw new Error('No HTML content received');
                }
            })
            .catch(error => {
                console.error('Error loading firm status:', error);
                modalBody.innerHTML = '<div class="alert alert-danger">Failed to load firm status. Please try again.</div>';
            });
        }
    }

    // NAV Chart rendering function
    function renderNavChart() {
        const canvas = document.getElementById('navPerformanceChart');
        if (!canvas) return;
        
        try {
            const navDates = JSON.parse(canvas.dataset.dates || '[]');
            const navUnitCosts = JSON.parse(canvas.dataset.costs || '[]');

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
        } catch (error) {
            console.error('Error rendering NAV chart:', error);
        }
    }

    // Initialize firm status charts
    function initializeFirmStatusCharts() {
        try {
            // Pie Chart
            const pieCanvas = document.getElementById('capitalPieChart');
            if (pieCanvas) {
                const invested = parseFloat(pieCanvas.dataset.invested) || 0;
                const reserve = parseFloat(pieCanvas.dataset.reserve) || 0;
                
                const pieCtx = pieCanvas.getContext('2d');
                new Chart(pieCtx, {
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
                        maintainAspectRatio: false,
                        plugins: { legend: { position: 'bottom' } }
                    }
                });
            }

            // Line Chart
            const lineCanvas = document.getElementById('capitalLineChart');
            if (lineCanvas) {
                const labels = JSON.parse(lineCanvas.dataset.labels || '[]');
                const data = JSON.parse(lineCanvas.dataset.data || '[]');
                
                const lineCtx = lineCanvas.getContext('2d');
                new Chart(lineCtx, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Total Capital',
                            data: data,
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
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                            x: { title: { display: true, text: 'Date' } },
                            y: { title: { display: true, text: 'Total Capital' }, beginAtZero: false }
                        }
                    }
                });
            }
        } catch (error) {
            console.error('Error initializing firm status charts:', error);
        }
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
        console.log('Action card clicked:', action);
        switch(action) {
            case 'upload-transaction':
                if (uploadTransactionMenu) {
                    uploadTransactionMenu.click();
                }
                break;
            case 'bank-details':
                if (viewBankDetailMenu) {
                    viewBankDetailMenu.click();
                }
                break;
            case 'payment-settings':
                if (modifyPaymentDetailMenu) {
                    modifyPaymentDetailMenu.click();
                }
                break;
            case 'firm-portfolio':
                if (firmStatusMenu) {
                    firmStatusMenu.click();
                }
                break;
        }
    }

    // Form handlers
    // Transaction upload form
    const transactionForm = document.getElementById('transaction-upload-form');
    const transactionMessageDiv = document.getElementById('transaction-upload-message');
    
    if (transactionForm) {
        transactionForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(transactionForm);

            fetch('/user/upload_transaction/', {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (transactionMessageDiv) {
                    if (data.success) {
                        transactionMessageDiv.innerHTML = '<div class="alert alert-success">Upload successful!</div>';
                        transactionForm.reset();
                    } else {
                        transactionMessageDiv.innerHTML = '<div class="alert alert-danger">' + (data.error || 'Upload failed.') + '</div>';
                    }
                }
            })
            .catch(error => {
                console.error('Upload error:', error);
                if (transactionMessageDiv) {
                    transactionMessageDiv.innerHTML = '<div class="alert alert-danger">An error occurred. Please try again.</div>';
                }
            });
        });
    }

    // Payment detail form
    const paymentForm = document.getElementById('modify-payment-detail-form');
    
    if (paymentForm) {
        paymentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(paymentForm);
            
            fetch('/user/payment_detail/', {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                const msgDiv = document.getElementById('modify-payment-detail-message');
                if (msgDiv) {
                    if (data.success) {
                        msgDiv.innerHTML = '<div class="alert alert-success">Payment detail updated!</div>';
                    } else {
                        msgDiv.innerHTML = '<div class="alert alert-danger">' + (data.error || 'Update failed.') + '</div>';
                    }
                }
            })
            .catch(error => {
                console.error('Payment update error:', error);
            });
        });
    }

    // Copy to clipboard functionality for bank details
    document.querySelectorAll('.copy-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const targetId = btn.getAttribute('data-copy');
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                const text = targetElement.textContent;
                navigator.clipboard.writeText(text).then(function() {
                    btn.textContent = 'Copied!';
                    setTimeout(() => { btn.textContent = 'Copy'; }, 1200);
                }).catch(function() {
                    // Fallback for older browsers
                    const textArea = document.createElement('textarea');
                    textArea.value = text;
                    document.body.appendChild(textArea);
                    textArea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textArea);
                    btn.textContent = 'Copied!';
                    setTimeout(() => { btn.textContent = 'Copy'; }, 1200);
                });
            }
        });
    });

    // Initialize
    console.log('Dashboard JavaScript initialized');
    renderNavChart();
});
