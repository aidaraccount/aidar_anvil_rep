from ._anvil_designer import RowTemplate_Labels_SelectionTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class RowTemplate_Labels_Selection(RowTemplate_Labels_SelectionTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def button_exclude_click(self, **event_args):
    new_entry = {'label_id':self.item['label_id'], 'label_name':self.item['label_name']}
    print(new_entry)
    
    label_data = self.parent.parent.parent.parent.rep_pan_label.items
    if label_data is None:
      label_data = [new_entry]
    else:
      if not any(entry['label_id'] == new_entry['label_id'] for entry in label_data):
        label_data.append(new_entry)
    
    self.parent.parent.parent.parent.rep_pan_label.items = label_data
    self.parent.parent.parent.parent.label_no_label_filters.visible = False

    print('label_data:', label_data)