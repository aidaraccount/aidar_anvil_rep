from ._anvil_designer import C_SearchArtistTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json

from anvil_extras import routing
from ..nav import click_link, click_button, logout, login_check, load_var


@routing.route('search', title='Search Artist')
class C_SearchArtist(C_SearchArtistTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.model_id = load_var("model_id")
    print(f"C_SearchArtist model_id: {self.model_id}")
    search = load_var("search")
    
    global user
    user = anvil.users.get_user()
    
    if search is not None:
      self.data_grid_artists_data.items = json.loads(anvil.server.call('search_artist', self.model_id, search.strip()))
  
  def text_box_search_pressed_enter(self, **event_args):
    search_text = self.text_box_search.text
    self.data_grid_artists_data.items = json.loads(anvil.server.call('search_artist', self.model_id, search_text.strip()))
    
