from ._anvil_designer import RelatedRowsTemplate
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


class RelatedRows(RelatedRowsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()

  # CLICKS 
  def related_click(self, **event_args):
    self.parent.parent.parent.close_alert()
    save_var('value', self.item["Name"])
    click_link(self.link_1, f'artists?artist_id={self.item["ArtistID"]}', event_args)


