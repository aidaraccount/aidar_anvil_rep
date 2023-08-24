from ._anvil_designer import C_SearchArtistTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json

class C_SearchArtist(C_SearchArtistTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()

    global cur_model_id
    #cur_model_id = anvil.server.call('get_model_id',  user["user_id"])
    cur_model_id = 2
    
  def text_box_search_change(self, **event_args):
    """This method is called when the text in this text box is edited"""
    print(self.text_box_search.text, flush=True)
    #print(json.loads(anvil.server.call('search_artist', cur_model_id, self.text_box_search.text)), flush=True)
    print("fct start", flush=True)
    self.data_grid_artists_data.items = json.loads(anvil.server.call('search_artist', cur_model_id, self.text_box_search.text))
    print("fct end", flush=True)
