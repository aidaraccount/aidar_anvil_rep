from ._anvil_designer import ItemTemplate5Template
from anvil import *
import stripe.checkout
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class ItemTemplate5(ItemTemplate5Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    if self.item['NoteID'] is None:
      self.link_delete.visible = False
      self.note.italic = True
      self.note.bold = False
      self.note.font_size = 13
  
  def link_delete_click(self, **event_args):
    anvil.server.call('delete_watchlist_note', self.link_delete.url)
    self.column_panel_1.visible = False