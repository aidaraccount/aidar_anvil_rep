from ._anvil_designer import C_WatchlistTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json


class C_Watchlist(C_WatchlistTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    global cur_model_id
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])
    
    print("watchlist start", flush=True)
    
    anvil.server.reset_session()
    
    print(json.loads(anvil.server.call('get_watchlist', cur_model_id)))
    self.repeating_panel_watchlist.items = json.loads(anvil.server.call('get_watchlist', cur_model_id))
    
    print("watchlist end", flush=True)
