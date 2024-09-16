from ._anvil_designer import RefRowsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ...Main_In import Main_In
from ...Discover import Discover

from anvil_extras import routing
from ...nav import click_link, click_button, logout, login_check, load_var, save_var


class RefRows(RefRowsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    self.model_id_in_creation = load_var('model_id_in_creation')

  # CLICKS
  def related_click(self, **event_args):
    self.parent.parent.parent.close_alert()

    status = anvil.server.call('add_ref_artist', user["user_id"], self.model_id_in_creation, self.item['SpotifyArtistID'])
    if status == 'Event created':    
      alert(title='Processing Reference Artist..', 
            content='We are processing your artist, which may take a short moment. You will find it at REF. ARTISTS soon.\n\nFeel free to add additional reference artists or start to DISCOVER - both  will improve your model accuracy.\n\nEnjoy it!')
    
    elif status == 'No SpotifyArtistID':
      alert(title='Error..', content='This is not a valid Spotify Artist ID.\n\nYou find the Spotify Artist ID on open.spotify.com. It contains 22 characters.\n\nMichael Jackson for example is available under https://open.spotify.com/artist/3fMbdgg4jU18AjLCKBhRSm. The last part of this URL is the Spotify Artist ID -> "3fMbdgg4jU18AjLCKBhRSm"')

  
