from ._anvil_designer import Main_InTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
import json

from ..C_Home import C_Home
from ..C_Investigate import C_Investigate
from ..C_Filter import C_Filter
from ..C_Watchlist_Details import C_Watchlist_Details
from ..C_Watchlist_Funnel import C_Watchlist_Funnel
from ..C_Watchlist_Overview import C_Watchlist_Overview
from ..C_Rating import C_Rating
from ..C_EditRefArtists import C_EditRefArtists
from ..C_AddRefArtists import C_AddRefArtists
from ..C_NoModel import C_NoModel
from ..C_SearchArtist import C_SearchArtist
from ..C_CreateModel import C_CreateModel
from ..C_ConnectModel import C_ConnectModel


class Main_In(Main_InTemplate):
  def __init__(self, temp_artist_id, target, value, **properties):
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
      self.change_nav_visibility(status=False)
    else:
      self.content_panel.add_component(C_Home())
      self.link_home.background = "theme:Accent 2"
      self.update_no_notifications()

    # ROUTING
    if target == 'C_Filter':
      self.content_panel.clear()
      self.content_panel.add_component(C_Filter())
      
    if target == 'C_AddRefArtists':
      self.content_panel.clear()
      self.content_panel.add_component(C_AddRefArtists())
      
    if target == 'C_Watchlist_Funnel':
      self.content_panel.clear()
      self.content_panel.add_component(C_Watchlist_Funnel())
      
    if target == 'C_Investigate':
      self.route_discover_ai(temp_artist_id = temp_artist_id)
      
    if target == 'C_Watchlist_Details':
      self.route_manage_watchlist(temp_artist_id = temp_artist_id)

    if target == 'C_SearchArtist':
      self.route_discover_name(search = value)

  
  def logo_click(self, **event_args):
    open_form('Main_Out')
    
  def logout_click(self, **event_args):
    anvil.users.logout()
    if (anvil.users.get_user() == None):
      open_form('Main_Out')

  def update_no_notifications(self, **event_args):
    NoNotifications = json.loads(anvil.server.call('get_no_notifications', cur_model_id))
    self.link_manage.text = 'MANAGE (' + str(NoNotifications[0]["count(*)"]) + ')'

  def reset_nav_backgrounds(self, **event_args):    
    self.link_home.background = None
    self.link_discover.background = None
    self.link_discover_ai.background = None
    self.link_discover_name.background = None
    self.link_discover_rated.background = None
    self.link_manage.background = None
    self.link_manage_watchlist.background = None
    self.link_manage_funnel.background = None
    self.link_manage_dev.background = None
    self.link_models.background = None
    self.link_models_setup.background = None
    self.link_models_artists.background = None
    #self.link_models_tracks.background = None
    #self.link_settings.background = None

  def change_nav_visibility(self, status, **event_args):
    self.link_home.visible = status
    self.link_discover.background = None
    self.link_discover_ai.background = None
    self.link_discover_name.background = None
    self.link_discover_rated.background = None
    self.link_manage.background = None
    self.link_manage_watchlist.background = None
    self.link_manage_funnel.background = None
    self.link_manage_dev.background = None
  
  # HOME
  def link_home_click(self, **event_args):
    self.content_panel.clear()
    self.content_panel.add_component(C_Home())
    self.reset_nav_backgrounds()
    self.link_home.background = "theme:Accent 2"
    
  # DISCOVER
  def change_discover_visibility(self, **event_args):
    if self.link_discover_ai.visible == False:
      self.link_discover.icon = 'fa:angle-up'
      self.link_discover_ai.visible = True
      self.link_discover_name.visible = True
      self.link_discover_rated.visible = True
    else:
      self.link_discover.icon = 'fa:angle-down'
      self.link_discover_ai.visible = False
      self.link_discover_name.visible = False
      self.link_discover_rated.visible = False
  
  def link_discover_ai_click(self, **event_args):
    self.route_discover_ai(temp_artist_id = None)

  def route_discover_ai(self, temp_artist_id, **event_args):
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])
    self.content_panel.clear()
    self.content_panel.add_component(C_Investigate(temp_artist_id = temp_artist_id))
    self.reset_nav_backgrounds()
    self.link_discover_ai.background = "theme:Accent 2"

  def link_discover_name_click(self, **event_args):
    self.route_discover_name(search = None)
  
  def route_discover_name(self, search, **event_args):
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])
    self.content_panel.clear()
    self.content_panel.add_component(C_SearchArtist(search = search))
    self.reset_nav_backgrounds()
    self.link_discover_name.background = "theme:Accent 2"

  def link_discover_rated_click(self, **event_args):
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])
    self.content_panel.clear()
    self.content_panel.add_component(C_Rating())
    self.reset_nav_backgrounds()
    self.link_discover_rated.background = "theme:Accent 2"

  # FILTER
  #def filter_click(self, **event_args):
  #  cur_model_id = anvil.server.call('get_model_id',  user["user_id"])
  #  self.content_panel.clear()    
  #  self.content_panel.add_component(C_Filter())

  #----------------------------------------------------------------------------------------------
  # MANAGE
  def change_manage_visibility(self, **event_args):
    if self.link_manage_watchlist.visible == False:
      self.link_manage.icon = 'fa:angle-up'
      self.link_manage_watchlist.visible = True
      self.link_manage_funnel.visible = True
      self.link_manage_dev.visible = True
    else:
      self.link_manage.icon = 'fa:angle-down'
      self.link_manage_watchlist.visible = False
      self.link_manage_funnel.visible = False
      self.link_manage_dev.visible = False
  
  def link_manage_watchlist_click(self, **event_args):
    self.route_manage_watchlist(temp_artist_id = None)

  def route_manage_watchlist(self, temp_artist_id, **event_args):
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])
    self.content_panel.clear()
    self.content_panel.add_component(C_Watchlist_Details(temp_artist_id))
    self.reset_nav_backgrounds()
    self.link_manage_watchlist.background = "theme:Accent 2"
    
  def link_manage_funnel_click(self, **event_args):
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])
    self.content_panel.clear()
    self.content_panel.add_component(C_Watchlist_Funnel())
    self.reset_nav_backgrounds()
    self.link_manage_funnel.background = "theme:Accent 2"

  def link_manage_dev_click(self, **event_args):
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])
    self.content_panel.clear()
    self.content_panel.add_component(C_Watchlist_Overview())
    self.reset_nav_backgrounds()
    self.link_manage_dev.background = "theme:Accent 2"

  
  # MODELS
  def change_models_visibility(self, **event_args):
    if self.link_models_artists.visible == False:
      self.link_models.icon = 'fa:angle-up'
      self.link_models_artists.visible = True
      #self.link_models_tracks.visible = True
    else:
      self.link_models.icon = 'fa:angle-down'
      self.link_models_artists.visible = False
      #self.link_models_tracks.visible = False

  def link_models_artists_click(self, **event_args):
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])
    self.content_panel.clear()
    self.content_panel.add_component(C_EditRefArtists())
    self.reset_nav_backgrounds()
    self.link_models_artists.background = "theme:Accent 2"
  
  #def add_ref_artists_click(self, **event_args):
  #  cur_model_id = anvil.server.call('get_model_id',  user["user_id"])
  #  self.content_panel.clear()
  #  self.content_panel.add_component(C_AddRefArtists())


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
