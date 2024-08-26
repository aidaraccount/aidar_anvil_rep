from ._anvil_designer import RowTemplate1Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil.js.window import playSpotify
import json
from anvil.js.window import document


class RowTemplate1(RowTemplate1Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def button_play_track_click(self, **event_args):
    self.isplaying = False
    
    if self.button_play_track.icon == 'fa:play-circle' and self.isplaying is False:
      self.button_play_track.icon = 'fa:pause-circle'
      print("if 1 before:", self.isplaying)
      self.isplaying = True
      print("if 1 after:",self.isplaying)
      self.parent.parent.parent.parent.parent.parent.spotify_player_spot.clear()
      self.parent.parent.parent.parent.parent.parent.spotify_HTML_player()
      print(self.item["SpotifyTrackID"])
      self.parent.parent.parent.parent.parent.parent.call_js('createOrUpdateSpotifyPlayer', 'track', self.item["SpotifyTrackID"])
      anvil.js.call_js('playSpotify')
    
    elif self.button_play_track.icon == 'fa:pause-circle' and self.isplaying is True:
      print("elif 1 before:", self.button_play_track.icon, self.isplaying)
      self.button_play_track.icon = 'fa:play-circle'
      print("elif 1 after:", self.button_play_track.icon, self.isplaying)
      anvil.js.call_js('playSpotify')

    elif self.button_play_track.icon == 'fa:play-circle' and self.isplaying is True:
      print("elif 2 before:", self.button_play_track.icon, self.isplaying)
      self.button_play_track.icon = 'fa:pause-circle'
      print("elif 2 after:", self.button_play_track.icon, self.isplaying)
      anvil.js.call_js('playSpotify')

    else:
      print("else statement", self.isplaying)
      self.button_play_track.icon = 'fa:play-circle'
      

    # print(self.parent.parent.parent.parent.parent.parent)
    # self.parent.parent.parent.parent.parent.parent.
    # temp_artist_id = self.parent.parent.parent.parent.parent.parent.url_dict['artist_id']
    # model_id = self.parent.parent.parent.parent.parent.parent.model_id
    # sug = json.loads(anvil.server.call('get_suggestion', 'Inspect', model_id, temp_artist_id)) # Free, Explore, Inspect, Dissect
    # embed_iframe_element_template = document.getElementById('embed-iframe')
    # print("FORM SHOW FROM PARENT", embed_iframe_element_template)