// 1. Cached DOM elements for performance optimization
let cachedElements = null;
let debugMode = false; // Set to true for debugging

// 2. Initialize DOM element cache
function initializeElementCache() {
  if (cachedElements) return cachedElements;
  
  cachedElements = {
    sidebar: document.getElementById('left-sidebar') || document.querySelector('.sidebar'),
    button: document.getElementById('nav-button') || document.querySelector('.nav-button'),
    content: document.querySelector('.main-content-move'),
    contentNav: document.querySelector('.main-content-move-nav'),
    spotifyFooter: document.querySelector('.anvil-role-cap-spotify-footer')
  };
  
  if (debugMode) {
    console.log("[NAVBAR] Elements cached:", {
      sidebar: !!cachedElements.sidebar,
      button: !!cachedElements.button,
      content: !!cachedElements.content,
      contentNav: !!cachedElements.contentNav,
      spotifyFooter: !!cachedElements.spotifyFooter
    });
  }
  
  return cachedElements;
}

// 3. Main navbar visibility control function
function navbar_noModel_noSubs(visible) {
  // Ensure DOM is ready
  if (document.readyState !== 'complete' && document.readyState !== 'interactive') {
    setTimeout(() => navbar_noModel_noSubs(visible), 50);
    return;
  }
  
  try {
    const elements = initializeElementCache();
    const isMobile = window.innerWidth <= 767;
    
    // 4. Handle sidebar visibility
    if (elements.sidebar) {
      elements.sidebar.style.display = visible ? "block" : "none";
      
      // Position sidebar for mobile/desktop
      if (visible) {
        elements.sidebar.style.left = isMobile ? '-200px' : '0px';
      }
    }
    
    // 5. Handle navigation button visibility and positioning
    if (elements.button) {
      elements.button.style.display = visible ? "block" : "none";
      
      if (visible) {
        elements.button.style.left = isMobile ? '0px' : '250px';
      }
    }
    
    // 6. Adjust content margins based on sidebar visibility
    const marginLeft = (visible && elements.sidebar && !isMobile) ? '250px' : '0px';
    
    if (elements.content) {
      elements.content.style.marginLeft = marginLeft;
    }
    
    if (elements.contentNav) {
      elements.contentNav.style.marginLeft = marginLeft;
    }
    
    // 7. Ensure Spotify footer remains visible
    if (elements.spotifyFooter) {
      elements.spotifyFooter.style.display = "block";
    }
    
    if (debugMode) {
      console.log(`[NAVBAR] Navbar ${visible ? 'shown' : 'hidden'}, mobile: ${isMobile}`);
    }
    
  } catch (error) {
    console.error("[NAVBAR] Error in navbar_noModel_noSubs:", error);
  }
}

// Set a global flag to indicate this script is loaded
window.hideNavBarLoaded = true;
console.log("[NAVBAR_DEBUG] hideNavBar.js loaded and initialized");