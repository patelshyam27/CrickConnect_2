// Cricket Community - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeBootstrapComponents();
    initializeFormValidation();
    initializeSearchFilters();
    initializePlayerCards();
    initializeWhatsAppIntegration();
    initializeModalHandlers();
    initializeImageLazyLoading();
    initializeScrollAnimations();
});

// Initialize Bootstrap components
function initializeBootstrapComponents() {
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

    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
}

// Form validation and enhancement
function initializeFormValidation() {
    // Add custom validation styles
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

    // Phone number formatting
    var phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(function(input) {
        input.addEventListener('input', function(e) {
            var value = e.target.value.replace(/\D/g, '');
            if (value.length > 0 && !value.startsWith('91')) {
                // Auto-add India country code if not present
                if (value.length === 10) {
                    e.target.value = '91' + value;
                }
            }
        });
    });

    // Real-time form feedback
    var inputs = document.querySelectorAll('.form-control, .form-select');
    inputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            validateField(input);
        });
    });
}

// Field validation helper
function validateField(field) {
    var isValid = field.checkValidity();
    var feedback = field.parentNode.querySelector('.invalid-feedback');
    
    if (!isValid) {
        field.classList.add('is-invalid');
        field.classList.remove('is-valid');
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            field.parentNode.appendChild(feedback);
        }
        feedback.textContent = field.validationMessage;
    } else {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
        if (feedback) {
            feedback.remove();
        }
    }
}

// Search filters enhancement
function initializeSearchFilters() {
    var searchForm = document.querySelector('#searchForm');
    if (!searchForm) return;

    var filterInputs = searchForm.querySelectorAll('input, select');
    var resultsContainer = document.querySelector('#searchResults');
    
    // Live search (debounced)
    var searchTimeout;
    filterInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(function() {
                updateSearchResults();
            }, 500);
        });
    });

    // Clear filters functionality
    var clearButton = document.querySelector('#clearFilters');
    if (clearButton) {
        clearButton.addEventListener('click', function() {
            filterInputs.forEach(function(input) {
                if (input.type === 'select-one') {
                    input.selectedIndex = 0;
                } else {
                    input.value = '';
                }
            });
            updateSearchResults();
        });
    }
}

// Player cards interaction
function initializePlayerCards() {
    var playerCards = document.querySelectorAll('.player-card');
    
    playerCards.forEach(function(card) {
        // Add hover effect
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px)';
            this.style.boxShadow = '0 12px 35px rgba(0, 0, 0, 0.2)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 8px 30px rgba(0, 0, 0, 0.15)';
        });

        // Quick actions
        var whatsappBtn = card.querySelector('.btn-success');
        if (whatsappBtn) {
            whatsappBtn.addEventListener('click', function(e) {
                // Track WhatsApp click
                trackEvent('whatsapp_contact', {
                    player_id: card.dataset.playerId || 'unknown',
                    source: 'player_card'
                });
            });
        }
    });
}

// WhatsApp integration enhancement
function initializeWhatsAppIntegration() {
    var whatsappLinks = document.querySelectorAll('a[href^="https://wa.me/"]');
    
    whatsappLinks.forEach(function(link) {
        // Add WhatsApp icon if not present
        if (!link.querySelector('.fa-whatsapp')) {
            var icon = document.createElement('i');
            icon.className = 'fab fa-whatsapp me-2';
            link.insertBefore(icon, link.firstChild);
        }

        // Add click tracking
        link.addEventListener('click', function(e) {
            var phoneNumber = this.href.match(/https:\/\/wa\.me\/(\d+)/);
            if (phoneNumber) {
                trackEvent('whatsapp_click', {
                    phone: phoneNumber[1],
                    source: this.closest('.card') ? 'card' : 'profile'
                });
            }
        });

        // Add hover tooltip
        link.setAttribute('data-bs-toggle', 'tooltip');
        link.setAttribute('data-bs-placement', 'top');
        link.setAttribute('title', 'Open WhatsApp to start conversation');
    });
}

// Modal handlers
function initializeModalHandlers() {
    // Auto-focus first input in modals
    var modals = document.querySelectorAll('.modal');
    modals.forEach(function(modal) {
        modal.addEventListener('shown.bs.modal', function() {
            var firstInput = this.querySelector('input, textarea, select');
            if (firstInput) {
                firstInput.focus();
            }
        });
    });

    // Clear form data when modal is hidden
    modals.forEach(function(modal) {
        modal.addEventListener('hidden.bs.modal', function() {
            var form = this.querySelector('form');
            if (form && !form.classList.contains('keep-data')) {
                form.reset();
                // Remove validation classes
                var inputs = form.querySelectorAll('.form-control, .form-select');
                inputs.forEach(function(input) {
                    input.classList.remove('is-valid', 'is-invalid');
                });
            }
        });
    });

    // Handle form submissions in modals
    var modalForms = document.querySelectorAll('.modal form');
    modalForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            var submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Saving...';
                
                // Re-enable after 3 seconds (in case of errors)
                setTimeout(function() {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = submitBtn.dataset.originalText || 'Save';
                }, 3000);
            }
        });
    });
}

// Image lazy loading
function initializeImageLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
}

// Scroll animations
function initializeScrollAnimations() {
    if ('IntersectionObserver' in window) {
        const animationObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                }
            });
        }, {
            threshold: 0.1
        });

        document.querySelectorAll('.card, .feature-card').forEach(el => {
            animationObserver.observe(el);
        });
    }
}

// Utility functions
function updateSearchResults() {
    // This would typically make an AJAX request to update results
    var form = document.querySelector('#searchForm');
    if (form) {
        // For now, just submit the form
        // In a more advanced version, you could use fetch() for AJAX
        console.log('Search filters updated');
    }
}

function trackEvent(eventName, properties) {
    // Analytics tracking (Google Analytics, etc.)
    if (typeof gtag !== 'undefined') {
        gtag('event', eventName, properties);
    }
    console.log('Event tracked:', eventName, properties);
}

// YouTube video helpers
function getYouTubeVideoId(url) {
    const regExp = /^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*/;
    const match = url.match(regExp);
    return (match && match[7].length === 11) ? match[7] : false;
}

function createYouTubeEmbed(url, options = {}) {
    const videoId = getYouTubeVideoId(url);
    if (!videoId) return null;
    
    const params = new URLSearchParams({
        enablejsapi: 1,
        origin: window.location.origin,
        ...options
    });
    
    return `https://www.youtube.com/embed/${videoId}?${params.toString()}`;
}

// Form helpers
function formatPhoneNumber(phone) {
    // Remove all non-digits
    const cleaned = phone.replace(/\D/g, '');
    
    // Add India country code if not present
    if (cleaned.length === 10) {
        return '91' + cleaned;
    }
    
    return cleaned;
}

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePhone(phone) {
    const cleaned = phone.replace(/\D/g, '');
    return cleaned.length >= 10 && cleaned.length <= 15;
}

// Network status handling
window.addEventListener('online', function() {
    showNetworkStatus('You are back online!', 'success');
});

window.addEventListener('offline', function() {
    showNetworkStatus('You are offline. Some features may not work.', 'warning');
});

function showNetworkStatus(message, type) {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alert.style.top = '70px';
    alert.style.right = '20px';
    alert.style.zIndex = '9999';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alert);
    
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    // You could send this to an error tracking service
});

// Service worker registration (for PWA functionality)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful');
            })
            .catch(function(err) {
                console.log('ServiceWorker registration failed');
            });
    });
}

// Export functions for use in other scripts
window.CricketCommunity = {
    trackEvent,
    formatPhoneNumber,
    validateEmail,
    validatePhone,
    getYouTubeVideoId,
    createYouTubeEmbed,
    showNetworkStatus
};
