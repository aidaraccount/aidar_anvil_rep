from ._anvil_designer import NoModelTemplate
from anvil import *
import stripe.checkout
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil.js.window import navbar_noModel_noSubs
from datetime import datetime

from anvil_extras import routing
from ..nav import click_link, click_button


@routing.route('no_model', title='No Model')
class NoModel(NoModelTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    global user
    user = anvil.users.get_user()
    
    # Any code you write here will run before the form opens.
    get_open_form().SearchBar.visible = False
    if user is None or user == 'None':
      self.visible = False
      print("NOMODEL INIT - No user, hiding form", flush=True)

    elif user['expiration_date'] is not None and (datetime.today().date() - user['expiration_date']).days > 0:
      routing.set_url_hash('settings?section=Subscription', load_from_cache=False)
      get_open_form().SearchBar.visible = False
      print("NOMODEL INIT - Subscription expired, redirecting", flush=True)

  
  def button_create_model_click(self, **event_args):
    click_button('model_setup?model_id=None&section=Basics', event_args)
    
    # view navigation sidebar
    anvil.js.call_js("navbar_noModel_noSubs", True)
