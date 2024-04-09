from ._anvil_designer import SearchRowsRelatedTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ...Main_In import Main_In
from ...C_Investigate import C_Investigate

class SearchRowsRelated(SearchRowsRelatedTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
  
  # BUTTONS
  def button_related_click(self, **event_args):
    open_form('Main_In', temp_artist_id = self.item["ArtistID"], target = 'C_RelatedArtistData', value=self.item["Name"])

  def button_inspect_click(self, **event_args):
    open_form('Main_In', temp_artist_id = self.item["ArtistID"], target='C_Investigate', value=None)
  