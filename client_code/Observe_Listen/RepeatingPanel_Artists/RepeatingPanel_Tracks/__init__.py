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
    global user
    user = anvil.users.get_user()

    self.play_button.visible = False
    
    # set album picture    
    if self.item["album_picture_url"] is not None:
      self.album_img.source = self.item["album_picture_url"]
    else:
      self.album_img.source = '_/theme/pics/Favicon_orange.JPG'

  
  def play_button_click(self, **event_args):
    save_var('has_played', 'True')
    all_rows = self.parent.parent.parent.parent.items
    all_track_ids = [track['spotify_track_id'] for artist in all_rows for track in artist['tracks']]
    all_artist_ids = [track['spotify_artist_id'] for artist in all_rows for track in artist['tracks']]
    all_artist_names = [track['name'] for artist in all_rows for track in artist['tracks']]
    
    if load_var("lastplayedtrackid") != self.item["spotify_track_id"]:
      save_var('lastplayedtrackid', self.item["spotify_track_id"])
      
      anvil.js.call_js(
        'playNextSong',
        anvil.js.get_dom_node(self),
        'track',
        all_track_ids,
        all_artist_ids,
        all_artist_names,
        self.item["spotify_track_id"]
      )
      
    else:
      anvil.js.call_js('playSpotify')

    # pushover
    anvil.server.call('sent_push_over',  'Observe_Listen', f'User {user["user_id"]}: track click')

  def album_img_mouse_enter(self, x, y, **event_args):
    # anvil.js.call_js('hidePlaylistButtons')
    self.play_button.visible = True

    # print('Parent Lvl 0:', self.get_components()[0].get_components()[0].get_components()[1].visible)

    
  def album_img_mouse_leave(self, x, y, **event_args):
    if x <= 0 or \
      x >= 50 or \
      y <= 0 or \
      y >= 50:
      self.play_button.visible = False      
    print(f"out: {x}/{y}")
