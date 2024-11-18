from ._anvil_designer import Watchlist_OverviewTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json
from datetime import datetime

from anvil_extras import routing
from ..nav import click_link, click_button, logout, login_check, load_var


@routing.route('watchlist_overview', title='Development')
class Watchlist_Overview(Watchlist_OverviewTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)


    global user
    user = anvil.users.get_user()
    
    # Any code you write here will run before the form opens.
    if user['expiration_date'] is not None and (datetime.today().date() - user['expiration_date']).days > 0:
      print("EXPIRED HOME")
      routing.set_url_hash('no_subs', load_from_cache=False)
      get_open_form().change_nav_visibility(status=False)
      get_open_form().SearchBar.visible = False
      
    else:
      model_id = load_var("model_id")
      print(f"Watchlist_Overview model_id: {model_id}")
      self.model_id = model_id
    
      data = self.get_data()
  
      if data != 'no_data':
        # standard sorting
        self.repeating_panel_data.items = sorted(data, key=lambda x: x.get('Name', float('inf')), reverse=True)
        self.link_artist.icon = 'fa:angle-down'  

  
  def get_data(self, **event_args):
    # get raw data
    data = anvil.server.call('get_watchlist_overview', user["user_id"])
    
    if data != 'no_data':
      data = json.loads(data)

      # fill Nones and turn to strings
      for item in data:
          for key, value in item.items():
              if value is None:
                  if key == "LatestReleaseDate":
                    item[key] = '-'
                  else: item[key] = '0'
          item['FollowerDev'] = "{:.1f}".format(round(float(item['FollowerDev']),1))
          item['PopularityDev'] = "{:.1f}".format(round(float(item['PopularityDev']),1))
      
      # add 1.000er seperators
      data = self.change_format(data=data, column='FollowerLat', direction='add')
      data = self.change_format(data=data, column='FollowerDif', direction='add')
    
    return data

  # FORMAT DATA
  def change_format (self, data, column, direction, **event_args):
    if direction == 'add':
      for item in data:
        for key, value in item.items():
          if key == column: item[key] = f'{int(item[key]):,}'
    elif direction == 'remove':
      for item in data:
        for key, value in item.items():
          if key == column: item[key] = int(item[key].replace(',', ''))
    
    return data

  # RESET ICONS
  def reset_icons (self, **event_args):
    self.link_artist.icon = ''
    self.link_release.icon = ''
    self.link_poplat.icon = ''
    self.link_popdif.icon = ''
    self.link_popdev.icon = ''
    self.link_follat.icon = ''
    self.link_foldif.icon = ''
    self.link_foldev.icon = ''
    
  # SORT BUTTONS
  def link_artist_click(self, **event_args):
    if self.link_artist.icon == '' or self.link_artist.icon == 'fa:angle-up':
      self.reset_icons()
      self.link_artist.icon = 'fa:angle-down'
      self.repeating_panel_data.items = sorted(self.repeating_panel_data.items, key=lambda x: x.get('Name', float('inf')), reverse=True)
    elif self.link_artist.icon == 'fa:angle-down':
      self.reset_icons()
      self.link_artist.icon = 'fa:angle-up'
      self.repeating_panel_data.items = sorted(self.repeating_panel_data.items, key=lambda x: x.get('Name', float('inf')), reverse=False)

  def link_release_click(self, **event_args):
    if self.link_release.icon == '' or self.link_release.icon == 'fa:angle-up':
      self.reset_icons()
      self.link_release.icon = 'fa:angle-down'
      self.repeating_panel_data.items = sorted(self.repeating_panel_data.items, key=lambda x: x.get('LastReleaseDate', float('inf')), reverse=True)
    elif self.link_release.icon == 'fa:angle-down':
      self.reset_icons()
      self.link_release.icon = 'fa:angle-up'
      self.repeating_panel_data.items = sorted(self.repeating_panel_data.items, key=lambda x: x.get('LastReleaseDate', float('inf')), reverse=False)

  def link_poplat_click(self, **event_args):
    if self.link_poplat.icon == '' or self.link_poplat.icon == 'fa:angle-up':
      self.reset_icons()
      self.link_poplat.icon = 'fa:angle-down'
      self.repeating_panel_data.items = sorted(self.repeating_panel_data.items, key=lambda x: x.get('PopularityLat', float('inf')), reverse=True)
    elif self.link_poplat.icon == 'fa:angle-down':
      self.reset_icons()
      self.link_poplat.icon = 'fa:angle-up'
      self.repeating_panel_data.items = sorted(self.repeating_panel_data.items, key=lambda x: x.get('PopularityLat', float('inf')), reverse=False)

  def link_popdif_click(self, **event_args):
    if self.link_popdif.icon == '' or self.link_popdif.icon == 'fa:angle-up':
      self.reset_icons()
      self.link_popdif.icon = 'fa:angle-down'
      self.repeating_panel_data.items = sorted(self.repeating_panel_data.items, key=lambda x: x.get('PopularityDif', float('inf')), reverse=True)
    elif self.link_popdif.icon == 'fa:angle-down':
      self.reset_icons()
      self.link_popdif.icon = 'fa:angle-up'
      self.repeating_panel_data.items = sorted(self.repeating_panel_data.items, key=lambda x: x.get('PopularityDif', float('inf')), reverse=False)

  def link_popdev_click(self, **event_args):
    if self.link_popdev.icon == '' or self.link_popdev.icon == 'fa:angle-up':
      self.reset_icons()
      self.link_popdev.icon = 'fa:angle-down'
      self.repeating_panel_data.items = sorted(self.repeating_panel_data.items, key=lambda x: float(x['PopularityDev']), reverse=True)
    elif self.link_popdev.icon == 'fa:angle-down':
      self.reset_icons()
      self.link_popdev.icon = 'fa:angle-up'
      self.repeating_panel_data.items = sorted(self.repeating_panel_data.items, key=lambda x: float(x['PopularityDev']), reverse=False)

  def link_follat_click(self, **event_args):
    if self.link_follat.icon == '' or self.link_follat.icon == 'fa:angle-up':
      self.reset_icons()
      self.link_follat.icon = 'fa:angle-down'
      data = self.change_format(data=self.repeating_panel_data.items, column='FollowerLat', direction='remove')
      data = sorted(data, key=lambda x: x.get('FollowerLat', float('inf')), reverse=True)
      data = self.change_format(data=data, column='FollowerLat', direction='add')
      self.repeating_panel_data.items = data
    elif self.link_follat.icon == 'fa:angle-down':
      self.reset_icons()
      self.link_follat.icon = 'fa:angle-up'
      data = self.change_format(data=self.repeating_panel_data.items, column='FollowerLat', direction='remove')
      data = sorted(data, key=lambda x: x.get('FollowerLat', float('inf')), reverse=False)
      data = self.change_format(data=data, column='FollowerLat', direction='add')
      self.repeating_panel_data.items = data

  def link_foldif_click(self, **event_args):
    if self.link_foldif.icon == '' or self.link_foldif.icon == 'fa:angle-up':
      self.reset_icons()
      self.link_foldif.icon = 'fa:angle-down'
      data = self.change_format(data=self.repeating_panel_data.items, column='FollowerDif', direction='remove')
      data = sorted(data, key=lambda x: x.get('FollowerDif', float('inf')), reverse=True)
      data = self.change_format(data=data, column='FollowerDif', direction='add')
      self.repeating_panel_data.items = data
    elif self.link_foldif.icon == 'fa:angle-down':
      self.reset_icons()
      self.link_foldif.icon = 'fa:angle-up'
      data = self.change_format(data=self.repeating_panel_data.items, column='FollowerDif', direction='remove')
      data = sorted(data, key=lambda x: x.get('FollowerDif', float('inf')), reverse=False)
      data = self.change_format(data=data, column='FollowerDif', direction='add')
      self.repeating_panel_data.items = data

  def link_foldev_click(self, **event_args):
    if self.link_foldev.icon == '' or self.link_foldev.icon == 'fa:angle-up':
      self.reset_icons()
      self.link_foldev.icon = 'fa:angle-down'
      self.repeating_panel_data.items = sorted(self.repeating_panel_data.items, key=lambda x: float(x['FollowerDev']), reverse=True)
    elif self.link_foldev.icon == 'fa:angle-down':
      self.reset_icons()
      self.link_foldev.icon = 'fa:angle-up'
      self.repeating_panel_data.items = sorted(self.repeating_panel_data.items, key=lambda x: float(x['FollowerDev']), reverse=False)

  
  # SEARCH
  def button_search_click(self, **event_args):
    # get data
    data = [entry for entry in self.get_data() if str(entry["Name"]).lower().find(str(self.text_box_search.text).lower()) != -1]

    # sort as defined before
    if self.link_artist.icon == 'fa:angle-down':
      self.repeating_panel_data.items = sorted(data, key=lambda x: x.get('Name', float('inf')), reverse=True)
    elif self.link_artist.icon == 'fa:angle-up':
      self.repeating_panel_data.items = sorted(data, key=lambda x: x.get('Name', float('inf')), reverse=False)
      
    elif self.link_release.icon == 'fa:angle-down':
      self.repeating_panel_data.items = sorted(data, key=lambda x: x.get('LastReleaseDate', float('inf')), reverse=True)
    elif self.link_release.icon == 'fa:angle-up':
      self.repeating_panel_data.items = sorted(data, key=lambda x: x.get('LastReleaseDate', float('inf')), reverse=False)
      
    elif self.link_poplat.icon == 'fa:angle-down':
      self.repeating_panel_data.items = sorted(data, key=lambda x: x.get('PopularityLat', float('inf')), reverse=True)
    elif self.link_poplat.icon == 'fa:angle-up':
      self.repeating_panel_data.items = sorted(data, key=lambda x: x.get('PopularityLat', float('inf')), reverse=False)
      
    elif self.link_popdif.icon == 'fa:angle-down':
      self.repeating_panel_data.items = sorted(data, key=lambda x: x.get('PopularityDif', float('inf')), reverse=True)
    elif self.link_popdif.icon == 'fa:angle-up':
      self.repeating_panel_data.items = sorted(data, key=lambda x: x.get('PopularityDif', float('inf')), reverse=False)
      
    elif self.link_popdev.icon == 'fa:angle-down':
      self.repeating_panel_data.items = sorted(data, key=lambda x: x.get('PopularityDev', float('inf')), reverse=True)
    elif self.link_popdev.icon == 'fa:angle-up':
      self.repeating_panel_data.items = sorted(data, key=lambda x: x.get('PopularityDev', float('inf')), reverse=False)
    
    elif self.link_follat.icon == 'fa:angle-down':
      self.repeating_panel_data.items = sorted(data, key=lambda x: x.get('FollowerLat', float('inf')), reverse=True)
    elif self.link_follat.icon == 'fa:angle-up':
      self.repeating_panel_data.items = sorted(data, key=lambda x: x.get('FollowerLat', float('inf')), reverse=False)
      
    elif self.link_foldif.icon == 'fa:angle-down':
      self.repeating_panel_data.items = sorted(data, key=lambda x: x.get('FollowerDif', float('inf')), reverse=True)
    elif self.link_foldif.icon == 'fa:angle-up':
      self.repeating_panel_data.items = sorted(data, key=lambda x: x.get('FollowerDif', float('inf')), reverse=False)
      
    elif self.link_foldev.icon == 'fa:angle-down':
      self.repeating_panel_data.items = sorted(data, key=lambda x: x.get('FollowerDev', float('inf')), reverse=True)
    elif self.link_foldev.icon == 'fa:angle-up':
      self.repeating_panel_data.items = sorted(data, key=lambda x: x.get('FollowerDev', float('inf')), reverse=False)
