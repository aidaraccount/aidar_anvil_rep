from ._anvil_designer import C_HomeTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json

class C_Home(C_HomeTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    global cur_model_id
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])

    # FUNNEL DATA
    data = json.loads(anvil.server.call('get_watchlist_selection', cur_model_id))
    if len(data) == 0:
      self.xy_panel_funnel.visible = False
      self.xy_panel_funnel_empty.visible = True
    else:
      self.repeating_panel_2.items = [item for item in data if item['Status'] in ['Action required', 'Requires revision', 'Waiting for decision']] #EVALUATION
      self.repeating_panel_3.items = [item for item in data if item['Status'] in ['Build connection', 'Awaiting response', 'Exploring opportunities', 'Positive response']] #CONTACTING
      self.repeating_panel_4.items = [item for item in data if item['Status'] in ['In negotiations', 'Contract in progress']] #NEGOTIATION

    # STATS
    stats = json.loads(anvil.server.call('get_stats', cur_model_id))
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

    # NEWS
    news = json.loads(anvil.server.call('get_watchlist_notes', cur_model_id, None))
    if len(news) == 0:
      self.xy_panel_news.visible = False
      self.xy_panel_news_empty.visible = True
    else:
      self.repeating_panel_news.items = news
    
  def link_discover_click(self, **event_args):
    open_form('Main_In', temp_artist_id = None, target = 'C_Discover', value=None)

  def link_funnel_click(self, **event_args):
    open_form('Main_In', temp_artist_id = None, target = 'C_Watchlist_Funnel', value=None)

  def text_search_pressed_enter(self, **event_args):
    open_form('Main_In', temp_artist_id = None, target = 'C_SearchArtist', value=self.text_search.text)

    