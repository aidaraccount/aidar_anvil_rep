from ._anvil_designer import SearchRefRowsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ...Main_In import Main_In
from ...C_Investigate import C_Investigate

class SearchRefRows(SearchRefRowsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def inspect_link_click(self, **event_args):
    open_form('Main_In', temp_artist_id = int(self.inspect_link.url))

  def inspect_pic_link_click(self, **event_args):
    open_form('Main_In', temp_artist_id = int(self.inspect_pic_link.url))

  def inspect_name_link_click(self, **event_args):
    open_form('Main_In', temp_artist_id = int(self.inspect_name_link.url))
