from ._anvil_designer import Main_InTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users

from ..C_Investigate import C_Investigate
from ..C_Filter import C_Filter
from ..C_Watchlist import C_Watchlist
from ..C_Rating import C_Rating
from ..C_AddRefArtists import C_AddRefArtists
from ..C_NoModel import C_NoModel
from ..C_SearchArtist import C_SearchArtist


class Main_In(Main_InTemplate):
  def __init__(self, temp_artist_id, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    
    # Any code you write here will run before the form opens.
    global user
    global cur_model_id
    user = anvil.users.get_user()

    print(user["user_id"])

    if user["user_id"] == None:
      cur_model_id = None
    else:
      cur_model_id = anvil.server.call('get_model_id',  user["user_id"])
    
    if (cur_model_id == None):
      self.content_panel.add_component(C_NoModel())
    else:
      self.content_panel.add_component(C_Investigate(temp_artist_id = temp_artist_id))
    
  def logo_click(self, **event_args):
    open_form('Main_Out')
    
  def logout_click(self, **event_args):
    anvil.users.logout()
    if (anvil.users.get_user() == None):
      open_form('Main_Out')

  def investigate_click(self, **event_args):
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])
    self.content_panel.clear()
    if (cur_model_id == None):
      self.content_panel.add_component(C_NoModel())
    else:
      self.content_panel.add_component(C_Investigate(temp_artist_id = None))

  def filter_click(self, **event_args):
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])
    self.content_panel.clear()
    if (cur_model_id == None):
      self.content_panel.add_component(C_NoModel())
    else:
      self.content_panel.add_component(C_Filter())

  def watchlist_click(self, **event_args):
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])
    self.content_panel.clear()
    if (cur_model_id == None):
      self.content_panel.add_component(C_NoModel())
    else:
      self.content_panel.add_component(C_Watchlist())

  def rating_click(self, **event_args):
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])
    self.content_panel.clear()
    if (cur_model_id == None):
      self.content_panel.add_component(C_NoModel())
    else:
      self.content_panel.add_component(C_Rating())

  def add_ref_artists_click(self, **event_args):
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])
    self.content_panel.clear()
    if (cur_model_id == None):
      self.content_panel.add_component(C_NoModel())
    else:
      self.content_panel.add_component(C_AddRefArtists())

  def link_search_click(self, **event_args):
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])
    self.content_panel.clear()
    if (cur_model_id == None):
      self.content_panel.add_component(C_NoModel())
    else:
      self.content_panel.add_component(C_SearchArtist())
