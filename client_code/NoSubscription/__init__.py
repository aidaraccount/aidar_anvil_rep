from ._anvil_designer import NoSubscriptionTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ..ConnectModel import ConnectModel
from ..C_CreateModel import C_CreateModel

from anvil_extras import routing
from ..nav import click_link, click_button


@routing.route("no_subs", title="No Subscription")
class NoSubscription(NoSubscriptionTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def button_connect_model_click(self, **event_args):
    # click_button("connect_model", event_args)
    print("Send email to AIDAR address")

  # def button_create_model_click(self, **event_args):
    # click_button("model_setup?model_id=None&section=Basics", event_args)

  def button_1_click(self, **event_args):
    print("Send email to AIDAR address")
    
