from ._anvil_designer import ReferenceTemplateTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...nav import click_link, click_button, load_var, save_var


class ReferenceTemplate(ReferenceTemplateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    self.model_id_view = load_var("model_id_in_creation")

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
      # self.parent.parent.parent.parent.parent.parent.no_references.text = int(self.parent.parent.parent.parent.parent.parent.no_references.text) - 1
      anvil.server.call('delete_reference', self.model_id_view, self.item[0]['ArtistID'])
      self.parent.parent.parent.get_references()

  def button_2_click(self, **event_args):
    c = confirm("Do you wish to delete this artist as a reference?")
    if c is True:
      # self.parent.parent.parent.parent.parent.parent.no_references.text = int(self.parent.parent.parent.parent.parent.parent.no_references.text) - 1
      anvil.server.call('delete_reference', self.model_id_view, self.item[1]['ArtistID'])
      self.parent.parent.parent.get_references()
    
  def button_3_click(self, **event_args):
    c = confirm("Do you wish to delete this artist as a reference?")
    if c is True:
      # self.parent.parent.parent.parent.parent.parent.no_references.text = int(self.parent.parent.parent.parent.parent.parent.no_references.text) - 1
      anvil.server.call('delete_reference', self.model_id_view, self.item[2]['ArtistID'])
      self.parent.parent.parent.get_references()
