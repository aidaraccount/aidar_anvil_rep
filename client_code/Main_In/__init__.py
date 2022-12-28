from ._anvil_designer import Main_InTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users

from ..C_Dashboard import C_Dashboard

class Main_In(Main_InTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.content_panel.add_component(C_Dashboard())

    # Any code you write here will run before the form opens.

    
    
  def link_2_click(self, **event_args):
    anvil.users.logout()
    if (anvil.users.get_user() == None):
      open_form('Main_Out', user_id = 2)