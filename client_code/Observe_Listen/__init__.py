from ._anvil_designer import Observe_ListenTemplate
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


@routing.route("listen", title="Observe - Listen-In")
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

    # GENERAL
    notifications = json.loads(anvil.server.call("get_notifications", user["user_id"], 'playlist'))
    print(notifications)
    print(notifications[1])
    
    if len(notifications) > 0:
      self.get_notifications()
    else:
      self.data_grid.visible = False
      self.no_notifications.visible = True

  # GET TABLE DATA
  def get_notifications(self, **event_args):
      self.no_notifications.visible = False
      self.repeating_panel_email.items = [notifications[1]]
      self.data_grid.visible = True


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
    anvil.server.call(
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

    # update the notifications table
    self.get_notifications()
