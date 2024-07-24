from ._anvil_designer import RowTemplate4Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class RowTemplate4(RowTemplate4Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    global model_id
    model_id = anvil.server.call("get_model_id", user["user_id"])

  def related_artist_pic_link_click(self, **event_args):
    open_form(
      "Main_In",
      model_id=model_id,
      temp_artist_id=int(self.related_artist_pic_link.url),
      target="Discover",
      value=None,
    )

  def related_artist_name_link_click(self, **event_args):
    open_form(
      "Main_In",
      model_id=model_id,
      temp_artist_id=int(self.related_artist_name_link.url),
      target="Discover",
      value=None,
    )
