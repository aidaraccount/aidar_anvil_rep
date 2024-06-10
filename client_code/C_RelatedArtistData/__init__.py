from ._anvil_designer import C_RelatedArtistDataTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json

class C_RelatedArtistData(C_RelatedArtistDataTemplate):
  def __init__(self, model_id, artist_id, name, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    
    self.label_name.text = name

    self.data_grid_artists_data.items = json.loads(anvil.server.call('search_related_artists', user["user_id"], model_id, artist_id))
