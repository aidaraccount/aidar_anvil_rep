from ._anvil_designer import SearchRowsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from anvil_extras import routing
from ...nav import click_link, click_button

from ...Main_In import Main_In
from ...Discover import Discover

class SearchRows(SearchRowsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    global model_id
    model_id = self.item["ModelID"]
    
    if self.item["Watchlist"] == 1:
      self.button_watchlist.background = '#fd652d' # orange
      self.button_watchlist.foreground = '#f5f4f1' # white
      self.button_watchlist.tooltip = 'go to Watchlist'
      self.button_watchlist_delete.visible = True
    else:
      self.button_watchlist.background = ''
      self.button_watchlist.foreground = ''
      self.button_watchlist.tooltip = 'add to Watchlist'
      self.button_watchlist_delete.visible = False

  
  def inspect_pic_link_click(self, **event_args):
    click_link(self.inspect_pic_link, f'artists?artist_id={self.inspect_pic_link.url}', event_args)
    #open_form('Main_In', model_id=model_id, temp_artist_id = int(self.inspect_pic_link.url), target='Discover', value=None)

  def inspect_name_link_click(self, **event_args):
    click_link(self.inspect_name_link, f'artists?artist_id={self.inspect_name_link.url}', event_args)
    #open_form('Main_In', model_id=model_id, temp_artist_id=int(self.inspect_name_link.url), target='Discover', value=None)
    
  # BUTTONS
  def button_watchlist_click(self, **event_args):
    if self.item["Watchlist"] == 1:
      # route to Watchlist Details
      open_form('Main_In', model_id=model_id, temp_artist_id = self.item["ArtistID"], target = 'Watchlist_Details', value=None)      
    else:
      # add to Watchlist (incl. change Button) and show delete Button
      anvil.server.call('update_watchlist_lead',
                        self.item["ModelID"],
                        self.item["ArtistID"],
                        True,
                        'Action required',
                        True
                        )
      self.parent.parent.parent.parent.parent.parent.update_no_notifications()
      self.item["Watchlist"] = 1
      
      self.button_watchlist.background = '#fd652d' # orange
      self.button_watchlist.foreground = '#f5f4f1' # white
      self.button_watchlist.tooltip = 'go to Watchlist'
      self.button_watchlist_delete.visible = True
      
      Notification("",
        title=f"{self.item['Name']} added to the watchlist!",
        style="success").show()
      
  def button_watchlist_delete_click(self, **event_args):
    c = confirm("Do you wish to delete this artist from your watchlist?")
    if c is True:
      anvil.server.call('update_watchlist_lead', self.item["ModelID"], self.item["ArtistID"], False, None, False)
      self.parent.parent.parent.parent.parent.parent.update_no_notifications()
      self.item["Watchlist"] = 0
      
      self.button_watchlist.background = ''
      self.button_watchlist.foreground = ''
      self.button_watchlist.tooltip = 'add to Watchlist'
      self.button_watchlist_delete.visible = False
      
      Notification("",
        title=f"{self.item['Name']} removed from the watchlist!",
        style="success").show()      

  def button_discover_click(self, **event_args):
    click_button(f'artists?artist_id={self.item["ArtistID"]}', event_args)
    #open_form('Main_In', model_id=model_id, temp_artist_id=self.item["ArtistID"], target='Discover', value=None)
