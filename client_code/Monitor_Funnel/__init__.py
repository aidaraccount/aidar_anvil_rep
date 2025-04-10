from ._anvil_designer import Monitor_FunnelTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json
from datetime import datetime
import time

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
      start_time = time.time()
      self.all_artists_data = json.loads(anvil.server.call('get_watchlist_selection', user["user_id"], None))
      loading_time = time.time() - start_time
      print(f"TIMING: Initial data load took {loading_time:.4f} seconds - Loaded {len(self.all_artists_data)} artists in total")
      
      # Load watchlists
      start_time = time.time()
      self.load_watchlists()
      watchlist_time = time.time() - start_time
      print(f"TIMING: Loading watchlists took {watchlist_time:.4f} seconds")
      
      # Initial display of all data
      start_time = time.time()
      self.filter_and_display_data(is_initial=True)
      display_time = time.time() - start_time
      print(f"TIMING: Initial display took {display_time:.4f} seconds")

  def load_watchlists(self):
    """
    Load watchlists and populate the flow panel with clickable links
    """
    start_time = time.time()
    watchlists = json.loads(anvil.server.call("get_watchlist_ids", user['user_id']))
    server_time = time.time() - start_time
    print(f"TIMING: Server call for watchlists took {server_time:.4f} seconds")
    print('watchlists:', watchlists)

    if watchlists is not None and len(watchlists) > 0:
      start_time = time.time()  
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
      
      ui_time = time.time() - start_time
      print(f"TIMING: Creating and adding watchlist UI components took {ui_time:.4f} seconds")
  
  def create_activate_watchlist_handler(self, watchlist_id):
    """
    Create a click handler for watchlist links
    
    Parameters:
        watchlist_id: ID of the watchlist to activate/deactivate
        
    Returns:
        handler: Event handler function
    """
    def handler(**event_args):
      start_time = time.time()
      self.activate_watchlist(watchlist_id)
      print(f"TIMING: Total activate_watchlist processing took {time.time() - start_time:.4f} seconds")
    return handler

  def activate_watchlist(self, watchlist_id):
    """
    Toggle watchlist activation and filter the funnel based on active watchlists
    
    Parameters:
        watchlist_id: ID of the watchlist to toggle
    """
    # Toggle the clicked watchlist's activation state
    start_time = time.time()
    for component in self.flow_panel_watchlists.get_components():
      if isinstance(component, Link):
        if int(component.tag) == watchlist_id:
          # Toggle the role - if active make inactive, and vice versa
          if component.role == "genre-box":
            component.role = "genre-box-deselect"
          else:
            component.role = "genre-box"
    toggle_time = time.time() - start_time
    print(f"TIMING: Toggling watchlist UI took {toggle_time:.4f} seconds")

    # After toggling, filter and display data
    start_time = time.time()
    self.filter_and_display_data()
    filter_time = time.time() - start_time
    print(f"TIMING: Filter and display after toggle took {filter_time:.4f} seconds")
    
  def filter_and_display_data(self, is_initial=False):
    """
    Filter and display data based on active watchlists and search term
    - Optimized for performance
    
    Parameters:
        is_initial: Whether this is the initial loading (to bypass certain checks)
    """
    overall_start = time.time()
    
    # Get active watchlist IDs (do this once)
    wl_start = time.time()
    active_wl_ids = []
    for component in self.flow_panel_watchlists.get_components():
      if isinstance(component, Link) and component.role == "genre-box":
        active_wl_ids.append(int(component.tag))
    
    wl_time = time.time() - wl_start
    print(f"TIMING: Getting active watchlist IDs took {wl_time:.4f} seconds")
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
    
    # Print size of data to process
    print(f"TIMING: Processing {len(self.all_artists_data)} total items")
    
    # Single-pass filtering - process each item only once
    filter_start = time.time()
    item_count = 0
    watchlist_skip_count = 0
    search_skip_count = 0
    
    for item in self.all_artists_data:
      item_count += 1
      
      # Only do expensive filtering if needed 
      if is_initial and not active_wl_ids and not search_term:
        # Fast path for initial load with no filters
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
      else:
        # Normal filtering path
        # Apply watchlist filter
        if active_wl_ids and ('watchlist_id' not in item or item['watchlist_id'] not in active_wl_ids):
          watchlist_skip_count += 1
          continue
          
        # Apply search filter
        if search_term and str(item.get("Name", "")).lower().find(search_term) == -1:
          search_skip_count += 1
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
    
    filter_time = time.time() - filter_start
    print(f"TIMING: Filtering {item_count} items took {filter_time:.4f} seconds")
    print(f"TIMING: Items skipped by watchlist filter: {watchlist_skip_count}")
    print(f"TIMING: Items skipped by search filter: {search_skip_count}")
    print(f"TIMING: Items in categories - Backlog: {len(backlog_items)}, Evaluation: {len(evaluation_items)}, Contacting: {len(contacting_items)}, Negotiation: {len(negotiation_items)}, Success: {len(success_items)}")
    
    # Update UI in batch (fewer UI updates)
    ui_start = time.time()
    self.repeating_panel_1.items = backlog_items
    self.repeating_panel_2.items = evaluation_items
    self.repeating_panel_3.items = contacting_items
    self.repeating_panel_4.items = negotiation_items
    self.repeating_panel_5.items = success_items
    ui_time = time.time() - ui_start
    
    print(f"TIMING: Updating UI panels took {ui_time:.4f} seconds")
    print(f"TIMING: Total filter_and_display took {time.time() - overall_start:.4f} seconds")

  def text_box_search_change(self, **event_args):
    """
    Handle search box changes and filter displayed data
    
    Parameters:
        event_args: Event arguments
    """
    # Simply call filter_and_display_data which will handle both
    # active watchlists and search term filtering
    start_time = time.time()
    self.filter_and_display_data()
    print(f"TIMING: Search filtering took {time.time() - start_time:.4f} seconds")
