from ._anvil_designer import SearchRowsRelated_html_newTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ...Main_In import Main_In
from ...C_Discover import C_Discover


class SearchRowsRelated_html_new(SearchRowsRelated_html_newTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    global model_id
    model_id = self.item["ModelID"]

  # BUTTONS 
  def button_related_click(self, **event_args):
    self.parent.parent.parent.close_alert()    
    open_form(
      "Main_In",
      model_id=model_id,
      temp_artist_id=self.item["ArtistID"],
      target="C_RelatedArtistSearch",
      value=self.item["Name"],
    )

  def button_inspect_click(self, **event_args):
    self.parent.parent.parent.close_alert()
    open_form(
      "Main_In",
      model_id=model_id,
      temp_artist_id=self.item["ArtistID"],
      target="C_Discover",
      value=None,
    )
