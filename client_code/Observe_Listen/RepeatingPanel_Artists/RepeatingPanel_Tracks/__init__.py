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

    self.play_button_copy.visible = False
    
    # set album picture    
    if self.item["album_picture_url"] is not None:
      self.album_img.source = self.item["album_picture_url"]
      self.album_img_copy.source = self.item["album_picture_url"]
    else:
      self.album_img.source = '_/theme/pics/Favicon_orange.JPG'
      self.album_img_copy.source = '_/theme/pics/Favicon_orange.JPG'

  
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

  def album_img_copy_mouse_enter(self, x, y, **event_args):
    self.play_button_copy.visible = True
    # print(f"in: {x}/{y}")
    save_var('x_in', x)
    save_var('y_in', y)

  def album_img_copy_mouse_leave(self, x, y, **event_args):
    x_in = float(load_var('x_in'))
    y_in = float(load_var('y_in'))
    
    # if x_in == 0 & 3 < x < 47: 
    #   # left in
    #   pass
    # elif x_in == 49 & 3 < x < 47: 
    #   # right in
    #   pass
    # elif y_in < 1 & 3 < y < 47: 
    #   # top in
    #   pass
    # elif y_in > 49 & 3 < y < 47: 
    #   # bottom in
    #   pass
    # else:
    #   self.play_button_copy.visible = False

    # if x == -1 or 
    # print(f"in: {x_in}/{y_in} | out: {x}/{y}")
    print(f"out: {x}/{y}")
