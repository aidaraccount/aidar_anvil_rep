from ._anvil_designer import C_HomeTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json
import datetime

class C_Home(C_HomeTemplate):
  def __init__(self, model_id, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    begin = datetime.datetime.now()
    
    global user
    user = anvil.users.get_user()
    self.model_id=model_id
    
    print(f"{datetime.datetime.now()}: C_Home - __init__ - 2", flush=True)
    # FUNNEL DATA
    # data = json.loads(anvil.server.call('get_watchlist_selection', model_id))
    print(f"{datetime.datetime.now()}: C_Home - __init__ - 2a", flush=True)
    
    data = anvil.server.call('app_home', model_id)
    print(f"{datetime.datetime.now()}: C_Home - __init__ - 2aa", flush=True)
    
    if len(data) == 0:
      self.xy_panel_funnel.visible = False
      self.xy_panel_funnel_empty.visible = True
    else:
      self.repeating_panel_2.items = data['funnel1']  #[item for item in data if item['Status'] in ['Action required', 'Requires revision', 'Waiting for decision']] #EVALUATION
      print(f"{datetime.datetime.now()}: C_Home - __init__ - 2b", flush=True)
      self.repeating_panel_3.items = data['funnel2']  #[item for item in data if item['Status'] in ['Build connection', 'Awaiting response', 'Exploring opportunities', 'Positive response']] #CONTACTING
      print(f"{datetime.datetime.now()}: C_Home - __init__ - 2c", flush=True)
      self.repeating_panel_4.items = data['funnel3']  #[item for item in data if item['Status'] in ['In negotiations', 'Contract in progress']] #NEGOTIATION
    print(f"{datetime.datetime.now()}: C_Home - __init__ - 3", flush=True)

    # STATS
    stats = data['stats']  #json.loads(anvil.server.call('get_stats', model_id))
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
    print(f"{datetime.datetime.now()}: C_Home - __init__ - 4", flush=True)

    # NEWS
    news = data['news']  #json.loads(anvil.server.call('get_watchlist_notes', model_id, None))
    if len(news) == 0:
      self.xy_panel_news.visible = False
      self.xy_panel_news_empty.visible = True
    else:
      self.repeating_panel_news.items = news
    print(f"{datetime.datetime.now()}: C_Home - __init__ - 5", flush=True)
    
    print(f"TotalTime C_Home: {datetime.datetime.now() - begin}", flush=True)
    
    
  def link_discover_click(self, **event_args):
    open_form('Main_In', self.model_id, temp_artist_id = None, target = 'C_Discover', value=None)

  def link_funnel_click(self, **event_args):
    open_form('Main_In', self.model_id, temp_artist_id = None, target = 'C_Watchlist_Funnel', value=None)

  def text_search_pressed_enter(self, **event_args):
    open_form('Main_In', self.model_id, temp_artist_id = None, target = 'C_SearchArtist', value=self.text_search.text)
