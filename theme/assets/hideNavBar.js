// Wait for DOM to be fully loaded before defining functions
document.addEventListener('DOMContentLoaded', function() {
  console.log("[NAVBAR_DEBUG] DOMContentLoaded event fired");
});

// Define the function with robust error handling
function navbar_noModel_noSubs(visible) {
  console.log("[NAVBAR_DEBUG] Function called with parameter:", visible);
  
  // Make sure DOM is ready before attempting to access elements
  if (document.readyState !== 'complete' && document.readyState !== 'interactive') {
    console.log("[NAVBAR_DEBUG] Document not ready, scheduling call for later");
    // Schedule for when DOM is ready
    setTimeout(function() {
      navbar_noModel_noSubs(visible);
    }, 100);
    return;
  }
  
  try {
    // Try different selector approaches
    var sidebar = document.getElementById('left-sidebar');
    if (!sidebar) {
      sidebar = document.querySelector('.sidebar');
      console.log("[NAVBAR_DEBUG] Using .sidebar selector instead:", sidebar ? "Found" : "Not found");
    }
    
    var button = document.getElementById('nav-button');
    if (!button) {
      button = document.querySelector('.nav-button');
      console.log("[NAVBAR_DEBUG] Using .nav-button selector instead:", button ? "Found" : "Not found");
    }
    
    var content = document.querySelector('.main-content-move');
    var contentNav = document.querySelector('.main-content-move-nav');
    var spotifyFooter = document.querySelector('.anvil-role-cap-spotify-footer');
    
    // Log detailed element information
    console.log("[NAVBAR_DEBUG] Elements found:", {
      sidebar: sidebar ? "Found" : "Not found",
      button: button ? "Found" : "Not found",
      content: content ? "Found" : "Not found",
      contentNav: contentNav ? "Found" : "Not found",
      spotifyFooter: spotifyFooter ? "Found" : "Not found"
    });
    
    // Handle sidebar visibility
    if (sidebar) {
      console.log("[NAVBAR_DEBUG] Setting sidebar display to:", visible ? "block" : "none");
      sidebar.style.display = visible ? "block" : "none";
      
      // Update agent sidebar width when in creation mode
      updateAgentSidebarWidth(visible);
    } else {
      console.log("[NAVBAR_DEBUG] WARNING: Sidebar element not found!");
    }
    
    // Handle button visibility
    if (button) {
      console.log("[NAVBAR_DEBUG] Setting button display to:", visible ? "block" : "none");
      button.style.display = visible ? "block" : "none";
    }
    
    // Handle content margin adjustments regardless of sidebar existence
    if (content) {
      // Don't hide content completely when sidebar is hidden, just adjust margins
      if (visible && sidebar) {
        content.style.marginLeft = window.innerWidth <= 767 ? '0px' : '250px';
      } else {
        content.style.marginLeft = '0px';
      }
    }
    
    if (contentNav) {
      // Don't hide contentNav completely when sidebar is hidden, just adjust margins
      if (visible && sidebar) {
        contentNav.style.marginLeft = window.innerWidth <= 767 ? '0px' : '250px';
      } else {
        contentNav.style.marginLeft = '0px';
      }
    }
    
    // Position sidebar and button if showing
    if (visible && sidebar) {
      if (window.innerWidth <= 767) {
        console.log("[NAVBAR_DEBUG] Mobile layout detected");
        sidebar.style.left = '-200px';
        if (button) button.style.left = '0px';
      } else {
        console.log("[NAVBAR_DEBUG] Desktop layout detected");
        sidebar.style.left = '0px';
        if (button) button.style.left = '250px';
      }
    }
    
    // Ensure Spotify player remains visible
    if (spotifyFooter) {
      console.log("[NAVBAR_DEBUG] Ensuring Spotify footer remains visible");
      spotifyFooter.style.display = "block";
    }
  } catch (error) {
    console.error("[NAVBAR_DEBUG] Error in navbar_noModel_noSubs:", error);
  }
}

// Function to update agent sidebar width based on left sidebar visibility
function updateAgentSidebarWidth(isLeftSidebarVisible) {
  const agentSidebar = document.getElementById('agent-sidebar');
  
  if (agentSidebar) {
    // Check if agent sidebar is in creation mode
    const isInCreation = agentSidebar.classList.contains('in-creation');
    
    if (isInCreation) {
      // In creation mode: adjust width based on left sidebar visibility
      // - If left sidebar is visible: agent sidebar width = 100% - 250px (normal)
      // - If left sidebar is hidden: agent sidebar width = 100% + 250px (extended)
      const offset = isLeftSidebarVisible ? '250px' : '-250px';
      
      // Update CSS variable
      document.documentElement.style.setProperty('--left-sidebar-offset', offset);
      
      console.log("[NAVBAR_DEBUG] Updated agent sidebar width for creation mode. Left sidebar visible:", isLeftSidebarVisible, "Offset:", offset);
    } else {
      // Normal mode: standard offset behavior
      const offset = isLeftSidebarVisible ? '250px' : '0px';
      document.documentElement.style.setProperty('--left-sidebar-offset', offset);
      
      console.log("[NAVBAR_DEBUG] Updated agent sidebar width for normal mode. Left sidebar visible:", isLeftSidebarVisible, "Offset:", offset);
    }
  }
}

// Initialize agent sidebar width on page load
function initializeAgentSidebarWidth() {
  const leftSidebar = document.getElementById('left-sidebar');
  if (leftSidebar) {
    const computedStyle = window.getComputedStyle(leftSidebar);
    const isVisible = computedStyle.display !== 'none' && leftSidebar.style.display !== 'none';
    updateAgentSidebarWidth(isVisible);
    console.log("[NAVBAR_DEBUG] Initialized agent sidebar width. Left sidebar visible:", isVisible);
  }
}

// Call initialization when DOM is ready
document.addEventListener('DOMContentLoaded', initializeAgentSidebarWidth);
// Also call on window load as backup
window.addEventListener('load', initializeAgentSidebarWidth);

// Set a global flag to indicate this script is loaded
window.hideNavBarLoaded = true;
console.log("[NAVBAR_DEBUG] hideNavBar.js loaded and initialized");