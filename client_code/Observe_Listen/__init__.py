from ._anvil_designer import Observe_ListenTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json
from anvil.js.window import document, playSpotify, setPlayButtonIcons
import anvil.js
import time
from anvil_labs.non_blocking import call_async
import uuid

from datetime import date, datetime
from anvil_extras import routing
from ..nav import click_link, click_button, logout, login_check, load_var, save_var

from ..C_NotificationSettings import C_NotificationSettings
from ..C_Discover import C_Discover


@routing.route("listen", url_keys=['notification_id'], title="Observe - Listen-In")
class Observe_Listen(Observe_ListenTemplate):
  # Class variable to track the current active instance
  _active_instance = None

  def __init__(self, **properties):
    # Generate a unique instance ID for tracking callbacks
    self.instance_id = str(uuid.uuid4())[:8]
    
    # Set this as the active instance
    Observe_Listen._active_instance = self
    
    get_open_form().start_timer()
    
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.add_event_handler('show', self.form_show)
    
    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    
    if user['expiration_date'] is not None and (datetime.today().date() - user['expiration_date']).days > 0:
      routing.set_url_hash('no_subs', load_from_cache=False)
      get_open_form().SearchBar.visible = False
      
    else:
      model_id = load_var("model_id")
      self.model_id = model_id
      print(f"Notifications model_id: {model_id}")
  
      url_notification_id = self.url_dict['notification_id']
      self.url_notification_id = url_notification_id
      
      save_var('has_played', 'False')
      self.footer_trick_spacer.visible = False
      
      self.discover_is_loading = False

      # -----------      
      # GENERAL
      # a) get notification/ playlist data
      self.get_all_notifications(url_notification_id)


  def form_show(self, **event_args):
    embed_iframe_element = document.getElementById('embed-iframe')
    if embed_iframe_element:
      self.call_js('createOrUpdateSpotifyPlayer', anvil.js.get_dom_node(self), 'track', self.initial_track_id, self.all_track_ids, self.all_artist_ids, self.all_artist_names)
      print("Embed iframe element found. Initialize Spotify player!")
    else:
      print("Embed iframe element not found. Will not initialize Spotify player.")

  def spotify_HTML_player(self):
    c_web_player_html = '''
      <div id="embed-iframe"></div>
      '''
    html_webplayer_panel = HtmlPanel(html=c_web_player_html)
    self.footer_left.add_component(html_webplayer_panel)
    print('self.footer_left.add_component(html_webplayer_panel)')
  
  # GET ALL NOTIFICATIONS
  def get_all_notifications(self, notification_id, **event_args):
    print('calling get_all_notifications')
    get_open_form().step_timer("Step 1")
    self.notifications = json.loads(anvil.server.call("get_notifications", user["user_id"], 'playlist'))
    get_open_form().step_timer("Step 2")
     
    # clear all navigation components
    self.flow_panel.clear()
    
    # adding navigation components
    self.flow_panel.visible = True
    self.flow_panel_create.visible = True
    
    for notification in self.notifications:
      notification_link = Link(
        text=notification["name"],
        role='section_buttons',
        tag=notification["notification_id"]
      )
      notification_link.set_event_handler('click', self.create_click_notification_handler(notification["notification_id"], notification_link))
      self.flow_panel.add_component(notification_link)
    get_open_form().step_timer("Step 3")
    
    # check notification presence & trained model presence
    if len(self.notifications) > 0:
      self.html = "@theme:ObserveListen.html"
      self.footer.visible = True
    
      # if existing notifications: load and activate defined/first notification
      self.no_notifications.visible = False
      self.no_trained_model.visible = False
  
      if notification_id is None or notification_id == 'None':
        notification_id = self.notifications[0]["notification_id"]
      else:
        notification_id = int(notification_id)
      
      get_open_form().step_timer("Step 4")
      self.activate_notification(notification_id)
      get_open_form().step_timer("End")
    
    else:
      self.html = ''
      self.footer.visible = False
      
      self.flow_panel.visible = False
      self.flow_panel_create.visible = False
      self.notification_settings.visible = False
      self.column_panel_content.visible = False
  
      models = json.loads(anvil.server.call('get_model_ids',  user["user_id"]))    
      if not any(item.get('fully_trained', True) for item in models):
        # if no trained model
        self.no_trained_model.visible = True
        self.no_notifications.visible = False
        self.no_artists.visible = False
  
      else:
        # else, just missing notification      
        self.no_trained_model.visible = False
        self.no_notifications.visible = True
        self.no_artists.visible = False
        
  
  # ACTIVATE NOTIFICATION
  def activate_notification(self, notification_id):
    get_open_form().step_timer("Step 6")
    print('calling activate_notification')
    for component in self.flow_panel.get_components():
      if isinstance(component, Link):          
        if int(component.tag) == notification_id:
          component.role = 'section_buttons_focused'
          self.get_notification_settings(notification_id)
        else:
          component.role = 'section_buttons'
  
  # GET NOTIFICATION SETTINGS
  def get_notification_settings(self, notification_id, **event_args):
    get_open_form().step_timer("Step 7")
    print('calling get_notification_settings')
    items = [item for item in self.notifications if item["notification_id"] == notification_id]
    
    self.notification_settings.clear()
    self.notification_settings.add_component(C_NotificationSettings(items, notification_id))
    self.notification_settings.visible = True

    get_open_form().step_timer("Step 8")
    self.get_observe_tracks(notification_id)
    
  # GET PLAYLIST DETAILS
  def get_observe_tracks(self, notification_id, **event_args):  
    # get data
    notification = [item for item in self.notifications if item["notification_id"] == notification_id][0]
    
    # Initialize loading variables and timing
    self.tracks_start_time = time.time()
    self.discover_start_time = time.time()
    print(f"OBSERVE_LISTEN [{self.instance_id}] - Starting async loading - {datetime.now()}")
    get_open_form().step_timer("Step 9 - Starting asynchronous loading")
    
    # Initialize with all_ai_artist_ids as None until we get data
    self.all_ai_artist_ids = None
    
    # Hide content until data is loaded
    self.column_panel_content.visible = False
    self.no_artists.visible = False
    
    # 1. Start asynchronous loading of tracks
    self.load_tracks_async(notification_id)
    get_open_form().step_timer("Step 9.1 - Tracks loading initialized")
    
    # 2. We'll start loading discover after tracks are loaded since we need the artist ID
    
  # ------
  # ASYNC METHODS FOR TRACKS
  def load_tracks_async(self, notification_id):
    """Starts asynchronous loading of track data"""
    async_call = call_async("get_observe_tracks_data", notification_id)
    async_call.on_result(self.tracks_loaded)
    
  def tracks_loaded(self, observed_tracks):
    """Handles successful server response for tracks data"""
    # Calculate loading time
    load_time = time.time() - self.tracks_start_time
    print(f"OBSERVE_LISTEN ASYNC [{self.instance_id}] - Tracks loaded (took {load_time:.2f} seconds)")
    get_open_form().step_timer("Step 9.2 - Tracks data received")
    
    # Get the active instance - this is the one currently visible to the user
    active_instance = Observe_Listen._active_instance
    
    # Check if we should update the current instance or the active instance
    if active_instance and active_instance.instance_id != self.instance_id:
      print(f"OBSERVE_LISTEN ASYNC [{self.instance_id}] - Updating active instance [{active_instance.instance_id}] with tracks")
      active_instance.process_tracks_data(observed_tracks)
    else:
      self.process_tracks_data(observed_tracks)
  
  def process_tracks_data(self, observed_tracks):
    """Process and display tracks data"""
    get_open_form().step_timer("Step 9.3 - Processing tracks data")
    
    if observed_tracks is not None and len(observed_tracks) > 0:
      # Extract track information
      self.initial_track_id = observed_tracks[0]['tracks'][0]['spotify_track_id']
      self.initial_artist_id = observed_tracks[0]['tracks'][0]['spotify_artist_id']
      
      save_var('lastplayedtrackid', self.initial_track_id)
      save_var('lastplayedartistid', self.initial_artist_id)
      get_open_form().step_timer("Step 9.4 - Saved track and artist IDs")
      
      self.all_track_ids = [track['spotify_track_id'] for artist in observed_tracks for track in artist['tracks']]
      self.all_artist_ids = [track['spotify_artist_id'] for artist in observed_tracks for track in artist['tracks']]
      self.all_ai_artist_ids = [track['artist_id'] for artist in observed_tracks for track in artist['tracks']]
      self.all_artist_names = [track['name'] for artist in observed_tracks for track in artist['tracks']]
      get_open_form().step_timer("Step 9.5 - Extracted all track and artist data")
      
      # Update UI with tracks data
      self.repeating_panel_artists.items = observed_tracks
      self.column_panel_content.visible = True
      get_open_form().step_timer("Step 9.6 - Updated UI with tracks data")
      
      # Load Spotify Player as early as possible - don't wait for discover
      self.footer_left.clear()
      self.spotify_HTML_player()
      get_open_form().step_timer("Step 9.7 - Spotify Player initialized")
      
      # Load dropdown data early
      self.load_dropdowns()
      get_open_form().step_timer("Step 9.8 - Dropdowns loaded")
      
      get_open_form().step_timer("Step 10 - Starting discover loading")
      
      # Now that we have the artist IDs, start loading the discover component
      if self.all_ai_artist_ids and len(self.all_ai_artist_ids) > 0:
        print(f"Starting discover load with artist ID: {self.all_ai_artist_ids[0]}")
        self.load_discover_async(self.all_ai_artist_ids[0])
    else:
      self.column_panel_content.visible = False
      self.no_artists.visible = True
      get_open_form().step_timer("Step 9.9 - No artists found")

  # Load dropdown data as a separate function so it can be called earlier
  def load_dropdowns(self):
    """Load watchlist and model dropdown data"""
    try:
      # Load watchlist dropdown
      wl_data = json.loads(anvil.server.call('get_watchlist_ids', user["user_id"]))
      self.drop_down_wl.selected_value = [item['watchlist_name'] for item in wl_data if item['is_last_used']][0]
      self.drop_down_wl.items = [item['watchlist_name'] for item in wl_data]
      
      # Load model dropdown
      model_data = json.loads(anvil.server.call('get_model_ids', user["user_id"]))
      self.drop_down_model.selected_value = [item['model_name'] for item in model_data if item['is_last_used']][0]
      self.drop_down_model.items = [item['model_name'] for item in model_data]
    except Exception as e:
      print(f"Error loading dropdowns: {e}")

  # ASYNC METHODS FOR DISCOVER
  def load_discover_async(self, artist_id):
    """Starts asynchronous loading of discover data"""
    get_open_form().step_timer("Step 10.1 - Starting discover async load")
    async_call = call_async("get_artist_discover_data", artist_id)
    async_call.on_result(self.discover_loaded)
  
  def discover_loaded(self, artist_id):
    """Handles successful server response for discover data"""
    # Calculate loading time
    load_time = time.time() - self.discover_start_time
    print(f"OBSERVE_LISTEN ASYNC [{self.instance_id}] - Discover data loaded (took {load_time:.2f} seconds)")
    get_open_form().step_timer("Step 10.2 - Discover data received")
    
    # Get the active instance - this is the one currently visible to the user
    active_instance = Observe_Listen._active_instance
    
    # Check if we should update the current instance or the active instance
    if active_instance and active_instance.instance_id != self.instance_id:
      print(f"OBSERVE_LISTEN ASYNC [{self.instance_id}] - Updating active instance [{active_instance.instance_id}] with discover")
      active_instance.process_discover_data(artist_id)
    else:
      self.process_discover_data(artist_id)
  
  def process_discover_data(self, artist_id):
    """Process and display discover data"""
    get_open_form().step_timer("Step 11 - Processing discover data")
    
    # Clear and add the C_Discover component
    self.column_panel_discover.clear()
    self.column_panel_discover.add_component(C_Discover(artist_id))
    get_open_form().step_timer("Step 11.1 - Added discover component")
    
    # a) set ratings status
    self.column_panel_discover.get_components()[0].set_rating_highlight()
    get_open_form().step_timer("Step 11.2 - Set rating highlights")
    
    # b) set watchlist status
    self.column_panel_discover.get_components()[0].set_watchlist_icons()
    get_open_form().step_timer("Step 11.3 - Set watchlist icons")
    
    # Update the form UI if needed
    self.form_show()
    get_open_form().step_timer("Step 11.4 - Form UI updated")
    
    # Spotify player is already loaded at this point
    # Dropdown data is already loaded at this point
    
    get_open_form().step_timer("Step 12 - Discover loading complete")
  
  # GET DISCOVER DETAILS - This will be replaced by the async version above
  def initial_load_discover(self, first_artist_id, **event_args):
    # This method is being replaced by asynchronous loading
    # Keep this method for backward compatibility, but use async loading internally
    self.load_discover_async(first_artist_id)
    
  def reload_discover(self, nextSpotifyArtistID, **event_args):
    if self.discover_is_loading:
      return  # Ignore this call if another is already in progress

    self.discover_is_loading = True  # Lock the function
    try:
      # Get the AI artist ID from the Spotify artist ID
      new_artist_id = self.all_ai_artist_ids[self.all_artist_ids.index(nextSpotifyArtistID)]
      
      # Use the async loading pattern
      self.discover_start_time = time.time()
      self.load_discover_async(new_artist_id)
    
    finally:
      self.discover_is_loading = False  # Unlock the function

  # CREATE A NEW PLAYLIST
  def add_spotify_playlist_click(self, **event_args):
    # get a trained model to activate it at the beginning
    models = json.loads(anvil.server.call("get_model_ids", user["user_id"]))

    model_id_pre_select = None
    for i in range(0, len(models)):
      if models[i]["is_last_used"] is True and models[i]["fully_trained"] is True:
        model_id_pre_select = models[i]["model_id"]

      else:
        for i in range(0, len(models)):
          if models[i]["fully_trained"] is True:
            model_id_pre_select = models[i]["model_id"]
            break

    if model_id_pre_select:
      model_ids = [model_id_pre_select]
    else:
      model_ids = []

    # save the initial notification
    notification_id = anvil.server.call(
      "create_notification",
      user_id=user["user_id"],
      type="playlist",
      name="My Playlist",
      active=True,
      freq_1="Daily",
      freq_2=7,
      freq_3=date.today().strftime("%Y-%m-%d"),
      metric="Top Fits",
      no_artists=15,
      repetition_1="Repeat suggestions",
      repetition_2=90,
      rated=False,
      watchlist=None,
      release_days=21,
      min_grow_fit=0.75,
      model_ids=model_ids,
      song_selection_1="Latest Releases",
      song_selection_2="2",
    )
    
    # update the notifications table
    click_link(self.create_playlist, f'listen?notification_id={notification_id}', event_args)

  
  # BASE FUNCTION FOR LINK EVENTS
  def create_click_notification_handler(self, notification_id, notification_link):
    def handler(**event_args):
      click_link(notification_link, f'listen?notification_id={notification_id}', event_args)
    return handler


  # ------------------------------------------------------------
  # FOOTER    
  # Play Controller
  # def specific_track(self, spotify_track_id, **event_args):
  #   # play previous song
  #   save_var('has_played', 'True')
  #   anvil.js.call_js('playNextSong', anvil.js.get_dom_node(self), 'track', self.all_track_ids, self.all_artist_ids, self.all_artist_names, 'backward')

  def play_button_central_click(self, **event_args):
    if load_var('has_played') == 'False':
      anvil.js.call_js('playNextSong', anvil.js.get_dom_node(self), 'track', self.all_track_ids, self.all_artist_ids, self.all_artist_names, 'initial')
    else:
      anvil.js.call_js('playSpotify')
    save_var('has_played', 'True')
    anvil.server.call('sent_push_over',  'Observe_Listen', f'User {user["user_id"]}: play/pause playlist')
  
  def backward_button_click(self, **event_args):
    # play previous song
    save_var('has_played', 'True')
    anvil.js.call_js('playNextSong', anvil.js.get_dom_node(self), 'track', self.all_track_ids, self.all_artist_ids, self.all_artist_names, 'backward')
    anvil.server.call('sent_push_over',  'Observe_Listen', f'User {user["user_id"]}: backward playlist')
  
  def forward_button_click(self, **event_args):
    # play next song
    save_var('has_played', 'True')
    anvil.js.call_js('playNextSong', anvil.js.get_dom_node(self), 'track', self.all_track_ids, self.all_artist_ids, self.all_artist_names, 'forward')
    anvil.server.call('sent_push_over',  'Observe_Listen', f'User {user["user_id"]}: forward playlist')
    
  def fast_backward_button_click(self, **event_args):
    # play first song of next artist
    save_var('has_played', 'True')
    anvil.js.call_js('playNextSong', anvil.js.get_dom_node(self), 'track', self.all_track_ids, self.all_artist_ids, self.all_artist_names, 'fast-backward')
    anvil.server.call('sent_push_over',  'Observe_Listen', f'User {user["user_id"]}: artist backward playlist')

  def fast_forward_button_click(self, **event_args):
    # play first song of next artist
    save_var('has_played', 'True')
    anvil.js.call_js('playNextSong', anvil.js.get_dom_node(self), 'track', self.all_track_ids, self.all_artist_ids, self.all_artist_names, 'fast-forward')
    anvil.server.call('sent_push_over',  'Observe_Listen', f'User {user["user_id"]}: artist forward playlist')

  # Ratings
  def set_rating_highlight(self, no=None, rating=False, **event_args):
    if (no == 1 and self.button_1.role != ['feature', 'highlight-button'] and rating is True) or (no == 1 and rating is False):
      self.button_1.role = ['feature', 'highlight-button']
    else:
      self.button_1.role = ['feature']
    if (no == 2 and self.button_2.role != ['feature', 'highlight-button'] and rating is True) or (no == 2 and rating is False):
      self.button_2.role = ['feature', 'highlight-button']
    else:
      self.button_2.role = ['feature']
    if (no == 3 and self.button_3.role != ['feature', 'highlight-button'] and rating is True) or (no == 3 and rating is False):
      self.button_3.role = ['feature', 'highlight-button']
    else:
      self.button_3.role = ['feature']
    if (no == 4 and self.button_4.role != ['feature', 'highlight-button'] and rating is True) or (no == 4 and rating is False):
      self.button_4.role = ['feature', 'highlight-button']
    else:
      self.button_4.role = ['feature']
    if (no == 5 and self.button_5.role != ['feature', 'highlight-button'] and rating is True) or (no == 5 and rating is False):
      self.button_5.role = ['feature', 'highlight-button']
    else:
      self.button_5.role = ['feature']
    if (no == 6 and self.button_6.role != ['feature', 'highlight-button'] and rating is True) or (no == 6 and rating is False):
      self.button_6.role = ['feature', 'highlight-button']
    else:
      self.button_6.role = ['feature']
    if (no == 7 and self.button_7.role != ['feature', 'highlight-button'] and rating is True) or (no == 7 and rating is False):
      self.button_7.role = ['feature', 'highlight-button']
    else:
      self.button_7.role = ['feature']
    
  def button_1_click(self, **event_args):
    # get notification model_ids
    notification_model_ids = []
    for component in self.notification_settings.get_components()[0].flow_panel_models.get_components():
      if (isinstance(component, Link) and component.role == "genre-box"):  # Only active models
        notification_model_ids.append(component.tag)

    # add interest
    if int(self.model_id) in notification_model_ids:
      self.column_panel_discover.get_components()[0].button_1_click(True, self.drop_down_model.selected_value)
    else:
      self.column_panel_discover.get_components()[0].button_1_click(False, self.drop_down_model.selected_value)

    # set rating highlight
    self.set_rating_highlight(1, True)
    
  def button_2_click(self, **event_args):
    # get notification model_ids
    notification_model_ids = []
    for component in self.notification_settings.get_components()[0].flow_panel_models.get_components():
      if (isinstance(component, Link) and component.role == "genre-box"):  # Only active models
        notification_model_ids.append(component.tag)

    # add interest
    if int(self.model_id) in notification_model_ids:
      self.column_panel_discover.get_components()[0].button_2_click(True, self.drop_down_model.selected_value)
    else:
      self.column_panel_discover.get_components()[0].button_2_click(False, self.drop_down_model.selected_value)

    # set rating highlight
    self.set_rating_highlight(2, True)
    
  def button_3_click(self, **event_args):
    # get notification model_ids
    notification_model_ids = []
    for component in self.notification_settings.get_components()[0].flow_panel_models.get_components():
      if (isinstance(component, Link) and component.role == "genre-box"):  # Only active models
        notification_model_ids.append(component.tag)

    # add interest
    if int(self.model_id) in notification_model_ids:
      self.column_panel_discover.get_components()[0].button_3_click(True, self.drop_down_model.selected_value)
    else:
      self.column_panel_discover.get_components()[0].button_3_click(False, self.drop_down_model.selected_value)

    # set rating highlight
    self.set_rating_highlight(3, True)
    
  def button_4_click(self, **event_args):
    # get notification model_ids
    notification_model_ids = []
    for component in self.notification_settings.get_components()[0].flow_panel_models.get_components():
      if (isinstance(component, Link) and component.role == "genre-box"):  # Only active models
        notification_model_ids.append(component.tag)

    # add interest
    if int(self.model_id) in notification_model_ids:
      self.column_panel_discover.get_components()[0].button_4_click(True, self.drop_down_model.selected_value)
    else:
      self.column_panel_discover.get_components()[0].button_4_click(False, self.drop_down_model.selected_value)

    # set rating highlight
    self.set_rating_highlight(4, True)
    
  def button_5_click(self, **event_args):
    # get notification model_ids
    notification_model_ids = []
    for component in self.notification_settings.get_components()[0].flow_panel_models.get_components():
      if (isinstance(component, Link) and component.role == "genre-box"):  # Only active models
        notification_model_ids.append(component.tag)

    # add interest
    if int(self.model_id) in notification_model_ids:
      self.column_panel_discover.get_components()[0].button_5_click(True, self.drop_down_model.selected_value)
    else:
      self.column_panel_discover.get_components()[0].button_5_click(False, self.drop_down_model.selected_value)

    # set rating highlight
    self.set_rating_highlight(5, True)
    
  def button_6_click(self, **event_args):
    # get notification model_ids
    notification_model_ids = []
    for component in self.notification_settings.get_components()[0].flow_panel_models.get_components():
      if (isinstance(component, Link) and component.role == "genre-box"):  # Only active models
        notification_model_ids.append(component.tag)

    # add interest
    if int(self.model_id) in notification_model_ids:
      self.column_panel_discover.get_components()[0].button_6_click(True, self.drop_down_model.selected_value)
    else:
      self.column_panel_discover.get_components()[0].button_6_click(False, self.drop_down_model.selected_value)

    # set rating highlight
    self.set_rating_highlight(6, True)
    
  def button_7_click(self, **event_args):
    # get notification model_ids
    notification_model_ids = []
    for component in self.notification_settings.get_components()[0].flow_panel_models.get_components():
      if (isinstance(component, Link) and component.role == "genre-box"):  # Only active models
        notification_model_ids.append(component.tag)

    # add interest
    if int(self.model_id) in notification_model_ids:
      self.column_panel_discover.get_components()[0].button_7_click(True, self.drop_down_model.selected_value)
    else:
      self.column_panel_discover.get_components()[0].button_7_click(False, self.drop_down_model.selected_value)

    # set rating highlight
    self.set_rating_highlight(7, True)

  # watchlist
  def link_watchlist_name_click(self, **event_args):
    self.column_panel_discover.get_components()[0].link_watchlist_name_click()

  # Model dropdown
  def drop_down_model_change(self, **event_args):
    model_data = json.loads(anvil.server.call('get_model_ids',  user["user_id"]))
    model_id_new = [item['model_id'] for item in model_data if item['model_name'] == self.drop_down_model.selected_value][0]
    self.model_id=model_id_new
    save_var('model_id', model_id_new)
    anvil.server.call('update_model_usage', user["user_id"], model_id_new)
    get_open_form().refresh_models_underline()
    self.reload_discover(load_var('lastplayedartistid'))

  # Watchlist dropdown
  def drop_down_wl_change(self, **event_args):
    wl_data = json.loads(anvil.server.call('get_watchlist_ids',  user["user_id"]))
    wl_id_new = [item['watchlist_id'] for item in wl_data if item['watchlist_name'] == self.drop_down_wl.selected_value][0]
    self.watchlist_id=wl_id_new
    save_var('watchlist_id', wl_id_new)
    anvil.server.call('update_watchlist_usage', user["user_id"], wl_id_new)
    get_open_form().refresh_watchlists_underline()
    self.reload_discover(load_var('lastplayedartistid'))