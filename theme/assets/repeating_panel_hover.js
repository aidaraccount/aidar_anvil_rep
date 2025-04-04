// Repeating Panel Hover Effect
// This script adds hover effects to repeating panel rows

document.addEventListener('DOMContentLoaded', function() {
  // Apply hover effect to all repeating panel rows
  function applyHoverEffects() {
    // Target all column-panel elements inside repeating-panel
    var repPanelRows = document.querySelectorAll('.repeating-panel .hide-while-paginating .column-panel');
    
    repPanelRows.forEach(function(row) {
      // Add a class to make targeting with CSS easier
      row.classList.add('rep-panel-row');
      
      // Add hover event listeners
      row.addEventListener('mouseenter', function() {
        this.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';
        this.style.borderRadius = '4px';
      });
      
      row.addEventListener('mouseleave', function() {
        this.style.backgroundColor = 'transparent';
      });
    });
  }
  
  // Initial application
  applyHoverEffects();
  
  // Re-apply when DOM changes (for dynamically loaded content)
  // Using a simple polling approach for compatibility
  setInterval(applyHoverEffects, 2000);
});
