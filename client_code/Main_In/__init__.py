from ._anvil_designer import Main_InTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users

from ..C_Investigate import C_Investigate
from ..C_Filter import C_Filter
from ..C_Rating import C_Rating
from ..C_NoModel import C_NoModel

class Main_In(Main_InTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    
    # Any code you write here will run before the form opens.
    global user
    global cur_model_id
    user = anvil.users.get_user()
    cur_model_id = anvil.server.call('GetModelID',  user["user_id"])
    
    if (cur_model_id == None):
      self.content_panel.add_component(C_NoModel())
    else:
      self.content_panel.add_component(C_Investigate())
    
  def logo_click(self, **event_args):
    open_form('Main_Out')
    
  def logout_click(self, **event_args):
    anvil.users.logout()
    if (anvil.users.get_user() == None):
      open_form('Main_Out')

  def investigate_click(self, **event_args):
    self.content_panel.clear()
    if (cur_model_id == None):
      self.content_panel.add_component(C_NoModel())
    else:
      self.content_panel.add_component(C_Investigate())

  def filter_click(self, **event_args):
    self.content_panel.clear()
    if (cur_model_id == None):
      self.content_panel.add_component(C_NoModel())
    else:
      self.content_panel.add_component(C_Filter())

  def rating_click(self, **event_args):
    self.content_panel.clear()
    if (cur_model_id == None):
      self.content_panel.add_component(C_NoModel())
    else:
      self.content_panel.add_component(C_Rating())
