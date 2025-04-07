// Mobile reordering script for Home component
// This script dynamically reorders the Home sections on mobile devices

(function() {
  // Function to check if device is mobile
  function isMobile() {
    return window.innerWidth <= 768;
  }

  // Function to reorder the sections
  function reorderSections() {
    if (!isMobile()) return;
    
    // Get the parent container
    const contentPanel = document.querySelector('.anvil-container[anvil-container-name="content_panel"]');
    if (!contentPanel) return;
    
    // Get all the sections
    const agentsSection = document.querySelector('.anvil-container[anvil-container-name="sec_agents"]');
    const nextSection = document.querySelector('.anvil-container[anvil-container-name="sec_next"]');
    const hotSection = document.querySelector('.anvil-container[anvil-container-name="sec_hot"]');
    const shortsSection = document.querySelector('.anvil-container[anvil-container-name="sec_shorts"]');
    
    // Check if all sections exist
    if (!agentsSection || !nextSection || !hotSection || !shortsSection) return;
    
    // Store original parents to restore on desktop
    if (!agentsSection.originalParent) {
      agentsSection.originalParent = agentsSection.parentNode;
      nextSection.originalParent = nextSection.parentNode;
      hotSection.originalParent = hotSection.parentNode;
      shortsSection.originalParent = shortsSection.parentNode;
    }
    
    // Create a temporary container for our ordered sections
    let tempContainer = document.createElement('div');
    tempContainer.id = "mobile-ordered-sections";
    tempContainer.style.width = "100%";
    tempContainer.style.display = "flex";
    tempContainer.style.flexDirection = "column";
    
    // Append sections in the desired order
    tempContainer.appendChild(agentsSection);
    tempContainer.appendChild(nextSection);
    tempContainer.appendChild(hotSection);
    tempContainer.appendChild(shortsSection);
    
    // Clear out the content panel and append our ordered container
    while (contentPanel.firstChild) {
      contentPanel.removeChild(contentPanel.firstChild);
    }
    contentPanel.appendChild(tempContainer);
  }
  
  // Function to restore original structure for desktop
  function restoreOriginalOrder() {
    if (isMobile()) return;
    
    const tempContainer = document.getElementById("mobile-ordered-sections");
    if (!tempContainer) return;
    
    // Get all the sections
    const agentsSection = document.querySelector('.anvil-container[anvil-container-name="sec_agents"]');
    const nextSection = document.querySelector('.anvil-container[anvil-container-name="sec_next"]');
    const hotSection = document.querySelector('.anvil-container[anvil-container-name="sec_hot"]');
    const shortsSection = document.querySelector('.anvil-container[anvil-container-name="sec_shorts"]');
    
    // Check if all sections exist and have stored original parents
    if (!agentsSection || !agentsSection.originalParent) return;
    
    // Restore each section to its original parent
    agentsSection.originalParent.appendChild(agentsSection);
    nextSection.originalParent.appendChild(nextSection);
    hotSection.originalParent.appendChild(hotSection);
    shortsSection.originalParent.appendChild(shortsSection);
    
    // Remove the temporary container
    tempContainer.parentNode.removeChild(tempContainer);
  }
  
  // Handle resizing
  function handleResize() {
    if (isMobile()) {
      reorderSections();
    } else {
      restoreOriginalOrder();
    }
  }
  
  // Initialize when DOM is fully loaded
  document.addEventListener('DOMContentLoaded', function() {
    handleResize();
    window.addEventListener('resize', handleResize);
  });
  
  // For Anvil, we need to hook into their components system
  // Check periodically if sections are available (they might load after our script)
  let checkInterval = setInterval(function() {
    const agentsSection = document.querySelector('.anvil-container[anvil-container-name="sec_agents"]');
    if (agentsSection) {
      clearInterval(checkInterval);
      handleResize();
    }
  }, 100);
})();
