from ._anvil_designer import C_Watchlist_Details_oldTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json


class C_Watchlist_Details_old(C_Watchlist_Details_oldTemplate):
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
    if len(watchlist_selection) > 0:
      self.repeating_panel_selection.items = watchlist_selection
      self.repeating_panel_selection.get_components()[0].border = '1px solid #fd652d' # orange

      global cur_ai_artist_id
      cur_ai_artist_id = watchlist_selection[0]['ArtistID']
      self.refresh_watchlist_detail(cur_model_id, cur_ai_artist_id)

      self.label_1.visible = False
      self.label_2.visible = False
      self.spacer_1.visible = False

    else:
      self.label_description.visible = False
      self.repeating_panel_selection.visible = False
      self.repeating_panel_detail.visible = False
      self.text_area_note.visible = False
      self.button_note.visible = False


  def update_cur_ai_artist_id(self, new_value):
    global cur_ai_artist_id
    cur_ai_artist_id = new_value

  def refresh_watchlist_detail (self, cur_model_id, cur_ai_artist_id, **event_args):
    cur_ai_artist_id = cur_ai_artist_id
    self.repeating_panel_detail.items = json.loads(anvil.server.call('get_watchlist_detail', cur_model_id, cur_ai_artist_id))

  def button_note_click(self, **event_args):
    anvil.server.call('add_note', user["user_id"], cur_model_id, cur_ai_artist_id, "", "", self.text_area_note.text)
    self.text_area_note.text = ""
    self.refresh_watchlist_detail(cur_model_id, cur_ai_artist_id)
