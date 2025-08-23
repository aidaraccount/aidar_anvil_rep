// 1. Model Navigation Menu JavaScript
class ModelNavMenu {
    constructor() {
        this.activeMenu = null;
        this.init();
    }

    // 2. Initialize event listeners
    init() {
        document.addEventListener('click', (e) => {
            // Close any open menu when clicking outside
            if (!e.target.closest('.model-nav-options')) {
                this.closeAllMenus();
            }
        });
    }

    // 3. Create options menu for a model container
    createOptionsMenu(modelId, onSettingsClick) {
        const optionsContainer = document.createElement('div');
        optionsContainer.className = 'model-nav-options';
        optionsContainer.dataset.modelId = modelId;

        // Create three dots button
        const dotsButton = document.createElement('div');
        dotsButton.className = 'model-nav-dots';
        dotsButton.innerHTML = '<i class="fa fa-ellipsis-h"></i>';
        dotsButton.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleMenu(optionsContainer);
        });

        // Create expanded options
        const expandedContainer = document.createElement('div');
        expandedContainer.className = 'model-nav-expanded';

        // Pin icon
        const pinOption = this.createOption('fa-thumb-tack', 'Pin model', () => {
            console.log('Pin clicked for model:', modelId);
            this.closeMenu(optionsContainer);
        });

        // Megaphone icon
        const megaphoneOption = this.createOption('fa-bullhorn', 'Notifications', () => {
            console.log('Notifications clicked for model:', modelId);
            this.closeMenu(optionsContainer);
        });

        // Settings icon (existing functionality)
        const settingsOption = this.createOption('fa-sliders', 'Settings', () => {
            if (onSettingsClick) {
                onSettingsClick();
            }
            this.closeMenu(optionsContainer);
        });

        // Trash icon
        const trashOption = this.createOption('fa-trash', 'Delete model', () => {
            console.log('Delete clicked for model:', modelId);
            this.closeMenu(optionsContainer);
        });

        expandedContainer.appendChild(pinOption);
        expandedContainer.appendChild(megaphoneOption);
        expandedContainer.appendChild(settingsOption);
        expandedContainer.appendChild(trashOption);

        optionsContainer.appendChild(dotsButton);
        optionsContainer.appendChild(expandedContainer);

        return optionsContainer;
    }

    // 4. Create individual option button
    createOption(iconClass, title, onClick) {
        const option = document.createElement('div');
        option.className = 'model-nav-option';
        option.title = title;
        option.innerHTML = `<i class="fa ${iconClass}"></i>`;
        option.addEventListener('click', (e) => {
            e.stopPropagation();
            onClick();
        });
        return option;
    }

    // 5. Toggle menu visibility
    toggleMenu(optionsContainer) {
        if (this.activeMenu && this.activeMenu !== optionsContainer) {
            this.closeMenu(this.activeMenu);
        }

        const isExpanding = !optionsContainer.classList.contains('expanding');
        
        if (isExpanding) {
            this.openMenu(optionsContainer);
        } else {
            this.closeMenu(optionsContainer);
        }
    }

    // 6. Open menu with animation
    openMenu(optionsContainer) {
        this.activeMenu = optionsContainer;
        optionsContainer.classList.add('expanding');
        
        // Truncate model name to make space
        const modelLink = optionsContainer.closest('[role="nav_flow_panel"]')
            ?.querySelector('.model-nav-link');
        if (modelLink) {
            modelLink.classList.add('truncated');
        }
    }

    // 7. Close menu with animation
    closeMenu(optionsContainer) {
        if (!optionsContainer) return;
        
        optionsContainer.classList.remove('expanding');
        
        // Restore model name
        const modelLink = optionsContainer.closest('[role="nav_flow_panel"]')
            ?.querySelector('.model-nav-link');
        if (modelLink) {
            modelLink.classList.remove('truncated');
        }
        
        if (this.activeMenu === optionsContainer) {
            this.activeMenu = null;
        }
    }

    // 8. Close all open menus
    closeAllMenus() {
        const allMenus = document.querySelectorAll('.model-nav-options.expanding');
        allMenus.forEach(menu => this.closeMenu(menu));
    }

    // 9. Update menu for model container
    updateModelContainer(container, modelId, onSettingsClick) {
        // Remove existing options menu
        const existingOptions = container.querySelector('.model-nav-options');
        if (existingOptions) {
            existingOptions.remove();
        }

        // Create new options menu
        const optionsMenu = this.createOptionsMenu(modelId, onSettingsClick);
        
        // Find the flow-panel-gutter and append the options menu there
        const gutter = container.querySelector('.flow-panel-gutter');
        if (gutter) {
            gutter.appendChild(optionsMenu);
        } else {
            // Fallback: append to container
            container.appendChild(optionsMenu);
        }
    }
}

// 10. Global instance and initialization
window.modelNavMenu = new ModelNavMenu();

// 11. Helper function for Anvil integration
function initializeModelNavigation() {
    if (!window.modelNavMenu) {
        window.modelNavMenu = new ModelNavMenu();
    }
}

// 12. Function to clear model navigation (for refresh)
function clearModelNavigation() {
    if (window.modelNavMenu) {
        window.modelNavMenu.closeAllMenus();
    }
    
    // Remove all options menus from DOM
    const optionsMenus = document.querySelectorAll('.model-nav-options');
    optionsMenus.forEach(menu => menu.remove());
}

// 13. Function to add options menu to existing model container
function addModelOptionsMenu(containerId, modelId, onSettingsClick) {
    // Use setTimeout to ensure DOM is ready
    setTimeout(() => {
        // Try multiple selectors to find the container
        let container = document.querySelector(`[tag="${containerId}"]`);
        if (!container) {
            container = document.querySelector(`[anvil-tag="${containerId}"]`);
        }
        if (!container) {
            // Look for flow panel with role nav_flow_panel that contains a link with the model ID
            const flowPanels = document.querySelectorAll('[anvil-role="nav_flow_panel"]');
            for (let panel of flowPanels) {
                const link = panel.querySelector(`[tag="${containerId}"]`);
                if (link) {
                    container = panel;
                    break;
                }
            }
        }
        
        console.log('Looking for container with ID:', containerId, 'Found:', container);
        
        if (container && window.modelNavMenu) {
            console.log('Adding options menu for model:', modelId);
            // Create a wrapper function for Anvil callback
            const settingsCallback = () => {
                if (typeof onSettingsClick === 'function') {
                    onSettingsClick();
                } else {
                    // Fallback to direct navigation if callback fails
                    console.log('Settings clicked for model:', modelId);
                }
            };
            window.modelNavMenu.updateModelContainer(container, modelId, settingsCallback);
        } else {
            console.log('Container or modelNavMenu not found. Container:', container, 'ModelNavMenu:', window.modelNavMenu);
            console.log('Available flow panels:', document.querySelectorAll('[anvil-role="nav_flow_panel"]'));
        }
    }, 500); // Increased timeout to ensure Anvil DOM is ready
}

// 14. Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeModelNavigation);
} else {
    initializeModelNavigation();
}
