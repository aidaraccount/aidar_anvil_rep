from ._anvil_designer import NotificationsTemplate
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
    # notifications = \
    #   [{'type': 'mail', 'name': 'This weeks Top releases', 'no_artists': 10},
    #    {'type': 'mail', 'name': 'Growing Top10', 'no_artists': 20},
    #    {'type': 'playlist', 'name': 'My Playlist', 'no_artists': 5}]
    print(notifications)
    
    if len(notifications) > 0:
      self.no_notifications.visible = False
      self.repeating_panel_table.items = notifications
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
                      freq_2 = None,
                      freq_3 = None,
                      metric = 'Top Fits',
                      no_artists = 5,
                      repetition = 'Show artists again',
                      rated = False,
                      watchlist = None,
                      release_days = None,
                      min_grow_fit = None,
                      model_ids = [2])
    
    self.get_notifications()
    