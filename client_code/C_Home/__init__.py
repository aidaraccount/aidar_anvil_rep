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
    if data == '[]':
      self.xy_panel_funnel.visible = False
    else:
      self.repeating_panel_2.items = [item for item in data if item['Status'] in ['Action required', 'Requires revision', 'Waiting for decision']] #EVALUATION
      self.repeating_panel_3.items = [item for item in data if item['Status'] in ['Build connection', 'Awaiting response', 'Exploring opportunities', 'Positive response']] #CONTACTING
      self.repeating_panel_4.items = [item for item in data if item['Status'] in ['In negotiations', 'Contract in progress']] #NEGOTIATION

    # STATS
    stats = json.loads(anvil.server.call('get_stats', cur_model_id))
    self.label_won_no.text = stats[0]['cnt']
    self.label_wl_no.text = stats[1]['cnt']
    self.label_hp_no.text = stats[2]['cnt']
    self.label_tot_no.text = stats[3]['cnt']
    if stats[0]['cnt'] == 1: self.label_won_txt.text = 'artist\nwon'
    else: self.label_won_txt.text = 'artists\nwon'
    if stats[1]['cnt'] == 1: self.label_wl_txt.text =  'artist on\nwatchlist'
    else: self.label_wl_txt.text =  'artists on\nwatchlist'
    if stats[2]['cnt'] == 1: self.label_hp_txt.text =  'high\npotential'
    else: self.label_hp_txt.text =  'high\npotentials'
    if stats[3]['cnt'] == 1: self.label_tot_txt.text = 'total\nrating'
    else: self.label_tot_txt.text = 'total\nratings'

    # NEWS
    self.repeating_panel_news.items = json.loads(anvil.server.call('get_watchlist_notes', cur_model_id, None))
  
    
  def link_discover_click(self, **event_args):
    open_form('Main_In', temp_artist_id = None, target = 'C_Investigate', value=None)

  def link_funnel_click(self, **event_args):
    open_form('Main_In', temp_artist_id = None, target = 'C_Watchlist_Funnel', value=None)

  def text_search_pressed_enter(self, **event_args):
    open_form('Main_In', temp_artist_id = None, target = 'C_SearchArtist', value=self.text_search.text)

    