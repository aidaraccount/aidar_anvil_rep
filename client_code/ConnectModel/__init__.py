from ._anvil_designer import ConnectModelTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ..Discover import Discover

from anvil_extras import routing
from ..nav import click_link, click_button


@routing.route('connect_model', title='Connect Model')
class ConnectModel(ConnectModelTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()

  def button_connect_model_click(self, **event_args):
    status = anvil.server.call('connect_model_by_access_token', user["user_id"], self.text_box_access_token.text)
    if status == 'Connection Successful':
      alert(title='Agent Connected!',
            content='You connected successfully to the Agent and are ready to go.\n\nEnjoy it!')
      click_button('home', event_args)

    else:
      alert(title='Error..', content=status)