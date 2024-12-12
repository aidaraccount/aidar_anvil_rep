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

from ...nav import click_link, click_button, load_var, save_var



class RowTemplate1(RowTemplate1Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    
    # Any code you write here will run before the form opens.

  def button_play_track_click(self, **event_args):

    all_rows = self.parent.items
    track_ids = [entry["SpotifyTrackID"] for entry in all_rows]
    # print(track_ids)
    current_index = all_rows.index(self.item)
    # print("line 51 - current index:", current_index)
    next_index = current_index + 1
    # print("line 52 - next index:", next_index)
    
    # if next_index < len(all_rows):  # Check if there's a next row
    #   current_track_id = all_rows[current_index]["SpotifyTrackID"]
    #   next_track_id = all_rows[next_index]["SpotifyTrackID"]
    #   print(f"Current Track ID: {current_track_id}")
    #   print(f"Next Track ID: {next_track_id}")
    #   # Optionally, perform an action with the next track ID, like preloading
    # else:
    #   print("No next track available.")
      
    if load_var("lastplayed") != self.item["SpotifyTrackID"]:
      self.parent.parent.parent.parent.parent.parent.spotify_player_spot.clear()
      self.parent.parent.parent.parent.parent.parent.spotify_HTML_player()
      self.parent.parent.parent.parent.parent.parent.call_js('createOrUpdateSpotifyPlayer', 'track', self.item["SpotifyTrackID"], track_ids)
      anvil.js.call_js('playSpotify')
      
    else:
      anvil.js.call_js('playSpotify')
      # pass

    self.lastplayed = self.item["SpotifyTrackID"]
    save_var('lastplayed', self.item["SpotifyTrackID"])
    # print(self.lastplayed)

    if self.button_play_track.icon == 'fa:play-circle':
      # reset all other:
      self.parent.parent.parent.parent.parent.parent.reset_track_play_buttons()
      # set specific one
      self.button_play_track.icon = 'fa:pause-circle'
    else:
      self.button_play_track.icon = 'fa:play-circle'
    
    self.parent.parent.parent.parent.parent.parent.spotify_artist_button.icon = 'fa:play-circle'
    
    self.update_play_pause_buttons(self.item["SpotifyTrackID"])

  @anvil.server.callable
  def update_play_pause_buttons(self, current_track_id):
    # Iterate through rows and update button icons
    for row in self.parent.get_components():
      if row.item['SpotifyTrackID'] == current_track_id:
        row.button_play_track.icon = 'fa:pause-circle'
      else:
        row.button_play_track.icon = 'fa:play-circle'

    print("THIS FUNCTION IS RUNNING WILD")

    