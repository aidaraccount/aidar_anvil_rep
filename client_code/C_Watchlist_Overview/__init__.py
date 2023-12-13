from ._anvil_designer import C_Watchlist_OverviewTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json


class C_Watchlist_Overview(C_Watchlist_OverviewTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    global user
    user = anvil.users.get_user()
    global cur_model_id
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])
    
    # Any code you write here will run before the form opens.
    data = self.get_data()

    # standard sorting
    self.repeating_panel_data.items = sorted(data, key=lambda x: x.get('ArtistID', float('inf')), reverse=True)
    self.link_artistid.icon = 'fa:angle-down'  
    
  
  def get_data(self, **event_args):
    # get raw data
    data = json.loads(anvil.server.call('get_watchlist_overview', cur_model_id))

    # fill Nones
    for item in data:
        for key, value in item.items():
            if value is None:
                if key == "Status": item[key] = 'Action required'
                if key == "Priority": item[key] = 'mid'

    return data      
  
  def link_artistid_click(self, **event_args):
    self.link_status.icon = ''
    self.link_priority.icon = ''
    if self.link_artistid.icon == '' or self.link_artistid.icon == 'fa:angle-up':
      self.link_artistid.icon = 'fa:angle-down'
      self.repeating_panel_data.items = sorted(self.repeating_panel_data.items, key=lambda x: x.get('ArtistID', float('inf')), reverse=True)
    elif self.link_artistid.icon == 'fa:angle-down':
      self.link_artistid.icon = 'fa:angle-up'
      self.repeating_panel_data.items = sorted(self.repeating_panel_data.items, key=lambda x: x.get('ArtistID', float('inf')), reverse=False)

  def link_status_click(self, **event_args):
    self.link_artistid.icon = ''
    self.link_priority.icon = ''
    if self.link_status.icon == '' or self.link_status.icon == 'fa:angle-up':
      self.link_status.icon = 'fa:angle-down'
      self.repeating_panel_data.items = sorted(self.repeating_panel_data.items, key=lambda x: x.get('Status', float('inf')), reverse=True)
    elif self.link_status.icon == 'fa:angle-down':
      self.link_status.icon = 'fa:angle-up'
      self.repeating_panel_data.items = sorted(self.repeating_panel_data.items, key=lambda x: x.get('Status', float('inf')), reverse=False)

  def link_priority_click(self, **event_args):
    self.link_artistid.icon = ''
    self.link_status.icon = ''
    if self.link_priority.icon == '' or self.link_priority.icon == 'fa:angle-up':
      self.link_priority.icon = 'fa:angle-down'
      self.repeating_panel_data.items = sorted(self.repeating_panel_data.items, key=lambda x: x.get('Priority', float('inf')), reverse=True)
    elif self.link_priority.icon == 'fa:angle-down':
      self.link_priority.icon = 'fa:angle-up'
      self.repeating_panel_data.items = sorted(self.repeating_panel_data.items, key=lambda x: x.get('Priority', float('inf')), reverse=False)

  def button_search_click(self, **event_args):
    # get data
    data = [entry for entry in self.get_data() if str(entry["ArtistID"]).find(str(self.text_box_search.text)) != -1]

    # sort as defined before
    if self.link_artistid.icon == 'fa:angle-down':
      self.repeating_panel_data.items = sorted(data, key=lambda x: x.get('ArtistID', float('inf')), reverse=True)
    elif self.link_artistid.icon == 'fa:angle-up':
      self.repeating_panel_data.items = sorted(data, key=lambda x: x.get('ArtistID', float('inf')), reverse=False)
    elif self.link_status.icon == 'fa:angle-down':
      self.repeating_panel_data.items = sorted(data, key=lambda x: x.get('Status', float('inf')), reverse=True)
    elif self.link_status.icon == 'fa:angle-up':
      self.repeating_panel_data.items = sorted(data, key=lambda x: x.get('Status', float('inf')), reverse=False)
    elif self.link_priority.icon == 'fa:angle-down':
      self.repeating_panel_data.items = sorted(data, key=lambda x: x.get('Priority', float('inf')), reverse=True)
    elif self.link_priority.icon == 'fa:angle-up':
      self.repeating_panel_data.items = sorted(data, key=lambda x: x.get('Priority', float('inf')), reverse=False)
    
    
