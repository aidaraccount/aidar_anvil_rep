from ._anvil_designer import C_SearchPopupTableTemplate
from anvil import *
import stripe.checkout
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json

from anvil_extras import routing
from ..nav import click_link, click_button, logout, save_var, load_var


class C_SearchPopupTable(C_SearchPopupTableTemplate):
  def __init__(self, model_id, search_text, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    global user
    user = anvil.users.get_user()

    model_id = load_var("model_id")
    print(f"C_RelatedPopupTable model_id: {model_id}")

    # Any code you write here will run before the form opens.
    self.data_grid_artists_data.items = json.loads(
      anvil.server.call("search_artist", user["user_id"], search_text.strip())
    )

  def close_alert(self, **event_args):
    self.raise_event("x-close-alert")
