from ._anvil_designer import C_RelatedArtistSearch_html_newTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json

class C_RelatedArtistSearch_html_new(C_RelatedArtistSearch_html_newTemplate):
  def __init__(self, model_id=2, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.model_id=model_id
    

  def text_box_search_pressed_enter(self, **event_args):
    search_text = self.text_box_search.text
    self.data_grid_artists_data.items = json.loads(anvil.server.call('search_artist', self.model_id, search_text.strip()))
