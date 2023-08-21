from ._anvil_designer import SearchRowsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ...Main_In import Main_In
from ...C_Investigate import C_Investigate

class SearchRows(SearchRowsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def inspect_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    
    print("Link geklickt.." + str(self.inspect_link.text))

    open_form('Main_In', user_id = 1)