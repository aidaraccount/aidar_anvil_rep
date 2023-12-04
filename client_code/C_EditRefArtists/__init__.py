from ._anvil_designer import C_EditRefArtistsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json


class C_EditRefArtists(C_EditRefArtistsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    global cur_model_id
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])

    self.get_references()

  
  def get_references(self, **event_args):
    references = json.loads(anvil.server.call('get_references', cur_model_id))
    self.repeating_panel_reference.items = references
