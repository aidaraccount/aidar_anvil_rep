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
    global user
    global cur_model_id
    user = anvil.users.get_user()
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])


  def button_del_genre_click(self, **event_args):
    del_entry = {'Column':self.label_genre.text, 'Value':self.label_value.text}
    genre_data = self.parent.items
    genre_data.remove(del_entry)
    self.parent.items = genre_data
    print(self.parent.parent)
    self.parent.parent.label_no_genre_filters.visible = True
