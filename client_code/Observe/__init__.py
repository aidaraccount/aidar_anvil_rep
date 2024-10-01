from ._anvil_designer import ObserveTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json

from anvil_extras import routing
from ..nav import click_link, click_button, logout, login_check, load_var


@routing.route("observe", title="Observe")
class Observe(ObserveTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()

    model_id = load_var("model_id")
    self.model_id = model_id
    print(f"Observe model_id: {model_id}")
    
    # FUNNEL DATA
    artists = json.loads(anvil.server.call('get_references', model_id))
    self.repeating_panel.items = artists
