from ._anvil_designer import C_ModelProfileTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import random
import string
import json

from ..C_EditRefArtists import C_EditRefArtists
from ..C_Filter import C_Filter


class C_ModelProfile(C_ModelProfileTemplate):
  def __init__(self, model_id, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    self.model_id = model_id
    
    # initial visibile settings
    self.model_name_text.visible = False
    self.model_description_text.visible = False
    
    self.nav_references.role = 'section_buttons_focused'
    self.sec_filters.visible = False

    # HEADER
    infos = json.loads(anvil.server.call('get_model_stats', model_id))[0]
    
    self.model_name.text = infos["model_name"]
    if infos["description"] is None:
      self.model_description.text = '-'
    else:
      self.model_description.text = infos["description"]
    if infos["creation_date"] == 'None':
      self.creation_date.text = '-'
    else:
      self.creation_date.text = infos["creation_date"]
    self.usage_date.text = infos["usage_date"]

    self.no_references.text = infos["no_references"]
    self.total_ratings.text = infos["total_ratings"]
    self.high_ratings.text = infos["high_ratings"]
    if infos["train_model_date"] == 'None':
      self.train_model_date.text = '-'
    else:
      self.train_model_date.text = infos["train_model_date"]
    self.status.text = infos["status"]
    
    # FIRST SECTION
    self.sec_references.add_component(C_EditRefArtists(model_id))

  
  def edit_icon_click(self, **event_args):
    if self.model_name.visible is True: 
      self.model_name.visible = False
      self.model_description.visible = False
      self.model_name_text.visible = True
      self.model_description_text.visible = True
      self.model_name_text.text = self.model_name.text
      self.model_description_text.text = self.model_description.text
    else:
      self.model_name_text.visible = False
      self.model_description_text.visible = False
      self.model_name.visible = True
      self.model_description.visible = True
      self.model_name.text = self.model_name_text.text
      self.model_description.text = self.model_description_text.text

  def nav_references_click(self, **event_args):
    self.nav_references.role = 'section_buttons_focused'
    self.nav_filters.role = 'section_buttons'
    self.sec_references.visible = True
    self.sec_filters.visible = False

  def nav_filters_click(self, **event_args):
    self.nav_references.role = 'section_buttons'
    self.nav_filters.role = 'section_buttons_focused'
    self.sec_references.visible = False
    self.sec_filters.visible = True
    self.sec_filters.add_component(C_Filter(self.model_id))
  