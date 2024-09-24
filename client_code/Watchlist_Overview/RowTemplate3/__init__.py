from ._anvil_designer import RowTemplate3Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ...WatchlistDetails import WatchlistDetails

from anvil_extras import routing
from ...nav import click_link, click_button, logout, login_check, load_var, save_var


class RowTemplate3(RowTemplate3Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
  def form_show(self, **event_args):
    self.label_7.role = 'col1'
    self.label_7.text = self.item['name']

  
  def button_details_click(self, **event_args):
    click_button(f'watchlist_details?artist_id={self.item["ArtistID"]}', event_args)

  def link_artist_click(self, **event_args):
    click_link(self.link_artist, f'artists?artist_id={self.item["ArtistID"]}', event_args)
