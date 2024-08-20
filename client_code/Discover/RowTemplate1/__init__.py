from ._anvil_designer import RowTemplate1Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil.js.window import playSpotify


class RowTemplate1(RowTemplate1Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def button_play_track_click(self, **event_args):
    # self.parent.parent.parent.parent.parent.parent.button_track_test_click(self.item['SpotifyTrackID'])
    anvil.js.call_js('playSpotify')
