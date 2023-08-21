from ._anvil_designer import C_CreateModelTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import random
import string

from ..C_AddRefArtists import C_AddRefArtists

class C_CreateModel(C_CreateModelTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    global cur_model_id
    user = anvil.users.get_user()
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])

    self.text_box_access_token.text = f"{''.join(random.choice((string.ascii_letters + string.digits)) for _ in range(3))}-{''.join(random.choice((string.ascii_letters + string.digits)) for _ in range(3))}-{''.join(random.choice((string.ascii_letters + string.digits)) for _ in range(3))}"
  
  def button_create_model_click(self, **event_args):
    status = anvil.server.call('create_model',
                               user["user_id"],
                               self.text_box_model_name.text,
                               self.text_box_description.text,
                               self.text_box_access_token.text)
    if (status == 'Congratulations, your Model was successfully created!'):
      # refresh model_id
      cur_model_id = anvil.server.call('get_model_id',  user["user_id"])
      
      # continue to add ref artists
      alert(title='Congratulations..',
            content="your Model was successfully created!\n\nNow, let's set your model up by adding some artists as reference.")
      self.content_panel.clear()
      self.content_panel.add_component(C_AddRefArtists())
    else:
      alert(title='Error..', content=status)