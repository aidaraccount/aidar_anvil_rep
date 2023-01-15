from ._anvil_designer import C_ConnectModelTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class C_ConnectModel(C_ConnectModelTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def button_connect_model_click(self, **event_args):
    anvil.server.call('ConnectModel', self.text_box_access_token.text)

