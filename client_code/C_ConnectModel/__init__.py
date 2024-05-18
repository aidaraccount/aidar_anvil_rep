from ._anvil_designer import C_ConnectModelTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ..C_Discover import C_Discover

class C_ConnectModel(C_ConnectModelTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()

  def button_connect_model_click(self, **event_args):
    status = anvil.server.call('connect_model_by_access_token', user["user_id"], self.text_box_access_token.text)
    if status == 'Connection Successfull':
      alert(title='Model Connected!',
            content='You connected successfully to the model and are ready to go.\n\nEnjoy it!')
      self.content_panel.clear()
      self.content_panel.add_component(C_Discover())
    else:
      alert(title='Error..', content=status)