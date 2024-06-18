from ._anvil_designer import C_RelatedArtistSearchTemplate
from ..C_RelatedPopupTable import C_RelatedPopupTable

from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json

class C_RelatedArtistSearch(C_RelatedArtistSearchTemplate):
  def __init__(self, model_id, artist_id=None, name=None, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.model_id=model_id  
    self.artist_id = artist_id
    self.name = name
    
    global user
    user = anvil.users.get_user()
    
    # Set up the initial UI state
    if self.name:
      self.header_artist_name.text = "Related Artist to " + self.name
    else:
      self.header_artist_name.text = "Related Artists"

    if self.name:
      self.title_related_artist_name.content = '<p class="anvil-role-title">UPDATE IN PROGRESS<br>  <span style="color: rgb(200, 200, 200); font-size: 16px;">back soon</span></p>'
    else:
      self.title_related_artist_name.content = '<p class=anvil-role-title>Related Artists</p>'
    
    self.data_grid_related_artists_header.visible = False
    self.rate_artists_button.visible = False
    
    # Load related artists data if artist_id is provided
    if self.artist_id:
      self.load_related_artists()
      self.data_grid_related_artists_header.visible = True
      self.rate_artists_button.visible = True

  def text_box_search_pressed_enter(self, **event_args):
    search_text = self.text_box_search.text
    popup_table = alert(
      content=C_RelatedPopupTable(self.model_id, search_text),
      large=True,
      buttons=[]
    )

  def load_related_artists(self):
    if self.artist_id:
      self.data_grid_related_artists_data.items = json.loads(
        anvil.server.call('search_related_artists', user["user_id"], self.model_id, self.artist_id)
      )
      
