function navbar_noModel_noSubs(visible) {
  // Try both selection methods to ensure compatibility
  var sidebar = document.getElementById('left-sidebar') || document.querySelector('.sidebar');
  var button = document.getElementById('nav-button') || document.querySelector('.nav-button');
  var content = document.querySelector('.main-content-move');
  var contentNav = document.querySelector('.main-content-move-nav');
  
  // Log for debugging
  console.log("navbar_noModel_noSubs called with:", visible);
  console.log("Elements found:", {sidebar, button, content, contentNav});
  
  // Check if sidebar exists before proceeding
  if (sidebar) {
    sidebar.style.display = visible ? "block" : "none";
    
    // Only change button style if it exists
    if (button) {
      button.style.display = visible ? "block" : "none";
    }
    
    // If showing the sidebar, also handle position
    if (visible) {
      if (window.innerWidth <= 767) {
        sidebar.style.left = '-200px';
        if (button) button.style.left = '0px';
        if (content) content.style.marginLeft = '0px';
        if (contentNav) contentNav.style.marginLeft = '0px';
      } else {
        sidebar.style.left = '0px';
        if (button) button.style.left = '250px';
        if (content) content.style.marginLeft = '250px';
        if (contentNav) contentNav.style.marginLeft = '250px';
      }
    }
  } else {
    // If sidebar doesn't exist, at least try to adjust content margins
    if (content) {
      content.style.display = visible ? "block" : "none";
    }
    if (contentNav) {
      contentNav.style.display = visible ? "block" : "none";
    }
  }
}

// Set a global flag to indicate this script is loaded
window.hideNavBarLoaded = true;