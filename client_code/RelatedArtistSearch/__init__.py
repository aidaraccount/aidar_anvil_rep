from ._anvil_designer import RelatedArtistSearchTemplate
from ..C_RelatedPopupTable import C_RelatedPopupTable

from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json
from datetime import datetime

from anvil_extras import routing
from ..nav import click_link, click_button, logout, login_check, save_var, load_var


@routing.route('rel_artists', url_keys=['artist_id'], title='Rel. Artists')
class RelatedArtistSearch(RelatedArtistSearchTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    
    if user['expiration_date'] is not None and (datetime.today().date() - user['expiration_date']).days > 0:
      print("EXPIRED HOME")
      routing.set_url_hash('no_subs', load_from_cache=False)
      get_open_form().change_nav_visibility(status=False)
      get_open_form().SearchBar.visible = False
      
    else:
      model_id = load_var("model_id")
      name = load_var("value")
      artist_id = self.url_dict['artist_id']
      print(f"RelatedArtistSearch artist_id: {artist_id}")
      
      self.model_id=model_id  
      self.artist_id = artist_id
      self.name = name
      
      if artist_id == 'None':
        self.title_related_artist_name.content = '<p>Related Artists</p>'
        self.data_grid_related_artists_header.visible = False
        self.rate_artists_button.visible = False
      
      else:
        self.title_related_artist_name.content = f"<p>Related Artists to <span style='color: rgb(253, 101, 45);''>{self.name}</span></p>"
        self.load_related_artists()
        self.data_grid_related_artists_header.visible = True
        # self.rate_artists_button.visible = True

  
  def text_box_search_pressed_enter(self, **event_args):
    search_text = self.text_box_search.text
    popup_table = alert(
      content=C_RelatedPopupTable(self.model_id, search_text),
      large=True,
      buttons=[]
    )

  def load_related_artists(self):
    if self.artist_id:
      self.data_grid_related_artists_data.items = json.loads(
        anvil.server.call('search_related_artists', user["user_id"], self.artist_id)
      )
      
