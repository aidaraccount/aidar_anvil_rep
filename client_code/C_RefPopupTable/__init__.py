from ._anvil_designer import C_RefPopupTableTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json

from anvil_extras import routing
from ..nav import click_link, click_button, logout, save_var, load_var


class C_RefPopupTable(C_RefPopupTableTemplate):
  def __init__(self, ref_data, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    global user
    user = anvil.users.get_user()

    # Any code you write here will run before the form opens.    
    self.data_grid_artists_data.items = ref_data

  def close_alert(self, **event_args):
    self.raise_event("x-close-alert")
