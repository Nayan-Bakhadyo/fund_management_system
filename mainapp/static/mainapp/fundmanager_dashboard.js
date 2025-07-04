// Simple fuzzy search for email dropdown
document.addEventListener("DOMContentLoaded", function() {
    const emailSearch = document.getElementById("email_search");
    const emailSelect = document.getElementById("email_select");
    if (emailSearch && emailSelect) {
        emailSearch.addEventListener("input", function() {
            const value = emailSearch.value.toLowerCase();
            Array.from(emailSelect.options).forEach(function(option) {
                option.style.display = option.text.toLowerCase().includes(value) ? "" : "none";
            });
        });
    }
});

// Sidebar toggle functionality
document.addEventListener("DOMContentLoaded", function() {
    const sidebar = document.getElementById("sidebar");
    const toggleBtn = document.getElementById("sidebarToggle");
    const topbar = document.querySelector(".topbar");
    const mainContent = document.querySelector(".main-content");
    if (sidebar && toggleBtn && topbar && mainContent) {
        toggleBtn.addEventListener("click", function() {
            sidebar.classList.toggle("collapsed");
            topbar.classList.toggle("collapsed");
            mainContent.classList.toggle("collapsed");
        });
    }
});

// Add transaction form loading
document.addEventListener("DOMContentLoaded", function() {
    const addTransactionLink = document.getElementById("addTransactionLink");
    const viewTransactionsLink = document.getElementById("viewTransactionsLink");
    const dashboardContent = document.getElementById("dashboard-content");

    if (addTransactionLink && dashboardContent) {
        addTransactionLink.addEventListener("click", function(e) {
            e.preventDefault();
            fetch("/fundmanager/add_transaction_form/")
                .then(response => response.json())
                .then(data => {
                    dashboardContent.innerHTML = data.html;

                    // Attach handler only once, after form is loaded
                    function attachTransactionFormHandler() {
                        const form = document.querySelector(".transaction-form");
                        if (form) {
                            form.addEventListener("submit", function(e) {
                                e.preventDefault();
                                const formData = new FormData(form);
                                fetch(form.action, {
                                    method: "POST",
                                    headers: {
                                        "X-CSRFToken": csrftoken
                                    },
                                    body: formData
                                })
                                .then(response => response.json())
                                .then(data => {
                                    if (data.success) {
                                        alert("Transaction successful!");
                                        location.reload();
                                    } else {
                                        alert("Transaction failed: " + (data.error || "Unknown error"));
                                    }
                                });
                            }, { once: true }); // Attach only once!
                        }
                    }

                    // Call this after loading the form via AJAX
                    attachTransactionFormHandler();
                });
        });
    }

    if (viewTransactionsLink && dashboardContent) {
        viewTransactionsLink.addEventListener("click", function(e) {
            e.preventDefault();
            fetch("/fundmanager/view_transactions/")
                .then(response => response.json())
                .then(data => {
                    dashboardContent.innerHTML = data.html;

                    // Add filter form handler
                    const filterForm = document.getElementById("transaction-filter-form");
                    if (filterForm) {
                        filterForm.addEventListener("submit", function(ev) {
                            ev.preventDefault();
                            const email = document.getElementById("filter_email").value;
                            fetch(`/fundmanager/view_transactions/?filter_email=${encodeURIComponent(email)}`)
                                .then(response => response.json())
                                .then(data => {
                                    dashboardContent.innerHTML = data.html;
                                });
                        });
                    }
                });
        });
    }

    // CSRF for AJAX form submission
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');
});

// View user dashboard link functionality
document.addEventListener('DOMContentLoaded', function() {
    const viewUserDashboardLink = document.getElementById('viewUserDashboardLink');
    const dashboardContent = document.getElementById('dashboard-content');

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
                    renderNavChart();
                });
            }
        });
    }
});

// Add this function to render the NAV line chart (same as user dashboard)
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

// Example: Call renderNavChart after loading portfolio.html via AJAX
// (Place this after you inject the portfolio HTML into dashboardContent)
// if (typeof dashboardContent !== 'undefined') {
//     // If you load portfolio.html via AJAX, call renderNavChart() after injection
//     // Example:
//     // dashboardContent.innerHTML = html;
//     // renderNavChart();
// }

// Add investment form loading
$(document).on('click', '#addInvestmentLink', function(e) {
    e.preventDefault();
    $.get('/fundmanager/add_investment_modal/', function(html) {
        $('#addInvestmentModal').remove(); // Remove any existing modal
        $('body').append(html);            // Append the new modal
        var modal = new bootstrap.Modal(document.getElementById('addInvestmentModal'));
        modal.show();
    });
});

$(document).off('click', '#addInvestmentTransactionLink').on('click', '#addInvestmentTransactionLink', function(e) {
    e.preventDefault();
    $('#investmentTransaction').remove(); // Remove any existing modal
    $.get('/fundmanager/add_investment_transaction/', function(html) {
        $('body').append(html);
        var modal = new bootstrap.Modal(document.getElementById('investmentTransaction'));
        modal.show();
    });
});

// Handle form submission
$(document).on('submit', '#addInvestment', function(e) {
    e.preventDefault();
    $.ajax({
        url: '/fundmanager/add_investment_modal/',
        type: 'POST',
        data: $(this).serialize(),
        headers: {'X-Requested-With': 'XMLHttpRequest'},
        success: function(response) {
            if (response.success) {
                alert('Investment added successfully!');
                location.reload();
            } else {
                $('#addInvestmentAlert').html(
                    '<div class="alert alert-danger" role="alert">' + response.error + '</div>'
                );
            }
        },
        error: function(xhr, status, error) {
            $('#addInvestmentAlert').html(
                '<div class="alert alert-danger" role="alert">An error occurred: ' + error + '</div>'
            );
        }
    });
});

$(document).off('click', '#addInvestmentLink').on('click', '#addInvestmentLink', function(e) {
    e.preventDefault();
    $('#addInvestmentModal').remove(); // Remove any existing modal
    $.get('/fundmanager/add_investment_modal/', function(html) {
        $('body').append(html);
        var modal = new bootstrap.Modal(document.getElementById('addInvestmentModal'));
        modal.show();
    });
});


$(document).off('submit', '#addInvestmentForm').on('submit', '#addInvestmentForm', function(e) {
    e.preventDefault();
    $('#investmentAlert').empty();
    $.ajax({
        url: '/fundmanager/add_investment_modal/',
        type: 'POST',
        data: $(this).serialize(),
        headers: {'X-Requested-With': 'XMLHttpRequest'},
        success: function(response) {
            console.log(response); // Add this line
            if (response.success) {
                $('#investmentAlert').html(
                    '<div class="alert alert-success" role="alert">Investment added successfully!</div>'
                );
                $('#addInvestmentForm')[0].reset();
                setTimeout(function() {
                    var modal = bootstrap.Modal.getInstance(document.getElementById('addInvestmentModal'));
                    modal.hide();
                }, 1200);
            } else {
                $('#investmentAlert').html(
                    '<div class="alert alert-danger" role="alert">' + response.error + '</div>'
                );
            }
        },
        error: function() {
            $('#investmentAlert').html(
                '<div class="alert alert-danger" role="alert">An error occurred. Please try again.</div>'
            );
        }
    });
});

$(document).off('submit', '#investmentTransactionForm').on('submit', '#investmentTransactionForm', function(e) {
    e.preventDefault();
    $('#investmentTransactionAlert').empty();
    $.ajax({
        url: '/fundmanager/add_investment_transaction/', // <-- Make sure this is correct!
        type: 'POST',
        data: $(this).serialize(),
        headers: {'X-Requested-With': 'XMLHttpRequest'},
        success: function(response) {
            if (response.success) {
                $('#investmentTransactionAlert').html(
                    '<div class="alert alert-success" role="alert">Transaction successful!</div>'
                );
                $('#investmentTransactionForm')[0].reset();
                setTimeout(function() {
                    var modal = bootstrap.Modal.getInstance(document.getElementById('investmentTransaction'));
                    modal.hide();
                }, 1200);
            } else {
                $('#investmentTransactionAlert').html(
                    '<div class="alert alert-danger" role="alert">' + (response.error || 'Unknown error') + '</div>'
                );
            }
        },
        error: function(xhr, status, error) {
            $('#investmentTransactionAlert').html(
                '<div class="alert alert-danger" role="alert">An error occurred: ' + error + '</div>'
            );
        }
    });
});

// Open the modal
$(document).off('click', '#closeInvestmentLink').on('click', '#closeInvestmentLink', function(e) {
    e.preventDefault();
    $('#closeInvestmentModal').remove();
    $.get('/fundmanager/close_investment_modal/', function(html) {
        $('body').append(html);
        var modal = new bootstrap.Modal(document.getElementById('closeInvestmentModal'));
        modal.show();
    });
});

// Handle form submission
$(document).off('submit', '#closeInvestmentForm').on('submit', '#closeInvestmentForm', function(e) {
    e.preventDefault();
    $('#closeInvestmentAlert').empty();
    var $submitBtn = $(this).find('button[type="submit"]');
    $submitBtn.prop('disabled', true);

    $.ajax({
        url: '/fundmanager/close_investment_modal/',
        type: 'POST',
        data: $(this).serialize(),
        headers: {'X-Requested-With': 'XMLHttpRequest'},
        success: function(response) {
            if (response.success) {
                $('#closeInvestmentAlert').html(
                    '<div class="alert alert-success" role="alert">Investment closed successfully!</div>'
                );
                setTimeout(function() {
                    var modal = bootstrap.Modal.getInstance(document.getElementById('closeInvestmentModal'));
                    modal.hide();
                }, 1200);
            } else {
                $('#closeInvestmentAlert').html(
                    '<div class="alert alert-danger" role="alert">' + response.error + '</div>'
                );
            }
            $submitBtn.prop('disabled', false);
        },
        error: function() {
            $('#closeInvestmentAlert').html(
                '<div class="alert alert-danger" role="alert">An error occurred. Please try again.</div>'
            );
            $submitBtn.prop('disabled', false);
        }
    });
});