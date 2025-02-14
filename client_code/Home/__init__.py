from ._anvil_designer import HomeTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
# from anvil.js.window import location
import json
import datetime

from anvil_extras import routing
from ..nav import click_link, click_button, click_box, logout, login_check, load_var, save_var

from ..C_Short_simple import C_Short_simple
from ..C_Short import C_Short
from ..C_Shorts import C_Shorts


@routing.route('',     title='Login')
@routing.route('home', title='Home')
class Home(HomeTemplate):
  def __init__(self, **properties):
    
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    global user
    user = anvil.users.get_user()
    
    # Any code you write here will run before the form opens.
    if user is None or user == 'None':
      self.visible = False
      
    elif user['expiration_date'] is not None and (datetime.today().date() - user['expiration_date']).days > 0:
      routing.set_url_hash('no_subs', load_from_cache=False)
      get_open_form().SearchBar.visible = False
      
    else:
      model_id = load_var("model_id")
      print(f"Home model_id: {model_id}")
      
      self.model_id=model_id

      # welcome name
      if user["first_name"] is not None:
        self.label_welcome.text = f'Welcome {user["first_name"]}'        
      
      print(f"{datetime.datetime.now()}: Home - __init__ - 1", flush=True)


      # -------------
      # SHORTS      
      # get watchlists
      watchlists = json.loads(anvil.server.call("get_watchlist_ids", user["user_id"]))
      # print(watchlists)
      # active_watchlists = items["watchlist_id"]

      if watchlists is not None and len(watchlists) > 0:
        self.no_watchlists.visible = False
        
        for i in range(0, len(watchlists)):
          # if watchlists[i]["watchlist_id"] in active_watchlists:
          wl_link = Link(
            text=watchlists[i]["watchlist_name"], tag=watchlists[i]["watchlist_id"], role="genre-box"
          )
          # else:
          #   wl_link = Link(
          #     text=watchlists[i]["watchlist_name"],
          #     tag=watchlists[i]["watchlist_id"],
          #     role="genre-box-deselect",
          #   )
    
          # if watchlists[i]["fully_trained"] is False:
          #   wl_link = Link(
          #     text=watchlists[i]["watchlist_name"],
          #     tag=watchlists[i]["watchlist_id"],
          #     role="genre-box-deactive",
          #   )
    
          wl_link.set_event_handler(
            "click", self.create_activate_watchlist_handler(watchlists[i]["watchlist_id"])
          )
          self.flow_panel_watchlists.add_component(wl_link)

      else:
        self.no_watchlists.visible = True
      
      # get data
      self.get_shorts()
      
      print(f"{datetime.datetime.now()}: Home - __init__ - 2", flush=True)
    
      
      data = anvil.server.call('app_home', user["user_id"])
      # # FUNNEL
      # #print(f"{datetime.datetime.now()}: Home - __init__ - 2a", flush=True)    
  
      # if len(data['funnel1']) == 0 and len(data['funnel2']) == 0 and len(data['funnel3']) == 0:
      #   self.xy_panel_funnel.visible = False
      #   self.xy_panel_funnel_empty.visible = True
      # else:
      #   self.repeating_panel_2.items = data['funnel1']  #[item for item in funnel if item['Status'] in ['Action required', 'Requires revision', 'Waiting for decision']] #EVALUATION
      #   #print(f"{datetime.datetime.now()}: Home - __init__ - 2b", flush=True)
      #   self.repeating_panel_3.items = data['funnel2']  #[item for item in funnel if item['Status'] in ['Build connection', 'Awaiting response', 'Exploring opportunities', 'Positive response']] #CONTACTING
      #   #print(f"{datetime.datetime.now()}: Home - __init__ - 2c", flush=True)
      #   self.repeating_panel_4.items = data['funnel3']  #[item for item in funnel if item['Status'] in ['In negotiations', 'Contract in progress']] #NEGOTIATION
      # #print(f"{datetime.datetime.now()}: Home - __init__ - 3", flush=True)
  
      print(f"{datetime.datetime.now()}: Home - __init__ - 3", flush=True)
      
      # STATS
      stats = data['stats']
      for stat in stats:
        if stat['stat'] == 'Success': won_cnt = stat['cnt']
        if stat['stat'] == 'Watchlist': wl_cnt = stat['cnt']
        if stat['stat'] == 'HighRated': hp_cnt = stat['cnt']
        if stat['stat'] == 'RatedTotal': tot_cnt = stat['cnt']
      
      self.label_won_no.text = won_cnt
      self.label_wl_no.text = wl_cnt
      self.label_hp_no.text = hp_cnt
      self.label_tot_no.text = tot_cnt
      
      if won_cnt == 1: self.label_won_txt.text = 'artist\nwon'
      else: self.label_won_txt.text = 'artists\nwon'
      if wl_cnt == 1: self.label_wl_txt.text =  'artist on\nwatchlist'
      else: self.label_wl_txt.text =  'artists on\nwatchlist'
      if hp_cnt == 1: self.label_hp_txt.text =  'high\npotential'
      else: self.label_hp_txt.text =  'high\npotentials'
      if tot_cnt == 1: self.label_tot_txt.text = 'total\nrating'
      else: self.label_tot_txt.text = 'total\nratings'
        
      print(f"{datetime.datetime.now()}: Home - __init__ - 4", flush=True)
  
      # NEWS
      news = data['news']
      if len(news) == 0:
        self.xy_panel_news.visible = False
        self.xy_panel_news_empty.visible = True
      else:
        self.repeating_panel_news.items = news
      print(f"{datetime.datetime.now()}: Home - __init__ - 5", flush=True)
      
    
    
  def link_discover_click(self, **event_args):
    temp_artist_id = anvil.server.call('get_next_artist_id', load_var('model_id'))
    click_link(self.artist_link, f'artists?artist_id={temp_artist_id}', event_args)
    
  def button_discover_click(self, **event_args):
    temp_artist_id = anvil.server.call('get_next_artist_id', load_var('model_id'))
    click_button(f'artists?artist_id={temp_artist_id}', event_args)
    
  def link_funnel_click(self, **event_args):
    click_link(self.link_funnel, 'watchlist_funnel', event_args)

  def get_shorts(self, **event_args):
    # get active watchlist ids
    wl_ids = []
    for component in self.flow_panel_watchlists.get_components():
      if (isinstance(component, Link) and component.role == "genre-box"):  # Only active models
        wl_ids.append(component.tag)
      
    # clean present shorts
    self.flow_panel_shorts.clear()

    # add new shorts
    if wl_ids != []:      
      # get data
      shorts = anvil.server.call('get_shorts', wl_ids, 0, 12)  # user["user_id"]
      
      # present shorts
      if shorts is not None and len(shorts) > 0:
        shorts = json.loads(shorts)

        self.no_shorts = len(shorts)
        for i in range(0, len(shorts)):
          self.flow_panel_shorts.add_component(C_Short_simple(data=shorts[i]))

  def add_shorts(self, **event_args):
    # get active watchlist ids
    wl_ids = []
    for component in self.flow_panel_watchlists.get_components():
      if (isinstance(component, Link) and component.role == "genre-box"):  # Only active models
        wl_ids.append(component.tag)
    
    # add new shorts
    if wl_ids != []:      
      # get data
      shorts = anvil.server.call('get_shorts', wl_ids, self.no_shorts, 9)  # user["user_id"]
      
      # present shorts
      if shorts is not None and len(shorts) > 0:
        shorts = json.loads(shorts)
        
        for i in range(0, len(shorts)):
          self.flow_panel_shorts.add_component(C_Short_simple(data=shorts[i]))
        
        self.no_shorts = self.no_shorts + len(shorts)
        
      else:
        self.reload.visible = False
              
  
  # ------------------
  # WATCHLIST BUTTONS
  def create_activate_watchlist_handler(self, watchlist_id):
    def handler(**event_args):
      self.activate_watchlist(watchlist_id)

    return handler
  
  # change active status of MODEL BUTTONS
  def activate_watchlist(self, watchlist_id):
    for component in self.flow_panel_watchlists.get_components():
      if isinstance(component, Link):
        # change activation
        if int(component.tag) == watchlist_id:
          if component.role == "genre-box":
            component.role = "genre-box-deselect"
          else:
            component.role = "genre-box"

    # Check if any watchlists are selected
    # a) collect selected watchlist IDs
    wl_ids = []
    for component in self.flow_panel_watchlists.get_components():
      if (
        isinstance(component, Link) and component.role == "genre-box"
      ):  # Only active models
        wl_ids.append(component.tag)

    print('wl_ids:', wl_ids)
    self.get_shorts()
