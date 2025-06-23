from ._anvil_designer import ColumnTemplate_Genre_OriginTemplate
from anvil import *
import stripe.checkout
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class ColumnTemplate_Genre_Origin(ColumnTemplate_Genre_OriginTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()

  def button_del_click(self, **event_args):
    del_entry_genre = {'column':self.label_column.text, "operator":"IN", 'value':self.label_value.text}
    del_entry_origin = {'column':self.label_column.text, "operator":"IN", 'value':self.label_value.text}
    data = self.parent.items
    if del_entry_genre in data:
      data.remove(del_entry_genre)
    elif del_entry_origin in data:
      data.remove(del_entry_origin)
    self.parent.items = data


