from ._anvil_designer import Monitor_FunnelTemplate
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
    - Optimized for performance
    """
    # Get active watchlist IDs (do this once)
    active_wl_ids = []
    for component in self.flow_panel_watchlists.get_components():
      if isinstance(component, Link) and component.role == "genre-box":
        active_wl_ids.append(int(component.tag))
    
    print('active_wl_ids', active_wl_ids)
    
    # Get search term (do this once)
    search_term = self.text_box_search.text.strip().lower() if hasattr(self, 'text_box_search') and self.text_box_search.text else ""
    
    # Prepare category lists
    backlog_items = []
    evaluation_items = []
    contacting_items = []
    negotiation_items = []
    success_items = []
    
    # Set up status category checks (avoid repeated string comparisons)
    backlog_statuses = {'Reconnect later', 'Not interested', None}
    evaluation_statuses = {'Action required', 'Requires revision', 'Waiting for decision'}
    contacting_statuses = {'Build connection', 'Awaiting response', 'Exploring opportunities', 'Positive response'}
    negotiation_statuses = {'In negotiations', 'Contract in progress'}
    success_statuses = {'Success'}
    
    # Single-pass filtering - process each item only once
    for item in self.all_artists_data:
      # Apply watchlist filter
      if active_wl_ids and ('watchlist_id' not in item or item['watchlist_id'] not in active_wl_ids):
        continue
        
      # Apply search filter
      if search_term and str(item.get("Name", "")).lower().find(search_term) == -1:
        continue
      
      # Categorize the item (only once)
      status = item.get('Status')
      if status in backlog_statuses or (status is None and None in backlog_statuses):
        backlog_items.append(item)
      elif status in evaluation_statuses:
        evaluation_items.append(item)
      elif status in contacting_statuses:
        contacting_items.append(item)
      elif status in negotiation_statuses:
        negotiation_items.append(item)
      elif status in success_statuses:
        success_items.append(item)
    
    # Update UI in batch (fewer UI updates)
    self.repeating_panel_1.items = backlog_items
    self.repeating_panel_2.items = evaluation_items
    self.repeating_panel_3.items = contacting_items
    self.repeating_panel_4.items = negotiation_items
    self.repeating_panel_5.items = success_items

  def text_box_search_change(self, **event_args):
    """
    Handle search box changes and filter displayed data
    
    Parameters:
        event_args: Event arguments
    """
    # Simply call filter_and_display_data which will handle both
    # active watchlists and search term filtering
    self.filter_and_display_data()
