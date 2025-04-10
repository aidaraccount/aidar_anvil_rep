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


from datetime import date, datetime
from anvil_extras import routing
from ..nav import click_link, click_button, logout, login_check, load_var, save_var

from ..C_NotificationSettings import C_NotificationSettings
from ..C_Discover import C_Discover


@routing.route("listen", url_keys=['notification_id'], title="Observe - Listen-In")
class Observe_Listen(Observe_ListenTemplate):
  def __init__(self, **properties):
    
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
    self.notifications = json.loads(anvil.server.call("get_notifications", user["user_id"], 'playlist'))
     
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
      
      self.activate_notification(notification_id)
      
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
    print('calling get_notification_settings')
    items = [item for item in self.notifications if item["notification_id"] == notification_id]
    
    self.notification_settings.clear()
    self.notification_settings.add_component(C_NotificationSettings(items, notification_id))
    self.notification_settings.visible = True
    
    self.get_observe_tracks(notification_id)
    
  # GET PLAYLIST DETAILS
  def get_observe_tracks(self, notification_id, **event_args):  
    # get data
    notification = [item for item in self.notifications if item["notification_id"] == notification_id][0]
    observed_tracks = anvil.server.call('get_observed_tracks', notification["notification_id"])
    
    # hand-over the data
    if len(observed_tracks) > 0:
      self.no_artists.visible = False

      self.initial_track_id = observed_tracks[0]['tracks'][0]['spotify_track_id']
      self.initial_artist_id = observed_tracks[0]['tracks'][0]['spotify_artist_id']
      
      save_var('lastplayedtrackid', self.initial_track_id)
      save_var('lastplayedartistid', self.initial_artist_id)
      
      self.all_track_ids = [track['spotify_track_id'] for artist in observed_tracks for track in artist['tracks']]
      self.all_artist_ids = [track['spotify_artist_id'] for artist in observed_tracks for track in artist['tracks']]
      self.all_ai_artist_ids = [track['artist_id'] for artist in observed_tracks for track in artist['tracks']]
      self.all_artist_names = [track['name'] for artist in observed_tracks for track in artist['tracks']]
      
      self.repeating_panel_artists.items = observed_tracks
      self.initial_load_discover()
      
      self.column_panel_content.visible = True
      
    else:
      self.column_panel_content.visible = False
      self.no_artists.visible = True


  # GET DISCOVER DETAILS
  def initial_load_discover(self, **event_args):
    print('calling initial_load_discover')
    # b) fill C_Discover
    first_artist_id = self.repeating_panel_artists.items[0]["artist_id"]
    self.column_panel_discover.clear()
    self.column_panel_discover.add_component(C_Discover(first_artist_id))

    # -----------
    # FOOTER
    # a) set ratings status
    self.column_panel_discover.get_components()[0].set_rating_highlight()
    
    # b) set watchlist status
    self.column_panel_discover.get_components()[0].set_watchlist_icons()
          
    # c) Instantiate Spotify Player
    self.footer_left.clear()
    self.spotify_HTML_player()
    self.form_show()
    
    # d) Watchlist Drop-Down
    wl_data = json.loads(anvil.server.call('get_watchlist_ids',  user["user_id"]))
    self.drop_down_wl.selected_value = [item['watchlist_name'] for item in wl_data if item['is_last_used']][0]
    self.drop_down_wl.items = [item['watchlist_name'] for item in wl_data]

    # e) Models Drop-Down
    model_data = json.loads(anvil.server.call('get_model_ids',  user["user_id"]))
    self.drop_down_model.selected_value = [item['model_name'] for item in model_data if item['is_last_used']][0]
    self.drop_down_model.items = [item['model_name'] for item in model_data]
    
  def reload_discover(self, nextSpotifyArtistID, **event_args):
    if self.discover_is_loading:
      return  # Ignore this call if another is already in progress

    self.discover_is_loading = True  # Lock the function
    try:
      # load C_Discover
      new_artist_id = self.all_ai_artist_ids[self.all_artist_ids.index(nextSpotifyArtistID)]
      self.column_panel_discover.clear()
      self.column_panel_discover.add_component(C_Discover(new_artist_id))
      # set ratings status
      self.column_panel_discover.get_components()[0].set_rating_highlight()    
      # set watchlist status
      self.column_panel_discover.get_components()[0].set_watchlist_icons()
      # refresh play buttons
      anvil.js.call_js('setPlayButtonIcons', 'track')
    
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