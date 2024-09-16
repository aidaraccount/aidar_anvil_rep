from ._anvil_designer import C_RefArtistsSettingsTemplate
from ..C_RefPopupTable import C_RefPopupTable
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json

from anvil_extras import routing
from ..nav import click_link, click_button, logout, save_var, load_var


@routing.route("add_ref_artists", title="Add Ref. Artists")
class C_RefArtistsSettings(C_RefArtistsSettingsTemplate):
  def __init__(self, model_id, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    self.model_id = model_id

  # def text_box_search_enter(self, **event_args):
  #   anvil.server.reset_session()
  #   self.data_grid_artists_header.visible = True
  #   search_text = self.text_box_search.text
  #   self.data_grid_artists_data.items = json.loads(
  #     anvil.server.call("search_artist", user["user_id"], search_text.strip())
  #   )
  
  def text_box_search_pressed_enter(self, **event_args):
    search_text = self.text_box_search.text
    popup_table = alert(
      content=C_RefPopupTable(self.model_id, search_text),
      large=True,
      buttons=[]
    )

