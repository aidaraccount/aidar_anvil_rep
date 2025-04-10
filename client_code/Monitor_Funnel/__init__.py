from ._anvil_designer import Monitor_FunnelTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json
from datetime import datetime

from anvil_extras import routing
from ..nav import click_link, click_button, logout, login_check, load_var


@routing.route('funnel', title='Funnel')
class Monitor_Funnel(Monitor_FunnelTemplate):
  def __init__(self, **properties):
    
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    global user
    user = anvil.users.get_user()
    
    # Any code you write here will run before the form opens.
    if user['expiration_date'] is not None and (datetime.today().date() - user['expiration_date']).days > 0:
      routing.set_url_hash('no_subs', load_from_cache=False)
      get_open_form().SearchBar.visible = False
      
    else:
      model_id = load_var("model_id")
      self.model_id = model_id
      print(f"Monitor_Funnel model_id: {model_id}")
      
      # Load watchlists
      self.load_watchlists()
      
      # Load funnel data
      self.load_funnel_data()

  def load_watchlists(self):
    """
    Load watchlists and populate the flow panel with clickable links
    """
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
    """
    Create a click handler for watchlist links
    
    Parameters:
        watchlist_id: ID of the watchlist to activate/deactivate
        
    Returns:
        handler: Event handler function
    """
    def handler(**event_args):
      self.activate_watchlist(watchlist_id)
    return handler

  def activate_watchlist(self, watchlist_id):
    """
    Toggle watchlist activation and filter the funnel based on active watchlists
    
    Parameters:
        watchlist_id: ID of the watchlist to toggle
    """
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

    # Filter funnel for active watchlists
    print('active_wl_ids', active_wl_ids)
    
    # Load data filtered by active watchlist IDs
    self.load_funnel_data(active_wl_ids)
    
  def load_funnel_data(self, active_watchlist_ids=None):
    """
    Load and filter funnel data based on active watchlists and search term
    
    Parameters:
        active_watchlist_ids: List of active watchlist IDs to filter by
    """
    search_term = self.text_box_search.text.strip() if hasattr(self, 'text_box_search') and self.text_box_search.text else ""
    
    # Call the server to get filtered data - pass watchlist IDs directly
    data = json.loads(anvil.server.call('get_watchlist_selection', user["user_id"], active_watchlist_ids))
    
    # Apply search filter if there's a search term
    if search_term:
      data = [entry for entry in data if str(entry["Name"]).lower().find(search_term.lower()) != -1]
    
    # Update repeating panels with filtered data
    self.repeating_panel_1.items = [item for item in data if item['Status'] in ['Reconnect later', 'Not interested', None]] #BACKLOG
    self.repeating_panel_2.items = [item for item in data if item['Status'] in ['Action required', 'Requires revision', 'Waiting for decision']] #EVALUATION
    self.repeating_panel_3.items = [item for item in data if item['Status'] in ['Build connection', 'Awaiting response', 'Exploring opportunities', 'Positive response']] #CONTACTING
    self.repeating_panel_4.items = [item for item in data if item['Status'] in ['In negotiations', 'Contract in progress']] #NEGOTIATION
    self.repeating_panel_5.items = [item for item in data if item['Status'] in ['Success']] #SUCCESS
  
  def text_box_search_change(self, **event_args):
    """
    Handle search box changes and update funnel data
    
    Parameters:
        event_args: Event arguments
    """
    # Get active watchlist IDs
    active_wl_ids = []
    for component in self.flow_panel_watchlists.get_components():
      if isinstance(component, Link) and component.role == "genre-box":
        active_wl_ids.append(component.tag)
    
    # Only pass watchlist IDs if there are active ones
    watchlist_ids = active_wl_ids if active_wl_ids else None
    
    # Reload data with current filters
    self.load_funnel_data(watchlist_ids)
