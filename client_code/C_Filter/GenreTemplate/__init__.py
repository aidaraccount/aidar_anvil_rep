from ._anvil_designer import GenreTemplateTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class GenreTemplate(GenreTemplateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def button_del_genre_click(self, **event_args):
    del_entry = {'Genre': self.label_genre.text, 'Value': self.label_value.text}
    genre_data = self.parent.items
    genre_data.remove(del_entry)
    self.parent.items = genre_data
