from ._anvil_designer import C_TalentDev_ToggleTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class C_TalentDev_Toggle(C_TalentDev_ToggleTemplate):
  def __init__(self, **properties):
    """
    Initialize the Toggle component for Talent Development
    
    Parameters:
        properties: Additional properties to pass to the parent class
    """
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    
    # 1. Initialize component variables
    self.active_period = "30-Day"  # Default to 30-day stats
    self.on_toggle_change = None  # Callback when toggle changes
    
    # 2. Create HTML for the toggle
    self.create_toggle()
  
  def create_toggle(self):
    """
    Creates the toggle UI with 7-day and 30-day options
    """
    # Create the HTML for the toggle
    self.html = f"""
    <div class="talentdev-toggle-container">
      <div class="talentdev-toggle-label">Show growth:</div>
      <div class="talentdev-toggle-options">
        <div class="talentdev-toggle-option {self._is_active('7-Day')}" onclick="window.pyTogglePeriod('7-Day')">
          <span class="talentdev-toggle-text">7-Day</span>
        </div>
        <div class="talentdev-toggle-option {self._is_active('30-Day')}" onclick="window.pyTogglePeriod('30-Day')">
          <span class="talentdev-toggle-text">30-Day</span>
        </div>
      </div>
    </div>
    """
    
    # Register JavaScript callbacks
    self._register_callbacks()
  
  def _is_active(self, period):
    """
    Helper method to determine if a period is active
    
    Parameters:
        period: The period to check (7-Day or 30-Day)
        
    Returns:
        str: CSS class for active status
    """
    return "active" if period == self.active_period else ""
  
  def _register_callbacks(self):
    """
    Register JavaScript callbacks for the toggle functionality
    """
    # Define the toggle_period method to be called from JavaScript
    self.toggle_period_js = self.toggle_period
    
    # Export the method to JavaScript
    anvil.js.window.pyTogglePeriod = self.toggle_period_js
    
    # Log registration
    print("TOGGLE-LOG: JavaScript callbacks registered")
  
  def toggle_period(self, period):
    """
    Toggle the active period between 7-Day and 30-Day
    
    Parameters:
        period: The period to activate (7-Day or 30-Day)
        
    Returns:
        bool: True indicating successful handling of toggle request
    """
    if period != self.active_period:
      print(f"TOGGLE-LOG: Toggling period from {self.active_period} to {period}")
      self.active_period = period
      
      # Update the UI
      self.create_toggle()
      
      # Call the callback if it exists
      if self.on_toggle_change:
        self.on_toggle_change(period)
    
    return True
  
  def set_toggle_callback(self, callback):
    """
    Set the callback function to be called when the toggle changes
    
    Parameters:
        callback: The function to call when toggle changes
    """
    self.on_toggle_change = callback
