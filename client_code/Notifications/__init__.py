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
    # print(f"{datetime.now()}: Observe 0", flush=True)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()

    model_id = load_var("model_id")
    self.model_id = model_id
    print(f"Notifications model_id: {model_id}")

    # GENERAL
    pass

  
  # GET TABLE DATA
  def get_notifications(self, **event_args):
    self.no_notifications.visible = False
