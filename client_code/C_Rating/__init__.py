from ._anvil_designer import C_RatingTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json
import datetime


class C_Rating(C_RatingTemplate):
  def __init__(self, model_id, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    print(f"{datetime.datetime.now()}: C_Rating - __init__ - 1", flush=True)
    
    global user
    user = anvil.users.get_user()    
    self.model_id=model_id
    print(f"{datetime.datetime.now()}: C_Rating - __init__ - 2", flush=True)

    data = self.get_data()
    print(f"{datetime.datetime.now()}: C_Rating - __init__ - 3", flush=True)

    # standard sorting
    self.data_ratings_data.items = sorted(data, key=lambda x: x.get('DateOfRecommendation', float('inf')), reverse=True)
    self.link_date.icon = 'fa:angle-down'
    
    print(f"{datetime.datetime.now()}: C_Rating - __init__ - 4", flush=True)
    
  
  def get_data(self, **event_args):
    data = json.loads(anvil.server.call('get_ratings', self.model_id))    
    return data

  # RESET ICONS
  def reset_icons (self, **event_args):
    self.link_date.icon = ''
    self.link_artist.icon = ''
    self.link_interest.icon = ''
    
  # SORT BUTTONS
  def link_date_click(self, **event_args):
    if self.link_date.icon == '' or self.link_date.icon == 'fa:angle-up':
      self.reset_icons()
      self.link_date.icon = 'fa:angle-down'
      self.data_ratings_data.items = sorted(self.data_ratings_data.items, key=lambda x: x.get('DateOfRecommendation', float('inf')), reverse=True)
    elif self.link_date.icon == 'fa:angle-down':
      self.reset_icons()
      self.link_date.icon = 'fa:angle-up'
      self.data_ratings_data.items = sorted(self.data_ratings_data.items, key=lambda x: x.get('DateOfRecommendation', float('inf')), reverse=False)

  def link_artist_click(self, **event_args):
    if self.link_artist.icon == '' or self.link_artist.icon == 'fa:angle-up':
      self.reset_icons()
      self.link_artist.icon = 'fa:angle-down'
      self.data_ratings_data.items = sorted(self.data_ratings_data.items, key=lambda x: x.get('Name', float('inf')), reverse=True)
    elif self.link_artist.icon == 'fa:angle-down':
      self.reset_icons()
      self.link_artist.icon = 'fa:angle-up'
      self.data_ratings_data.items = sorted(self.data_ratings_data.items, key=lambda x: x.get('Name', float('inf')), reverse=False)

  def link_interest_click(self, **event_args):
    if self.link_interest.icon == '' or self.link_interest.icon == 'fa:angle-up':
      self.reset_icons()
      self.link_interest.icon = 'fa:angle-down'
      self.data_ratings_data.items = sorted(self.data_ratings_data.items, key=lambda x: x.get('Interest', float('inf')), reverse=True)
    elif self.link_interest.icon == 'fa:angle-down':
      self.reset_icons()
      self.link_interest.icon = 'fa:angle-up'
      self.data_ratings_data.items = sorted(self.data_ratings_data.items, key=lambda x: x.get('Interest', float('inf')), reverse=False)

  
  # SEARCH
  def button_search_click(self, **event_args):
    # get data
    data = [entry for entry in self.get_data() if str(entry["Name"]).lower().find(str(self.text_box_search.text).lower()) != -1]

    # sort as defined before
    if self.link_date.icon == 'fa:angle-down':
      self.data_ratings_data.items = sorted(data, key=lambda x: x.get('DateOfRecommendation', float('inf')), reverse=True)
    elif self.link_date.icon == 'fa:angle-up':
      self.data_ratings_data.items = sorted(data, key=lambda x: x.get('DateOfRecommendation', float('inf')), reverse=False)
      
    elif self.link_artist.icon == 'fa:angle-down':
      self.data_ratings_data.items = sorted(data, key=lambda x: x.get('Name', float('inf')), reverse=True)
    elif self.link_artist.icon == 'fa:angle-up':
      self.data_ratings_data.items = sorted(data, key=lambda x: x.get('Name', float('inf')), reverse=False)
      
    elif self.link_interest.icon == 'fa:angle-down':
      self.data_ratings_data.items = sorted(data, key=lambda x: x.get('Interest', float('inf')), reverse=True)
    elif self.link_interest.icon == 'fa:angle-up':
      self.data_ratings_data.items = sorted(data, key=lambda x: x.get('Interest', float('inf')), reverse=False)
      
