// Baby Care Tracker JavaScript Functions

// Global variables
let socket = null;
let toastContainer = null;
let autoRefreshInterval = null;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    initializeWebSocket();
    setupToastContainer();
    setupAutoRefresh();
    setupThemeHandling();
});

// Initialize main application
function initializeApp() {
    console.log('Baby Care Tracker initialized');
    
    // Add loading states to all forms
    setupFormLoadingStates();
    
    // Setup keyboard shortcuts
    setupKeyboardShortcuts();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Setup auto-save for forms
    setupAutoSave();
}

// Initialize WebSocket connection
function initializeWebSocket() {
    if (typeof io !== 'undefined') {
        socket = io();
        
        socket.on('connect', function() {
            console.log('WebSocket connected');
            showToast('Connected to server', 'success', 2000);
        });
        
        socket.on('disconnect', function() {
            console.log('WebSocket disconnected');
            showToast('Disconnected from server', 'warning', 3000);
        });
        
        socket.on('baby_care_event', function(data) {
            console.log('Received baby care event:', data);
            handleNewEvent(data);
        });
        
        socket.on('device_status_update', function(data) {
            console.log('Device status update:', data);
            updateDeviceStatus(data);
        });
        
        socket.on('error', function(error) {
            console.error('WebSocket error:', error);
            showToast('Connection error: ' + error.message, 'danger');
        });
    }
}

// Setup toast notification container
function setupToastContainer() {
    toastContainer = document.createElement('div');
    toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
    toastContainer.style.zIndex = '1055';
    document.body.appendChild(toastContainer);
}

// Show toast notification
function showToast(message, type = 'info', duration = 5000) {
    const toastId = 'toast-' + Date.now();
    const iconMap = {
        success: 'fas fa-check-circle',
        danger: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    
    const toastHTML = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <i class="${iconMap[type] || iconMap.info} text-${type} me-2"></i>
                <strong class="me-auto">Baby Care Tracker</strong>
                <small class="text-muted">just now</small>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        autohide: duration > 0,
        delay: duration
    });
    
    toast.show();
    
    // Remove toast element after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

// Handle new baby care events
function handleNewEvent(eventData) {
    // Update dashboard if we're on the dashboard page
    if (window.location.pathname === '/' || window.location.pathname === '/dashboard') {
        updateDashboard(eventData);
    }
    
    // Show notification if enabled
    const eventTypeMap = {
        feeding_start_left: '🍼 Left breast feeding started',
        feeding_start_right: '🍼 Right breast feeding started',
        feeding_end: '✅ Feeding session ended',
        sleep_start: '😴 Sleep started',
        sleep_end: '☀️ Wake up recorded',
        diaper_wet: '💧 Wet diaper changed',
        diaper_dirty: '💩 Dirty diaper changed',
        diaper_both: '🔄 Diaper changed (wet & dirty)'
    };
    
    const message = eventTypeMap[eventData.type] || `📝 ${eventData.type} recorded`;
    showToast(message, 'success', 3000);
    
    // Play notification sound if enabled
    playNotificationSound();
}

// Update device status
function updateDeviceStatus(statusData) {
    const deviceElements = document.querySelectorAll(`[data-device-id="${statusData.device_id}"]`);
    
    deviceElements.forEach(element => {
        const statusBadge = element.querySelector('.device-status');
        if (statusBadge) {
            statusBadge.className = `badge bg-${statusData.available ? 'success' : 'danger'} device-status`;
            statusBadge.textContent = statusData.available ? 'Available' : 'Unavailable';
        }
    });
}

// Setup auto-refresh functionality
function setupAutoRefresh() {
    const refreshInterval = window.autoRefreshInterval || 0;
    
    if (refreshInterval > 0) {
        autoRefreshInterval = setInterval(() => {
            if (typeof refreshData === 'function') {
                refreshData();
            }
        }, refreshInterval * 1000);
    }
}

// Setup theme handling
function setupThemeHandling() {
    // Listen for theme changes
    document.getElementById('theme')?.addEventListener('change', function() {
        applyTheme(this.value);
    });
    
    // Listen for system theme changes
    if (window.matchMedia) {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
            const currentTheme = document.getElementById('theme')?.value;
            if (currentTheme === 'auto') {
                applyTheme('auto');
            }
        });
    }
}

// Apply theme
function applyTheme(theme) {
    const html = document.documentElement;
    
    if (theme === 'dark') {
        html.setAttribute('data-bs-theme', 'dark');
    } else if (theme === 'auto') {
        const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        html.setAttribute('data-bs-theme', prefersDark ? 'dark' : 'light');
    } else {
        html.setAttribute('data-bs-theme', 'light');
    }
    
    // Store theme preference
    localStorage.setItem('babycare-theme', theme);
}

// Setup form loading states
function setupFormLoadingStates() {
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                const originalText = submitButton.innerHTML;
                submitButton.innerHTML = '<span class="loading-spinner"></span> Saving...';
                submitButton.disabled = true;
                
                // Reset after 5 seconds as fallback
                setTimeout(() => {
                    submitButton.innerHTML = originalText;
                    submitButton.disabled = false;
                }, 5000);
            }
        });
    });
}

// Setup keyboard shortcuts
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + shortcuts
        if (e.ctrlKey || e.metaKey) {
            switch(e.key) {
                case '1':
                    e.preventDefault();
                    if (typeof logEvent === 'function') logEvent('feeding_start_left');
                    break;
                case '2':
                    e.preventDefault();
                    if (typeof logEvent === 'function') logEvent('feeding_start_right');
                    break;
                case '3':
                    e.preventDefault();
                    if (typeof logEvent === 'function') logEvent('sleep_start');
                    break;
                case '4':
                    e.preventDefault();
                    if (typeof logEvent === 'function') logEvent('diaper_both');
                    break;
                case 'r':
                    e.preventDefault();
                    window.location.reload();
                    break;
            }
        }
        
        // Escape key to close modals
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                const modal = bootstrap.Modal.getInstance(openModal);
                if (modal) modal.hide();
            }
        }
    });
}

// Initialize tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Setup auto-save for forms
function setupAutoSave() {
    const autoSaveForms = document.querySelectorAll('[data-auto-save]');
    
    autoSaveForms.forEach(form => {
        const inputs = form.querySelectorAll('input, select, textarea');
        let saveTimeout;
        
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                clearTimeout(saveTimeout);
                saveTimeout = setTimeout(() => {
                    autoSaveForm(form);
                }, 2000); // Save after 2 seconds of inactivity
            });
        });
    });
}

// Auto-save form data
function autoSaveForm(form) {
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    // Save to localStorage
    const formId = form.id || 'unnamed-form';
    localStorage.setItem(`babycare-autosave-${formId}`, JSON.stringify(data));
    
    // Show subtle indication
    const saveIndicator = document.createElement('small');
    saveIndicator.className = 'text-muted fade-in';
    saveIndicator.textContent = 'Draft saved';
    
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton && !form.querySelector('.auto-save-indicator')) {
        saveIndicator.className += ' auto-save-indicator';
        submitButton.parentNode.insertBefore(saveIndicator, submitButton);
        
        setTimeout(() => {
            saveIndicator.remove();
        }, 2000);
    }
}

// Restore auto-saved form data
function restoreAutoSavedData(formId) {
    const savedData = localStorage.getItem(`babycare-autosave-${formId}`);
    if (savedData) {
        const data = JSON.parse(savedData);
        const form = document.getElementById(formId);
        
        if (form) {
            Object.keys(data).forEach(key => {
                const input = form.querySelector(`[name="${key}"]`);
                if (input) {
                    if (input.type === 'checkbox') {
                        input.checked = data[key] === 'on';
                    } else {
                        input.value = data[key];
                    }
                }
            });
        }
    }
}

// Play notification sound
function playNotificationSound() {
    const settings = JSON.parse(localStorage.getItem('babycare-settings') || '{}');
    
    if (settings.soundNotifications !== false) {
        // Create a simple notification sound
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
        oscillator.frequency.setValueAtTime(600, audioContext.currentTime + 0.1);
        
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.3);
    }
}

// Format duration for display
function formatDuration(minutes) {
    if (minutes < 60) {
        return `${minutes}min`;
    } else {
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        return mins > 0 ? `${hours}h ${mins}min` : `${hours}h`;
    }
}

// Format timestamp for display
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffMins < 1) {
        return 'just now';
    } else if (diffMins < 60) {
        return `${diffMins}min ago`;
    } else if (diffHours < 24) {
        return `${diffHours}h ago`;
    } else if (diffDays === 1) {
        return 'yesterday';
    } else if (diffDays < 7) {
        return `${diffDays} days ago`;
    } else {
        return date.toLocaleDateString();
    }
}

// Validate form data
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Debounce function for search inputs
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Search functionality
function setupSearch(inputSelector, itemsSelector, searchFunction) {
    const searchInput = document.querySelector(inputSelector);
    const items = document.querySelectorAll(itemsSelector);
    
    if (searchInput && items.length > 0) {
        const debouncedSearch = debounce((query) => {
            searchFunction(query, items);
        }, 300);
        
        searchInput.addEventListener('input', (e) => {
            debouncedSearch(e.target.value.toLowerCase().trim());
        });
    }
}

// Generic search function
function performSearch(query, items) {
    items.forEach(item => {
        const text = item.textContent.toLowerCase();
        const matches = text.includes(query);
        item.style.display = matches || query === '' ? '' : 'none';
    });
}

// Export data functionality
function exportData(format, data, filename) {
    let blob;
    let mimeType;
    
    switch(format) {
        case 'csv':
            blob = new Blob([data], { type: 'text/csv' });
            mimeType = 'text/csv';
            break;
        case 'json':
            blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            mimeType = 'application/json';
            break;
        default:
            console.error('Unsupported export format:', format);
            return;
    }
    
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename || `baby_care_export.${format}`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

// Check if device is online
function checkOnlineStatus() {
    const updateOnlineStatus = () => {
        const statusIndicator = document.querySelector('.online-status');
        if (statusIndicator) {
            if (navigator.onLine) {
                statusIndicator.className = 'badge bg-success online-status';
                statusIndicator.textContent = 'Online';
            } else {
                statusIndicator.className = 'badge bg-danger online-status';
                statusIndicator.textContent = 'Offline';
            }
        }
    };
    
    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    updateOnlineStatus(); // Initial check
}

// Initialize offline support
function initializeOfflineSupport() {
    checkOnlineStatus();
    
    // Cache important data when online
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(registration => {
                console.log('Service Worker registered:', registration);
            })
            .catch(error => {
                console.log('Service Worker registration failed:', error);
            });
    }
}

// Cleanup function
function cleanup() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
    
    if (socket) {
        socket.disconnect();
    }
}

// Handle page unload
window.addEventListener('beforeunload', cleanup);

// Global utility functions
window.BabyCareTracker = {
    showToast,
    formatDuration,
    formatTimestamp,
    validateForm,
    exportData,
    debounce,
    setupSearch,
    performSearch
};
