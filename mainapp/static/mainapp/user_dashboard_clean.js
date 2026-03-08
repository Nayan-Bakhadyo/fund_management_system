document.addEventListener('DOMContentLoaded', function() {
    // Declare global functions immediately to avoid timing issues
    window.handleSetupBankDetails = window.handleSetupBankDetails || function() {
        console.log('Global handleSetupBankDetails called');
        if (typeof window.goToBankDetails === 'function') {
            return window.goToBankDetails();
        }
        const bankDetailLink = document.getElementById('bank-detail-link');
        if (bankDetailLink) {
            bankDetailLink.click();
            return true;
        }
        alert('Please use the "Bank Details" option in the sidebar menu.');
        return false;
    };

    window.handleBackToDashboard = window.handleBackToDashboard || function() {
        console.log('Global handleBackToDashboard called');
        if (typeof window.goToMainDashboard === 'function') {
            return window.goToMainDashboard();
        }
        if (typeof window.showMainDashboard === 'function') {
            window.showMainDashboard();
            return true;
        }
        const portfolioLink = document.getElementById('portfolio-link');
        if (portfolioLink) {
            portfolioLink.click();
            return true;
        }
        window.location.href = '/user/dashboard/';
        return true;
    };

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

    // ===== COMPLETE SIDEBAR SYSTEM - REWRITTEN =====
    
    // Sidebar state management
    const sidebarState = {
        isOpen: false,
        isMobile: () => window.innerWidth <= 768,
        isDesktop: () => window.innerWidth > 768
    };

    // Sidebar functions
    function openSidebar() {
        console.log('Opening sidebar...');
        if (!sidebar) return;
        
        sidebarState.isOpen = true;
        sidebar.classList.add('open');
        document.body.classList.add('sidebar-open');
        
        // Mobile-specific handling
        if (sidebarState.isMobile()) {
            // Force positioning with JavaScript for mobile
            sidebar.style.transform = 'translateX(0)';
            sidebar.style.left = '0px';
            sidebar.style.position = 'fixed';
            sidebar.style.zIndex = '1050';
            
            // Show overlay
            if (sidebarOverlay) {
                sidebarOverlay.style.display = 'block';
                sidebarOverlay.style.opacity = '1';
            }
            
            // Prevent body scroll
            document.body.style.overflow = 'hidden';
        }
        
        console.log('Sidebar opened successfully');
    }
    
    function closeSidebar() {
        console.log('Closing sidebar...');
        if (!sidebar) return;
        
        sidebarState.isOpen = false;
        sidebar.classList.remove('open');
        document.body.classList.remove('sidebar-open');
        
        // Mobile-specific handling
        if (sidebarState.isMobile()) {
            // Force positioning for mobile
            sidebar.style.transform = 'translateX(-100%)';
            sidebar.style.left = '-280px';
            
            // Hide overlay
            if (sidebarOverlay) {
                sidebarOverlay.style.display = 'none';
                sidebarOverlay.style.opacity = '0';
            }
            
            // Restore body scroll
            document.body.style.overflow = '';
        }
        
        console.log('Sidebar closed successfully');
    }
    
    function toggleSidebar() {
        console.log('Toggling sidebar, current state:', sidebarState.isOpen);
        if (sidebarState.isOpen) {
            closeSidebar();
        } else {
            openSidebar();
        }
    }
    
    // Initialize sidebar positioning
    function initializeSidebar() {
        console.log('Initializing sidebar system...');
        if (!sidebar) {
            console.error('Sidebar element not found!');
            return;
        }
        
        if (sidebarState.isMobile()) {
            // Mobile: start hidden
            closeSidebar();
            sidebar.style.transition = 'transform 0.3s ease, left 0.3s ease';
        } else {
            // Desktop: always visible
            sidebar.style.transform = '';
            sidebar.style.left = '';
            sidebar.style.position = '';
            sidebar.style.zIndex = '';
            document.body.style.overflow = '';
            if (sidebarOverlay) {
                sidebarOverlay.style.display = 'none';
            }
        }
        
        console.log('Sidebar initialized for', sidebarState.isMobile() ? 'mobile' : 'desktop');
    }

    // Event Handlers
    
    // Toggle button click
    if (toggleBtn) {
        console.log('Setting up toggle button event listener');
        toggleBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('Toggle button clicked, window width:', window.innerWidth);
            toggleSidebar();
        });
    } else {
        console.warn('Toggle button not found!');
    }

    // Overlay click
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', function(e) {
            console.log('Overlay clicked');
            if (sidebarState.isMobile()) {
                closeSidebar();
            }
        });
    }

    // Click outside to close on mobile
    document.addEventListener('click', function(e) {
        if (sidebarState.isMobile() && sidebarState.isOpen) {
            // Check if click is outside sidebar and toggle button
            const isClickInsideSidebar = sidebar && sidebar.contains(e.target);
            const isClickOnToggle = toggleBtn && toggleBtn.contains(e.target);
            
            if (!isClickInsideSidebar && !isClickOnToggle) {
                console.log('Clicked outside sidebar on mobile');
                closeSidebar();
            }
        }
    });

    // Escape key to close
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && sidebarState.isOpen) {
            console.log('Escape key pressed');
            closeSidebar();
        }
    });

    // Window resize handler
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(function() {
            console.log('Window resized to:', window.innerWidth);
            initializeSidebar();
        }, 250);
    });

    // Initialize on page load
    initializeSidebar();

    // ===== END SIDEBAR SYSTEM =====

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

    // Make showMainDashboard globally accessible
    window.showMainDashboard = showMainDashboard;

    // Global navigation functions for use in dynamically loaded content
    window.navigateToBankDetails = function() {
        console.log('Navigating to bank details via global function');
        // Use fresh DOM query to ensure element is available
        const bankLink = document.getElementById('bank-detail-link');
        if (bankLink) {
            console.log('Bank detail link found, triggering click');
            bankLink.click();
            return true;
        } else {
            console.error('Bank detail link not found in DOM');
            return false;
        }
    };

    window.navigateToMainDashboard = function() {
        console.log('Navigating to main dashboard via global function');
        showMainDashboard();
        return true;
    };

    // Make navigation functions available immediately
    window.goToBankDetails = function() {
        console.log('goToBankDetails called');
        return window.navigateToBankDetails();
    };

    window.goToMainDashboard = function() {
        console.log('goToMainDashboard called');
        return window.navigateToMainDashboard();
    };

    // Debug function to check what's available globally
    window.debugGlobalFunctions = function() {
        console.log('Available global functions:');
        console.log('- showMainDashboard:', typeof window.showMainDashboard);
        console.log('- navigateToBankDetails:', typeof window.navigateToBankDetails);
        console.log('- navigateToMainDashboard:', typeof window.navigateToMainDashboard);
        console.log('- goToBankDetails:', typeof window.goToBankDetails);
        console.log('- goToMainDashboard:', typeof window.goToMainDashboard);
        console.log('Sidebar elements available:');
        console.log('- bankDetailLink:', !!document.getElementById('bank-detail-link'));
        console.log('- portfolioLink:', !!document.getElementById('portfolio-link'));
        console.log('- withdrawRequestLink:', !!document.getElementById('withdrawRequestMenu'));
    };

    // Test functions for manual testing
    window.testBankDetailsNavigation = function() {
        console.log('Testing bank details navigation...');
        return window.goToBankDetails();
    };

    window.testMainDashboardNavigation = function() {
        console.log('Testing main dashboard navigation...');
        return window.goToMainDashboard();
    };

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
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                             document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
            
            fetch('/user/withdraw_request/', {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
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
                console.log('Data keys:', Object.keys(data));
                if (data.html) {
                    console.log('HTML length:', data.html.length);
                    console.log('HTML preview:', data.html.substring(0, 500) + '...');
                    
                    // Check if HTML contains template variables
                    if (data.html.includes('available_units')) {
                        console.log('✓ HTML contains available_units');
                    } else {
                        console.log('✗ HTML missing available_units');
                    }
                    
                    if (data.html.includes('portfolio_value')) {
                        console.log('✓ HTML contains portfolio_value');
                    } else {
                        console.log('✗ HTML missing portfolio_value');
                    }
                    
                    withdrawRequestSection.innerHTML = data.html;
                    
                    // Debug the rendered content
                    setTimeout(() => {
                        const portfolioValueElement = withdrawRequestSection.querySelector('.balance-total');
                        if (portfolioValueElement) {
                            console.log('Portfolio value element content:', portfolioValueElement.textContent);
                        } else {
                            console.log('Portfolio value element not found in rendered content');
                        }
                        
                        const balanceItems = withdrawRequestSection.querySelectorAll('.balance-item');
                        console.log('Found', balanceItems.length, 'balance items');
                        balanceItems.forEach((item, index) => {
                            console.log(`Balance item ${index}:`, item.textContent.trim());
                        });
                    }, 100);
                    
                    attachWithdrawRequestFormHandler();
                } else {
                    console.error('No HTML in response data');
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
            const grad = ctx.createLinearGradient(0, 0, 0, ctx.canvas.height || 300);
            grad.addColorStop(0, 'rgba(16,185,129,0.35)');
            grad.addColorStop(0.6, 'rgba(59,130,246,0.10)');
            grad.addColorStop(1, 'rgba(16,185,129,0.0)');
            window.navChartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: navDates,
                    datasets: [{
                        label: 'Unit Cost (NAV)',
                        data: navUnitCosts,
                        borderColor: '#10b981',
                        backgroundColor: grad,
                        tension: 0.4,
                        fill: true,
                        pointRadius: 0,
                        pointHoverRadius: 6,
                        pointHoverBackgroundColor: '#10b981',
                        pointHoverBorderColor: '#fff',
                        pointHoverBorderWidth: 2,
                        borderWidth: 3
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: { intersect: false, mode: 'index' },
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: 'rgba(15,23,42,0.85)',
                            titleColor: '#94a3b8',
                            bodyColor: '#10b981',
                            borderColor: '#10b981',
                            borderWidth: 1,
                            cornerRadius: 8,
                            displayColors: false,
                            callbacks: {
                                title: function(ctx) { return ctx[0].label; },
                                label: function(ctx) { return 'NAV: NRs. ' + ctx.parsed.y.toFixed(2); }
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: { display: false },
                            border: { display: false },
                            ticks: { color: '#9ca3af', font: { size: 11 }, maxTicksLimit: 6 }
                        },
                        y: {
                            beginAtZero: false,
                            grid: { color: 'rgba(0,0,0,0.04)', drawBorder: false },
                            border: { display: false },
                            ticks: {
                                color: '#9ca3af',
                                font: { size: 11 },
                                callback: function(v) { return 'NRs. ' + v.toFixed(2); }
                            }
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
    console.log('Global functions registered:');
    console.log('- showMainDashboard:', typeof window.showMainDashboard);
    console.log('- navigateToBankDetails:', typeof window.navigateToBankDetails);
    console.log('- navigateToMainDashboard:', typeof window.navigateToMainDashboard);
    console.log('- goToBankDetails:', typeof window.goToBankDetails);
    console.log('- goToMainDashboard:', typeof window.goToMainDashboard);
    
    renderNavChart();
});
