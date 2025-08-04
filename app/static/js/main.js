// Basic JavaScript for the helpdesk application

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide flash messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });

    // Voting functionality
    const voteButtons = document.querySelectorAll('.vote-btn');
    voteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const ticketId = this.dataset.ticketId;
            const isUpvote = this.dataset.isUpvote === 'true';
            
            fetch('/votes/toggle', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    ticket_id: parseInt(ticketId),
                    is_upvote: isUpvote
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else {
                    // Update vote score
                    const scoreElement = document.querySelector(`#vote-score-${ticketId}`);
                    if (scoreElement) {
                        scoreElement.textContent = data.vote_score;
                    }
                    
                    // Update button states
                    updateVoteButtons(ticketId, data.user_vote);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to process vote');
            });
        });
    });

    // Comment form submission
    const commentForms = document.querySelectorAll('.comment-form');
    commentForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const content = form.querySelector('textarea[name="content"]').value.trim();
            if (!content) {
                e.preventDefault();
                alert('Please enter a comment');
            }
        });
    });

    // File upload validation
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                // Check file size (16MB limit)
                const maxSize = 16 * 1024 * 1024; // 16MB
                if (file.size > maxSize) {
                    alert('File is too large. Maximum size is 16MB.');
                    this.value = '';
                    return;
                }
                
                // Show file name
                const fileInfo = this.parentElement.querySelector('.file-info');
                if (fileInfo) {
                    fileInfo.textContent = `Selected: ${file.name} (${formatFileSize(file.size)})`;
                }
            }
        });
    });

    // Search form handling
    const searchForm = document.querySelector('#search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const searchInput = this.querySelector('input[name="search"]');
            if (searchInput && !searchInput.value.trim()) {
                searchInput.value = '';
            }
        });
    }

    // Ticket status update
    const statusSelects = document.querySelectorAll('.status-select');
    statusSelects.forEach(select => {
        select.addEventListener('change', function() {
            const ticketId = this.dataset.ticketId;
            const newStatus = this.value;
            
            if (confirm(`Change ticket status to "${newStatus.replace('_', ' ')}"?`)) {
                updateTicketStatus(ticketId, newStatus);
            } else {
                // Reset to original value
                this.value = this.dataset.originalValue;
            }
        });
    });
});

function updateVoteButtons(ticketId, userVote) {
    const upvoteBtn = document.querySelector(`[data-ticket-id="${ticketId}"][data-is-upvote="true"]`);
    const downvoteBtn = document.querySelector(`[data-ticket-id="${ticketId}"][data-is-upvote="false"]`);
    
    if (upvoteBtn && downvoteBtn) {
        // Reset button states
        upvoteBtn.classList.remove('btn-success');
        upvoteBtn.classList.add('btn-outline');
        downvoteBtn.classList.remove('btn-danger');
        downvoteBtn.classList.add('btn-outline');
        
        // Set active state based on user vote
        if (userVote === 'upvote') {
            upvoteBtn.classList.remove('btn-outline');
            upvoteBtn.classList.add('btn-success');
        } else if (userVote === 'downvote') {
            downvoteBtn.classList.remove('btn-outline');
            downvoteBtn.classList.add('btn-danger');
        }
    }
}

function updateTicketStatus(ticketId, newStatus) {
    fetch(`/tickets/${ticketId}/update`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            status: newStatus
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            location.reload(); // Reload to show updated status
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to update ticket status');
    });
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Utility function to show/hide elements
function toggleElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = element.style.display === 'none' ? 'block' : 'none';
    }
}

// Confirmation dialogs for destructive actions
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}