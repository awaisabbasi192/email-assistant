/**
 * Email Assistant Web UI - Main Application JavaScript
 */

// Utility function to make API calls
async function apiCall(endpoint, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json'
        }
    };

    const mergedOptions = { ...defaultOptions, ...options };

    try {
        const response = await fetch(endpoint, mergedOptions);
        if (!response.ok && response.status !== 404) {
            throw new Error(`HTTP ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API Call Failed:', error);
        return null;
    }
}

// Refresh dashboard statistics
async function refreshStats() {
    const data = await apiCall('/api/stats');
    if (data) {
        document.getElementById('total-emails').textContent = data.total_emails;
        document.getElementById('processed-emails').textContent = data.processed_emails;
        document.getElementById('pending-drafts').textContent = data.pending_drafts;

        const rate = data.total_emails > 0
            ? ((data.processed_emails / data.total_emails) * 100).toFixed(1)
            : 0;
        document.getElementById('processing-rate').textContent = rate + '%';
    }
}

// Refresh pending drafts list
async function refreshDrafts() {
    const data = await apiCall('/api/drafts/pending');
    if (data) {
        const container = document.getElementById('drafts-container');
        if (container) {
            location.reload();
        }
    }
}

// Format date
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

// Show notification toast
function showNotification(message, type = 'info', duration = 3000) {
    const alertClass = `alert-${type}`;
    const toast = document.createElement('div');
    toast.className = `alert ${alertClass} position-fixed top-0 start-50 translate-middle-x mt-3`;
    toast.textContent = message;
    toast.style.zIndex = '9999';

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, duration);
}

// Initialize tooltips and popovers
document.addEventListener('DOMContentLoaded', function() {
    // Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-refresh stats every 30 seconds on dashboard
    if (document.getElementById('total-emails')) {
        setInterval(refreshStats, 30000);
    }
});

// Export table to CSV
function exportTableToCSV(filename = 'export.csv') {
    const table = document.querySelector('table');
    if (!table) return;

    let csv = [];
    const rows = table.querySelectorAll('tr');

    rows.forEach(row => {
        let csvRow = [];
        row.querySelectorAll('td, th').forEach(cell => {
            csvRow.push('"' + cell.textContent.trim() + '"');
        });
        csv.push(csvRow.join(','));
    });

    downloadCSV(csv.join('\n'), filename);
}

// Download CSV file
function downloadCSV(csv, filename) {
    const link = document.createElement('a');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);

    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Confirm action dialog
function confirmAction(message) {
    return confirm(message);
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard', 'success', 2000);
    });
}

// Format number with comma separators
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Calculate percentage
function calculatePercentage(part, total) {
    if (total === 0) return 0;
    return ((part / total) * 100).toFixed(1);
}

// Get URL parameters
function getUrlParameter(name) {
    const url = new URL(window.location);
    return url.searchParams.get(name);
}

// Debounce function for search
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Handle logout
function handleLogout() {
    if (confirmAction('Are you sure you want to logout?')) {
        window.location.href = '/logout';
    }
}

// Log to console with timestamp
function log(message, level = 'info') {
    const timestamp = new Date().toLocaleTimeString();
    console[level](`[${timestamp}] ${message}`);
}

export { apiCall, refreshStats, refreshDrafts, showNotification, formatDate };
