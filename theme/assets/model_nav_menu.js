// 1. Model Navigation Menu JavaScript - Simple approach
function initializeModelNavigation() {
    // Add click listeners to all three-dot icons
    document.addEventListener('click', (e) => {
        // Handle three-dot icon clicks
        if (e.target.closest('.icon-link-discreet')) {
            e.preventDefault();
            e.stopPropagation();
            
            const dotsLink = e.target.closest('.icon-link-discreet');
            const modelId = dotsLink.getAttribute('tag');
            const flowPanel = dotsLink.closest('[anvil-role="nav_flow_panel"]');
            
            toggleModelOptions(flowPanel, modelId);
            return;
        }
        
        // Handle individual option clicks
        if (e.target.closest('.option-icon')) {
            e.preventDefault();
            e.stopPropagation();
            
            const optionIcon = e.target.closest('.option-icon');
            const action = optionIcon.dataset.action;
            const modelId = optionIcon.dataset.modelId;
            
            handleOptionClick(action, modelId);
            return;
        }
        
        // Close all menus when clicking outside
        if (!e.target.closest('.model-options-expanded')) {
            closeAllMenus();
        }
    });
}

// 2. Toggle model options display
function toggleModelOptions(flowPanel, modelId) {
    // Close other open menus first
    closeAllMenus();
    
    // Check if this panel already has expanded options
    let expandedContainer = flowPanel.querySelector('.model-options-expanded');
    
    if (!expandedContainer) {
        // Create the expanded options container
        expandedContainer = createExpandedOptions(modelId);
        
        // Find the flow-panel-gutter to append to
        const gutter = flowPanel.querySelector('.flow-panel-gutter');
        if (gutter) {
            gutter.appendChild(expandedContainer);
        }
    }
    
    // Add expanded class to flow panel and dots
    flowPanel.classList.add('expanded');
    const dotsLink = flowPanel.querySelector('.icon-link-discreet');
    if (dotsLink) {
        dotsLink.classList.add('expanded');
    }
    
    // Show the expanded container
    setTimeout(() => {
        expandedContainer.classList.add('active');
    }, 10);
}

// 3. Create expanded options container
function createExpandedOptions(modelId) {
    const container = document.createElement('div');
    container.className = 'model-options-expanded';
    
    // Pin icon
    const pinIcon = createOptionIcon('fa-thumb-tack', 'pin', modelId, 'Pin model');
    
    // Megaphone icon
    const megaphoneIcon = createOptionIcon('fa-bullhorn', 'notifications', modelId, 'Notifications');
    
    // Settings icon
    const settingsIcon = createOptionIcon('fa-sliders', 'settings', modelId, 'Settings');
    
    // Trash icon
    const trashIcon = createOptionIcon('fa-trash', 'delete', modelId, 'Delete model');
    
    container.appendChild(pinIcon);
    container.appendChild(megaphoneIcon);
    container.appendChild(settingsIcon);
    container.appendChild(trashIcon);
    
    return container;
}

// 4. Create individual option icon
function createOptionIcon(iconClass, action, modelId, title) {
    const option = document.createElement('div');
    option.className = 'option-icon';
    option.title = title;
    option.dataset.action = action;
    option.dataset.modelId = modelId;
    option.innerHTML = `<i class="fa ${iconClass}"></i>`;
    return option;
}

// 5. Handle option clicks
function handleOptionClick(action, modelId) {
    console.log('Option clicked:', action, 'for model:', modelId);
    
    switch (action) {
        case 'settings':
            // Use Anvil's routing system instead of direct hash change
            if (typeof routing !== 'undefined' && routing.set_url_hash) {
                routing.set_url_hash(`model_profile?model_id=${modelId}&section=Main`, false);
            } else {
                // Fallback to direct hash change
                window.location.hash = `model_profile?model_id=${modelId}&section=Main`;
            }
            break;
        case 'pin':
            console.log('Pin functionality not implemented yet');
            break;
        case 'notifications':
            console.log('Notifications functionality not implemented yet');
            break;
        case 'delete':
            console.log('Delete functionality not implemented yet');
            break;
    }
    
    // Close the menu after action
    closeAllMenus();
}

// 6. Close all open menus
function closeAllMenus() {
    // Remove expanded class from all flow panels
    const expandedPanels = document.querySelectorAll('[anvil-role="nav_flow_panel"].expanded');
    expandedPanels.forEach(panel => {
        panel.classList.remove('expanded');
        
        // Remove expanded class from dots
        const dotsLink = panel.querySelector('.icon-link-discreet');
        if (dotsLink) {
            dotsLink.classList.remove('expanded');
        }
        
        // Remove expanded options
        const expandedContainer = panel.querySelector('.model-options-expanded');
        if (expandedContainer) {
            expandedContainer.classList.remove('active');
            setTimeout(() => {
                expandedContainer.remove();
            }, 300);
        }
    });
}

// 7. Function to clear model navigation (for refresh)
function clearModelNavigation() {
    closeAllMenus();
}

// 8. Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeModelNavigation);
} else {
    initializeModelNavigation();
}
