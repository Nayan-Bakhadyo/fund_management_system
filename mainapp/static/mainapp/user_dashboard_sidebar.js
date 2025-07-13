document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded - Starting sidebar initialization');
    
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

    // DOM element references with detailed logging
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');
    const toggleBtn = document.getElementById('sidebarToggle');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    const portfolioLink = document.getElementById('portfolio-link');
    const transactionHistoryLink = document.getElementById('transaction-history');
    const bankDetailLink = document.getElementById('bank-detail-link');
    const withdrawRequestLink = document.getElementById('withdrawRequestMenu');
    const dynamicContent = document.getElementById('dynamic-content');
    const portfolioSection = document.getElementById('portfolio-section');
    const transactionSection = document.getElementById('transaction-history-section');
    const bankDetailSection = document.getElementById('bank-detail-section');
    const withdrawRequestSection = document.getElementById('withdraw-request-section');
    
    console.log('Elements found:', {
        sidebar: !!sidebar,
        mainContent: !!mainContent,
        toggleBtn: !!toggleBtn,
        sidebarOverlay: !!sidebarOverlay
    });
    
    if (!sidebar) {
        console.error('Sidebar element not found!');
        return;
    }
    
    if (!toggleBtn) {
        console.error('Toggle button not found!');
        return;
    }

    // Sidebar functionality
    function openSidebar() {
        if (sidebar) {
            console.log('Opening sidebar...');
            console.log('Sidebar before opening - left:', sidebar.style.left, 'classList:', sidebar.classList.toString());
            
            sidebar.classList.add('open');
            document.body.classList.add('sidebar-open');
            
            // Force position for mobile using JavaScript with !important
            if (window.innerWidth <= 768) {
                sidebar.style.setProperty('left', '0px', 'important');
                sidebar.style.setProperty('transition', 'left 0.3s ease', 'important');
                sidebar.style.setProperty('position', 'fixed', 'important');
                sidebar.style.setProperty('z-index', '1050', 'important');
                
                // Debug: Check if styles are applied
                setTimeout(() => {
                    console.log('Sidebar after opening - left:', sidebar.style.left, 'computed left:', window.getComputedStyle(sidebar).left);
                    console.log('Sidebar visibility:', window.getComputedStyle(sidebar).visibility);
                    console.log('Sidebar display:', window.getComputedStyle(sidebar).display);
                }, 100);
            }
            
            // Show overlay on mobile
            if (sidebarOverlay && window.innerWidth <= 768) {
                sidebarOverlay.style.display = 'block';
            }
        }
    }
    
    function closeSidebar() {
        if (sidebar) {
            console.log('Closing sidebar...');
            console.log('Sidebar before closing - left:', sidebar.style.left, 'classList:', sidebar.classList.toString());
            
            sidebar.classList.remove('open');
            document.body.classList.remove('sidebar-open');
            
            // Force position for mobile using JavaScript with !important
            if (window.innerWidth <= 768) {
                sidebar.style.setProperty('left', '-280px', 'important');
                sidebar.style.setProperty('transition', 'left 0.3s ease', 'important');
                
                // Debug: Check if styles are applied
                setTimeout(() => {
                    console.log('Sidebar after closing - left:', sidebar.style.left, 'computed left:', window.getComputedStyle(sidebar).left);
                }, 100);
            }
            
            // Hide overlay
            if (sidebarOverlay) {
                sidebarOverlay.style.display = 'none';
            }
        }
    }

    // Toggle sidebar on button click
    if (toggleBtn) {
        console.log('Adding event listener to toggle button');
        toggleBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('Sidebar toggle clicked, current state:', sidebar.classList.contains('open'));
            
            if (sidebar && sidebar.classList.contains('open')) {
                console.log('Closing sidebar');
                closeSidebar();
            } else {
                console.log('Opening sidebar');
                openSidebar();
            }
        });
    }

    // Sidebar overlay click
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', function() {
            console.log('Overlay clicked');
            closeSidebar();
        });
    }

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768 && 
            sidebar && sidebar.classList.contains('open') && 
            !sidebar.contains(e.target) && 
            toggleBtn && !toggleBtn.contains(e.target)) {
            console.log('Clicked outside sidebar on mobile');
            closeSidebar();
        }
    });

    // Close sidebar on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && sidebar && sidebar.classList.contains('open')) {
            console.log('Escape key pressed');
            closeSidebar();
        }
    });

    // Handle window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            // Desktop: show sidebar and clean up mobile states
            sidebar.style.setProperty('left', '0px', 'important');
            document.body.classList.remove('sidebar-open');
            if (sidebarOverlay) {
                sidebarOverlay.style.display = 'none';
            }
        } else {
            // Mobile: if sidebar is not open, ensure it's hidden
            if (!sidebar.classList.contains('open')) {
                sidebar.style.setProperty('left', '-280px', 'important');
            }
        }
    });

    // Initialize sidebar state based on screen size
    function initializeSidebar() {
        console.log('Initializing sidebar, window width:', window.innerWidth);
        if (window.innerWidth <= 768) {
            // Mobile: hide sidebar and ensure correct positioning
            sidebar.classList.remove('open');
            document.body.classList.remove('sidebar-open');
            sidebar.style.setProperty('left', '-280px', 'important');
            sidebar.style.setProperty('transition', 'left 0.3s ease', 'important');
            if (sidebarOverlay) {
                sidebarOverlay.style.display = 'none';
            }
        } else {
            // Desktop: show sidebar and reset positioning
            sidebar.style.setProperty('left', '0px', 'important');
            sidebar.style.setProperty('transition', 'left 0.3s ease', 'important');
            document.body.classList.remove('sidebar-open');
            if (sidebarOverlay) {
                sidebarOverlay.style.display = 'none';
            }
        }
    }

    // Initialize on page load
    initializeSidebar();

    // Section management functionality
    function hideAllSections() {
        if (portfolioSection) portfolioSection.style.display = 'none';
        if (transactionSection) transactionSection.style.display = 'none';
        if (bankDetailSection) bankDetailSection.style.display = 'none';
        if (withdrawRequestSection) withdrawRequestSection.style.display = 'none';
        
        // Clear dynamic content
        if (dynamicContent) {
            dynamicContent.innerHTML = '';
        }
    }

    function showSection(section) {
        hideAllSections();
        if (section) {
            section.style.display = 'block';
        }
    }

    function setActiveNavItem(activeLink) {
        // Remove active class from all nav links
        const navLinks = document.querySelectorAll('.sidebar .nav-link');
        navLinks.forEach(link => link.classList.remove('active'));
        
        // Add active class to current link
        if (activeLink) {
            activeLink.classList.add('active');
        }
    }

    // Navigation functionality
    window.showMainDashboard = function() {
        console.log('Showing main dashboard');
        showSection(portfolioSection);
        setActiveNavItem(portfolioLink);
        
        // Close sidebar on mobile after navigation
        if (window.innerWidth <= 768) {
            closeSidebar();
        }
    };

    window.goToMainDashboard = function() {
        return window.showMainDashboard();
    };

    // Portfolio link
    if (portfolioLink) {
        portfolioLink.addEventListener('click', function(e) {
            e.preventDefault();
            window.showMainDashboard();
        });
    }

    // Transaction History
    if (transactionHistoryLink) {
        transactionHistoryLink.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Loading transaction history');
            showSection(transactionSection);
            setActiveNavItem(transactionHistoryLink);
            
            // Close sidebar on mobile after navigation
            if (window.innerWidth <= 768) {
                closeSidebar();
            }
        });
    }

    // Bank Details functionality
    window.goToBankDetails = function() {
        console.log('Going to bank details');
        showSection(bankDetailSection);
        setActiveNavItem(bankDetailLink);
        
        // Close sidebar on mobile after navigation
        if (window.innerWidth <= 768) {
            closeSidebar();
        }
        return true;
    };

    if (bankDetailLink) {
        bankDetailLink.addEventListener('click', function(e) {
            e.preventDefault();
            window.goToBankDetails();
        });
    }

    // Withdraw Request functionality
    if (withdrawRequestLink) {
        withdrawRequestLink.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Loading withdraw request form');
            
            showSection(null); // Hide all sections
            setActiveNavItem(withdrawRequestLink);
            
            // Load withdraw request form via AJAX
            fetch('/user/withdraw_request/', {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.html && dynamicContent) {
                    dynamicContent.innerHTML = data.html;
                    
                    // Setup form handlers
                    setupWithdrawFormHandlers();
                }
            })
            .catch(error => {
                console.error('Error loading withdraw request:', error);
                if (dynamicContent) {
                    dynamicContent.innerHTML = '<div class="alert alert-danger">Error loading withdraw request form.</div>';
                }
            });
            
            // Close sidebar on mobile after navigation
            if (window.innerWidth <= 768) {
                closeSidebar();
            }
        });
    }

    // Initialize with main dashboard view
    window.showMainDashboard();

    // Withdraw form handlers
    function setupWithdrawFormHandlers() {
        const form = document.getElementById('withdraw-request-form');
        if (form) {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                const formData = new FormData(form);
                
                fetch('/user/withdraw_request/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Withdrawal request submitted successfully!');
                        // Reload the main dashboard
                        window.showMainDashboard();
                    } else if (data.error) {
                        alert('Error: ' + data.error);
                    } else if (data.redirect_to_bank_details) {
                        if (confirm('You need to set up your bank details first. Would you like to do that now?')) {
                            window.goToBankDetails();
                        }
                    }
                })
                .catch(error => {
                    console.error('Error submitting withdraw request:', error);
                    alert('Error submitting withdrawal request.');
                });
            });
        }
    }

    console.log('Sidebar initialization complete');
});
