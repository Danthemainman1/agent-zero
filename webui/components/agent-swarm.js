/**
 * Agent Swarm Visualization Component
 * Displays multi-agent orchestration status, active agents, and task queue
 */

const AgentSwarm = {
    container: null,
    isCollapsed: false,
    refreshInterval: null,
    
    // Agent type configurations
    agentTypes: {
        planner: { icon: '📋', color: '#3498db', label: 'Planner' },
        executor: { icon: '⚡', color: '#2ecc71', label: 'Executor' },
        knowledge: { icon: '📚', color: '#9b59b6', label: 'Knowledge' },
        verifier: { icon: '✓', color: '#f1c40f', label: 'Verifier' },
        default: { icon: '🤖', color: '#95a5a6', label: 'Agent' }
    },

    /**
     * Initialize the component
     */
    init(containerId = 'agent-swarm-container') {
        const template = document.getElementById('agent-swarm-template');
        if (!template) {
            console.warn('Agent swarm template not found');
            return;
        }

        const targetContainer = document.getElementById(containerId);
        if (!targetContainer) {
            console.warn(`Container ${containerId} not found`);
            return;
        }

        // Clone and append template
        const content = template.content.cloneNode(true);
        targetContainer.appendChild(content);
        
        this.container = targetContainer.querySelector('.agent-swarm-container');
        
        // Start auto-refresh
        this.startAutoRefresh();
        
        // Initial render
        this.refresh();
    },

    /**
     * Toggle collapsed state
     */
    toggle() {
        this.isCollapsed = !this.isCollapsed;
        const content = this.container.querySelector('.swarm-content');
        const toggleBtn = this.container.querySelector('.toggle-btn .material-icons');
        
        if (this.isCollapsed) {
            content.classList.add('collapsed');
            toggleBtn.textContent = 'expand_more';
        } else {
            content.classList.remove('collapsed');
            toggleBtn.textContent = 'expand_less';
        }
    },

    /**
     * Refresh all data
     */
    async refresh() {
        try {
            await Promise.all([
                this.refreshOrchestration(),
                this.refreshAgents(),
                this.refreshTasks()
            ]);
        } catch (error) {
            console.error('Failed to refresh agent swarm:', error);
        }
    },

    /**
     * Start auto-refresh interval
     */
    startAutoRefresh(intervalMs = 3000) {
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
     * Refresh orchestration status
     */
    async refreshOrchestration() {
        const content = document.getElementById('orchestration-content');
        if (!content) return;

        // Get orchestration status from current context
        const status = this.getOrchestrationStatus();
        
        if (!status || status.status === 'idle') {
            content.innerHTML = '<div class="no-orchestration">No active orchestration</div>';
            return;
        }

        const progressPercent = status.progress?.percentage || 0;
        const phases = ['Planning', 'Executing', 'Verifying'];
        const currentPhase = this.getCurrentPhase(status.status);

        content.innerHTML = `
            <div class="orchestration-active">
                <div class="orchestration-goal">${this.escapeHtml(status.main_goal || 'Processing...')}</div>
                
                <div class="orchestration-progress">
                    <div class="progress-bar-container">
                        <div class="progress-bar" style="width: ${progressPercent}%"></div>
                    </div>
                    <div class="progress-text">
                        ${status.progress?.completed || 0}/${status.progress?.total || 0} subtasks 
                        (${progressPercent.toFixed(0)}%)
                    </div>
                </div>
                
                <div class="orchestration-phases">
                    ${phases.map((phase, i) => `
                        <div class="phase-indicator ${i < currentPhase ? 'completed' : ''} ${i === currentPhase ? 'active' : ''}">
                            ${phase}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    },

    /**
     * Get current phase index
     */
    getCurrentPhase(status) {
        switch (status) {
            case 'planning': return 0;
            case 'executing': return 1;
            case 'verifying': return 2;
            case 'completed': return 3;
            default: return 0;
        }
    },

    /**
     * Refresh active agents display
     */
    async refreshAgents() {
        const grid = document.getElementById('agents-grid');
        if (!grid) return;

        const agents = this.getActiveAgents();
        
        if (agents.length === 0) {
            grid.innerHTML = `
                <div class="agent-card">
                    <div class="agent-avatar default">🤖</div>
                    <div class="agent-name">Agent 0</div>
                    <div class="agent-role">Main</div>
                    <div class="agent-status">Ready</div>
                </div>
            `;
            return;
        }

        grid.innerHTML = agents.map(agent => {
            const type = this.agentTypes[agent.profile] || this.agentTypes.default;
            const statusClass = agent.status === 'working' ? 'working' : 'idle';
            
            return `
                <div class="agent-card ${agent.status === 'working' ? 'active' : ''}">
                    <div class="agent-avatar ${agent.profile || 'default'}">${type.icon}</div>
                    <div class="agent-name">${this.escapeHtml(agent.name)}</div>
                    <div class="agent-role">${type.label}</div>
                    <div class="agent-status ${statusClass}">${agent.status}</div>
                </div>
            `;
        }).join('');
    },

    /**
     * Refresh task queue display
     */
    async refreshTasks() {
        const list = document.getElementById('tasks-list');
        if (!list) return;

        const tasks = this.getTasks();
        
        if (tasks.length === 0) {
            list.innerHTML = '<div class="no-tasks">No tasks in queue</div>';
            return;
        }

        list.innerHTML = tasks.slice(0, 10).map(task => {
            const statusIcon = this.getStatusIcon(task.status);
            
            return `
                <div class="task-item">
                    <span class="material-icons task-status-icon ${task.status}">${statusIcon}</span>
                    <span class="task-name" title="${this.escapeHtml(task.description)}">${this.escapeHtml(task.name)}</span>
                    <span class="task-progress">${task.progress?.toFixed(0) || 0}%</span>
                </div>
            `;
        }).join('');
    },

    /**
     * Get status icon
     */
    getStatusIcon(status) {
        switch (status) {
            case 'pending': return 'schedule';
            case 'running': return 'sync';
            case 'completed': return 'check_circle';
            case 'failed': return 'error';
            default: return 'radio_button_unchecked';
        }
    },

    /**
     * Get orchestration status from global state
     */
    getOrchestrationStatus() {
        // This would typically come from the API or global state
        // For now, return a mock or check window state
        if (window.orchestrationStatus) {
            return window.orchestrationStatus;
        }
        return null;
    },

    /**
     * Get active agents from global state
     */
    getActiveAgents() {
        // This would typically come from the API or global state
        if (window.activeAgents) {
            return window.activeAgents;
        }
        
        // Default: show main agent
        return [{
            name: 'Agent 0',
            profile: 'default',
            status: 'ready'
        }];
    },

    /**
     * Get tasks from global state
     */
    getTasks() {
        // This would typically come from the API or global state
        if (window.taskQueue) {
            return window.taskQueue;
        }
        return [];
    },

    /**
     * Update orchestration status (call from orchestrator)
     */
    updateOrchestration(status) {
        window.orchestrationStatus = status;
        this.refreshOrchestration();
    },

    /**
     * Update active agents (call from agent system)
     */
    updateAgents(agents) {
        window.activeAgents = agents;
        this.refreshAgents();
    },

    /**
     * Update task queue
     */
    updateTasks(tasks) {
        window.taskQueue = tasks;
        this.refreshTasks();
    },

    /**
     * Add a new agent to display
     */
    addAgent(agent) {
        const agents = window.activeAgents || [];
        agents.push(agent);
        window.activeAgents = agents;
        this.refreshAgents();
    },

    /**
     * Remove an agent from display
     */
    removeAgent(agentName) {
        const agents = window.activeAgents || [];
        window.activeAgents = agents.filter(a => a.name !== agentName);
        this.refreshAgents();
    },

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
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
    module.exports = AgentSwarm;
}
