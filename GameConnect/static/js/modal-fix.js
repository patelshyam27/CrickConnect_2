/**
 * Modal Fix for Blinking/Flickering Issues
 * 
 * This script addresses the issue where Bootstrap modals blink or flicker when opened.
 * Based on common solutions for this problem:
 * 1. Ensures modals are placed at the top level of the DOM
 * 2. Prevents multiple initializations of the same modal
 * 3. Properly handles modal events
 */

document.addEventListener('DOMContentLoaded', function() {
    // Fix for modal blinking/flickering
    function fixModalBlinking() {
        // 1. Move all modals to the end of the body to prevent z-index issues
        const modals = document.querySelectorAll('.modal');
        modals.forEach(function(modal) {
            // Only move if not already at body level
            if (modal.parentElement !== document.body) {
                document.body.appendChild(modal);
            }
        });

        // 2. Ensure proper backdrop handling
        const deleteButtons = document.querySelectorAll('[data-bs-toggle="modal"][data-bs-target^="#deleteModal"]');
        deleteButtons.forEach(function(button) {
            button.addEventListener('click', function(e) {
                // Get the target modal
                const modalId = this.getAttribute('data-bs-target');
                const modal = document.querySelector(modalId);
                
                if (modal) {
                    // Ensure the modal is properly initialized only once
                    if (!modal._bsModal) {
                        modal._bsModal = new bootstrap.Modal(modal, {
                            backdrop: 'static',  // Prevents closing when clicking outside
                            keyboard: false      // Prevents closing with escape key
                        });
                    }
                    
                    // Show the modal programmatically instead of relying on data attributes
                    e.preventDefault();
                    modal._bsModal.show();
                }
            });
        });

        // 3. Ensure forms in modals don't cause issues
        const modalForms = document.querySelectorAll('.modal form');
        modalForms.forEach(function(form) {
            form.addEventListener('submit', function() {
                // Disable the submit button to prevent double submission
                const submitBtn = this.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.disabled = true;
                }
            });
        });
    }

    // Run the fix
    fixModalBlinking();

    // Also run after any AJAX content is loaded
    document.addEventListener('ajax:success', fixModalBlinking);
});