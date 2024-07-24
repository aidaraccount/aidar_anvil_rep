from ._anvil_designer import SearchRowsRelated_html_newTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ...Main_In import Main_In
from ...Discover import Discover


class SearchRowsRelated_html_new(SearchRowsRelated_html_newTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    global model_id
    model_id = self.item["ModelID"]

  # CLICKS 
  def related_click(self, **event_args):
    self.parent.parent.parent.close_alert()    
    open_form(
      "Main_In",
      model_id=model_id,
      temp_artist_id=self.item["ArtistID"],
      target="RelatedArtistSearch",
      value=self.item["Name"],
    )

