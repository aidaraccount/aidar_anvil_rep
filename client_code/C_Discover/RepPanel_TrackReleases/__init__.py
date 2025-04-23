from ._anvil_designer import RepPanel_TrackReleasesTemplate
from anvil import *
import stripe.checkout
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
    all_rows = self.parent.items
    all_track_ids = [entry["SpotifyTrackID"] for entry in all_rows]
    
    if load_var("lastplayedtrackid") != self.item["SpotifyTrackID"]:
      self.lastplayedtrackid = self.item["SpotifyTrackID"]
      save_var('lastplayedtrackid', self.item["SpotifyTrackID"])
    
      self.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.footer_left.clear()
      self.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent.spotify_HTML_player()
      anvil.js.call_js(
        "createOrUpdateSpotifyPlayer",
        anvil.js.get_dom_node(self),
        "track",
        self.item["SpotifyTrackID"],
        all_track_ids
      )
      anvil.js.call_js("playSpotify")

    else:
      anvil.js.call_js("playSpotify")

    if self.button_play_track.icon == "fa:play-circle":
      # reset all other:
      self.parent.parent.parent.parent.parent.parent.reset_track_play_buttons()
      # set specific one
      self.button_play_track.icon = "fa:pause-circle"
    else:
      self.button_play_track.icon = "fa:play-circle"
