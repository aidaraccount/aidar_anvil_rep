from ._anvil_designer import Main_InTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
import json
from datetime import datetime
from anvil.js.window import location
from ..C_SearchPopupTable import C_SearchPopupTable

from anvil_extras import routing
from ..nav import click_link, click_button, logout, login_check, save_var, load_var

from ..Main_Out import Main_Out
from ..Home import Home
from ..Discover import Discover
from ..WatchlistDetails import WatchlistDetails
from ..Watchlist_Funnel import Watchlist_Funnel
from ..Watchlist_Overview import Watchlist_Overview
from ..NoModel import NoModel
from ..NoSubscription import NoSubscription
from ..SearchArtist import SearchArtist
from ..RelatedArtistSearch import RelatedArtistSearch
from ..C_CreateModel import C_CreateModel
from ..ConnectModel import ConnectModel
from ..CreateWatchlist import CreateWatchlist
from ..Observe import Observe
from ..ModelProfile import ModelProfileTemplate
from ..RampUp import RampUpTemplate
from ..Notifications import Notifications


routing.logger.debug = False


@routing.main_router
class Main_In(Main_InTemplate):
  def __init__(self, **properties):
    #print(f"{datetime.datetime.now()}: Main_In - link_login_click - 1", flush=True)
    
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    
    model_id = load_var("model_id")
    print(f"Main_In model_id: {model_id}")
    print(f"Main_In user_id: {load_var('user_id')}")

    # Any code you write here will run before the form opens.    
    global user
    user = anvil.users.get_user()
    print(f"Main_In user: {user}")
        
    if user is None:
      self.visible = False
        
    else:      
      self.role = 'POST_LOGIN_PAGE'
      self.visible = True
    
      global status
      status = True
      
      #begin = datetime.datetime.now()
      #print(f"{datetime.datetime.now()}: Main_In - link_login_click - 2", flush=True)

      # model_id
      if user["user_id"] is None:
        self.model_id = None
      else:
        if model_id is None:
          self.model_id = save_var("model_id", anvil.server.call('get_model_id',  user["user_id"]))
        else:
          self.model_id = model_id

      # watchlist_id
      watchlist_id = load_var("watchlist_id")
      if watchlist_id is None:
        save_var("watchlist_id", anvil.server.call('get_watchlist_id',  user["user_id"]))
      self.watchlist_id = watchlist_id
      print(f"Main_In watchlist_id: {watchlist_id}")
          
      #print(f"{datetime.datetime.now()}: Main_In - link_login_click - 3", flush=True)  # 20s, 17s - 4s
            
      if self.model_id is None:
        routing.set_url_hash('no_model', load_from_cache=False)
        self.change_nav_visibility(status=True)
        self.SearchBar.visible = False

      else:
        #print(f"{datetime.datetime.now()}: Main_In - link_login_click - 4", flush=True)
        self.update_no_notifications()
      
      #print(f"{datetime.datetime.now()}: Main_In - link_login_click - 5", flush=True)
      #print(f"TotalTime Main_In: {datetime.datetime.now() - begin}", flush=True)
      
      # WATCHLIST & MODEL PROFILES IN NAV
      self.refresh_watchlists_components()
      self.refresh_models_components()


  # WATCHLIST ROUTING
  def refresh_watchlists_components(self):
    self.remove_watchlist_components()
    
    wl_ids = json.loads(anvil.server.call('get_watchlist_ids',  user["user_id"]))
    for i in range(0, len(wl_ids)):
      if wl_ids[i]["is_last_used"] is True:
        wl_link = Link(
          icon='fa:angle-right',
          text=wl_ids[i]["watchlist_name"],
          tag=wl_ids[i]["watchlist_id"],
          role='underline-link'
          )
      else:
        wl_link = Link(
          icon='fa:angle-right',
          text=wl_ids[i]["watchlist_name"],
          tag=wl_ids[i]["watchlist_id"]
          )
      wl_link.set_event_handler('click', self.create_watchlist_click_handler(wl_ids[i]["watchlist_id"], wl_link))
      self.nav_watchlists.add_component(wl_link)
      print('add_component', self.nav_watchlists.get_components())

  def remove_watchlist_components(self):
    for component in self.nav_watchlists.get_components():
      if isinstance(component, Link):
        component.remove_from_parent()
    
  def refresh_watchlists_underline(self):
    for component in self.nav_watchlists.get_components():
      if isinstance(component, Link):
        if int(component.tag) == int(load_var("watchlist_id")):
          component.role = 'underline-link'
        else:
          component.role = ''
  
  def create_watchlist_click_handler(self, watchlist_id, wl_link):
    def handler(**event_args):
      self.watchlists_click(watchlist_id, wl_link, **event_args)
    return handler

  def watchlists_click(self, link_watchlist_id, wl_link, **event_args):
    click_link(wl_link, f'watchlist_details?watchlist_id={link_watchlist_id}&artist_id=None', event_args)
    self.reset_nav_backgrounds()
    wl_link.background = "theme:Accent 3"
  # ------------

  # MODEL ROUTING
  def refresh_models_components(self):
    self.remove_model_components()
    
    model_ids = json.loads(anvil.server.call('get_model_ids',  user["user_id"]))
    for i in range(0, len(model_ids)):
      if model_ids[i]["is_last_used"] is True:
        model_link = Link(
          icon='fa:angle-right',
          text=model_ids[i]["model_name"],
          tag=model_ids[i]["model_id"],
          role='underline-link'
          )
      else:
        model_link = Link(
          icon='fa:angle-right',
          text=model_ids[i]["model_name"],
          tag=model_ids[i]["model_id"]
          )
      model_link.set_event_handler('click', self.create_model_click_handler(model_ids[i]["model_id"], model_link))
      self.nav_models.add_component(model_link)
  
  def remove_model_components(self):
    for component in self.nav_models.get_components():
      if isinstance(component, Link):
        component.remove_from_parent()
    
  def refresh_models_underline(self):
    for component in self.nav_models.get_components():
      if isinstance(component, Link):
        if int(component.tag) == int(load_var("model_id")):
          component.role = 'underline-link'
        else:
          component.role = ''
  
  def create_model_click_handler(self, model_id, model_link):
    def handler(**event_args):
      self.models_click(model_id, model_link, **event_args)
    return handler

  def models_click(self, link_model_id, model_link, **event_args):
    click_link(model_link, f'model_profile?model_id={link_model_id}&section=Main', event_args)
    self.reset_nav_backgrounds()
    model_link.background = "theme:Accent 3"
  # ------------
      
  def logout_click(self, **event_args):
    logout()

  def update_no_notifications(self, **event_args):
    NoNotifications = json.loads(anvil.server.call('get_no_notifications', user["user_id"]))
    self.link_watchlists.text = 'WATCHLISTS (' + str(NoNotifications[0]["cnt"]) + ')'

  def reset_nav_backgrounds(self, **event_args):
    # delete old background
    self.link_home.background = None
    
    self.link_discover.background = None
    self.link_discover_ai.background = None
    self.link_discover_rel.background = None
    
    self.link_observe.background = None

    self.link_watchlists.background = None
    for component in self.nav_watchlists.get_components():
      component.background = None
    
    self.link_monitor_funnel.background = None
    self.link_monitor_dev.background = None
    
    self.link_models.background = None    
    for component in self.nav_models.get_components():
      component.background = None

    # set new bacckground
    if location.hash[:5] == '#home':
      self.link_home.background = "theme:Accent 3"
      
    elif location.hash[:9] == '#artists?':
      self.link_discover_ai.background = "theme:Accent 3"
    elif location.hash[:13] == '#rel_artists?':
      self.link_discover_rel.background = "theme:Accent 3"
      
    if location.hash[:8] == '#observe':
      self.link_observe.background = "theme:Accent 3"
      
    elif location.hash[:17] == '#watchlist_funnel':
      self.link_monitor_funnel.background = "theme:Accent 3"
    elif location.hash[:19] == '#watchlist_overview':
      self.link_monitor_dev.background = "theme:Accent 3"
      
  
  def change_nav_visibility(self, status, **event_args):
    self.link_home.visible = status

    self.linear_panel_discover.visible = status
    self.link_discover.visible = status
    # self.link_discover_ai.visible = status
    # self.link_discover_rel.visible = status

    self.link_observe.visible = status

    self.column_panel_nav_wl.visible = status
        
    self.linear_panel_monitor.visible = status
    # self.link_monitor_funnel.visible = status
    # self.link_monitor_dev.visible = status

    self.column_panel_nav.visible = status
    
    # self.link_models.visible = True
  
  #----------------------------------------------------------------------------------------------
  # HOME
  def link_home_click(self, **event_args):
    click_link(self.link_home, 'home', event_args)
    self.reset_nav_backgrounds()
    self.link_home.background = "theme:Accent 3"
  
  #----------------------------------------------------------------------------------------------  
  # DISCOVER
  def change_discover_visibility(self, **event_args):
    if self.link_discover_ai.visible is False:
      self.link_discover.icon = 'fa:angle-up'
      self.link_discover_ai.visible = True
      self.link_discover_rel.visible = True

    else:
      self.link_discover.icon = 'fa:angle-down'
      self.link_discover_ai.visible = False
      self.link_discover_rel.visible = False

  
  def link_discover_ai_click(self, temp_artist_id=None, **event_args):
    artist_id = anvil.server.call('get_next_artist_id', load_var('model_id'))
    click_link(self.link_discover_ai, f'artists?artist_id={artist_id}', event_args)
    self.reset_nav_backgrounds()
    self.link_discover_ai.background = "theme:Accent 3"

  def link_discover_rel_click(self, **event_args):
    click_link(self.link_discover_rel, 'rel_artists?artist_id=None', event_args)
    self.reset_nav_backgrounds()
    self.link_discover_rel.background = "theme:Accent 3"

  #----------------------------------------------------------------------------------------------
  # HOME
  def link_observe_click(self, **event_args):
    click_link(self.link_observe, 'observe', event_args)
    self.reset_nav_backgrounds()
    self.link_observe.background = "theme:Accent 3"
    
  #----------------------------------------------------------------------------------------------
  # WATCHLISTS
  def change_watchlists_visibility(self, **event_args):
    if self.link_watchlists.icon == 'fa:angle-down':
      self.link_watchlists.icon = 'fa:angle-up'
      for component in self.nav_watchlists.get_components():
        component.visible = False
      self.column_panel_nav_wl.visible = True
    else:
      self.link_watchlists.icon = 'fa:angle-down'
      for component in self.nav_watchlists.get_components():
        component.visible = True

  def create_watchlist_click(self, **event_args):
    click_link(self.create_watchlist, 'create_watchlist', event_args)
    self.reset_nav_backgrounds()
  
  #----------------------------------------------------------------------------------------------
  # MANAGE
  def change_monitor_visibility(self, **event_args):
    if self.link_monitor_funnel.visible is False:
      self.link_monitor.icon = 'fa:angle-up'
      self.link_monitor_funnel.visible = True
      self.link_monitor_dev.visible = True
    else:
      self.link_monitor.icon = 'fa:angle-down'
      self.link_monitor_funnel.visible = False
      self.link_monitor_dev.visible = False
    
  def link_monitor_funnel_click(self, **event_args):
    click_link(self.link_monitor_funnel, 'watchlist_funnel', event_args)
    self.reset_nav_backgrounds()
    self.link_monitor_funnel.background = "theme:Accent 3"

  def link_monitor_dev_click(self, **event_args):
    click_link(self.link_monitor_dev, 'watchlist_overview', event_args)
    self.reset_nav_backgrounds()
    self.link_monitor_dev.background = "theme:Accent 3"

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
    click_link(self.create_model, 'model_setup?model_id=None&section=Basics', event_args)
    self.reset_nav_backgrounds()

  #----------------------------------------------------------------------------------------------
  # SETTINGS
  def link_settings_click(self, **event_args):
    pass

  def SearchBar_pressed_enter(self, **event_args):
    searchdata = json.loads(anvil.server.call('search_artist', user["user_id"], self.SearchBar.text.strip()))
    search_text = self.SearchBar.text
    self.SearchBar.focus()
    if not searchdata:
      alert(title="Artist is not found or missing",
        content="If the artist you are looking for is not found or is missing, please add the Spotify Id in the search bar so that we can add them to our catalogue",
        # large=True,
        buttons=[("OK", "OK")],
        role=["alert-notification","remove-focus"]
      )
      
    else:
      popup_table = alert(
        content=C_SearchPopupTable(self.model_id, search_text),
        large=True,
        buttons=[]
      )

  def shorten_number(self, num):
    thresholds = [
      (1_000_000_000_000, 'T'),  # Trillion
      (1_000_000_000, 'B'),      # Billion
      (1_000_000, 'M'),          # Million
      (1_000, 'K')               # Thousand
    ]
    
    def shorten_single_number(n):
      # Check if n is None or not a number-like object
      if n is None or not (isinstance(n, (int, float)) or (isinstance(n, str) and n.isdigit())):
        return '-'
      n = int(n)
      for threshold, suffix in thresholds:
        if n >= threshold:
          return f'{n / threshold:.1f}{suffix}'
      return f'{n:.0f}'
    
    # If input is a list, process each number
    if isinstance(num, list):
      return [shorten_single_number(n) for n in num]
    # If input is a single number, just process it
    else:
      return shorten_single_number(num)

