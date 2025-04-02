from ._anvil_designer import RepPanel_TrackReleasesTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil.js.window import playSpotify
import json
from anvil.js.window import document

from ...nav import click_link, click_button, load_var, save_var



class RepPanel_TrackReleases(RepPanel_TrackReleasesTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    
    # Any code you write here will run before the form opens.
    pass

  
  def button_play_track_click(self, **event_args):
    # 1. Get track information
    all_rows = self.parent.items
    track_ids = [entry["SpotifyTrackID"] for entry in all_rows]
    current_track_id = self.item["SpotifyTrackID"]
    
    # 2. Check if we're playing a different track than before
    if load_var("lastplayed") != current_track_id:
      # 2.1 Restore original behavior: always clear and recreate player for different tracks
      # This ensures correct track selection functionality
      self.parent.parent.parent.parent.parent.parent.spotify_player_spot.clear()
      self.parent.parent.parent.parent.parent.parent.spotify_HTML_player()
      self.parent.parent.parent.parent.parent.parent.call_js(
        'createOrUpdateSpotifyPlayer', 
        anvil.js.get_dom_node(self), 
        'track', 
        current_track_id, 
        track_ids
      )
      anvil.js.call_js('playSpotify')
    else:
      # 2.2 Same track - just toggle play/pause
      anvil.js.call_js('playSpotify')
    
    # 3. Update state
    self.lastplayed = current_track_id
    save_var('lastplayed', current_track_id)
    
    # 4. Update UI
    if self.button_play_track.icon == 'fa:play-circle':
      # Reset all other buttons
      self.parent.parent.parent.parent.parent.parent.reset_track_play_buttons()
      # Set this button to pause
      self.button_play_track.icon = 'fa:pause-circle'
    else:
      self.button_play_track.icon = 'fa:play-circle'
    
    # 5. Update artist button
    self.parent.parent.parent.parent.parent.parent.spotify_artist_button.icon = 'fa:play-circle'