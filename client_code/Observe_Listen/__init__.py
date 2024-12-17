from ._anvil_designer import Observe_ListenTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json
import anvil.js
from datetime import date, datetime
from anvil_extras import routing
from ..nav import click_link, click_button, logout, login_check, load_var, save_var

from ..C_Notification_Settings import C_Notification_Settings
from anvil.js.window import playSpotify_2


@routing.route("listen", url_keys=['notification_id'], title="Observe - Listen-In")
class Observe_Listen(Observe_ListenTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()

    model_id = load_var("model_id")
    self.model_id = model_id
    print(f"Notifications model_id: {model_id}")

    url_notification_id = self.url_dict['notification_id']
    self.url_notification_id = url_notification_id
    
    save_var('toggle', 'up')
    self.footer_trick_spacer.visible = False
    
    # GENERAL
    self.get_all_notifications(url_notification_id)


  # GET ALL NOTIFICATIONS
  def get_all_notifications(self, notification_id, **event_args):
    self.notifications = json.loads(anvil.server.call("get_notifications", user["user_id"], 'playlist'))
    print('get_all_notifications - all:', self.notifications)
    print('get_all_notifications:', notification_id)
    print('get_all_notifications - type:', type(notification_id))
    
    # clear all navigation components
    self.flow_panel.clear()
    
    # adding navigation components
    self.flow_panel.visible = True
    for notification in self.notifications:
      notification_link = Link(
        text=notification["name"],
        role='section_buttons',
        tag=notification["notification_id"]
      )
      notification_link.set_event_handler('click', self.create_click_notification_handler(notification["notification_id"], notification_link))
      self.flow_panel.add_component(notification_link)

    # load and activate defined/first notification
    if len(self.notifications) > 0:      
      self.no_notifications.visible = False
  
      if notification_id is None or notification_id == 'None':
        notification_id = self.notifications[0]["notification_id"]
      else:
        notification_id = int(notification_id)
      
      self.activate_notification(notification_id)
      
    else:
      self.flow_panel.visible = False
      self.notification_settings.visible = False
      self.no_notifications.visible = True
  
  # ACTIVATE NOTIFICATION
  def activate_notification(self, notification_id):
    print('activate_notification:', notification_id)
    for component in self.flow_panel.get_components():
      if isinstance(component, Link):          
        if int(component.tag) == notification_id:
          component.role = 'section_buttons_focused'
          self.get_notification_settings(notification_id)
        else:
          component.role = 'section_buttons'
  
  # GET NOTIFICATION SETTINGS
  def get_notification_settings(self, notification_id, **event_args):
    print('get_notification_settings:', notification_id)
    items = [item for item in self.notifications if item["notification_id"] == notification_id]
    
    self.notification_settings.clear()
    self.notification_settings.add_component(C_Notification_Settings(items, notification_id))
    self.notification_settings.visible = True
    
    self.get_observe_tracks(notification_id)
    
  # GET PLAYLIST DETAILS
  def get_observe_tracks(self, notification_id, **event_args):
    print('get_observe_tracks:', notification_id)
  
    notification = [item for item in self.notifications if item["notification_id"] == notification_id][0]
    
    observed_tracks = anvil.server.call('get_observed_tracks', 
                                        user["user_id"],
                                        notification["model_ids"],
                                        notification["metric"],
                                        notification["rated"],
                                        notification["watchlist"],
                                        notification["min_grow_fit"],
                                        notification["release_days"],
                                        notification["no_artists"],
                                        notification["song_selection_2"]
                                        )

    # print(observed_tracks)
    
    self.repeating_panel_artists.items = observed_tracks
    self.repeating_panel_artists.visible = True


  # GET DISCOVER DETAILS
  # .....
  # .....
  # .....
  

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
      name="My Spotify Playlist",
      active=True,
      freq_1="Daily",
      freq_2=7,
      freq_3=date.today().strftime("%Y-%m-%d"),
      metric="Top Fits",
      no_artists=5,
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
    print('add_spotify_playlist_click:', notification_id)
    
    # update the notifications table
    save_var('toggle', 'down')
    click_link(self.create_playlist, f'listen?notification_id={notification_id}', event_args)

  
  # BASE FUNCTION FOR LINK EVENTS
  def create_click_notification_handler(self, notification_id, notification_link):
    def handler(**event_args):
      click_link(notification_link, f'listen?notification_id={notification_id}', event_args)
    return handler

  # FOOTER
  def spotify_HTML_player(self):
    c_web_player_html = '''
      <div id="embed-iframe"></div>
      '''
    html_webplayer_panel = HtmlPanel(html=c_web_player_html)
    self.footer_left.add_component(html_webplayer_panel)
    
  def play_button_central_click(self, **event_args):
    if self.play_button_central.icon == 'fa:play':
      self.play_button_central.icon = 'fa:pause'
      self.footer_left.clear()
      self.spotify_HTML_player()
      self.call_js('createOrUpdateSpotifyPlayer', 'track', '1JoM3HEBn0cNTi8bNSyqTb')
      anvil.js.call_js('playSpotify_2')
    else:
      self.play_button_central.icon = 'fa:play'
      anvil.js.call_js('playSpotify_2')

    # self.reset_track_play_buttons()
