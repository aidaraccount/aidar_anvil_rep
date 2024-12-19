from ._anvil_designer import RepeatingPanel_TracksTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ....nav import click_link, click_button, load_var, save_var

class RepeatingPanel_Tracks(RepeatingPanel_TracksTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    
    # Any code you write here will run before the form opens.

    # set album picture    
    if self.item["album_picture_url"] is not None:
      self.album_img.source = self.item["album_picture_url"]
    else:
      self.album_img.source = '_/theme/pics/Favicon_orange.JPG'

  def play_button_click(self, **event_args):
    all_rows = self.parent.parent.parent.parent.items
    all_track_ids = [track['spotify_track_id'] for artist in all_rows for track in artist['tracks']]
    # print("all_track_ids", all_track_ids)
    # print("item",self.item)
    # print('lastplayedtrackid:', load_var("lastplayedtrackid"))
    # print('self.item["spotify_track_id"]:', self.item["spotify_track_id"])
    
    if load_var("lastplayedtrackid") != self.item["spotify_track_id"]:
      self.lastplayedtrackid = self.item["spotify_track_id"]
      save_var('lastplayedtrackid', self.item["spotify_track_id"])
      # print(self.lastplayedtrackid)
      
      self.parent.parent.parent.parent.parent.parent.parent.footer_left.clear()
      self.parent.parent.parent.parent.parent.parent.parent.spotify_HTML_player()
      self.parent.parent.parent.parent.parent.parent.parent.call_js('createOrUpdateSpotifyPlayer', 'track', self.item["spotify_track_id"], all_track_ids)
      anvil.js.call_js('playSpotify')
      
    else:
      anvil.js.call_js('playSpotify')

    # # Update buttons dynamically    
    # if self.play_button.icon == 'fa:pause-circle':
    #   # set all other:
    #   self.parent.parent.parent.parent.parent.parent.parent.set_small_track_play_buttons()
    #   # set specific one
    #   self.play_button.icon = 'fa:play-circle'
    #   self.parent.parent.parent.parent.parent.parent.parent.play_button_central.icon = 'fa:play-circle'
    # else:
    #   self.play_button.icon = 'fa:pause-circle'
    #   self.parent.parent.parent.parent.parent.parent.parent.play_button_central.icon = 'fa:pause-circle'
    