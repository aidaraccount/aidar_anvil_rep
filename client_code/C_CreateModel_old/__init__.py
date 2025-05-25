from ._anvil_designer import C_CreateModel_oldTemplate
from anvil import *
import stripe.checkout
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
class C_CreateModel_old(C_CreateModel_oldTemplate):
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
      status = 'Missing Access Token'
      
    elif self.text_box_model_name.text == '':
      alert(title='Missing Agent Name',
        content="Please add an Agent Name!")
      status = 'Missing Agent Name'
        
    else:
      model_id = anvil.server.call('create_model',
                                 user["user_id"],
                                 self.text_box_model_name.text,
                                 self.text_box_description.text,
                                 self.text_box_access_token.text)
      if (model_id is not None):
        # refresh model_id
        model_id = anvil.server.call('get_model_id',  user["user_id"])
        anvil.server.call('update_model_usage', user["user_id"], model_id)
        save_var('model_id', model_id)
    
        # refresh models components
        get_open_form().refresh_models_components()

        # view navigation sidebar
        anvil.js.call_js("navbar_noModel_noSubs", True)
        
      else:
        alert(title='Error..', content=status)

    return status

  def text_box_model_name_lost_focus(self, **event_args):
    self.text_box_description.focus()

  def text_box_description_lost_focus(self, **event_args):
    self.text_box_access_token.focus()

  def text_box_model_name_change(self, **event_args):
    if self.text_box_model_name.text == '' and self.text_box_access_token.text == '':
      self.parent.parent.get_components()[-1].get_components()[1].role = 'call-to-action-button'
    else:
      self.parent.parent.get_components()[-1].get_components()[1].role = ''
