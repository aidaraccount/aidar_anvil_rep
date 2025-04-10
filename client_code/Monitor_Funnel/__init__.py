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
      
      # Load all artists data once
      self.all_artists_data = json.loads(anvil.server.call('get_watchlist_selection', user["user_id"], None))
      print(f"Loaded {len(self.all_artists_data)} artists in total")
      
      # Load watchlists
      self.load_watchlists()
      
      # Initial display of all data
      self.filter_and_display_data()

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

    # After toggling, filter and display data
    self.filter_and_display_data()
    
  def filter_and_display_data(self):
    """
    Filter and display data based on active watchlists and search term
    """
    # Get active watchlist IDs
    active_wl_ids = []
    for component in self.flow_panel_watchlists.get_components():
      if isinstance(component, Link) and component.role == "genre-box":
        active_wl_ids.append(int(component.tag))
    
    print('active_wl_ids', active_wl_ids)
    
    # Get search term
    search_term = self.text_box_search.text.strip() if hasattr(self, 'text_box_search') and self.text_box_search.text else ""
    
    # Start with all data
    filtered_data = self.all_artists_data.copy()
    
    # Filter by watchlists if any are active
    if active_wl_ids:
      filtered_data = [item for item in filtered_data if 'watchlist_id' in item and item['watchlist_id'] in active_wl_ids]
    
    # Apply search filter if there's a search term
    if search_term:
      filtered_data = [entry for entry in filtered_data if str(entry["Name"]).lower().find(search_term.lower()) != -1]
    
    # Update repeating panels with filtered data
    self.repeating_panel_1.items = [item for item in filtered_data if item['Status'] in ['Reconnect later', 'Not interested', None]] #BACKLOG
    self.repeating_panel_2.items = [item for item in filtered_data if item['Status'] in ['Action required', 'Requires revision', 'Waiting for decision']] #EVALUATION
    self.repeating_panel_3.items = [item for item in filtered_data if item['Status'] in ['Build connection', 'Awaiting response', 'Exploring opportunities', 'Positive response']] #CONTACTING
    self.repeating_panel_4.items = [item for item in filtered_data if item['Status'] in ['In negotiations', 'Contract in progress']] #NEGOTIATION
    self.repeating_panel_5.items = [item for item in filtered_data if item['Status'] in ['Success']] #SUCCESS
  
  def text_box_search_change(self, **event_args):
    """
    Handle search box changes and filter displayed data
    
    Parameters:
        event_args: Event arguments
    """
    # Simply call filter_and_display_data which will handle both
    # active watchlists and search term filtering
    self.filter_and_display_data()
