from ._anvil_designer import C_AddRefArtistsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class C_AddRefArtists(C_AddRefArtistsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    global cur_model_id
    user = anvil.users.get_user()    
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])

  def button_add_ref_artist_click(self, **event_args):
    status = anvil.server.call('add_ref_artist', user["user_id"], cur_model_id, self.text_box_spotify_artist_id.text)
    if status == 'Event created':
      alert(title='Processing Reference Artist..',
            content='We are processing your artist, which may take a short moment. You will find it at RATINGS soon.\n\nFeel free to add additional reference artists or start to INVESTIGATE - both  will improve your model accuracy.\n\nEnjoy it!')
    elif status == 'No SpotifyArtistID':
      alert(title='Error..', content='This is not a valid Spotify Artist ID.\n\nYou find the Spotify Artist ID on open.spotify.com. It contains 22 characters.\n\nMichael Jackson for example is available under https://open.spotify.com/artist/3fMbdgg4jU18AjLCKBhRSm. The last part of this URL is the Spotify Artist ID -> "3fMbdgg4jU18AjLCKBhRSm"')
      
  def text_box_access_token_pressed_enter(self, **event_args):
    status = anvil.server.call('add_ref_artist', user["user_id"], cur_model_id, self.text_box_spotify_artist_id.text)
    if status == 'Event created':
      alert(title='Processing Reference Artist..',
            content='We are processing your artist, which may take a short moment. You will find it at RATINGS soon.\n\nFeel free to add additional reference artists or start to INVESTIGATE - both  will improve your model accuracy.\n\nEnjoy it!')
    elif status == 'No SpotifyArtistID':
      alert(title='Error..', content='This is not a valid Spotify Artist ID.\n\nYou find the Spotify Artist ID on open.spotify.com. It contains 22 characters.\n\nMichael Jackson for example is available under https://open.spotify.com/artist/3fMbdgg4jU18AjLCKBhRSm. The last part of this URL is the Spotify Artist ID -> "3fMbdgg4jU18AjLCKBhRSm"')
