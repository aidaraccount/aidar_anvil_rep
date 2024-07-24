from ._anvil_designer import NoModelTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ..ConnectModel import ConnectModel
from ..CreateModel import CreateModel

from anvil_extras import routing
from ..nav import click_link, click_button


@routing.route('no_model', title='No Model')
class NoModel(NoModelTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  
  def button_connect_model_click(self, **event_args):
    self.content_panel.clear()
    self.content_panel.add_component(ConnectModel())

  def button_create_model_click(self, **event_args):
    self.content_panel.clear()
    self.content_panel.add_component(CreateModel())