// Nigerian E-Learning Platform Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Feather Icons
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Form validation and UX improvements
    initializeFormValidation();
    
    // File upload enhancements
    initializeFileUploads();
    
    // Currency formatting
    initializeCurrencyFormatting();
    
    // Quiz functionality
    initializeQuizFeatures();
    
    // Search and filter functionality
    initializeSearch();
});

// Form Validation and UX
function initializeFormValidation() {
    // Add Bootstrap validation classes
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Password strength indicator
    var passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            checkPasswordStrength(this);
        });
    });
    
    // Real-time form feedback
    var inputs = document.querySelectorAll('.form-control');
    inputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            validateField(this);
        });
    });
}

// File Upload Enhancements
function initializeFileUploads() {
    var fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            handleFileSelection(this);
        });
        
        // Add drag and drop functionality
        var container = input.closest('.mb-3');
        if (container) {
            container.addEventListener('dragover', function(e) {
                e.preventDefault();
                this.classList.add('dragover');
            });
            
            container.addEventListener('dragleave', function(e) {
                e.preventDefault();
                this.classList.remove('dragover');
            });
            
            container.addEventListener('drop', function(e) {
                e.preventDefault();
                this.classList.remove('dragover');
                var files = e.dataTransfer.files;
                if (files.length > 0) {
                    input.files = files;
                    handleFileSelection(input);
                }
            });
        }
    });
}

// Currency Formatting
function initializeCurrencyFormatting() {
    // Format all currency amounts
    var currencyElements = document.querySelectorAll('.currency, .price-display');
    currencyElements.forEach(function(element) {
        var amount = parseFloat(element.textContent.replace(/[₦,]/g, ''));
        if (!isNaN(amount)) {
            element.textContent = formatCurrency(amount);
        }
    });
    
    // Format currency inputs on blur
    var currencyInputs = document.querySelectorAll('input[data-currency]');
    currencyInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            var value = parseFloat(this.value);
            if (!isNaN(value)) {
                this.value = value.toFixed(2);
            }
        });
    });
}

// Quiz Features
function initializeQuizFeatures() {
    // Auto-save quiz progress
    var quizForm = document.getElementById('quizForm');
    if (quizForm) {
        var inputs = quizForm.querySelectorAll('input[type="radio"]');
        inputs.forEach(function(input) {
            input.addEventListener('change', function() {
                saveQuizProgress();
            });
        });
        
        // Load saved progress
        loadQuizProgress();
    }
    
    // Quiz timer warnings
    var timerElement = document.getElementById('timer');
    if (timerElement) {
        // Timer is handled in the quiz template
        // This is for additional timer features
        setInterval(function() {
            var timeText = document.getElementById('time-remaining').textContent;
            var parts = timeText.split(':');
            var minutes = parseInt(parts[0]);
            var seconds = parseInt(parts[1]);
            var totalSeconds = minutes * 60 + seconds;
            
            if (totalSeconds <= 60 && totalSeconds > 0) {
                showTimerWarning();
            }
        }, 1000);
    }
}

// Search and Filter
function initializeSearch() {
    var searchInput = document.getElementById('courseSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            var query = this.value.toLowerCase();
            var courseCards = document.querySelectorAll('.course-card');
            
            courseCards.forEach(function(card) {
                var title = card.querySelector('.card-title').textContent.toLowerCase();
                var description = card.querySelector('.card-text').textContent.toLowerCase();
                
                if (title.includes(query) || description.includes(query)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
}

// Utility Functions
function formatCurrency(amount) {
    return '₦' + amount.toLocaleString('en-NG', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

function checkPasswordStrength(input) {
    var password = input.value;
    var strength = 0;
    
    if (password.length >= 8) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^A-Za-z0-9]/.test(password)) strength++;
    
    var strengthText = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
    var strengthColors = ['danger', 'warning', 'info', 'primary', 'success'];
    
    var feedback = input.parentNode.querySelector('.password-strength');
    if (!feedback) {
        feedback = document.createElement('div');
        feedback.className = 'password-strength small mt-1';
        input.parentNode.appendChild(feedback);
    }
    
    if (password.length > 0) {
        feedback.innerHTML = '<span class="text-' + strengthColors[strength] + '">Password strength: ' + strengthText[strength] + '</span>';
    } else {
        feedback.innerHTML = '';
    }
}

function validateField(input) {
    var isValid = input.checkValidity();
    var feedback = input.parentNode.querySelector('.invalid-feedback');
    
    if (!isValid && !feedback) {
        feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        feedback.textContent = input.validationMessage;
        input.parentNode.appendChild(feedback);
    }
    
    input.classList.toggle('is-valid', isValid);
    input.classList.toggle('is-invalid', !isValid);
}

function handleFileSelection(input) {
    var file = input.files[0];
    if (file) {
        var fileInfo = input.parentNode.querySelector('.file-info');
        if (!fileInfo) {
            fileInfo = document.createElement('div');
            fileInfo.className = 'file-info small text-muted mt-1';
            input.parentNode.appendChild(fileInfo);
        }
        
        var fileSize = (file.size / 1024 / 1024).toFixed(2);
        fileInfo.innerHTML = '<i data-feather="file"></i> ' + file.name + ' (' + fileSize + ' MB)';
        
        // Re-initialize feather icons for the new element
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
        
        // Validate file size (16MB limit)
        if (file.size > 16 * 1024 * 1024) {
            input.setCustomValidity('File size must be less than 16MB');
            fileInfo.innerHTML += ' <span class="text-danger">File too large!</span>';
        } else {
            input.setCustomValidity('');
        }
    }
}

function saveQuizProgress() {
    var quizForm = document.getElementById('quizForm');
    if (quizForm) {
        var formData = new FormData(quizForm);
        var progress = {};
        
        for (var pair of formData.entries()) {
            if (pair[0].startsWith('question_')) {
                progress[pair[0]] = pair[1];
            }
        }
        
        localStorage.setItem('quiz_progress_' + window.location.pathname, JSON.stringify(progress));
    }
}

function loadQuizProgress() {
    var saved = localStorage.getItem('quiz_progress_' + window.location.pathname);
    if (saved) {
        var progress = JSON.parse(saved);
        
        for (var questionName in progress) {
            var input = document.querySelector('input[name="' + questionName + '"][value="' + progress[questionName] + '"]');
            if (input) {
                input.checked = true;
            }
        }
    }
}

function showTimerWarning() {
    var warning = document.getElementById('timer-warning');
    if (!warning) {
        warning = document.createElement('div');
        warning.id = 'timer-warning';
        warning.className = 'alert alert-warning alert-dismissible fade show position-fixed';
        warning.style.top = '20px';
        warning.style.right = '20px';
        warning.style.zIndex = '9999';
        warning.innerHTML = `
            <strong>Time Warning!</strong> Less than 1 minute remaining.
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(warning);
    }
}

// Wallet Balance Update
function updateWalletBalance() {
    fetch('/api/wallet/balance')
        .then(response => response.json())
        .then(data => {
            var balanceElements = document.querySelectorAll('.wallet-balance');
            balanceElements.forEach(function(element) {
                element.textContent = formatCurrency(data.balance);
            });
        })
        .catch(error => {
            console.error('Error updating wallet balance:', error);
        });
}

// Notification System
function showNotification(message, type = 'info') {
    var notification = document.createElement('div');
    notification.className = 'alert alert-' + type + ' alert-dismissible fade show position-fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.innerHTML = message + '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>';
    
    document.body.appendChild(notification);
    
    setTimeout(function() {
        notification.remove();
    }, 5000);
}

// Confirm dialogs for dangerous actions
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('confirm-action')) {
        var message = e.target.getAttribute('data-confirm') || 'Are you sure?';
        if (!confirm(message)) {
            e.preventDefault();
        }
    }
});

// Auto-refresh for admin payment management
if (window.location.pathname.includes('/payments/manage')) {
    setInterval(function() {
        location.reload();
    }, 30000); // Refresh every 30 seconds
}

// Course search functionality
function filterCourses(searchTerm) {
    var courseCards = document.querySelectorAll('.course-card');
    searchTerm = searchTerm.toLowerCase();
    
    courseCards.forEach(function(card) {
        var title = card.querySelector('.card-title').textContent.toLowerCase();
        var description = card.querySelector('.card-text').textContent.toLowerCase();
        var instructor = card.querySelector('small').textContent.toLowerCase();
        
        var matches = title.includes(searchTerm) || 
                     description.includes(searchTerm) || 
                     instructor.includes(searchTerm);
        
        card.style.display = matches ? 'block' : 'none';
    });
}

// Export functions for global use
window.ELearning = {
    formatCurrency: formatCurrency,
    showNotification: showNotification,
    updateWalletBalance: updateWalletBalance,
    filterCourses: filterCourses
};
