from ._anvil_designer import Watchlist_FunnelTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json

from anvil_extras import routing
from ..nav import click_link, click_button, logout, login_check, load_var


@routing.route('watchlist_funnel', title='Funnel')
class Watchlist_Funnel(Watchlist_FunnelTemplate):
  def __init__(self, **properties):
    
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    model_id = load_var("model_id")
    print(f"Watchlist_Funnel model_id: {model_id}")

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    self.model_id = model_id

    # FUNNEL DATA
    data = json.loads(anvil.server.call('get_watchlist_selection', user["user_id"], None))
    self.repeating_panel_1.items = [item for item in data if item['Status'] in ['Reconnect later', 'Not interested', None]] #BACKLOG
    self.repeating_panel_2.items = [item for item in data if item['Status'] in ['Action required', 'Requires revision', 'Waiting for decision']] #EVALUATION
    self.repeating_panel_3.items = [item for item in data if item['Status'] in ['Build connection', 'Awaiting response', 'Exploring opportunities', 'Positive response']] #CONTACTING
    self.repeating_panel_4.items = [item for item in data if item['Status'] in ['In negotiations', 'Contract in progress']] #NEGOTIATION
    self.repeating_panel_5.items = [item for item in data if item['Status'] in ['Success']] #Success

  def button_search_click(self, **event_args):
    data = json.loads(anvil.server.call('get_watchlist_selection', user["user_id"], None))
    data = [entry for entry in data if str(entry["Name"]).lower().find(str(self.text_box_search.text).lower()) != -1]
    
    self.repeating_panel_1.items = [item for item in data if item['Status'] in ['Reconnect later', 'Not interested', None]] #BACKLOG
    self.repeating_panel_2.items = [item for item in data if item['Status'] in ['Action required', 'Requires revision', 'Waiting for decision']] #EVALUATION
    self.repeating_panel_3.items = [item for item in data if item['Status'] in ['Build connection', 'Awaiting response', 'Exploring opportunities', 'Positive response']] #CONTACTING
    self.repeating_panel_4.items = [item for item in data if item['Status'] in ['In negotiations', 'Contract in progress']] #NEGOTIATION
    self.repeating_panel_5.items = [item for item in data if item['Status'] in ['Success']] #Success
