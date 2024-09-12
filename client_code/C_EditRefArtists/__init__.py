from ._anvil_designer import C_EditRefArtistsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json

from anvil_extras import routing
from ..nav import click_link, click_button


class C_EditRefArtists(C_EditRefArtistsTemplate):
  def __init__(self, model_id, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    self.model_id=model_id

    self.get_references()

  
  def get_references(self, **event_args):
    self.repeating_panel_reference.items = json.loads(anvil.server.call('get_references', self.model_id))

  def button_add_refs_click(self, **event_args):
    click_button(f'model_profile?model_id={self.model_id}&section=AddRefArtists', event_args)
        
