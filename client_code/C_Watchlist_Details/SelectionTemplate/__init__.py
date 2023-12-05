from ._anvil_designer import SelectionTemplateTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json


class SelectionTemplate(SelectionTemplateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    global cur_model_id
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])
    
  def link_selection_click(self, **event_args):
    cur_ai_artist_id = self.link_selection.url
    self.parent.parent.parent.update_cur_ai_artist_id(self.link_selection.url)
    self.parent.parent.parent.refresh_watchlist_details(cur_model_id, cur_ai_artist_id)
    self.parent.parent.parent.refresh_watchlist_notes(cur_model_id, cur_ai_artist_id)
    
    components = self.parent.get_components()
    for comp in components:
      comp.border = 'none'
    self.border = '1px solid #fd652d' # orange