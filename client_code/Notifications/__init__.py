from ._anvil_designer import NotificationsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json
from datetime import date, datetime
from anvil_extras import routing
from ..nav import click_link, click_button, logout, login_check, load_var


@routing.route("notifications", title="Notifications")
class Notifications(NotificationsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()

    model_id = load_var("model_id")
    self.model_id = model_id
    print(f"Notifications model_id: {model_id}")

    # GENERAL
    self.get_notifications()

  
  # GET TABLE DATA
  def get_notifications(self, **event_args):

    notifications = json.loads(anvil.server.call('get_notifications',  user["user_id"]))
    
    if len(notifications) > 0:
      self.no_notifications.visible = False
      self.repeating_panel_email.items = notifications
      self.data_grid.visible = True

    else:
      self.data_grid.visible = False
      self.no_notifications.visible = True
      
  def add_mail_notification_click(self, **event_args):
    anvil.server.call('create_notification',
                      user_id = user["user_id"],
                      type = 'mail',
                      name = 'My Notification',
                      active = True,
                      freq_1 = 'Daily',
                      freq_2 = 7,
                      freq_3 = date.today().strftime("%Y-%m-%d"),
                      metric = 'Top Fits',
                      no_artists = 5,
                      repetition_1 = 'Repeat suggestions',
                      repetition_2 = 90,
                      rated = False,
                      watchlist = None,
                      release_days = 21,
                      min_grow_fit = 0.75,
                      model_ids = [])
    
    self.get_notifications()
    
  def add_spotify_playlist_click(self, **event_args):
    anvil.server.call('create_notification',
                      user_id = user["user_id"],
                      type = 'playlist',
                      name = 'My Notification',
                      active = True,
                      freq_1 = 'Daily',
                      freq_2 = 7,
                      freq_3 = date.today().strftime("%Y-%m-%d"),
                      metric = 'Top Fits',
                      no_artists = 5,
                      repetition_1 = 'Repeat suggestions',
                      repetition_2 = 90,
                      rated = False,
                      watchlist = None,
                      release_days = 21,
                      min_grow_fit = 0.75,
                      model_ids = [])
    
    self.get_notifications()
