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
