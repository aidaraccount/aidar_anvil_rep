from ._anvil_designer import Main_InTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
import json

from ..C_Investigate import C_Investigate
from ..C_Filter import C_Filter
from ..C_Watchlist_Details import C_Watchlist_Details
from ..C_Watchlist_Overview import C_Watchlist_Overview
from ..C_Rating import C_Rating
from ..C_EditRefArtists import C_EditRefArtists
from ..C_AddRefArtists import C_AddRefArtists
from ..C_NoModel import C_NoModel
from ..C_SearchArtist import C_SearchArtist
from ..C_CreateModel import C_CreateModel
from ..C_ConnectModel import C_ConnectModel


class Main_In(Main_InTemplate):
  def __init__(self, temp_artist_id, target, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    
    # Any code you write here will run before the form opens.    
    global user
    global cur_model_id
    user = anvil.users.get_user()

    if user["user_id"] == None:
      cur_model_id = None
    else:
      cur_model_id = anvil.server.call('get_model_id',  user["user_id"])
    
    if (cur_model_id == None):
      self.content_panel.add_component(C_NoModel())
      self.link_models.background = "theme:Accent 2"
      self.link_models_create.background = "theme:Sidebar Background"
      self.link_models_connect.background = "theme:Sidebar Background"
      self.link_models.visible = True
      self.link_investigate.visible = False
      self.link_filter.visible = False
      self.link_watchlist.visible = False
      self.link_rating.visible = False
      self.link_search.visible = False
      self.link_ref_artists.visible = False
    else:
      self.content_panel.add_component(C_Investigate(temp_artist_id = temp_artist_id))
      self.link_investigate.background = "theme:Accent 2"
      self.update_no_notifications()

    if target == 'C_Watchlist_Details':
      self.route_watchlist_details(temp_artist_id = temp_artist_id)

  
  def logo_click(self, **event_args):
    open_form('Main_Out')
    
  def logout_click(self, **event_args):
    anvil.users.logout()
    if (anvil.users.get_user() == None):
      open_form('Main_Out')

  def update_no_notifications(self, **event_args):
    NoNotifications = json.loads(anvil.server.call('get_no_notifications', cur_model_id))
    self.link_watchlist.text = 'Watchlist (' + str(NoNotifications[0]["count(*)"]) + ')'

  # AI-MODELS
  def link_models_click(self, **event_args):
    self.content_panel.clear()
    self.content_panel.add_component(C_NoModel())
    self.link_models.background = "theme:Accent 2"
    self.link_models_create.background = "theme:Sidebar Background"
    self.link_models_connect.background = "theme:Sidebar Background"

  def link_models_create_click(self, **event_args):
    self.content_panel.clear()
    self.content_panel.add_component(C_CreateModel())
    self.link_models_create.background = "theme:Accent 2"
    self.link_models.background = None
    self.link_models_connect.background = None

  def link_models_connect_click(self, **event_args):
    self.content_panel.clear()
    self.content_panel.add_component(C_ConnectModel())
    self.link_models_connect.background = "theme:Accent 2"
    self.link_models_create.background = None
    self.link_models.background = None

  # INVESTIGATE
  def investigate_click(self, **event_args):
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])
    self.content_panel.clear()
    self.content_panel.add_component(C_Investigate(temp_artist_id = None))
    self.link_investigate.background = "theme:Accent 2"
    self.link_filter.background = None
    self.link_watchlist.background = None
    self.link_watchlist_overview.background = None
    self.link_watchlist_details.background = None
    self.link_rating.background = None
    self.link_search.background = None
    self.link_ref_artists.background = None
    self.link_edit_ref_artists.background = None
    self.link_add_ref_artists.background = None

  # FILTER
  def filter_click(self, **event_args):
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])
    self.content_panel.clear()    
    self.content_panel.add_component(C_Filter())
    self.link_filter.background = "theme:Accent 2"
    self.link_investigate.background = None
    self.link_watchlist.background = None
    self.link_watchlist_overview.background = None
    self.link_watchlist_details.background = None
    self.link_rating.background = None
    self.link_search.background = None
    self.link_ref_artists.background = None
    self.link_edit_ref_artists.background = None
    self.link_add_ref_artists.background = None

  # RATINGS
  def rating_click(self, **event_args):
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])
    self.content_panel.clear()
    self.content_panel.add_component(C_Rating())
    self.link_rating.background = "theme:Accent 2"
    self.link_filter.background = None
    self.link_watchlist.background = None
    self.link_watchlist_overview.background = None
    self.link_watchlist_details.background = None
    self.link_investigate.background = None
    self.link_search.background = None
    self.link_ref_artists.background = None
    self.link_edit_ref_artists.background = None
    self.link_add_ref_artists.background = None

  # SEARCH
  def link_search_click(self, **event_args):
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])
    self.content_panel.clear()
    self.content_panel.add_component(C_SearchArtist())
    self.link_search.background = "theme:Accent 2"
    self.link_filter.background = None
    self.link_watchlist.background = None
    self.link_watchlist_overview.background = None
    self.link_watchlist_details.background = None
    self.link_rating.background = None
    self.link_investigate.background = None
    self.link_ref_artists.background = None
    self.link_edit_ref_artists.background = None
    self.link_add_ref_artists.background = None

  # REF ARTISTS
  def change_ref_artists_visibility(self, **event_args):
    if self.link_edit_ref_artists.visible == False:
      self.link_edit_ref_artists.visible = True
      self.link_add_ref_artists.visible = True
    else:
      self.link_edit_ref_artists.visible = False
      self.link_add_ref_artists.visible = False
  
  def edit_ref_artists_click(self, **event_args):
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])
    self.content_panel.clear()
    self.content_panel.add_component(C_EditRefArtists())
    self.link_edit_ref_artists.background = "theme:Accent 2"
    self.link_add_ref_artists.background = "theme:Sidebar Background"
    
    self.link_investigate.background = None
    self.link_filter.background = None
    self.link_watchlist.background = None
    self.link_watchlist_overview.background = None
    self.link_watchlist_details.background = None
    self.link_rating.background = None
    self.link_search.background = None
    self.link_ref_artists.background = None

  def add_ref_artists_click(self, **event_args):
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])
    self.content_panel.clear()
    self.content_panel.add_component(C_AddRefArtists())
    self.link_add_ref_artists.background = "theme:Accent 2"
    self.link_edit_ref_artists.background = "theme:Sidebar Background"
    
    self.link_investigate.background = None
    self.link_filter.background = None
    self.link_watchlist.background = None
    self.link_watchlist_overview.background = None
    self.link_watchlist_details.background = None
    self.link_rating.background = None
    self.link_search.background = None
    self.link_ref_artists.background = None

  #----------------------------------------------------------------------------------------------
  # WATCHLIST
  def change_watchlist_visibility(self, **event_args):
    if self.link_watchlist_overview.visible == False:
      self.link_watchlist_overview.visible = True
      self.link_watchlist_details.visible = True
    else:
      self.link_watchlist_overview.visible = False
      self.link_watchlist_details.visible = False
    
  def link_watchlist_overview_click(self, **event_args):
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])
    self.content_panel.clear()
    self.content_panel.add_component(C_Watchlist_Overview())
    
    self.link_watchlist_overview.background = "theme:Accent 2"
    self.link_watchlist_details.background = "theme:Sidebar Background"
    
    self.link_investigate.background = None
    self.link_filter.background = None
    self.link_watchlist.background = None
    self.link_rating.background = None
    self.link_search.background = None
    self.link_ref_artists.background = None
    self.link_edit_ref_artists.background = None
    self.link_add_ref_artists.background = None

  def watchlist_details_click(self, **event_args):
    self.route_watchlist_details(temp_artist_id = None)

  def route_watchlist_details(self, temp_artist_id, **event_args):
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])
    self.content_panel.clear()
    self.content_panel.add_component(C_Watchlist_Details(temp_artist_id))

    self.link_watchlist_overview.background = "theme:Sidebar Background"
    self.link_watchlist_details.background = "theme:Accent 2"
    
    self.link_investigate.background = None
    self.link_filter.background = None
    self.link_watchlist.background = None
    self.link_rating.background = None
    self.link_search.background = None
    self.link_ref_artists.background = None
    self.link_edit_ref_artists.background = None
    self.link_add_ref_artists.background = None
  