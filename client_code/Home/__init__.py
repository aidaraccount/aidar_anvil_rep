from ._anvil_designer import HomeTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json
from datetime import datetime
from anvil_labs.non_blocking import call_async
import time
import uuid

from anvil_extras import routing
from ..nav import click_link, click_button, click_box, logout, login_check, load_var, save_var

from ..C_Short import C_Short


@routing.route('', title='Home')
@routing.route('home', title='Home')
class Home(HomeTemplate):
  # Class variable to track the current active instance
  _active_instance = None
  _last_init_time = 0
  _min_time_between_inits = 0.5  # seconds
  
  def __init__(self, **properties):
    # Generate a unique instance ID
    self.instance_id = str(uuid.uuid4())[:8]
    
    # Print detailed diagnostics
    route_hash = anvil.js.window.location.hash
    current_time = time.time()
    print(f"HOME INIT [{self.instance_id}] - Route: '{route_hash}' - Time: {datetime.now()}", flush=True)
    
    # Always set this as the active instance so callbacks update the correct UI
    Home._active_instance = self
    
    # Check if this is a duplicate initialization within the threshold period
    time_since_last_init = current_time - Home._last_init_time
    
    if time_since_last_init < Home._min_time_between_inits:
      print(f"HOME INIT [{self.instance_id}] - Skipping initialization ({time_since_last_init:.3f}s since last init)", flush=True)
      self.init_components(**properties)
      
      # Still need to handle possible UI setup for this instance
      self.colpan_wl_selection.visible = False
      self.no_watchlists.visible = False
      self.no_shorts.visible = False
      self.reload.visible = False
      return
    
    # Update the last initialization time
    Home._last_init_time = current_time
    
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    global user
    user = anvil.users.get_user()
    
    # Any code you write here will run before the form opens.
    if user is None or user == 'None':
      self.visible = False
      print(f"HOME INIT [{self.instance_id}] - No user, hiding form", flush=True)
      
    elif user['expiration_date'] is not None and (datetime.today().date() - user['expiration_date']).days > 0:
      routing.set_url_hash('no_subs', load_from_cache=False)
      get_open_form().SearchBar.visible = False
      print(f"HOME INIT [{self.instance_id}] - Subscription expired, redirecting", flush=True)
      
    else:
      model_id = load_var("model_id")
      self.model_id = model_id
      print(f"HOME INIT [{self.instance_id}] - model_id: {model_id}", flush=True)
            
      self.num_shorts = 0

      # -------------
      # 1. INITIALIZE ASYNCHRONOUS LOADING        
      # 1.1 Hide "no data" messages during loading
      self.colpan_wl_selection.visible = False
      self.no_watchlists.visible = False
      self.no_shorts.visible = False
      self.reload.visible = False
      
      # 1.2 welcome name
      if user["first_name"] is not None:
        self.label_welcome.text = f'Welcome {user["first_name"]}'    
        
      # 1.3 Initialize loading of stats asynchronously
      self.stats_start_time = time.time()
      print(f"HOME INIT [{self.instance_id}] - Stats loading initialized - {datetime.now()}", flush=True)
      self.load_stats_async()
  
      # 1.4 Initialize loading of shorts asynchronously
      self.shorts_start_time = time.time()
      print(f"HOME INIT [{self.instance_id}] - Shorts loading initialized - {datetime.now()}", flush=True)
      self.load_shorts_async()
  
  
  # 2. ASYNC METHODS
  # 2.1 STATS METHODS
  def load_stats_async(self):
    """Starts asynchronous loading of stats data"""
    # Call asynchronously
    async_call = call_async("get_home_stats", user["user_id"])
    async_call.on_result(self.stats_loaded)
    print(f"HOME ASYNC [{self.instance_id}] - Stats async call dispatched", flush=True)
  
  def stats_loaded(self, data):
    """Handles successful server response for stats."""
    # Calculate loading time
    load_time = time.time() - self.stats_start_time
    print(f"HOME ASYNC [{self.instance_id}] - Stats loaded (took {load_time:.2f} seconds)", flush=True)
    
    # Get the active instance - this is the one currently visible to the user
    active_instance = Home._active_instance
    
    # Check if we should update the current instance or the active instance
    if active_instance and active_instance.instance_id != self.instance_id:
      print(f"HOME ASYNC [{self.instance_id}] - Updating active instance [{active_instance.instance_id}] with stats", flush=True)
      # Process stats in the active instance
      active_instance.process_stats_data(data)
    else:
      # Process stats in this instance
      self.process_stats_data(data)
    
  def process_stats_data(self, data):
    """Process and display stats data"""
    # Process stats data
    stats = data['stats']

    # Initialize counters
    won_cnt = 0
    wl_cnt = 0
    hp_cnt = 0
    tot_cnt = 0

    if stats:
      for stat in stats:
        if stat['stat'] == 'Success': won_cnt = stat['cnt']
        if stat['stat'] == 'Watchlist': wl_cnt = stat['cnt']
        if stat['stat'] == 'HighRated': hp_cnt = stat['cnt']
        if stat['stat'] == 'RatedTotal': tot_cnt = stat['cnt']
    
    # Update UI elements
    self.label_won_no.text = won_cnt
    self.label_wl_no.text = wl_cnt
    self.label_hp_no.text = hp_cnt
    self.label_tot_no.text = tot_cnt
    
    # Update text labels based on counts
    if won_cnt == 1: self.label_won_txt.text = 'artist\nwon'
    else: self.label_won_txt.text = 'artists\nwon'
    if wl_cnt == 1: self.label_wl_txt.text =  'artist on\nwatchlist'
    else: self.label_wl_txt.text =  'artists on\nwatchlist'
    if hp_cnt == 1: self.label_hp_txt.text =  'high\npotential'
    else: self.label_hp_txt.text =  'high\npotentials'
    if tot_cnt == 1: self.label_tot_txt.text = 'total\nrating'
    else: self.label_tot_txt.text = 'total\nratings'
    
    # Process news data
    news = data['news']
    if len(news) == 0:
      self.xy_panel_news.visible = False
      self.xy_panel_news_empty.visible = True
    else:
      self.repeating_panel_news.items = news
        
  # 2.2 SHORTS METHODS
  def load_shorts_async(self):
    """Starts asynchronous loading of shorts data"""
    # Call asynchronously
    async_call = call_async("get_home_shorts", user["user_id"])
    async_call.on_result(self.shorts_loaded)
    print(f"HOME ASYNC [{self.instance_id}] - Shorts async call dispatched", flush=True)
  
  def shorts_loaded(self, result):
    """Handles successful server response for shorts."""
    # Calculate loading time
    load_time = time.time() - self.shorts_start_time
    print(f"HOME ASYNC [{self.instance_id}] - Shorts loaded (took {load_time:.2f} seconds)", flush=True)
    
    # Get the active instance - this is the one currently visible to the user
    active_instance = Home._active_instance
    
    # Check if we should update the current instance or the active instance
    if active_instance and active_instance.instance_id != self.instance_id:
      print(f"HOME ASYNC [{self.instance_id}] - Updating active instance [{active_instance.instance_id}]", flush=True)
      # Process watchlists in the active instance
      active_instance.setup_watchlists(result["watchlists"])
      # Process shorts in the active instance
      active_instance.process_shorts(result["shorts"])
    else:
      # Process watchlists in this instance
      self.setup_watchlists(result["watchlists"])
      # Process shorts in this instance
      self.process_shorts(result["shorts"])
  
  def setup_watchlists(self, watchlists):
    """Set up watchlist UI components"""
    # Clear existing components
    self.flow_panel_watchlists.clear()
        
    if watchlists is not None and len(watchlists) > 0:
      # We have data - no need to show "no watchlists" message
      self.colpan_wl_selection.visible = True
      self.no_watchlists.visible = False
      self.reload.visible = False
      
      for i in range(0, len(watchlists)):
        wl_link = Link(
          text=watchlists[i]["watchlist_name"], tag=watchlists[i]["watchlist_id"], role="genre-box"
        )
  
        wl_link.set_event_handler(
          "click", self.create_activate_watchlist_handler(watchlists[i]["watchlist_id"])
        )
        self.flow_panel_watchlists.add_component(wl_link)
    else:
      # No watchlists found - show message
      self.no_watchlists.visible = True
      self.no_shorts.visible = False
      self.reload.visible = False
  
  def process_shorts(self, shorts):
    """Process and display shorts data"""
    # Clear existing shorts
    self.flow_panel_shorts.clear()
    
    # Hide "no data" indicators until we know the status
    self.no_shorts.visible = False
    
    # present shorts
    if shorts is not None and len(shorts) > 0:
      # We have shorts - hide "no shorts" message
      self.no_shorts.visible = False
      self.reload.visible = True
      shorts = json.loads(shorts)

      self.num_shorts = len(shorts)
      for i in range(0, len(shorts)):
        self.flow_panel_shorts.add_component(C_Short(data=shorts[i]))

      if len(shorts) < 12:
        self.reload.visible = False
    else:
      # No shorts found - show message if appropriate
      if self.no_watchlists.visible is False:
        self.no_shorts.visible = True
      else:
        self.no_shorts.visible = False
      self.reload.visible = False
  
  # 3. USER INTERACTION METHODS
  # 3.1 NAVIGATION
  def link_discover_click(self, **event_args):
    temp_artist_id = anvil.server.call('get_next_artist_id', load_var('model_id'))
    click_link(self.artist_link, f'artists?artist_id={temp_artist_id}', event_args)
    
  def button_discover_click(self, **event_args):
    temp_artist_id = anvil.server.call('get_next_artist_id', load_var('model_id'))
    click_button(f'artists?artist_id={temp_artist_id}', event_args)
    
  def link_funnel_click(self, **event_args):
    click_link(self.link_funnel, 'watchlist_funnel', event_args)

  # 3.2 SHORTS MANAGEMENT
  def add_shorts(self, **event_args):
    # get active watchlist ids
    wl_ids = []
    for component in self.flow_panel_watchlists.get_components():
      if (isinstance(component, Link) and component.role == "genre-box"):  # Only active models
        wl_ids.append(component.tag)
    
    # add new shorts
    if wl_ids:
      # Call asynchronously
      async_call = call_async("get_additional_shorts", user["user_id"], wl_ids, self.num_shorts, 9)
      async_call.on_result(self.additional_shorts_loaded)
  
  def additional_shorts_loaded(self, shorts):
    """Handles successful server response for additional shorts."""
    # Record the time when additional shorts are loaded
    print(f"HOME ASYNC [{self.instance_id}] - Additional shorts loaded", flush=True)
    
    # Get the active instance - this is the one currently visible to the user
    active_instance = Home._active_instance
    
    # Check if we should update the current instance or the active instance
    if active_instance and active_instance.instance_id != self.instance_id:
      print(f"HOME ASYNC [{self.instance_id}] - Updating active instance [{active_instance.instance_id}] with additional shorts", flush=True)
      active_instance.append_additional_shorts(shorts)
    else:
      self.append_additional_shorts(shorts)

  def append_additional_shorts(self, shorts):
    """Append additional shorts to the existing list"""
    # present shorts
    if shorts is not None and len(shorts) > 0:
      self.reload.visible = True
      shorts = json.loads(shorts)
      
      for i in range(0, len(shorts)):
        self.flow_panel_shorts.add_component(C_Short(data=shorts[i]))
      
      self.num_shorts = self.num_shorts + len(shorts)
      
      if len(shorts) < 9:
        self.reload.visible = False
    else:
      self.reload.visible = False
        
  # 3.3 WATCHLIST BUTTONS
  def create_activate_watchlist_handler(self, watchlist_id):
    def handler(**event_args):
      self.activate_watchlist(watchlist_id)

    return handler
  
  # change active status of MODEL BUTTONS
  def activate_watchlist(self, watchlist_id):
    for component in self.flow_panel_watchlists.get_components():
      if isinstance(component, Link):
        # change activation
        if int(component.tag) == watchlist_id:
          if component.role == "genre-box":
            component.role = "genre-box-deselect"
          else:
            component.role = "genre-box"

    # Check if any watchlists are selected
    # collect selected watchlist IDs
    wl_ids = []
    for component in self.flow_panel_watchlists.get_components():
      if (
        isinstance(component, Link) and component.role == "genre-box"
      ):  # Only active models
        wl_ids.append(component.tag)

    # Reset start time for reloading shorts
    self.shorts_start_time = time.time()
    print(f"HOME ASYNC [{self.instance_id}] - Shorts reloading after watchlist change", flush=True)
    
    self.load_shorts_async()
