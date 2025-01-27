from ._anvil_designer import MainInTemplate
from ..C_FeedbackForm import C_FeedbackForm

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

from ..MainOut import MainOut
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
from ..CreateWatchlist import CreateWatchlist
from ..Observe_Radar import Observe_Radar
from ..Observe_Listen import Observe_Listen
from ..ModelProfile import ModelProfileTemplate
from ..RampUp import RampUpTemplate
from ..Settings import Settings

routing.logger.debug = False


@routing.main_router
class MainIn(MainInTemplate):
  def __init__(self, **properties):
    #print(f"{datetime.datetime.now()}: MainIn - link_login_click - 1", flush=True)
    
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    
    # Any code you write here will run before the form opens.    
    global user
    user = anvil.users.get_user()
    
    if user is None:
      self.visible = False
      print("MainIn user_id: None")
    
    else:
      print(f"MainIn user_id: {user['user_id']}")
    
      self.role = 'POST_LOGIN_PAGE'
      self.visible = True
    
      global status
      status = True
      
      if user['expiration_date'] is not None and (datetime.today().date() - user['expiration_date']).days > 0:
        routing.set_url_hash('no_subs', load_from_cache=False)
        self.SearchBar.visible = False
      
      #begin = datetime.datetime.now()
      #print(f"{datetime.datetime.now()}: MainIn - link_login_click - 2", flush=True)

      # model_id & watchlist_id
      if user["user_id"] is None:
        self.model_id = None
        self.watchlist_id = None
        
      else:
        # model_id
        self.model_id = save_var("model_id", anvil.server.call('get_model_id',  user["user_id"]))
        print(f"MainIn model_id: {self.model_id}")

        # watchlist_id
        self.watchlist_id = save_var("watchlist_id", anvil.server.call('get_watchlist_id',  user["user_id"]))
        print(f"MainIn watchlist_id: {self.watchlist_id}")
                
      #print(f"{datetime.datetime.now()}: MainIn - link_login_click - 3", flush=True)  # 20s, 17s - 4s
            
      if self.model_id is None:
        routing.set_url_hash('no_model', load_from_cache=False)
        self.change_nav_visibility(status=True)
        self.SearchBar.visible = True

      #print(f"{datetime.datetime.now()}: MainIn - link_login_click - 4", flush=True)
      self.update_no_notifications()
      
      #print(f"{datetime.datetime.now()}: MainIn - link_login_click - 5", flush=True)
      #print(f"TotalTime MainIn: {datetime.datetime.now() - begin}", flush=True)
      
      # NAVIGATION
      self.refresh_watchlists_components()
      self.refresh_models_components()
      self.reset_nav_backgrounds()


  # WATCHLIST ROUTING
  def refresh_watchlists_components(self):
    self.remove_watchlist_components()
    wl_ids = json.loads(anvil.server.call('get_watchlist_ids',  user["user_id"]))
    
    if len(wl_ids) > 0:
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

    self.reset_nav_backgrounds()
    
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
    wl_link.background = "theme:Brown"
  # ------------

  # MODEL ROUTING
  def refresh_models_components(self):
    self.remove_model_components()    
    model_ids = json.loads(anvil.server.call('get_model_ids',  user["user_id"]))

    if len(model_ids) > 0:
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

    self.reset_nav_backgrounds()
  
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
    model_link.background = "theme:Brown"
  # ------------
  
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
    self.link_radar.background = None
    self.link_listen.background = None

    self.link_watchlists.background = None
    for component in self.nav_watchlists.get_components():
      component.background = None
    
    self.link_monitor_funnel.background = None
    self.link_monitor_dev.background = None
    
    self.link_models.background = None    
    for component in self.nav_models.get_components():
      component.background = None

    # set new bacckground    
    if location.hash[:5] == '#home' or location.hash == '':
      self.link_home.background = "theme:Brown"
      
    elif location.hash[:9] == '#artists?':
      self.link_discover_ai.background = "theme:Brown"
    elif location.hash[:13] == '#rel_artists?':
      self.link_discover_rel.background = "theme:Brown"
      
    elif location.hash[:6] == '#radar':
      self.link_radar.background = "theme:Brown"
    elif location.hash[:7] == '#listen':
      self.link_listen.background = "theme:Brown"

    elif location.hash[:19] == '#watchlist_details?':
      for component in self.nav_watchlists.get_components():
        query_string = location.hash.split("?")[1]
        params = dict(pair.split("=") for pair in query_string.split("&"))
        watchlist_id = params.get("watchlist_id")
        if watchlist_id != 'None':
          if isinstance(component, anvil.Link):
            if int(component.tag) == int(watchlist_id):
              component.background = "theme:Brown"          
    
    elif location.hash[:17] == '#watchlist_funnel':
      self.link_monitor_funnel.background = "theme:Brown"
    elif location.hash[:19] == '#watchlist_overview':
      self.link_monitor_dev.background = "theme:Brown"
      
    elif location.hash[:15] == '#model_profile?' or location.hash[:13] == '#model_setup?':
      for component in self.nav_models.get_components():
        query_string = location.hash.split("?")[1]
        params = dict(pair.split("=") for pair in query_string.split("&"))
        model_id = params.get("model_id")
        if model_id != 'None':
          if isinstance(component, anvil.Link):
            if int(component.tag) == int(model_id):
              component.background = "theme:Brown"
  
  def change_nav_visibility(self, status, **event_args):
    self.image_1.visible = status
    self.link_home.visible = status
    self.linear_panel_discover.visible = status
    self.link_discover.visible = status
    # self.link_discover_ai.visible = status
    # self.link_discover_rel.visible = status
    self.link_observe.visible = status
    self.nav_watchlists.visible = status
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
    self.link_home.background = "theme:Brown"
  
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
    self.link_discover_ai.background = "theme:Brown"

  def link_discover_rel_click(self, **event_args):
    click_link(self.link_discover_rel, 'rel_artists?artist_id=None', event_args)
    self.reset_nav_backgrounds()
    self.link_discover_rel.background = "theme:Brown"

  #----------------------------------------------------------------------------------------------
  # OBSERVE
  def change_observe_visibility(self, **event_args):
    if self.link_radar.visible is False:
      self.link_observe.icon = 'fa:angle-up'
      self.link_radar.visible = True
      self.link_listen.visible = True

    else:
      self.link_observe.icon = 'fa:angle-down'
      self.link_radar.visible = False
      self.link_listen.visible = False

  def link_observe_click(self, **event_args):
    click_link(self.link_radar, 'radar?notification_id=None', event_args)
    self.reset_nav_backgrounds()
    self.link_radar.background = "theme:Brown"

  def link_listen_click(self, **event_args):
    click_link(self.link_listen, 'listen?notification_id=None', event_args)
    self.reset_nav_backgrounds()
    self.link_listen.background = "theme:Brown"
  
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
    self.link_monitor_funnel.background = "theme:Brown"

  def link_monitor_dev_click(self, **event_args):
    click_link(self.link_monitor_dev, 'watchlist_overview', event_args)
    self.reset_nav_backgrounds()
    self.link_monitor_dev.background = "theme:Brown"

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
    search_data = json.loads(anvil.server.call('search_artist', user["user_id"], self.SearchBar.text.strip()))
    self.SearchBar.focus()
    
    if not search_data:
      alert(title="Artist is not found or missing",
        content="If you can't find the artist you're looking for, just enter their Spotify ID in the search bar, and we'll add them to our catalog.",
        buttons=[("OK", "OK")],
        role=["alert-notification","remove-focus"]
      )
            
    else:
      alert(
        content=C_SearchPopupTable(self.model_id, self.SearchBar.text),
        large=True,
        buttons=[]
      )

    self.SearchBar.text = ''
    
    # pushover
    anvil.server.call('sent_push_over',  'SearchBar', f'User {user["user_id"]}: using SearchBar')

    
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

  #----------------------------------------------------------------------------------------------
  # Top Right Buttons
  def logout_click(self, **event_args):
    logout()
    
  def feedback_click(self, **event_args):
    popup_table = alert(
      content=C_FeedbackForm(),
      large=True,
      buttons=[]
    )

  def settings_click(self, **event_args):
    click_link(self.settings, 'settings', event_args)
    self.reset_nav_backgrounds()
    