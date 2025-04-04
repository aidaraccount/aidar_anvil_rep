from ._anvil_designer import NewsTemplateTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class NewsTemplate(NewsTemplateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    if self.item['NoteID'] is None:
      self.note.italic = True
      self.note.bold = False
      self.note.font_size = 13
