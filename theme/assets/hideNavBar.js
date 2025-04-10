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
    
    // Log detailed element information
    console.log("[NAVBAR_DEBUG] Elements found:", {
      sidebar: sidebar ? "Found" : "Not found",
      button: button ? "Found" : "Not found",
      content: content ? "Found" : "Not found",
      contentNav: contentNav ? "Found" : "Not found"
    });
    
    // Handle sidebar visibility
    if (sidebar) {
      console.log("[NAVBAR_DEBUG] Setting sidebar display to:", visible ? "block" : "none");
      sidebar.style.display = visible ? "block" : "none";
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
      content.style.display = visible ? "block" : "none";
      if (visible && sidebar) {
        content.style.marginLeft = window.innerWidth <= 767 ? '0px' : '250px';
      } else {
        content.style.marginLeft = '0px';
      }
    }
    
    if (contentNav) {
      contentNav.style.display = visible ? "block" : "none";
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
  } catch (error) {
    console.error("[NAVBAR_DEBUG] Error in navbar_noModel_noSubs:", error);
  }
}

// Set a global flag to indicate this script is loaded
window.hideNavBarLoaded = true;
console.log("[NAVBAR_DEBUG] hideNavBar.js loaded and initialized");