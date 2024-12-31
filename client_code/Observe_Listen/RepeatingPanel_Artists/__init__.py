from ._anvil_designer import RepeatingPanel_ArtistsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.js

from ...C_Discover import C_Discover
from ...nav import click_link, click_button, logout, login_check, load_var, save_var


class RepeatingPanel_Artists(RepeatingPanel_ArtistsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.repeating_panel_tracks.items = self.item["tracks"]

    # set artist picture
    if self.item["artist_picture_url"] is not None:
      self.artist_img.source = self.item["artist_picture_url"]
    else:
      self.artist_img.source = '_/theme/pics/Favicon_orange.JPG'

  
  def link_artist_click(self, **event_args):
    # get all required data
    observed_tracks = self.parent.parent.parent.parent.parent.repeating_panel_artists.items
    self.all_track_ids = [track['spotify_track_id'] for artist in observed_tracks for track in artist['tracks']]
    self.all_artist_ids = [track['spotify_artist_id'] for artist in observed_tracks for track in artist['tracks']]
    self.all_ai_artist_ids = [track['artist_id'] for artist in observed_tracks for track in artist['tracks']]
    self.all_artist_names = [track['name'] for artist in observed_tracks for track in artist['tracks']]
        
    # start the first song of this artist
    save_var('has_played', 'True')
    anvil.js.call_js('playNextSong', anvil.js.get_dom_node(self), 'track', self.all_track_ids, self.all_artist_ids, self.all_artist_names, self.item["tracks"][0]['spotify_track_id'])

    # refresh artist profile
    self.parent.parent.parent.parent.parent.column_panel_discover.clear()
    self.parent.parent.parent.parent.parent.column_panel_discover.add_component(C_Discover(self.item["artist_id"]))