from ._anvil_designer import Main_InTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users

from ..C_Investigate import C_Investigate
from ..C_Filter import C_Filter
#from ..Ratings import Ratings

class Main_In(Main_InTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.content_panel.add_component(C_Investigate())

    # Any code you write here will run before the form opens.

    
  def logo_click(self, **event_args):
    open_form('Main_Out', user_id = 2)
    
  def logout_click(self, **event_args):
    anvil.users.logout()
    if (anvil.users.get_user() == None):
      open_form('Main_Out', user_id = 2)


  def investigate_click(self, **event_args):
    self.content_panel.clear()
    self.content_panel.add_component(C_Investigate())

  def filter_click(self, **event_args):
      self.content_panel.clear()
      self.content_panel.add_component(C_Filter())

