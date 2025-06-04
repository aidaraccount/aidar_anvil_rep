from ._anvil_designer import MainInTemplate
from ..C_FeedbackForm import C_FeedbackForm

from anvil import *
import stripe.checkout
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
import json
import time
from datetime import datetime
from anvil.js.window import location, updateLoadingSpinnerMargin
from ..C_SearchPopupTable import C_SearchPopupTable

from anvil_extras import routing
from ..nav import click_link, click_button, logout, login_check, save_var, load_var

from ..MainOut import MainOut
from ..Home import Home
from ..Discover import Discover
from ..DiscoverAgent import DiscoverAgent
from ..WatchlistDetails import WatchlistDetails
from ..Monitor_Funnel import Monitor_Funnel
from ..Monitor_TalentDev import Monitor_TalentDev
from ..NoModel import NoModel
from ..NoSubscription import NoSubscription
from ..SearchArtist import SearchArtist
from ..RelatedArtistSearch import RelatedArtistSearch
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
      
      # 1. Helper function to safely call JavaScript
      def ensure_js_function_available(function_name):
        """Ensures JavaScript function is available before calling it"""
        try:
          # First check if the function is already defined
          is_defined = anvil.js.call_js('eval', f'typeof {function_name} === "function"')
          if not is_defined:
            # Try to load the script
            anvil.js.call_js('eval', 
                           '''
                           var script = document.createElement("script");
                           script.src = "assets/hideNavBar.js";
                           script.onload = function() { 
                             console.log("[NAVBAR_DEBUG] hideNavBar.js loaded dynamically"); 
                           };
                           document.head.appendChild(script);
                           ''')
            # Give it a moment to load
            time.sleep(0.1)
          return True
        except Exception as e:
          print(f"[NAVBAR_DEBUG] Error ensuring JavaScript function: {str(e)}")
          return False

      if user is None:
        pass
      elif user['expiration_date'] is not None and (datetime.today().date() - user['expiration_date']).days > 0:
        routing.set_url_hash('settings?section=Subscription', load_from_cache=False)
        self.SearchBar.visible = False

        # 2. Hide navigation sidebar with JavaScript safety check
        try:
          # Ensure the function is available
          if ensure_js_function_available('navbar_noModel_noSubs'):
            anvil.js.call_js("navbar_noModel_noSubs", False)
        except Exception as e:
          print(f"[NAVBAR_DEBUG] Error calling navbar_noModel_noSubs: {str(e)}")
          
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
        self.SearchBar.visible = True
        
        # 3. Hide navigation sidebar with JavaScript safety check
        try:
          # Ensure the function is available
          if ensure_js_function_available('navbar_noModel_noSubs'):
            anvil.js.call_js("navbar_noModel_noSubs", False)
        except Exception as e:
          # Try to ensure the script is loaded first
          anvil.js.call_js("console.log", "[NAVBAR_DEBUG] Fallback: checking if hideNavBar.js is loaded")

      #print(f"{datetime.datetime.now()}: MainIn - link_login_click - 4", flush=True)
      self.update_no_notifications()
      
      #print(f"{datetime.datetime.now()}: MainIn - link_login_click - 5", flush=True)
      #print(f"TotalTime MainIn: {datetime.datetime.now() - begin}", flush=True)
      
      # NAVIGATION
      self.refresh_watchlists_components()
      self.refresh_models_components()
      # self.refresh_agents_components()
      
      # For Anvil Extras routing, we need to set the hash as is
      # Empty hash will automatically route to the '' route (Home)
      routing.set_url_hash(location.hash, load_from_cache=False)
      
      self.reset_nav_backgrounds()
      self.call_js('updateLoadingSpinnerMargin', '125px')

      save_var('initial_login', True)
      

  # WATCHLIST ROUTING
  def refresh_watchlists_components(self):
    # self.remove_watchlist_components()
    # wl_ids = json.loads(anvil.server.call('get_watchlist_ids',  user["user_id"]))
    
    # if len(wl_ids) > 0:
    #   for i in range(0, len(wl_ids)):
    #     if wl_ids[i]["is_last_used"] is True:
    #       wl_link = Link(
    #         icon='fa:angle-right',
    #         text=wl_ids[i]["watchlist_name"],
    #         tag=wl_ids[i]["watchlist_id"],
    #         role='underline-link'
    #         )
    #     else:
    #       wl_link = Link(
    #         icon='fa:angle-right',
    #         text=wl_ids[i]["watchlist_name"],
    #         tag=wl_ids[i]["watchlist_id"]
    #         )
    #     wl_link.set_event_handler('click', self.create_watchlist_click_handler(wl_ids[i]["watchlist_id"], wl_link))
    #     self.nav_watchlists.add_component(wl_link)

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
    # 1. Remove existing model components
    self.remove_model_components()    
    model_ids = json.loads(anvil.server.call('get_model_ids',  user["user_id"]))
    
    if len(model_ids) > 0:
      for i in range(0, len(model_ids)):
        # 2. Create a container for each model entry
        model_container = anvil.FlowPanel(
          tag=model_ids[i]["model_id"],
          role='nav_flow_panel'
        )
        
        # 3. Create the model link with navigation functionality
        if model_ids[i]["is_last_used"] is True:
          model_link = Link(
            icon='fa:angle-right',
            text=model_ids[i]["model_name"],
            tag=model_ids[i]["model_id"],
            role=['model-nav-link', 'underline-link']
          )
          save_var("model_id", model_ids[i]["model_id"])
        else:
          model_link = Link(
            icon='fa:angle-right',
            text=model_ids[i]["model_name"],
            tag=model_ids[i]["model_id"],
            role=['model-nav-link']
          )
        model_link.set_event_handler('click', self.create_model_click_handler(model_ids[i]["model_id"], model_link, model_container))
        
        # 4. Create settings icon link
        settings_link = Link(
          icon='fa:sliders',
          text="",  # Empty text for icon-only link
          tag=model_ids[i]["model_id"],
          role='icon-link-discreet'
        )
        settings_link.set_event_handler('click', self.create_settings_click_handler(model_ids[i]["model_id"]))
        
        # 5. Add both links to the container
        model_container.add_component(model_link, expand=True)  # Expand to fill available space
        model_container.add_component(settings_link)
        
        # 6. Add the container to nav_models
        self.nav_models.add_component(model_container)

    self.reset_nav_backgrounds()
  
  def remove_model_components(self):
    # Remove all components (now Flow containers) from nav_models
    for component in self.nav_models.get_components():
      if isinstance(component, anvil.FlowPanel):
        component.remove_from_parent()
    
  def refresh_models_underline(self):
    # Find all model links inside Flow containers and update their roles
    for container in self.nav_models.get_components():
      if isinstance(container, anvil.FlowPanel):
        for component in container.get_components():
          # Only apply underlines to the model links (not settings icons)
          if isinstance(component, Link) and component.icon == 'fa:angle-right':
            if int(component.tag) == int(load_var("model_id")):
              component.role = ['model-nav-link', 'underline-link']
            else:
              component.role = ['model-nav-link']
  
  def create_model_click_handler(self, model_id, model_link, model_container):
    def handler(**event_args):
      self.models_click(model_id, model_link, model_container, **event_args)
    return handler

  def models_click(self, link_model_id, model_link, model_container, **event_args):
    # activate model and navigate to discover
    anvil.server.call('update_model_usage', user["user_id"], link_model_id)
    save_var('model_id', link_model_id)
    self.refresh_models_underline()
    temp_artist_id = anvil.server.call('get_next_artist_id', link_model_id)
    # click_link(model_link, f'artists?artist_id={temp_artist_id}', event_args)
    click_link(model_link, f'agent_artists?artist_id={temp_artist_id}', event_args)
    
    self.reset_nav_backgrounds()
    model_container.background = "theme:Brown"

  # # ------------
  # # AGENT ROUTING
  # def refresh_agents_components(self):
  #   # 1. Remove existing agent components
  #   self.remove_agent_components()    
  #   agent_ids = json.loads(anvil.server.call('get_model_ids',  user["user_id"]))

  #   if len(agent_ids) > 0:
  #     for i in range(0, len(agent_ids)):
  #       # 2. Create a container for each agent entry
  #       agent_container = anvil.FlowPanel(
  #         tag=agent_ids[i]["model_id"],
  #         role='nav_flow_panel'
  #       )

  #       # 3. Create the agent link with navigation functionality
  #       if agent_ids[i]["is_last_used"] is True:
  #         agent_link = Link(
  #           icon='fa:angle-right',
  #           text=agent_ids[i]["model_name"],
  #           tag=agent_ids[i]["model_id"],
  #           role='underline-link'
  #         )
  #         save_var("model_id", agent_ids[i]["model_id"])
  #       else:
  #         agent_link = Link(
  #           icon='fa:angle-right',
  #           text=agent_ids[i]["model_name"],
  #           tag=agent_ids[i]["model_id"]
  #         )
  #       agent_link.set_event_handler('click', self.create_agent_click_handler(agent_ids[i]["model_id"], agent_link, agent_container))

  #       # 4. Create settings icon link
  #       settings_link = Link(
  #         icon='fa:sliders',
  #         text="",  # Empty text for icon-only link
  #         tag=agent_ids[i]["model_id"],
  #         role='icon-link-discreet'
  #       )
  #       settings_link.set_event_handler('click', self.create_settings_click_handler(agent_ids[i]["model_id"]))

  #       # 5. Add both links to the container
  #       agent_container.add_component(agent_link, expand=True)  # Expand to fill available space
  #       agent_container.add_component(settings_link)

  #       # 6. Add the container to nav_agents
  #       self.nav_agents.add_component(agent_container)

  #   self.reset_nav_backgrounds()

  # def remove_agent_components(self):
  #   # Remove all components (now Flow containers) from nav_agents
  #   for component in self.nav_agents.get_components():
  #     if isinstance(component, anvil.FlowPanel):
  #       component.remove_from_parent()

  # def refresh_agents_underline(self):
  #   # Find all agent links inside Flow containers and update their roles
  #   for container in self.nav_agents.get_components():
  #     if isinstance(container, anvil.FlowPanel):
  #       for component in container.get_components():
  #         # Only apply underlines to the agent links (not settings icons)
  #         if isinstance(component, Link) and component.icon == 'fa:angle-right':
  #           if int(component.tag) == int(load_var("model_id")):
  #             component.role = 'underline-link'
  #           else:
  #             component.role = ''

  # def create_agent_click_handler(self, model_id, agent_link, agent_container):
  #   def handler(**event_args):
  #     self.agents_click(model_id, agent_link, agent_container, **event_args)
  #   return handler

  # def agents_click(self, link_model_id, agent_link, agent_container, **event_args):
  #   # activate model and navigate to discover
  #   anvil.server.call('update_model_usage', user["user_id"], link_model_id)
  #   save_var('model_id', link_model_id)
  #   self.refresh_agents_underline()
  #   temp_artist_id = anvil.server.call('get_next_artist_id', link_model_id)
  #   click_link(agent_link, f'agent_artists?artist_id={temp_artist_id}', event_args)

  #   self.reset_nav_backgrounds()
  #   agent_container.background = "theme:Brown"

  # ------------
  # SETTINGS ROUTING
  def create_settings_click_handler(self, model_id):
    def settings_click_handler(**event_args):
      # Save the current model ID for reference
      save_var("model_id", model_id)
      # Navigate to model settings page
      routing.set_url_hash(f'model_profile?model_id={model_id}&section=Main', load_from_cache=False)
      self.reset_nav_backgrounds()
      
      # Find the container with this model_id and highlight it
      for container in self.nav_models.get_components():
        if isinstance(container, anvil.FlowPanel):
          for component in container.get_components():
            if isinstance(component, Link) and component.tag == model_id:
              container.background = "theme:Brown"
              break
      
    return settings_click_handler
    
  # ------------
  # NO NOTIFICCATIONS
  def update_no_notifications(self, **event_args):
    NoNotifications = json.loads(anvil.server.call('get_no_notifications', user["user_id"]))
    self.link_watchlists.text = 'WATCHLISTS (' + str(NoNotifications[0]["cnt"]) + ')'

  # ------------
  # NAV BACKGROUND
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

    # self.link_agents.background = None    
    # for component in self.nav_agents.get_components():
    #   component.background = None
      
    # set new background    
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
    
    elif location.hash[:7] == '#funnel':
      self.link_monitor_funnel.background = "theme:Brown"
    elif location.hash[:11] == '#talent_dev':
      self.link_monitor_dev.background = "theme:Brown"
    
    elif location.hash[:15] == '#model_profile?' or location.hash[:13] == '#model_setup?':
      query_string = location.hash.split("?")[1]
      params = dict(pair.split("=") for pair in query_string.split("&"))
      model_id = params.get("model_id")
      if model_id != 'None':            
        # Find the container with this model_id and highlight it
        for container in self.nav_models.get_components():
          if isinstance(container, anvil.FlowPanel) and container.tag == int(model_id):
            container.background = "theme:Brown"
            break
  
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
        component.visible = True
    else:
      self.link_watchlists.icon = 'fa:angle-down'
      for component in self.nav_watchlists.get_components():
        component.visible = False
      self.column_panel_nav_wl.visible = True

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
    click_link(self.link_monitor_funnel, 'funnel', event_args)
    self.reset_nav_backgrounds()
    self.link_monitor_funnel.background = "theme:Brown"

  def link_monitor_dev_click(self, **event_args):
    click_link(self.link_monitor_dev, 'talent_dev', event_args)
    self.reset_nav_backgrounds()
    self.link_monitor_dev.background = "theme:Brown"

  #----------------------------------------------------------------------------------------------
  # MODELS
  def change_models_visibility(self, **event_args):
    if self.link_models.icon == 'fa:angle-down':
      self.link_models.icon = 'fa:angle-up'
      for component in self.nav_models.get_components():
        component.visible = True
    else:
      self.link_models.icon = 'fa:angle-down'
      for component in self.nav_models.get_components():
        component.visible = False
      self.column_panel_nav.visible = True

  def create_model_click(self, **event_args):
    # click_link(self.create_model, 'model_setup?model_id=None&section=Basics', event_args)
    save_var("model_id", None)
    click_link(self.create_model, 'agent_artists?artist_id=create_agent', event_args)
    self.reset_nav_backgrounds()

  # #----------------------------------------------------------------------------------------------
  # # AGENTS
  # def change_agents_visibility(self, **event_args):
  #   if self.link_agents.icon == 'fa:angle-down':
  #     self.link_agents.icon = 'fa:angle-up'
  #     for component in self.nav_agents.get_components():
  #       component.visible = True
  #   else:
  #     self.link_agents.icon = 'fa:angle-down'
  #     for component in self.nav_agents.get_components():
  #       component.visible = False
  #     self.column_panel_agent.visible = True

  # def create_agent_click(self, **event_args):
  #   save_var("model_id", None)
  #   click_link(self.create_model, 'agent_artists?artist_id=create_agent', event_args)
  #   self.reset_nav_backgrounds()

  #----------------------------------------------------------------------------------------------
  # OTHER
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
    anvil.server.call('sent_push_over',  'SearchBar', f'User {user["user_id"]}: using SearchBar')

  def SearchBar_focus(self, **event_args):
    anvil.server.call('pre_warm', 'general.artists_names_norm')
    anvil.server.call('pre_warm', 'general.artists_names_norm_name_norm_trgm_idx')

  
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
    self.call_js('updateLoadingSpinnerMargin', '0px')
    
  def feedback_click(self, **event_args):
    alert(
      content=C_FeedbackForm(),
      large=True,
      buttons=[]
    )

  def settings_click(self, **event_args):
    click_link(self.settings, 'settings?section=Account', event_args)
    self.reset_nav_backgrounds()
