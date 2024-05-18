from ._anvil_designer import SearchRefRowsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ...Main_In import Main_In
from ...C_Discover import C_Discover

class SearchRefRows(SearchRefRowsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    global cur_model_id   
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])

  def inspect_link_click(self, **event_args):
    if int(self.item["ArtistPopularity_lat"]) > 30:
      c = confirm(content="Adding very popular artists will result in artist suggestions that are very popular as well.\n\nDo you wish to continue?",
                  title="ATTENTION! Popular Artist!")
      if c is True:
        self.add_ref_artist()
    else:
      self.add_ref_artist()
  
  def add_ref_artist(self, **event_args):
    status = anvil.server.call('add_ref_artist', user["user_id"], cur_model_id, self.inspect_link.tag)
    if status == 'Event created':
      alert(title='Processing Reference Artist..',
            content='We are processing your artist, which may take a short moment. You will find it at RATINGS soon.\n\nFeel free to add additional reference artists or start to INVESTIGATE - both  will improve your model accuracy.\n\nEnjoy it!')

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
