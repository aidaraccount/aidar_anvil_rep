from ._anvil_designer import Main_InTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
import json
import datetime

from ..C_Home import C_Home
from ..C_Discover import C_Discover
from ..C_Filter import C_Filter
from ..C_Watchlist_Details import C_Watchlist_Details
from ..C_Watchlist_Funnel import C_Watchlist_Funnel
from ..C_Watchlist_Overview import C_Watchlist_Overview
from ..C_Rating import C_Rating
from ..C_EditRefArtists import C_EditRefArtists
from ..C_AddRefArtists import C_AddRefArtists
from ..C_NoModel import C_NoModel
from ..C_SearchArtist import C_SearchArtist
from ..C_RelatedArtistSearch import C_RelatedArtistSearch
# from ..C_RelatedArtistData import C_RelatedArtistData
from ..C_CreateModel import C_CreateModel
from ..C_ConnectModel import C_ConnectModel
from ..C_ModelProfile import C_ModelProfile


class Main_In(Main_InTemplate):
  def __init__(self, model_id, temp_artist_id, target, value, **properties):
    print(f"{datetime.datetime.now()}: Main_In - link_login_click - 1", flush=True)
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.role = 'POST_LOGIN_PAGE'

    # Any code you write here will run before the form opens.    
    begin = datetime.datetime.now()
    
    global user
    user = anvil.users.get_user()
    global status
    status = True
    print(f"{datetime.datetime.now()}: Main_In - link_login_click - 2", flush=True)
    
    if user["user_id"] is None:
      self.model_id = None
    else:
      if model_id is None:
        self.model_id = anvil.server.call('get_model_id',  user["user_id"])
        #anvil.server.call('update_model_usage', user["user_id"], self.model_id)
      else:
        self.model_id = model_id
    
    print(f"{datetime.datetime.now()}: Main_In - link_login_click - 3", flush=True)  # 20s, 17s - 4s

    if self.model_id is None:
      status = False
      self.content_panel.add_component(C_NoModel())
      self.change_nav_visibility(status=status)
      
    elif self.model_id is not None and target is None:
      print(f"{datetime.datetime.now()}: Main_In - link_login_click - 3a", flush=True)
      self.content_panel.add_component(C_Home(model_id=self.model_id))
      print(f"{datetime.datetime.now()}: Main_In - link_login_click - 3b", flush=True)  # 3:10m, 2:12m - 19s
      self.link_home.background = "theme:Accent 2"
      print(f"{datetime.datetime.now()}: Main_In - link_login_click - 3c", flush=True)
      self.update_no_notifications()
      print(f"{datetime.datetime.now()}: Main_In - link_login_click - 3d", flush=True)  # 17s, 14s - 1.5s
    
    # ROUTING
    elif self.model_id is not None and target is not None:
      print(f"{datetime.datetime.now()}: Main_In - link_login_click - 4", flush=True)
      
      if target == 'C_Filter':
        self.content_panel.clear()
        self.content_panel.add_component(C_Filter(model_id=model_id))
        
      if target == 'C_AddRefArtists':
        self.content_panel.clear()
        self.content_panel.add_component(C_AddRefArtists(model_id=model_id))
        self.reset_nav_backgrounds()
        
      if target == 'C_Watchlist_Funnel':
        self.content_panel.clear()
        self.content_panel.add_component(C_Watchlist_Funnel(model_id=model_id))
        self.reset_nav_backgrounds()
        self.link_manage_funnel.background = "theme:Accent 2"
        
      if target == 'C_Discover':
        self.link_discover_ai_click(model_id=self.model_id, temp_artist_id=temp_artist_id)
        
      if target == 'C_Watchlist_Details':
        self.content_panel.clear()
        self.content_panel.add_component(C_Watchlist_Details(model_id=model_id, temp_artist_id=temp_artist_id))
        self.reset_nav_backgrounds()
        self.link_manage_watchlist.background = "theme:Accent 2"
  
      if target == 'C_RelatedArtistSearch':
        self.route_discover_rel_data(model_id=self.model_id, artist_id=temp_artist_id, name=value)
  
      if target == 'C_SearchArtist':
        self.link_discover_name_click(search=value)

      if target == 'C_ModelProfile':
        self.content_panel.clear()
        self.content_panel.add_component(C_ModelProfile(model_id=model_id, target=value))
        self.reset_nav_backgrounds()
            
    print(f"{datetime.datetime.now()}: Main_In - link_login_click - 5", flush=True)
    print(f"TotalTime Main_In: {datetime.datetime.now() - begin}", flush=True)

    
    # MODEL PROFILES IN NAV
    model_ids = json.loads(anvil.server.call('get_model_ids',  user["user_id"]))
    
    for i in range(0, len(model_ids)):
      if model_ids[i]["is_last_used"] is True:
        model_link = Link(
          icon='fa:angle-right',
          text=model_ids[i]["model_name"],
          role='underline-link'
          )
        #right_icon = Icon(name="fa:circle")
        #model_link.add_component(right_icon, slot='right')
      else:
        model_link = Link(
          icon='fa:angle-right',
          text=model_ids[i]["model_name"]
          )
      model_link.set_event_handler('click', self.create_model_click_handler(model_ids[i]["model_id"], model_link))
      self.nav_models.add_component(model_link)
      
    
  # MODEL ROUTING
  def create_model_click_handler(self, model_id, model_link):
    def handler(**event_args):
      self.models_click(model_id, model_link, **event_args)
    return handler

  def models_click(self, link_model_id, model_link, **event_args):
    self.reset_nav_backgrounds()
    model_link.background = "theme:Accent 2"
    self.content_panel.clear()
    self.content_panel.add_component(C_ModelProfile(model_id=link_model_id, target=None))
  # ------------
  
  def logo_click(self, **event_args):
    open_form('Main_Out')
    
  def logout_click(self, **event_args):
    anvil.users.logout()
    if (anvil.users.get_user() is None):
      open_form('Main_Out')

  def update_no_notifications(self, **event_args):
    NoNotifications = json.loads(anvil.server.call('get_no_notifications', self.model_id))
    self.link_manage.text = 'MANAGE (' + str(NoNotifications[0]["cnt"]) + ')'

  def reset_nav_backgrounds(self, **event_args):    
    self.link_home.background = None
    self.link_discover.background = None
    self.link_discover_ai.background = None
    self.link_discover_rel.background = None
    self.link_discover_name.background = None
    self.link_manage.background = None
    self.link_manage_watchlist.background = None
    self.link_manage_funnel.background = None
    self.link_manage_dev.background = None
    self.link_models.background = None
    for component in self.nav_models.get_components():
      component.background = None
    #self.link_settings.background = None

  def change_nav_visibility(self, status, **event_args):
    self.link_home.visible = status

    self.linear_panel_discover.visible = status
    self.link_discover.visible = status
    self.link_discover_ai.visible = status
    self.link_discover_rel.visible = status
    self.link_discover_name.visible = status

    self.linear_panel_manage.visible = status
    self.link_manage.visible = status
    self.link_manage_watchlist.visible = status
    self.link_manage_funnel.visible = status
    self.link_manage_dev.visible = status
    
    self.link_models.visible = True
  
  #----------------------------------------------------------------------------------------------
  # HOME
  def link_home_click(self, **event_args):
    self.content_panel.clear()
    self.content_panel.add_component(C_Home(model_id=self.model_id))
    self.reset_nav_backgrounds()
    self.link_home.background = "theme:Accent 2"
  
  #----------------------------------------------------------------------------------------------  
  # DISCOVER
  def change_discover_visibility(self, **event_args):
    if self.link_discover_ai.visible is False:
      self.link_discover.icon = 'fa:angle-up'
      self.link_discover_ai.visible = True
      self.link_discover_rel.visible = True
      self.link_discover_name.visible = True
    else:
      self.link_discover.icon = 'fa:angle-down'
      self.link_discover_ai.visible = False
      self.link_discover_rel.visible = False
      self.link_discover_name.visible = False
  
  def link_discover_ai_click(self, temp_artist_id=None, **event_args):
    self.content_panel.clear()
    self.content_panel.add_component(C_Discover(model_id=self.model_id, temp_artist_id=temp_artist_id))
    self.reset_nav_backgrounds()
    self.link_discover_ai.background = "theme:Accent 2"

  def link_discover_rel_click(self, **event_args):
    self.content_panel.clear()
    self.content_panel.add_component(C_RelatedArtistSearch(model_id=self.model_id))
    self.reset_nav_backgrounds()
    self.link_discover_rel.background = "theme:Accent 2"

  def route_discover_rel_data(self, artist_id, name, **event_args):
    self.content_panel.clear()
    self.content_panel.add_component(C_RelatedArtistSearch(model_id=self.model_id, artist_id=artist_id, name=name))
    self.reset_nav_backgrounds()
    self.link_discover_rel.background = "theme:Accent 2"    
    
  def link_discover_name_click(self, search=None, **event_args):
    self.content_panel.clear()
    self.content_panel.add_component(C_SearchArtist(model_id=self.model_id, search=search))
    self.reset_nav_backgrounds()
    self.link_discover_name.background = "theme:Accent 2"

  #----------------------------------------------------------------------------------------------
  # MANAGE
  def change_manage_visibility(self, **event_args):
    if self.link_manage_watchlist.visible is False:
      self.link_manage.icon = 'fa:angle-up'
      self.link_manage_watchlist.visible = True
      self.link_manage_funnel.visible = True
      self.link_manage_dev.visible = True
    else:
      self.link_manage.icon = 'fa:angle-down'
      self.link_manage_watchlist.visible = False
      self.link_manage_funnel.visible = False
      self.link_manage_dev.visible = False

  def link_manage_watchlist_click(self, temp_artist_id=None, **event_args):
    self.content_panel.clear()
    self.content_panel.add_component(C_Watchlist_Details(self.model_id, temp_artist_id))
    self.reset_nav_backgrounds()
    self.link_manage_watchlist.background = "theme:Accent 2"
    
  def link_manage_funnel_click(self, **event_args):
    self.content_panel.clear()
    self.content_panel.add_component(C_Watchlist_Funnel(model_id=self.model_id))
    self.reset_nav_backgrounds()
    self.link_manage_funnel.background = "theme:Accent 2"

  def link_manage_dev_click(self, **event_args):
    self.content_panel.clear()
    self.content_panel.add_component(C_Watchlist_Overview(model_id=self.model_id))
    self.reset_nav_backgrounds()
    self.link_manage_dev.background = "theme:Accent 2"

  #----------------------------------------------------------------------------------------------
  # MODELS
  def change_models_visibility(self, **event_args):
    if self.link_models.icon == 'fa:angle-down':
      self.link_models.icon = 'fa:angle-up'
      for component in self.nav_models.get_components():
        component.visible = False
      self.column_panel_nav.visible = True
    else:
      self.link_models.icon = 'fa:angle-down'
      for component in self.nav_models.get_components():
        component.visible = True

  def create_model_click(self, **event_args):
    self.content_panel.clear()
    self.content_panel.add_component(C_CreateModel())
    self.reset_nav_backgrounds()

  def link_settings_click(self, **event_args):
    pass