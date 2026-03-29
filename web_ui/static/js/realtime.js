/**
 * Real-time Updates Module
 * Handles live updates for email processing
 */

class RealtimeUpdater {
    constructor() {
        this.updateInterval = 5000; // 5 seconds
        this.isConnected = false;
        this.lastUpdate = Date.now();
        this.init();
    }

    init() {
        // Start polling for updates
        setInterval(() => this.fetchUpdates(), this.updateInterval);

        // Optional: WebSocket fallback
        this.tryWebSocket();
    }

    fetchUpdates() {
        fetch('/api/stats')
            .then(response => response.json())
            .then(data => {
                this.handleUpdate(data);
                this.updateStatusIndicator(true);
            })
            .catch(error => {
                console.error('Update failed:', error);
                this.updateStatusIndicator(false);
            });
    }

    handleUpdate(data) {
        // Update dashboard stats
        const totalElement = document.getElementById('total-emails');
        const processedElement = document.getElementById('processed-emails');
        const pendingElement = document.getElementById('pending-drafts');
        const rateElement = document.getElementById('processing-rate');

        if (totalElement) totalElement.textContent = data.total_emails;
        if (processedElement) processedElement.textContent = data.processed_emails;
        if (pendingElement) pendingElement.textContent = data.pending_drafts;

        if (rateElement) {
            const rate = data.total_emails > 0 ?
                ((data.processed_emails / data.total_emails) * 100).toFixed(1) : '0';
            rateElement.textContent = rate + '%';
        }

        // Show notification if new emails processed
        if (this.lastProcessedCount && data.processed_emails > this.lastProcessedCount) {
            this.showNotification(
                'New reply generated',
                'An AI response has been created',
                'success'
            );
        }

        this.lastProcessedCount = data.processed_emails;
        this.lastUpdate = Date.now();
    }

    updateStatusIndicator(connected) {
        const indicator = document.querySelector('[style*="green-500"]');
        if (indicator) {
            indicator.style.backgroundColor = connected ? '#22c55e' : '#ef4444';
        }
    }

    showNotification(title, message, type = 'info') {
        const container = document.getElementById('notifications');
        if (!container) return;

        const notif = document.createElement('div');
        const colors = {
            success: 'bg-green-500/20 border-green-500/30 text-green-300',
            error: 'bg-red-500/20 border-red-500/30 text-red-300',
            info: 'bg-blue-500/20 border-blue-500/30 text-blue-300'
        };

        notif.className = `notification p-4 rounded-lg border ${colors[type]} animate-slide-in`;
        notif.innerHTML = `
            <div class="flex items-start space-x-3">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'} mt-1"></i>
                <div>
                    <h4 class="font-semibold">${title}</h4>
                    <p class="text-sm opacity-90">${message}</p>
                </div>
            </div>
        `;

        container.appendChild(notif);
        setTimeout(() => notif.remove(), 5000);
    }

    tryWebSocket() {
        // Optional: Implement WebSocket for true real-time updates
        // This is a fallback to polling if WebSocket is not available
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    window.updater = new RealtimeUpdater();
});
