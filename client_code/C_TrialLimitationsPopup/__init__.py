from ._anvil_designer import C_TrialLimitationsPopupTemplate
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


class C_TrialLimitationsPopup(C_TrialLimitationsPopupTemplate):
  def __init__(self, total_count, today_count, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    global user
    user = anvil.users.get_user()

    model_id = load_var("model_id")
    print(f"C_TrialLimitationsPopup - total_count: {total_count}; today_count: {today_count}")


  def close_alert(self, **event_args):
    self.raise_event("x-close-alert")
