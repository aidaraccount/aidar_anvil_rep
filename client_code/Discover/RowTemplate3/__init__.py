from ._anvil_designer import RowTemplate3Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from anvil_extras import routing
from ...nav import click_link, click_button, logout, login_check, load_var, save_var


class RowTemplate3(RowTemplate3Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    

  def related_artist_pic_link_click(self, **event_args):
    click_link(self.related_artist_pic_link, f'artists?artist_id={self.related_artist_pic_link.url}', event_args)

  def related_artist_name_link_click(self, **event_args):
    click_link(self.related_artist_name_link, f'artists?artist_id={self.related_artist_name_link.url}', event_args)
