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
    global model_id
    model_id = anvil.server.call('get_model_id',  user["user_id"])

    if self.label_name_3.text is None:
      self.button_3.visible = False
      self.image_3.visible = False
      self.label_name_3.visible = False
    
    if self.label_name_2.text is None:
      self.button_2.visible = False
      self.image_2.visible = False
      self.label_name_2.visible = False

  def button_1_click(self, **event_args):
    c = confirm("Do you wish to delete this artist as a reference?")
    if c is True:
      anvil.server.call('delete_reference', model_id, self.item[0]['ArtistID'])
      self.parent.parent.parent.get_references()

  def button_2_click(self, **event_args):
    c = confirm("Do you wish to delete this artist as a reference?")
    if c is True:
      anvil.server.call('delete_reference', model_id, self.item[1]['ArtistID'])
      self.parent.parent.parent.get_references()
    
  def button_3_click(self, **event_args):
    c = confirm("Do you wish to delete this artist as a reference?")
    if c is True:
      anvil.server.call('delete_reference', model_id, self.item[2]['ArtistID'])
      self.parent.parent.parent.get_references()
