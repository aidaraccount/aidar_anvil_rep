from ._anvil_designer import RelatedRowsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ...MainIn import MainIn
from ...Discover import Discover

from anvil_extras import routing
from ...nav import click_link, click_button, logout, login_check, load_var, save_var


class RelatedRows(RelatedRowsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    
    if self.item["active"] == 1:
      self.button_watchlist.background = "#fd652d"  # orange
      self.button_watchlist.foreground = "#f5f4f1"  # white
      self.button_watchlist.tooltip = "remove Watchlist"
      self.button_watchlist.icon = 'fa:star'
      self.button_watchlist_view.visible = True
    else:
      self.button_watchlist.background = ""
      self.button_watchlist.foreground = ""
      self.button_watchlist.tooltip = "add to Watchlist"
      self.button_watchlist.icon = 'fa:star-o'
      self.button_watchlist_view.visible = False

  def inspect_pic_link_click(self, **event_args):
    click_link(self.inspect_pic_link, f'artists?artist_id={self.inspect_pic_link.url}', event_args)

  def inspect_name_link_click(self, **event_args):
    click_link(self.inspect_name_link, f'artists?artist_id={self.inspect_name_link.url}', event_args)

  # BUTTONS
  def button_watchlist_click(self, **event_args):
    if self.item["active"] == 1:
      c = confirm("Do you wish to delete this artist from your watchlist?")
      if c is True:
        anvil.server.call(
          "update_watchlist_lead",
          self.item["UserID"],
          self.item["watchlist_id"],
          self.item["ArtistID"],
          False,
          None,
          False,
        )
        get_open_form().update_no_notifications()
        self.item["active"] = 0
  
        self.button_watchlist.background = ""
        self.button_watchlist.foreground = ""
        self.button_watchlist.tooltip = "add to Watchlist"
        self.button_watchlist.icon = 'fa:star-o'
        self.button_watchlist_view.visible = False
  
        Notification(
          "", title=f"{self.item['Name']} removed from the watchlist!", style="success"
        ).show()
      
    else:
      # add to Watchlist (incl. change Button) and show delete Button
      self.item["watchlist_id"] = anvil.server.call("get_watchlist_id", user["user_id"])
      
      anvil.server.call(
        "update_watchlist_lead",
        self.item["UserID"],
        self.item["watchlist_id"],
        self.item["ArtistID"],
        True,
        "Action required",
        True,
      )
      get_open_form().update_no_notifications()
      self.item["active"] = 1

      self.button_watchlist.background = "#fd652d"  # orange
      self.button_watchlist.foreground = "#f5f4f1"  # white
      self.button_watchlist.tooltip = "remove from Watchlist"
      self.button_watchlist.icon = 'fa:star'
      self.button_watchlist_view.visible = True

      Notification(
        "", title=f"{self.item['Name']} added to the watchlist!", style="success"
      ).show()

  def button_watchlist_view_click(self, **event_args):
    # route to Watchlist Details
    click_link(self.inspect_name_link, f'watchlist_details?watchlist_id={self.item["watchlist_id"]}&artist_id={self.item["ArtistID"]}', event_args)
    

  def button_discover_click(self, **event_args):
    click_button(f'artists?artist_id={self.item["ArtistID"]}', event_args)
