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
    
      # Set up toggle callbacks
      self.period_toggle.set_toggle_callback(self.handle_toggle_change)
      self.format_toggle.set_toggle_callback(self.handle_toggle_change)
      self.sort_by_toggle.set_toggle_callback(self.handle_toggle_change)
      

  # HANDLE TOGGLE CHANGE
  def handle_toggle_change(self, toggle_type, value):
    """
    Handle toggle changes from any toggle component and update C_TalentDev_Table
    
    Parameters:
        toggle_type: The type of toggle being changed (period, format, sort_by)
        value: The new value selected
    """
    print(f"MONITOR-LOG: Toggle {toggle_type} changed to {value}")
    
    # Update the table component with the new settings
    if toggle_type == 'period':
      self.c_talent_dev_table_1.active_period = value
    elif toggle_type == 'format':
      self.c_talent_dev_table_1.active_format = value
    elif toggle_type == 'sort_by':
      self.c_talent_dev_table_1.active_sort_by = value
      
    # Refresh the table with new settings
    self.c_talent_dev_table_1.create_table()
    
    return True


  # SEARCH
  def button_search_click(self, **event_args):
    """
    Handle search button click
    
    Parameters:
        event_args: Event arguments
    """
    # Get data
    if self.text_box_search.text:
      artist_id = anvil.server.call('get_artist_id_by_name', user["user_id"], self.text_box_search.text)
      if artist_id == 'no_id':
        n = Notification('This artist is not in your watchlist!')
        n.show()
      else: 
        routing.set_url_hash(f'artists?artist_id={artist_id}')
    else:
      n = Notification('Please enter an artist name!')
      n.show()
