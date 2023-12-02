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
    
    # get information for selection bar on the left
    anvil.server.reset_session()

    watchlist_selection = json.loads(anvil.server.call('get_watchlist_selection', cur_model_id))
    self.repeating_panel_selection.items = watchlist_selection
    self.repeating_panel_selection.get_components()[0].border = '1px solid #fd652d' # orange

    global cur_ai_artist_id
    cur_ai_artist_id = watchlist_selection[0]['ArtistID']
    print(f"watchlist initial: {cur_ai_artist_id}")
    self.refresh_watchlist_detail(cur_model_id, cur_ai_artist_id)
  
  def refresh_watchlist_detail (self, cur_model_id, cur_ai_artist_id, **event_args):
    print(f"watchlist refresh: {cur_ai_artist_id}")
    cur_ai_artist_id = cur_ai_artist_id
    self.repeating_panel_detail.items = json.loads(anvil.server.call('get_watchlist_detail', cur_model_id, cur_ai_artist_id))
  
  def button_note_click(self, **event_args):
    print(f"watchlist add_note: {cur_ai_artist_id}")
    anvil.server.call('add_note', user["user_id"], cur_model_id, cur_ai_artist_id, "", "", self.text_area_note.text)
    self.text_area_note.text = ""
    self.refresh_watchlist_detail(cur_model_id, cur_ai_artist_id)
