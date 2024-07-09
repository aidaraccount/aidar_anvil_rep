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
import time

from ..C_Home import C_Home
from ..C_EditRefArtists import C_EditRefArtists
from ..C_AddRefArtists import C_AddRefArtists
from ..C_Filter import C_Filter


class C_ModelProfile(C_ModelProfileTemplate):
  def __init__(self, model_id, target=None, **properties):
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
    self.retrain_date = infos["train_model_date"]
    
    if infos["total_ratings"] < 75:
      self.retrain.visible = False
      self.retrain_wait.visible = True
      self.retrain_wait.text = 'At least 75 ratings required for training the model'
    elif self.retrain_date != time.strftime("%Y-%m-%d"):
      self.retrain.visible = True
      self.retrain_wait.visible = False
    else:
      self.retrain.visible = False
      self.retrain_wait.visible = True
    
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
    
    # TARGET
    if target is None:
      self.nav_references_click()
    elif target == 'C_Filter':
      self.nav_filters_click()
    elif target == 'C_AddRefArtists':
      self.nav_add_references_click()

  
  def edit_icon_click(self, **event_args):
    if self.model_name.visible is True: 
      self.model_name.visible = False
      self.model_description.visible = False
      self.model_name_text.visible = True
      self.model_description_text.visible = True
      self.model_name_text.text = self.model_name.text
      self.model_description_text.text = self.model_description.text
      self.edit_icon.icon = 'fa:save'
    else:
      self.model_name_text.visible = False
      self.model_description_text.visible = False
      self.model_name.visible = True
      self.model_description.visible = True
      self.model_name.text = self.model_name_text.text
      self.model_description.text = self.model_description_text.text
      self.edit_icon.icon = 'fa:pencil'
      res = anvil.server.call('update_model_stats', self.model_id, self.model_name_text.text, self.model_description_text.text)
      if res == 'success':
        Notification("",
          title="Model updated!",
          style="success").show()

  def nav_references_click(self, **event_args):
    self.nav_references.role = 'section_buttons_focused'
    self.nav_filters.role = 'section_buttons'
    self.sec_references.visible = True
    self.sec_filters.visible = False
    self.sec_references.clear()
    self.sec_references.add_component(C_EditRefArtists(self.model_id))

  def nav_add_references_click(self, **event_args):
    self.nav_references.role = 'section_buttons_focused'
    self.nav_filters.role = 'section_buttons'
    self.sec_references.visible = True
    self.sec_filters.visible = False
    self.sec_references.clear()
    self.sec_references.add_component(C_AddRefArtists(self.model_id))
  
  def nav_filters_click(self, **event_args):
    self.nav_references.role = 'section_buttons'
    self.nav_filters.role = 'section_buttons_focused'
    self.sec_references.visible = False
    self.sec_filters.visible = True
    self.sec_filters.clear()
    self.sec_filters.add_component(C_Filter(self.model_id))

  def delete_click(self, **event_args):
    result = alert(title='Do you want to delete this model?',
          content="Are you sure to delete this model?\n\nEverything will be lost! All reference artists, all previously rated artists - all you did will be gone for ever.",
          buttons=[
            ("Cancel", "Cancel"),
            ("Delete", "Delete")
          ])
    if result == 'Delete':
      print(self.model_id)
      res = anvil.server.call('delete_model', self.model_id)
      if res == 'success':
        Notification("",
          title="Model deleted!",
          style="success").show()

        print(self.model_id)
        #self.content_panel.clear()
        #self.content_panel.add_component(C_Home(model_id=model_id_new))
        open_form('Main_In', model_id=None, temp_artist_id = None, target = None, value=None)
  
  def discover_click(self, **event_args):
    open_form('Main_In', self.model_id, temp_artist_id = None, target = 'C_Discover', value=None)

  def retrain_click(self, **event_args):
    res = anvil.server.call('retrain_model', self.model_id)
    if res == 'success':
      self.retrain.visible = False
      self.retrain_wait.visible = True
      self.train_model_date.text = time.strftime("%Y-%m-%d")
      alert(title='Re-training of your model is running',
            content="We started to re-train your model. This will take roughly 10 minutes to be effective.\n\nDue to high computational effort, re-training the model is only available once per day.",
            buttons=[("Ok", "Ok")]
      )