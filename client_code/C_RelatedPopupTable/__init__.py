from ._anvil_designer import C_RelatedPopupTableTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json


class C_RelatedPopupTable(C_RelatedPopupTableTemplate):
  def __init__(self, model_id, search_text, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.data_grid_artists_data.items = json.loads(anvil.server.call('search_artist', model_id, search_text.strip()))

  def close_alert(self, **event_args):
    self.raise_event("x-close-alert")