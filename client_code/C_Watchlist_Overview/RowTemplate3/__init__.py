from ._anvil_designer import RowTemplate3Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ...C_Watchlist_Details import C_Watchlist_Details


class RowTemplate3(RowTemplate3Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def button_details_click(self, **event_args):
    open_form('Main_In', temp_artist_id = self.item["ArtistID"], target = 'C_Watchlist_Details')

  def link_artist_click(self, **event_args):
    open_form('Main_In', temp_artist_id = self.item["ArtistID"], target = None)
