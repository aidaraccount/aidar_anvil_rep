from ._anvil_designer import Monitor_TalentDevTemplate
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


@routing.route('talent_dev', title='Development')
class Monitor_TalentDev(Monitor_TalentDevTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)


    global user
    user = anvil.users.get_user()
    
    # Any code you write here will run before the form opens.
    if user['expiration_date'] is not None and (datetime.today().date() - user['expiration_date']).days > 0:
      routing.set_url_hash('no_subs', load_from_cache=False)
      get_open_form().SearchBar.visible = False
      
    else:
      model_id = load_var("model_id")
      print(f"Monitor_TalentDev model_id: {model_id}")
      self.model_id = model_id
    
      # Set up toggle callback
      self.c_talent_dev_toggle_1.set_toggle_callback(self.handle_period_toggle)
      
  
  # HANDLE TOGGLE PERIOD CHANGE
  def handle_period_toggle(self, period):
    """
    Handle period toggle change from C_TalentDev_Toggle and update C_TalentDev_Table
    
    Parameters:
        period: The new period selected (7-Day or 30-Day)
    """
    print(f"MONITOR-LOG: Period toggle changed to {period}")
    
    # Update the table component with the new period
    self.c_talent_dev_table_1.active_period = period
    self.c_talent_dev_table_1.create_table()
    
    return True

    
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
