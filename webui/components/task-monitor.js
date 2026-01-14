/**
 * Task Monitor Component
 * Displays and manages persistent background tasks
 */

const TaskMonitor = {
    container: null,
    refreshInterval: null,
    contextId: null,

    /**
     * Initialize the component
     */
    init(containerId = 'task-monitor-container', contextId = null) {
        const template = document.getElementById('task-monitor-template');
        if (!template) {
            console.warn('Task monitor template not found');
            return;
        }

        const targetContainer = document.getElementById(containerId);
        if (!targetContainer) {
            console.warn(`Container ${containerId} not found`);
            return;
        }

        this.contextId = contextId;

        // Clone and append template
        const content = template.content.cloneNode(true);
        targetContainer.appendChild(content);
        
        this.container = targetContainer.querySelector('.task-monitor-container');
        
        // Start auto-refresh
        this.startAutoRefresh();
        
        // Initial render
        this.refresh();
    },

    /**
     * Refresh task list
     */
    async refresh() {
        if (!this.contextId) {
            this.contextId = this.getCurrentContextId();
        }

        try {
            const response = await fetch('/task_status', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ context_id: this.contextId })
            });

            if (response.ok) {
                const data = await response.json();
                this.render(data.tasks || []);
                this.updateBadge(data.active_count || 0);
            }
        } catch (error) {
            console.error('Failed to fetch tasks:', error);
            this.render([]);
        }
    },

    /**
     * Render task list
     */
    render(tasks) {
        const list = document.getElementById('task-monitor-list');
        if (!list) return;

        if (tasks.length === 0) {
            list.innerHTML = `
                <div class="no-tasks-message">
                    <span class="material-icons">check_circle_outline</span>
                    <div>No background tasks</div>
                </div>
            `;
            return;
        }

        list.innerHTML = tasks.map(task => this.renderTask(task)).join('');
    },

    /**
     * Render single task
     */
    renderTask(task) {
        const stateClass = task.state || 'pending';
        const icon = this.getTaskIcon(stateClass);
        const progress = task.progress || 0;
        const timeAgo = this.formatTimeAgo(task.updated_at);

        return `
            <div class="task-monitor-item" data-task-id="${task.id}">
                <div class="task-icon ${stateClass}">
                    <span class="material-icons">${icon}</span>
                </div>
                <div class="task-info">
                    <div class="task-name" title="${this.escapeHtml(task.description || task.name)}">${this.escapeHtml(task.name)}</div>
                    <div class="task-meta">
                        <span class="task-state ${stateClass}">${stateClass}</span>
                        <span class="task-time">${timeAgo}</span>
                    </div>
                </div>
                ${stateClass === 'running' ? `
                    <div class="task-progress-mini">
                        <div class="task-progress-mini-bar" style="width: ${progress}%"></div>
                    </div>
                ` : ''}
                <div class="task-actions">
                    ${stateClass === 'running' || stateClass === 'pending' ? `
                        <button class="task-action-btn cancel" onclick="TaskMonitor.cancelTask('${task.id}')" title="Cancel">
                            <span class="material-icons">close</span>
                        </button>
                    ` : ''}
                    ${stateClass === 'completed' || stateClass === 'failed' ? `
                        <button class="task-action-btn" onclick="TaskMonitor.viewTask('${task.id}')" title="View details">
                            <span class="material-icons">visibility</span>
                        </button>
                    ` : ''}
                </div>
            </div>
        `;
    },

    /**
     * Get icon for task state
     */
    getTaskIcon(state) {
        switch (state) {
            case 'running': return 'sync';
            case 'completed': return 'check_circle';
            case 'failed': return 'error';
            case 'cancelled': return 'cancel';
            case 'paused': return 'pause_circle';
            default: return 'schedule';
        }
    },

    /**
     * Update badge count
     */
    updateBadge(count) {
        const badge = document.getElementById('task-count-badge');
        if (badge) {
            badge.textContent = count;
            badge.classList.toggle('empty', count === 0);
        }
    },

    /**
     * Cancel a task
     */
    async cancelTask(taskId) {
        try {
            const response = await fetch('/task_cancel', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    context_id: this.contextId,
                    task_id: taskId 
                })
            });

            if (response.ok) {
                this.refresh();
            }
        } catch (error) {
            console.error('Failed to cancel task:', error);
        }
    },

    /**
     * View task details
     */
    viewTask(taskId) {
        // Could open a modal or navigate to task details
        console.log('View task:', taskId);
        // For now, just log - implement modal later
    },

    /**
     * Get current context ID
     */
    getCurrentContextId() {
        // Try to get from global state or URL
        if (window.currentContextId) {
            return window.currentContextId;
        }
        // Fallback
        return 'default';
    },

    /**
     * Format time ago
     */
    formatTimeAgo(dateStr) {
        if (!dateStr) return '';
        
        const date = new Date(dateStr);
        const now = new Date();
        const diffMs = now - date;
        const diffSec = Math.floor(diffMs / 1000);
        const diffMin = Math.floor(diffSec / 60);
        const diffHour = Math.floor(diffMin / 60);
        const diffDay = Math.floor(diffHour / 24);

        if (diffSec < 60) return 'just now';
        if (diffMin < 60) return `${diffMin}m ago`;
        if (diffHour < 24) return `${diffHour}h ago`;
        return `${diffDay}d ago`;
    },

    /**
     * Start auto-refresh
     */
    startAutoRefresh(intervalMs = 5000) {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        this.refreshInterval = setInterval(() => this.refresh(), intervalMs);
    },

    /**
     * Stop auto-refresh
     */
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    },

    /**
     * Escape HTML
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text || '';
        return div.innerHTML;
    },

    /**
     * Cleanup
     */
    destroy() {
        this.stopAutoRefresh();
        if (this.container) {
            this.container.remove();
        }
    }
};

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TaskMonitor;
}
