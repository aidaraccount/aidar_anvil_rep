from ._anvil_designer import CreateWatchlistTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import random
import string

from anvil_extras import routing
from ..nav import click_link, click_button, save_var


@routing.route("create_watchlist", title="Create Watchlist")
class CreateWatchlist(CreateWatchlistTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()

  
  def button_create_watchlist_click(self, **event_args):
    if self.text_box_watchlist_name.text == "":
      alert(title="Missing Watchlist Name", content="Please add a Watchlist Name!")
      status = "Missing Watchlist Name"

    else:
      status = anvil.server.call(
        "create_watchlist",
        user["user_id"],
        self.text_box_watchlist_name.text,
        self.text_box_description.text
      )
      print("status:", status)
      if status == "Congratulations, your Watchlist was successfully created!":
        # refresh watchlist_id
        watchlist_id = anvil.server.call("get_watchlist_id", user["user_id"])
        print("watchlist_id:", watchlist_id)
        anvil.server.call("update_watchlist_usage", user["user_id"], watchlist_id)
        save_var("watchlist_id", watchlist_id)

        # refresh models components
        get_open_form().refresh_watchlists_components()
        routing.set_url_hash(f'watchlist_details?watchlist_id={watchlist_id}&artist_id=None', load_from_cache=False)

      else:
        alert(title="Error..", content=status)

    return status

  def text_box_watchlist_name_lost_focus(self, **event_args):
    self.text_box_description.focus()

  def text_box_watchlist_name_change(self, **event_args):
    if self.text_box_watchlist_name.text != "":
      self.CreateButton.role = ['call-to-action-button', 'header-5', 'opacity-100', '150px-width']
    else:
      self.CreateButton.role = ['header-5', 'opacity-100', '150px-width']
