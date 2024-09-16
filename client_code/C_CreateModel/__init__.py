from ._anvil_designer import C_CreateModelTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import random
import string

from anvil_extras import routing
from ..nav import click_link, click_button, save_var

from ..C_AddRefArtists import C_AddRefArtists


@routing.route('create_model', title='Create Model')
class C_CreateModel(C_CreateModelTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()

    self.text_box_access_token.text = f"{''.join(random.choice((string.ascii_letters + string.digits)) for _ in range(3))}-{''.join(random.choice((string.ascii_letters + string.digits)) for _ in range(3))}-{''.join(random.choice((string.ascii_letters + string.digits)) for _ in range(3))}"
  
  def button_create_model_click(self, **event_args):
    if self.text_box_access_token.text == '':
      alert(title='Missing Access Token',
        content="Please add an Access Token!")
        
    else:
      status = anvil.server.call('create_model',
                                 user["user_id"],
                                 self.text_box_model_name.text,
                                 self.text_box_description.text,
                                 self.text_box_access_token.text)
      if (status == 'Congratulations, your Model was successfully created!'):
        # refresh model_id
        model_id = anvil.server.call('get_model_id',  user["user_id"])
        anvil.server.call('update_model_usage', user["user_id"], model_id)
        save_var('model_id', model_id)
    
        # continue to add ref artists
        alert(title='Congratulations..',
          content="your Model was successfully created!\n\nNow, let's set your model up by adding some artists as reference.")        
        click_button(f'model_profile?model_id={model_id}&section=AddRefArtists', event_args)
        
        # refresh models components
        get_open_form().refresh_models_components()
        get_open_form().change_nav_visibility(status=True)
        
      else:
        alert(title='Error..', content=status)

  def text_box_model_name_lost_focus(self, **event_args):
    self.text_box_description.focus()

  def text_box_description_lost_focus(self, **event_args):
    self.text_box_access_token.focus()
