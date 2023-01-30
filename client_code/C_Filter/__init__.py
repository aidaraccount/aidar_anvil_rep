from ._anvil_designer import C_FilterTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json

from ..C_Investigate import C_Investigate

class C_Filter(C_FilterTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.    
    global user
    global cur_model_id
    user = anvil.users.get_user()
    cur_model_id = anvil.server.call('GetModelID',  user["user_id"])
    
    self.load_filters()

  def load_filters(self, **event_args):
    fil = json.loads(anvil.server.call('GetFilters', cur_model_id))
    # 1. General
    self.artist_popularity_lat_min.text = fil["artist_popularity_lat_min"]
    self.artist_popularity_lat_max.text = fil["artist_popularity_lat_max"]
    self.artist_follower_lat_min.text = fil["artist_follower_lat_min"]
    self.artist_follower_lat_max.text = fil["artist_follower_lat_max"]
    # 2. Musical Features
    self.avg_duration_min.text = fil["avg_duration_min"]
    self.avg_duration_max.text = fil["avg_duration_max"]
    self.avg_danceability_min.text = fil["avg_danceability_min"]
    self.avg_danceability_max.text = fil["avg_danceability_max"]
    self.avg_energy_min.text = fil["avg_energy_min"]
    self.avg_energy_max.text = fil["avg_energy_max"]
    self.avg_key_min.text = fil["avg_key_min"]
    self.avg_key_max.text = fil["avg_key_max"]
    self.avg_loudness_min.text = fil["avg_loudness_min"]
    self.avg_loudness_max.text = fil["avg_loudness_max"]
    self.avg_mode_min.text = fil["avg_mode_min"]
    self.avg_mode_max.text = fil["avg_mode_max"]
    self.avg_speechiness_min.text = fil["avg_speechiness_min"]
    self.avg_speechiness_max.text = fil["avg_speechiness_max"]
    self.avg_acousticness_min.text = fil["avg_acousticness_min"]
    self.avg_acousticness_max.text = fil["avg_acousticness_max"]
    self.avg_instrumentalness_min.text = fil["avg_instrumentalness_min"]
    self.avg_instrumentalness_max.text = fil["avg_instrumentalness_max"]
    self.avg_liveness_min.text = fil["avg_liveness_min"]
    self.avg_liveness_max.text = fil["avg_liveness_max"]
    self.avg_valence_min.text = fil["avg_valence_min"]
    self.avg_valence_max.text = fil["avg_valence_max"]
    self.avg_tempo_min.text = fil["avg_tempo_min"]
    self.avg_tempo_max.text = fil["avg_tempo_max"]
    
  def apply_filters_click(self, **event_args):
    # 1. General
    artist_popularity_lat_min = self.artist_popularity_lat_min.text
    artist_popularity_lat_max = self.artist_popularity_lat_max.text
    artist_follower_lat_min = self.artist_follower_lat_min.text
    artist_follower_lat_max = self.artist_follower_lat_max.text
    # 2. Musical Features
    avg_duration_min = self.avg_duration_min.text
    avg_duration_max = self.avg_duration_max.text
    avg_danceability_min = self.avg_danceability_min.text
    avg_danceability_max = self.avg_danceability_max.text
    avg_energy_min = self.avg_energy_min.text
    avg_energy_max = self.avg_energy_max.text
    avg_key_min = self.avg_key_min.text
    avg_key_max = self.avg_key_max.text
    avg_loudness_min = self.avg_loudness_min.text
    avg_loudness_max = self.avg_loudness_max.text
    avg_mode_min = self.avg_mode_min.text
    avg_mode_max = self.avg_mode_max.text
    avg_speechiness_min = self.avg_speechiness_min.text
    avg_speechiness_max = self.avg_speechiness_max.text
    avg_acousticness_min = self.avg_acousticness_min.text
    avg_acousticness_max = self.avg_acousticness_max.text
    avg_instrumentalness_min = self.avg_instrumentalness_min.text
    avg_instrumentalness_max = self.avg_instrumentalness_max.text
    avg_liveness_min = self.avg_liveness_min.text
    avg_liveness_max = self.avg_liveness_max.text
    avg_valence_min = self.avg_valence_min.text
    avg_valence_max = self.avg_valence_max.text
    avg_tempo_min = self.avg_tempo_min.text
    avg_tempo_max = self.avg_tempo_max.text
       
    anvil.server.call('ChangeFilters',
                      cur_model_id,
                      artist_popularity_lat_min,
                      artist_popularity_lat_max,
                      artist_follower_lat_min,
                      artist_follower_lat_max,
                      avg_duration_min,
                      avg_duration_max,
                      avg_danceability_min,
                      avg_danceability_max,
                      avg_energy_min,
                      avg_energy_max,
                      avg_key_min,
                      avg_key_max,
                      avg_loudness_min,
                      avg_loudness_max,
                      avg_mode_min,
                      avg_mode_max,
                      avg_speechiness_min,
                      avg_speechiness_max,
                      avg_acousticness_min,
                      avg_acousticness_max,
                      avg_instrumentalness_min,
                      avg_instrumentalness_max,
                      avg_liveness_min,
                      avg_liveness_max,
                      avg_valence_min,
                      avg_valence_max,
                      avg_tempo_min,
                      avg_tempo_max
                     )
    self.content_panel.clear()
    self.content_panel.add_component(C_Investigate())