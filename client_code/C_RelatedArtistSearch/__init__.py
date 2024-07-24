from ._anvil_designer import C_RelatedArtistSearchTemplate
from ..C_RelatedPopupTable import C_RelatedPopupTable

from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json

from anvil_extras import routing
from ..nav import click_link, click_button, logout, login_check, save_var, load_var


@routing.route('rel_artists', title='Rel. Artists')
class C_RelatedArtistSearch(C_RelatedArtistSearchTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    save_var("artist_id", None)
    save_var("name", None)

    model_id = load_var("model_id")
    artist_id = load_var("artist_id")
    name = load_var("name")
    
    # Any code you write here will run before the form opens.
    self.model_id=model_id  
    self.artist_id = artist_id
    self.name = name
    
    global user
    user = anvil.users.get_user()

    if self.name:
      self.title_related_artist_name.content = f"<p>Related Artists to <span style='color: rgb(253, 101, 45);''>{self.name}</span></p>"
    else:
      self.title_related_artist_name.content = '<p>Related Artists</p>'
    
    self.data_grid_related_artists_header.visible = False
    self.rate_artists_button.visible = False
    
    # Load related artists data if artist_id is provided
    if self.artist_id:
      self.load_related_artists()
      self.data_grid_related_artists_header.visible = True
      # self.rate_artists_button.visible = True

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
      
