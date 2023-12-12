from ._anvil_designer import RatingRowsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ...C_Watchlist_Details import C_Watchlist_Details
from ...Main_In import Main_In

class RatingRows(RatingRowsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    print(self.item)
    if self.item["Watchlist"] == 1:
      self.button_watchlist.background = '#fd652d' # orange
      self.button_watchlist.foreground = '#f5f4f1' # white
      self.button_watchlist_delete.visible = True
    else:
      self.button_watchlist.background = ''
      self.button_watchlist.foreground = ''
      self.button_watchlist_delete.visible = False
    
  
  def check_link_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.check_link.url = 'www.google.com'
    self.content_panel.clear()
    self.content_panel.add_component(C_Investigate())

  def inspect_pic_link_click(self, **event_args):
    open_form('Main_In', temp_artist_id = int(self.inspect_pic_link.url))

  def inspect_name_link_click(self, **event_args):
    open_form('Main_In', temp_artist_id = int(self.inspect_name_link.url))

  def button_watchlist_click(self, **event_args):
    if self.item["Watchlist"] == 1:
      #print(self.parent.parent.parent.parent.parent.parent.parent)
      #print(self.parent.parent.parent.parent.parent.parent)
      #self.parent.parent.parent.parent.parent.parent.content_panel.clear()
      #self.parent.parent.add_component(C_Watchlist_Details())

      print(f"open Form:")
      open_form('Main_In', temp_artist_id = self.item["ArtistID"], target = 'C_Watchlist_Details')
      
    else:
      pass
      
  def button_watchlist_delete_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
