from ._anvil_designer import C_AddRefArtistsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json


class C_AddRefArtists(C_AddRefArtistsTemplate):
  def __init__(self, model_id, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    self.model_id=model_id

    # fill the status bars
    references = json.loads(anvil.server.call('get_references',  model_id))
    cnt = 0
    for refs in references:
      for ref in refs:
        if ref["ArtistID"] is not None:
          cnt = cnt + 1
    if cnt >= 1: self.label_cnt_1.background = 'theme:Orange'
    if cnt >= 2: self.label_cnt_2.background = 'theme:Orange'
    if cnt >= 3: self.label_cnt_3.background = 'theme:Orange'
  
  def button_add_ref_artist_click(self, **event_args):
    status = anvil.server.call('add_ref_artist', user["user_id"], self.model_id, self.text_box_spotify_artist_id.text)
    if status == 'Event created':
      if self.label_cnt_1.background == 'theme:Accent 1':
        self.label_cnt_1.background = 'theme:Orange'
      elif self.label_cnt_2.background == 'theme:Accent 1':
        self.label_cnt_2.background = 'theme:Orange'
      elif self.label_cnt_3.background == 'theme:Accent 1':
        self.label_cnt_3.background = 'theme:Orange'
      
      alert(title='Processing Reference Artist..',
            content='We are processing your artist, which may take a short moment. You will find it at REF. ARTISTS soon.\n\nFeel free to add additional reference artists or start to DISCOVER - both  will improve your model accuracy.\n\nEnjoy it!')
    elif status == 'No SpotifyArtistID':
      alert(title='Error..', content='This is not a valid Spotify Artist ID.\n\nYou find the Spotify Artist ID on open.spotify.com. It contains 22 characters.\n\nMichael Jackson for example is available under https://open.spotify.com/artist/3fMbdgg4jU18AjLCKBhRSm. The last part of this URL is the Spotify Artist ID -> "3fMbdgg4jU18AjLCKBhRSm"')

  def text_box_search_enter(self, **event_args):
    anvil.server.reset_session()
    self.data_grid_artists_header.visible = True
    search_text = self.text_box_search.text
    self.data_grid_artists_data.items = json.loads(anvil.server.call('search_artist', self.model_id, search_text.strip()))
