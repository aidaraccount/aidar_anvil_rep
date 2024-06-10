from ._anvil_designer import ColumnTemplateTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class ColumnTemplate(ColumnTemplateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    global model_id
    #model_id = anvil.server.call('get_model_id',  user["user_id"])
    model_id = self.item["ModelID"]

  def button_del_click(self, **event_args):
    del_entry_genre = {"ModelID":model_id, "Type":"genre", 'Column':self.label_column.text, "Operator":"is", 'Value':self.label_value.text}
    del_entry_origin = {"ModelID":model_id, "Type":"origin", 'Column':self.label_column.text, "Operator":"is", 'Value':self.label_value.text}
    data = self.parent.items
    if del_entry_genre in data:
      data.remove(del_entry_genre)
    elif del_entry_origin in data:
      data.remove(del_entry_origin)
    self.parent.items = data


