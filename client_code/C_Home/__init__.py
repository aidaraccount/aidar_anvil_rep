from ._anvil_designer import C_HomeTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json

class C_Home(C_HomeTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    global cur_model_id
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])

    # FUNNEL DATA
    data = json.loads(anvil.server.call('get_watchlist_selection', cur_model_id))
    self.repeating_panel_2.items = [item for item in data if item['Status'] in ['Action required', 'Requires revision', 'Waiting for decision']] #EVALUATION
    self.repeating_panel_3.items = [item for item in data if item['Status'] in ['Build connection', 'Awaiting response', 'Exploring opportunities', 'Positive response']] #CONTACTING
    self.repeating_panel_4.items = [item for item in data if item['Status'] in ['In negotiations', 'Contract in progress']] #NEGOTIATION

  def button_search_click(self, **event_args):
    data = json.loads(anvil.server.call('get_watchlist_selection', cur_model_id))
    data = [entry for entry in data if str(entry["Name"]).lower().find(str(self.text_box_search.text).lower()) != -1]
    
    self.repeating_panel_2.items = [item for item in data if item['Status'] in ['Action required', 'Requires revision', 'Waiting for decision']] #EVALUATION
    self.repeating_panel_3.items = [item for item in data if item['Status'] in ['Build connection', 'Awaiting response', 'Exploring opportunities', 'Positive response']] #CONTACTING
    self.repeating_panel_4.items = [item for item in data if item['Status'] in ['In negotiations', 'Contract in progress']] #NEGOTIATION

  def link_discover_click(self, **event_args):
    open_form('Main_In', temp_artist_id = None, target = 'C_Investigate')

  def link_funnel_click(self, **event_args):
    open_form('Main_In', temp_artist_id = None, target = 'C_Watchlist_Funnel')
    