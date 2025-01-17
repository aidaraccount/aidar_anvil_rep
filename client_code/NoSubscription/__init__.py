from ._anvil_designer import NoSubscriptionTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.js

from anvil_extras import routing
from ..nav import click_link, click_button


@routing.route("no_subs", title="No Subscription")
class NoSubscription(NoSubscriptionTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    pass

  
  def button_1_click(self, **event_args):    
    email_address = "info@aidar.ai"
    subject = "Renew Subscription"
    body = "Dear AIDAR team, I would like to..."
    mailto_link = f"mailto:{email_address}?subject={subject}&body={body}"
    
    # Open the mailto link using JavaScript
    anvil.js.window.open(mailto_link, "_self")    
