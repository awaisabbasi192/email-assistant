/**
 * Draft Editor Functionality
 */

class DraftEditor {
    constructor() {
        this.currentDraftId = null;
        this.originalContent = '';
    }

    openDraft(draftId) {
        this.currentDraftId = draftId;
        fetch(`/api/drafts/${draftId}`)
            .then(r => r.json())
            .then(draft => {
                this.originalContent = draft.reply_body;
                document.getElementById('edit-textarea').value = draft.reply_body;
                new bootstrap.Modal(document.getElementById('editModal')).show();
            })
            .catch(err => console.error('Error loading draft:', err));
    }

    saveDraft() {
        if (!this.currentDraftId) return;

        const newContent = document.getElementById('edit-textarea').value;

        fetch(`/api/drafts/${this.currentDraftId}/update`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ reply_body: newContent })
        })
        .then(r => r.json())
        .then(data => {
            if (data.status === 'success') {
                document.getElementById(`reply-${this.currentDraftId}`).value = newContent;
                bootstrap.Modal.getInstance(document.getElementById('editModal')).hide();
                showNotification('Draft updated successfully!', 'success');
            } else {
                showNotification('Error updating draft', 'danger');
            }
        })
        .catch(err => {
            console.error('Error:', err);
            showNotification('Error updating draft', 'danger');
        });
    }

    approveDraft(draftId) {
        if (!confirm('This will approve the draft. Continue?')) return;

        fetch(`/api/drafts/${draftId}/status`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: 'approved' })
        })
        .then(r => r.json())
        .then(data => {
            if (data.status === 'success') {
                const card = document.querySelector(`[data-draft-id="${draftId}"]`);
                if (card) card.remove();
                showNotification('Draft approved!', 'success');
            }
        })
        .catch(err => console.error('Error:', err));
    }

    regenerateDraft(draftId) {
        if (!confirm('Regenerate this draft with a new reply?')) return;

        fetch(`/api/drafts/${draftId}/regenerate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(r => r.json())
        .then(data => {
            showNotification('Draft regenerated!', 'success');
            setTimeout(() => location.reload(), 1500);
        })
        .catch(err => console.error('Error:', err));
    }

    deleteDraft(draftId) {
        if (!confirm('Delete this draft?')) return;

        fetch(`/api/drafts/${draftId}/status`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: 'deleted' })
        })
        .then(r => r.json())
        .then(data => {
            const card = document.querySelector(`[data-draft-id="${draftId}"]`);
            if (card) card.remove();
            showNotification('Draft deleted', 'info');
        })
        .catch(err => console.error('Error:', err));
    }

    openInGmail(draftId) {
        // This would typically open Gmail draft in a new tab
        // For now, show a message
        showNotification('Draft is ready in Gmail. You can review and send it manually.', 'info');
    }
}

// Initialize editor
const draftEditor = new DraftEditor();

// Global functions for onclick handlers
function editDraft(draftId) {
    draftEditor.openDraft(draftId);
}

function saveDraftEdit() {
    draftEditor.saveDraft();
}

function approveDraft(draftId) {
    draftEditor.approveDraft(draftId);
}

function regenerateDraft(draftId) {
    draftEditor.regenerateDraft(draftId);
}

function deleteDraft(draftId) {
    draftEditor.deleteDraft(draftId);
}

function openInGmail(draftId) {
    draftEditor.openInGmail(draftId);
}

function refreshDrafts() {
    location.reload();
}

// Utility function
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
