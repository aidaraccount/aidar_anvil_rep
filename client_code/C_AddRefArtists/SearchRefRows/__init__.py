from ._anvil_designer import SearchRefRowsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ...Main_In import Main_In
from ...Discover import Discover
from ...nav import click_link, click_button, logout, login_check, load_var, save_var

class SearchRefRows(SearchRefRowsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    
    self.model_id = load_var("model_id")
  
  def inspect_link_click(self, **event_args):
    if int(self.item["ArtistPopularity_lat"]) > 30:
      c = confirm(content="Adding very popular artists will result in artist suggestions that are very popular as well.\n\nDo you wish to continue?",
                  title="ATTENTION! Popular Artist!")
      if c is True:
        self.add_ref_artist()
    else:
      self.add_ref_artist()
  
  def add_ref_artist(self, **event_args):
    status = anvil.server.call('add_ref_artist', user["user_id"], self.model_id, self.item['SpotifyArtistID'])
    if status == 'Event created':
      # increase No. references by 1
      self.parent.parent.parent.parent.parent.parent.parent.no_references.text = int(self.parent.parent.parent.parent.parent.parent.parent.no_references.text) + 1
    
      alert(title='Processing Reference Artist..',
            content='We are processing your artist, which may take a short moment. You will find it at REF. ARTISTS soon.\n\nFeel free to add additional reference artists or start to DISCOVER - both  will improve your model accuracy.\n\nEnjoy it!')

      if self.parent.parent.parent.parent.label_cnt_1.background == 'theme:Accent 1':
        self.parent.parent.parent.parent.label_cnt_1.background = 'theme:Orange'
      elif self.parent.parent.parent.parent.label_cnt_2.background == 'theme:Accent 1':
        self.parent.parent.parent.parent.label_cnt_2.background = 'theme:Orange'
      elif self.parent.parent.parent.parent.label_cnt_3.background == 'theme:Accent 1':
        self.parent.parent.parent.parent.label_cnt_3.background = 'theme:Orange'

      self.parent.parent.parent.parent.data_grid_artists_header.visible = False
      self.parent.parent.parent.parent.text_box_search.text = ''

    elif status == 'No SpotifyArtistID':
      alert(title='Error..', content='This is not a valid Spotify Artist ID.\n\nYou find the Spotify Artist ID on open.spotify.com. It contains 22 characters.\n\nMichael Jackson for example is available under https://open.spotify.com/artist/3fMbdgg4jU18AjLCKBhRSm. The last part of this URL is the Spotify Artist ID -> "3fMbdgg4jU18AjLCKBhRSm"')
