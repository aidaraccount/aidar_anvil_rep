from ._anvil_designer import C_FilterTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json

from ..C_Investigate import C_Investigate

model_id = 2

class C_Filter(C_FilterTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.    
    self.load_filters()

  def load_filters(self, **event_args):
    fil = json.loads(anvil.server.call('GetFilters', model_id))
    self.artist_popularity_lat_min.text = fil["artist_popularity_lat_min"]
    self.artist_popularity_lat_max.text = fil["artist_popularity_lat_max"]
    self.artist_follower_lat_min.text = fil["artist_follower_lat_min"]
    self.artist_follower_lat_max.text = fil["artist_follower_lat_max"]
    
  def apply_filters_click(self, **event_args):
    artist_popularity_lat_min = self.artist_popularity_lat_min.text
    artist_popularity_lat_max = self.artist_popularity_lat_max.text
    artist_follower_lat_min = self.artist_follower_lat_min.text
    artist_follower_lat_max = self.artist_follower_lat_max.text
    anvil.server.call('ChangeFilters',
                      model_id,
                      artist_popularity_lat_min,
                      artist_popularity_lat_max,
                      artist_follower_lat_min,
                      artist_follower_lat_max)
    #Main.link_investigate_click()
    self.content_panel.clear()
    self.content_panel.add_component(C_Investigate())