from ._anvil_designer import Main_OutTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users

from ..Main_In import Main_In
from ..C_LandingPage import C_LandingPage
from ..C_Investigate import C_Investigate


class Main_Out(Main_OutTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.content_panel.add_component(C_LandingPage())
    
    # Any code you write here will run before the form opens.
    check_log_status(self)
    
  def link_1_click(self, **event_args):
    anvil.users.login_with_form(allow_cancel=True, remember_by_default=True)
    check_log_status(self)
    user = anvil.users.get_user()
    if (user != None):
      open_form('Main_In', user_id = user["UserID"])
      
  def link_2_click(self, **event_args):
    anvil.users.logout()
    check_log_status(self)
    

def check_log_status(self, **event_args):
  if (anvil.users.get_user() == None):
    self.link_1.visible = True
    self.link_2.visible = False
  else:
    self.link_1.visible = False
    self.link_2.visible = True

