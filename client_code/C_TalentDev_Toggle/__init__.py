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
    self.toggle_type = properties.get('toggle_type', 'period')  # period, format, or sort_by
    self.options = properties.get('options', [])
    self.labels = properties.get('labels', [])
    self.toggle_label = properties.get('toggle_label', '')
    self.active_value = ''
    self.on_toggle_change = None  # Callback when toggle changes
    
    # Set default active value based on toggle type
    if self.toggle_type == 'period':
      self.active_value = "30d"
      if not self.options:
        self.options = ["7d", "30d"]
      if not self.labels:
        self.labels = ["7-Day", "30-Day"]
      if not self.toggle_label:
        self.toggle_label = "display"
    elif self.toggle_type == 'format':
      self.active_value = "abs"
      if not self.options:
        self.options = ["abs", "pct"]
      if not self.labels:
        self.labels = ["#", "%"]
      if not self.toggle_label:
        self.toggle_label = "display"
    elif self.toggle_type == 'sort_by':
      self.active_value = "growth"
      if not self.options:
        self.options = ["current", "growth"]
      if not self.labels:
        self.labels = ["Current", "Growth"]
      if not self.toggle_label:
        self.toggle_label = "sort by"
    
    # 2. Create HTML for the toggle
    self.create_toggle()
  
  def create_toggle(self):
    """
    Creates the toggle UI with the configured options
    """
    # Create options HTML
    options_html = ""
    for i, option in enumerate(self.options):
      label = self.labels[i] if i < len(self.labels) else option
      options_html += f"""
        <div class="talentdev-toggle-option {self._is_active(option)}" 
             onclick="window.{self.js_function_name}('{self.toggle_type}', '{option}')">
          {label}
        </div>
      """
    
    # Create the HTML for the toggle
    self.html = f"""
    <div class="talentdev-toggle-container">
      <div class="talentdev-toggle-label">{self.toggle_label}</div>
      <div class="talentdev-toggle-options">
        {options_html}
      </div>
    </div>
    """
    
    # Register JavaScript callbacks
    self._register_callbacks()
  
  def _is_active(self, option):
    """
    Helper method to determine if an option is active
    
    Parameters:
        option: The option to check
        
    Returns:
        str: CSS class for active status
    """
    return "active" if option == self.active_value else ""
  
  def _register_callbacks(self):
    """
    Register JavaScript callbacks for the toggle functionality
    """
    # Define the toggle_option method to be called from JavaScript
    self.toggle_option_js = self.toggle_option
    
    # Get a unique function name for this toggle instance
    self.js_function_name = f"pyToggleOption_{self.toggle_type}"
    
    # Export the method to JavaScript with the unique name
    anvil.js.window[self.js_function_name] = self.toggle_option_js
    
    # Update the HTML to use the unique function name
    self.create_toggle()
    
    # Log registration
    print(f"TOGGLE-LOG: JavaScript callbacks registered for {self.toggle_type} as {self.js_function_name}")
  
  def toggle_option(self, toggle_type, option):
    """
    Toggle the active option when clicked
    
    Parameters:
        toggle_type: The type of toggle being changed
        option: The option to activate
        
    Returns:
        bool: True indicating successful handling of toggle request
    """
    # Only process if this is the correct toggle type
    if toggle_type != self.toggle_type:
      return True
      
    if option != self.active_value:
      print(f"TOGGLE-LOG: Toggling {self.toggle_type} from {self.active_value} to {option}")
      self.active_value = option
      
      # Update the UI
      self.create_toggle()
      
      # Call the callback if it exists
      if self.on_toggle_change:
        self.on_toggle_change(toggle_type, option)
    
    return True
  
  def set_toggle_callback(self, callback):
    """
    Set the callback function to be called when the toggle changes
    
    Parameters:
        callback: The function to call when toggle changes
    """
    self.on_toggle_change = callback
    
  def get_active_value(self):
    """
    Get the currently active toggle value
    
    Returns:
        str: The active toggle value
    """
    return self.active_value
