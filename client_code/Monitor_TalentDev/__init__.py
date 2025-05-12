from ._anvil_designer import Monitor_TalentDevTemplate
from anvil import *
import stripe.checkout
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json
from datetime import datetime

from anvil_extras import routing
from ..nav import click_link, click_button, logout, login_check, load_var


@routing.route('talent_dev', title='Development')
class Monitor_TalentDev(Monitor_TalentDevTemplate):
  def __init__(self, **properties):
    """
    Initialize the Monitor_TalentDev component
    
    Parameters:
        properties: Additional properties to pass to the parent class
    """
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Get current user
    global user
    user = anvil.users.get_user()
    
    # Check user subscription status
    if user is None:
      pass
    elif user['expiration_date'] is not None and (datetime.today().date() - user['expiration_date']).days > 0:
      routing.set_url_hash('settings?section=Subscription', load_from_cache=False)
      get_open_form().SearchBar.visible = False
    else:
      # Load model ID
      model_id = load_var("model_id")
      print(f"Monitor_TalentDev model_id: {model_id}")
      self.model_id = model_id

      # load_watchlists
      self.load_watchlists()
      
      # Wait for all components to fully initialize before setting up callbacks
      anvil.js.call_js('setTimeout', self._setup_toggle_callbacks, 100)

  
  def load_watchlists(self):
    watchlists = json.loads(anvil.server.call("get_watchlist_ids", user['user_id']))
    print('watchlists:', watchlists)

    if watchlists is not None and len(watchlists) > 0:      
      active_wl_ids = []
      
      for i in range(0, len(watchlists)):
        wl_id = watchlists[i]["watchlist_id"]
        wl_id_str = str(wl_id)
                
        # Create the link with the appropriate role
        wl_link = Link(
          text=watchlists[i]["watchlist_name"], tag=wl_id, role="genre-box"
        )
  
        wl_link.set_event_handler(
          "click", self.create_activate_watchlist_handler(wl_id)
        )
        self.flow_panel_watchlists.add_component(wl_link)
        
  def create_activate_watchlist_handler(self, watchlist_id):
    def handler(**event_args):
      self.activate_watchlist(watchlist_id)
    return handler

  def activate_watchlist(self, watchlist_id):    
    # Toggle the clicked watchlist's activation state
    for component in self.flow_panel_watchlists.get_components():
      if isinstance(component, Link):
        if int(component.tag) == watchlist_id:
          # Toggle the role - if active make inactive, and vice versa
          if component.role == "genre-box":
            component.role = "genre-box-deselect"
          else:
            component.role = "genre-box"

    # Collect all currently active watchlist IDs (role = "genre-box")
    active_wl_ids = []
    for component in self.flow_panel_watchlists.get_components():
      if isinstance(component, Link) and component.role == "genre-box":
        active_wl_ids.append(component.tag)

    # Filter table for active watchlists
    print('active_wl_ids', active_wl_ids)
    
    # Pass the active watchlist IDs to the table component for filtering
    if hasattr(self, 'c_talent_dev_table_1') and self.c_talent_dev_table_1 is not None:
      self.c_talent_dev_table_1.filter_by_watchlists(active_wl_ids)

  
  def _setup_toggle_callbacks(self):
    """
    Set up toggle callbacks after ensuring components are fully initialized
    """
    try:
      # Set up toggle callbacks
      print("Setting up toggle callbacks...")
      if hasattr(self, 'period_toggle') and self.period_toggle is not None:
        self.period_toggle.set_toggle_callback(self.handle_toggle_change)
        print("Period toggle callback set")
        
      if hasattr(self, 'format_toggle') and self.format_toggle is not None:
        self.format_toggle.set_toggle_callback(self.handle_toggle_change)
        print("Format toggle callback set")
        
      if hasattr(self, 'sort_by_toggle') and self.sort_by_toggle is not None:
        self.sort_by_toggle.set_toggle_callback(self.handle_toggle_change)
        print("Sort by toggle callback set")
        
      print("All toggle callbacks set up successfully")
    except Exception as e:
      print(f"Error setting up toggle callbacks: {e}")

  # HANDLE TOGGLE CHANGE
  def handle_toggle_change(self, toggle_type, value):
    """
    Handle toggle changes from any toggle component and update C_TalentDev_Table
    
    Parameters:
        toggle_type: The type of toggle being changed (period, format, sort_by)
        value: The new value selected
    """
    print(f"MONITOR-LOG: Toggle {toggle_type} changed to {value}")
    
    # Update the table component with the new settings
    if toggle_type == 'period':
      self.c_talent_dev_table_1.active_period = value
    elif toggle_type == 'format':
      self.c_talent_dev_table_1.active_format = value
    elif toggle_type == 'sort_by':
      self.c_talent_dev_table_1.active_sort_by = value
      
    # Check if sorting is currently active and reapply it with new toggle settings
    if hasattr(self.c_talent_dev_table_1, 'sort_column') and self.c_talent_dev_table_1.sort_column:
      # Store current sort settings
      current_sort_column = self.c_talent_dev_table_1.sort_column
      current_sort_direction = self.c_talent_dev_table_1.sort_direction
      
      # Resort the data with the new toggle settings
      self.c_talent_dev_table_1._sort_data()
    
    # Refresh the table with new settings
    self.c_talent_dev_table_1.create_table()
    
    return True

  # SEARCH
  def text_box_search_change(self, **event_args):
    """
    Handle search box changes
    
    Parameters:
        event_args: Event arguments
    """
    # Pass the search term to the table for filtering
    search_term = self.text_box_search.text.strip() if self.text_box_search.text else ""
    
    # Update the filter in the table component
    if hasattr(self, 'c_talent_dev_table_1') and self.c_talent_dev_table_1 is not None:
      self.c_talent_dev_table_1.filter_by_artist_name(search_term)
