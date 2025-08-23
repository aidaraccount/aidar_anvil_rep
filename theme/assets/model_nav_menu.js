// 1. Model Navigation Menu JavaScript - Simple approach with extensive logging
function initializeModelNavigation() {
    console.log('🔧 Initializing model navigation...');
    
    // Add click listeners to all three-dot icons
    document.addEventListener('click', (e) => {
        console.log('🖱️ Click detected on:', e.target);
        console.log('🖱️ Click target classes:', e.target.className);
        console.log('🖱️ Closest [anvil-role="icon-link-discreet"]:', e.target.closest('[anvil-role="icon-link-discreet"]'));
        
        // Handle three-dot icon clicks
        if (e.target.closest('[anvil-role="icon-link-discreet"]')) {
            console.log('✅ Three-dot icon clicked!');
            e.preventDefault();
            e.stopPropagation();
            
            let dotsLink = e.target.closest('[anvil-role="icon-link-discreet"]');
            if (!dotsLink) {
                dotsLink = findClosestByRole(e.target, 'icon-link-discreet');
                console.log('🧭 Fallback dotsLink by role scan:', dotsLink);
            }
            const modelId = resolveModelIdFromElement(dotsLink);
            // Robust container resolution
            let flowPanel = dotsLink.closest('[anvil-role="nav_flow_panel"]');
            if (!flowPanel) {
                flowPanel = dotsLink.closest('.flow-panel, .flow-panel-item, .anvil-container, .sidebar-elt, .content');
                console.log('🧭 Fallback flowPanel:', flowPanel);
            }
            
            console.log('📋 Model ID:', modelId);
            console.log('📋 Flow Panel:', flowPanel);
            
            if (flowPanel) {
                toggleModelOptions(flowPanel, modelId);
            } else {
                console.warn('⚠️ Could not find a suitable container for options menu.');
            }
            return;
        }
        
        // Handle individual option clicks
        if (e.target.closest('.option-icon')) {
            console.log('✅ Option icon clicked!');
            e.preventDefault();
            e.stopPropagation();
            
            const optionIcon = e.target.closest('.option-icon');
            const action = optionIcon.dataset.action;
            const modelId = optionIcon.dataset.modelId;
            
            console.log('📋 Action:', action, 'Model ID:', modelId);
            
            handleOptionClick(action, modelId);
            return;
        }
        
        // Close all menus when clicking outside
        if (!e.target.closest('.model-options-expanded')) {
            console.log('🔄 Closing all menus (clicked outside)');
            closeAllMenus();
        }
    });
    
    console.log('✅ Model navigation initialized successfully');
}

// Helper: Walk up the DOM to find the nearest element with a specific anvil-role
function findClosestByRole(startEl, roleName) {
    let el = startEl;
    while (el) {
        const role = el.getAttribute && el.getAttribute('anvil-role');
        if (role === roleName) {
            return el;
        }
        el = el.parentElement;
    }
    return null;
}

// Helper: Resolve modelId from DOM element
function resolveModelIdFromElement(el) {
    if (!el) return null;
    // 1) tag attribute (if rendered)
    let id = el.getAttribute('tag');
    if (id) {
        console.log('🔑 Found modelId via tag attribute:', id);
        return id;
    }
    // 2) data-model-id on element
    if (el.dataset && el.dataset.modelId) {
        console.log('🔑 Found modelId via data-model-id on element:', el.dataset.modelId);
        return el.dataset.modelId;
    }
    // 3) from closest nav_flow_panel container
    const fp = el.closest('[anvil-role="nav_flow_panel"]');
    if (fp) {
        const fpTag = fp.getAttribute('tag');
        if (fpTag) {
            console.log('🔑 Found modelId via flow panel tag:', fpTag);
            return fpTag;
        }
        if (fp.dataset && fp.dataset.modelId) {
            console.log('🔑 Found modelId via flow panel data-model-id:', fp.dataset.modelId);
            return fp.dataset.modelId;
        }
    }
    console.warn('⚠️ Could not resolve modelId from element.');
    return null;
}

// 2. Toggle model options display
function toggleModelOptions(flowPanel, modelId) {
    console.log('🔄 Toggling model options for:', modelId);
    console.log('🔄 Flow panel:', flowPanel);
    
    // Close other open menus first
    closeAllMenus();
    
    // Check if this panel already has expanded options
    let expandedContainer = flowPanel.querySelector('.model-options-expanded');
    console.log('🔍 Existing expanded container:', expandedContainer);
    
    if (!expandedContainer) {
        // Create the expanded options container
        expandedContainer = createExpandedOptions(modelId);
        
        // Find the flow-panel-gutter to append to
        const gutter = flowPanel.querySelector('.flow-panel-gutter');
        console.log('🔍 Flow panel gutter:', gutter);
        if (gutter) {
            gutter.appendChild(expandedContainer);
            console.log('✅ Appended expanded container to gutter');
        } else {
            console.log('❌ No gutter found, appending to flow panel');
            flowPanel.appendChild(expandedContainer);
        }
    }
    
    // Add expanded class to flow panel and dots
    flowPanel.classList.add('expanded');
    console.log('✅ Added expanded class to flow panel');
    
    const dotsLink = flowPanel.querySelector('[anvil-role="icon-link-discreet"]');
    console.log('🔍 Dots link:', dotsLink);
    if (dotsLink) {
        dotsLink.classList.add('expanded');
        console.log('✅ Added expanded class to dots link');
    }
    
    // Ensure positioning context for absolute menu
    const currentPosition = getComputedStyle(flowPanel).position;
    if (currentPosition === 'static' || !currentPosition) {
        flowPanel.style.position = 'relative';
        console.log('🧭 Set flowPanel position: relative for menu positioning');
    }
    
    // Show the expanded container
    setTimeout(() => {
        expandedContainer.classList.add('active');
        console.log('✅ Added active class to expanded container');
    }, 10);
}

// 3. Create expanded options container
function createExpandedOptions(modelId) {
    console.log('🏗️ Creating expanded options for model:', modelId);
    
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
    
    console.log('✅ Created expanded options container with 4 icons');
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
        const dotsLink = panel.querySelector('[anvil-role="icon-link-discreet"]');
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
console.log('🚀 Model navigation script loaded');
console.log('🚀 Document ready state:', document.readyState);

if (document.readyState === 'loading') {
    console.log('📅 Adding DOMContentLoaded listener');
    document.addEventListener('DOMContentLoaded', initializeModelNavigation);
} else {
    console.log('📅 DOM already ready, initializing immediately');
    initializeModelNavigation();
}

// Also try to initialize after a delay to catch Anvil's dynamic content
setTimeout(() => {
    console.log('⏰ Delayed initialization attempt');
    const existingDots = document.querySelectorAll('[anvil-role="icon-link-discreet"]');
    console.log('🔍 Found', existingDots.length, 'three-dot icons');
    existingDots.forEach((dot, index) => {
        console.log(`🔍 Dot ${index}:`, dot, 'Tag:', dot.getAttribute('tag'));
    });
}, 2000);
