from ._anvil_designer import C_CreateModelTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ..C_AddRefArtists import C_AddRefArtists

class C_CreateModel(C_CreateModelTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()

  def button_create_model_click(self, **event_args):
    status = anvil.server.call('CreateModel',
                               user["user_id"],
                               self.text_box_model_name.text,
                               self.text_box_description.text,
                               self.text_box_access_token.text)
    alert(status)
    if (status == 'Model successfully created!'):
      self.content_panel.clear()
      self.content_panel.add_component(C_AddRefArtists())
