from ._anvil_designer import C_HomeTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ..C_ConnectModel import C_ConnectModel
from ..C_CreateModel import C_CreateModel

class C_Home(C_HomeTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.


  def button_connect_model_click(self, **event_args):
    self.content_panel.clear()
    self.content_panel.add_component(C_ConnectModel())

  def button_create_model_click(self, **event_args):
    self.content_panel.clear()
    self.content_panel.add_component(C_CreateModel())
