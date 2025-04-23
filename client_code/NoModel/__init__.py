from ._anvil_designer import NoModelTemplate
from anvil import *
import stripe.checkout
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil.js.window import navbar_noModel_noSubs

from anvil_extras import routing
from ..nav import click_link, click_button


@routing.route('no_model', title='No Model')
class NoModel(NoModelTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    get_open_form().SearchBar.visible = False

  
  def button_create_model_click(self, **event_args):
    click_button('model_setup?model_id=None&section=Basics', event_args)
    
    # view navigation sidebar
    anvil.js.call_js("navbar_noModel_noSubs", True)
