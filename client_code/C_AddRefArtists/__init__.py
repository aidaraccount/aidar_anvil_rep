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
    cur_model_id = anvil.server.call('GetModelID',  user["user_id"])

  def button_add_ref_artist_click(self, **event_args):
    status = anvil.server.call('AddRefArtist', user["user_id"], cur_model_id, self.text_box_spotify_artist_id.text)
    alert(status)

  def text_box_access_token_pressed_enter(self, **event_args):
    status = anvil.server.call('AddRefArtist', user["user_id"], cur_model_id, self.text_box_spotify_artist_id.text)
    alert(status)

    