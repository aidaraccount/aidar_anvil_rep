from ._anvil_designer import Observe_2Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json

from anvil_extras import routing
from ..nav import click_link, click_button, logout, login_check, load_var


@routing.route("observe_2", title="Observe")
class Observe_2(Observe_2Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)


    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()

    model_id = load_var("model_id")
    self.model_id = model_id
    print(f"Observe model_id: {model_id}")
    
    # OBSERVED DATA
    observed = json.loads(anvil.server.call('get_observed', model_id))

    # add running Number
    for i, artist in enumerate(observed, start=1):
      artist['Number'] = i
    
    print(observed[0])
    self.repeating_panel_table.items = observed
    