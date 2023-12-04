from ._anvil_designer import ReferenceTemplateTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class ReferenceTemplate(ReferenceTemplateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    global cur_model_id
    cur_model_id = anvil.server.call('get_model_id',  user["user_id"])

    if self.label_name_3.text == None:
      self.button_3.visible = False
      self.image_3.visible = False
      self.label_name_3.visible = False
    
    if self.label_name_2.text == None:
      self.button_2.visible = False
      self.image_2.visible = False
      self.label_name_2.visible = False

  def button_1_click(self, **event_args):
    anvil.server.call('delete_reference', cur_model_id, self.item[0]['ArtistID'])
    self.parent.parent.parent.get_references()

  def button_2_click(self, **event_args):
    anvil.server.call('delete_reference', cur_model_id, self.item[1]['ArtistID'])
    self.parent.parent.parent.get_references()
    
  def button_3_click(self, **event_args):
    anvil.server.call('delete_reference', cur_model_id, self.item[2]['ArtistID'])
    self.parent.parent.parent.get_references()
