from ._anvil_designer import RampUpTemplate

from anvil import *
import plotly.graph_objects as go
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import random
import string
import json
import time
import math

from ..Home import Home
from ..C_RefArtistsSettings import C_RefArtistsSettings
# from ..C_CreateModel import C_CreateModel

from anvil_extras import routing
from ..nav import click_link, click_button, load_var, save_var

from anvil import js
import anvil.js
import anvil.js.window


@routing.route("model_setup", url_keys=["section"], title="Model Setup")
class RampUp(RampUpTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    
    section = self.url_dict["section"]
    self.section = section
    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()

    # initial variable defenition
    self.model_id_in_creation = load_var('model_id_in_creation')
    self.model_name_txt = load_var('model_name_txt')
    self.model_description_txt = load_var('model_description_txt')
    
    # ---------------
    # HEADER
    if self.model_name_txt is not None:
      self.column_panel_header.visible = True
      self.model_name.text = self.model_name_txt
      self.model_description.text = self.model_description_txt
    else:
      self.column_panel_header.visible = False

    # ---------------
    # SECTION ROUTING
    if section == "Basics":
      self.nav_Basics_load()
      self.Back.visible = False
      self.Next.visible = True
      self.Discovering.visible = False
    elif section == "Reference_Artists":
      self.nav_References_load()
      self.Back.visible = True
      self.Next.visible = True
      self.Discovering.visible = False
    elif section == "Level_of_Pop":
      self.nav_Level_Pop_load()
      self.Back.visible = True
      self.Next.visible = False
      self.Discovering.visible = True
    
    self.text_box_change()

  def nav_Basics_load (self, **event_args):
    self.nav_Basics.role = "section_buttons_focused"
    self.nav_References.role = "section_buttons"
    self.nav_Level_Pop.role = "section_buttons"
    self.sec_Basics.visible = True
    self.sec_Reference_Artists.visible = False
    self.sec_Level_of_Pop.visible = False
    
    if self.model_name_txt:
      self.text_box_model_name.text = self.model_name_txt
      self.text_box_description.text = self.model_description_txt
    
    self.text_box_access_token.text = f"{''.join(random.choice((string.ascii_letters + string.digits)) for _ in range(3))}-{''.join(random.choice((string.ascii_letters + string.digits)) for _ in range(3))}-{''.join(random.choice((string.ascii_letters + string.digits)) for _ in range(3))}"
    
  def nav_Basics_click(self, **event_args):
    click_link(self.nav_Basics, 'model_setup?section=Basics', event_args)
    
  def nav_References_load(self, **event_args):
    self.nav_Basics.role = "section_buttons"
    self.nav_References.role = "section_buttons_focused"
    self.nav_Level_Pop.role = "section_buttons"
    self.sec_Basics.visible = False
    self.sec_Reference_Artists.visible = True
    self.sec_Level_of_Pop.visible = False
    self.sec_Reference_Artists.clear()
    self.sec_Reference_Artists.add_component(C_RefArtistsSettings())

  def nav_References_click(self, **event_args):    
    if self.text_box_access_token.text == '':
      alert(title='Missing Access Token',
        content="Please add an Access Token!")      
    elif self.text_box_model_name.text == '':
      alert(title='Missing Model Name',
        content="Please add a Model Name!")
    else:
      self.button_create_model_click()
      click_link(self.nav_References, 'model_setup?section=Reference_Artists', event_args)
  
  def nav_Level_Pop_load(self, **event_args):
    self.nav_Basics.role = "section_buttons"
    self.nav_References.role = "section_buttons"
    self.nav_Level_Pop.role = "section_buttons_focused"
    self.sec_Basics.visible = False
    self.sec_Reference_Artists.visible = False
    self.sec_Level_of_Pop.visible = True
    self.sec_Level_of_Pop.clear()
    # self.sec_Reference_Artists.add_component(C_RefArtistsSettings())

  def nav_Level_Pop_click(self, **event_args):
    click_link(self.nav_Level_Pop, 'model_setup?section=Level_of_Pop', event_args)

  # ---------------
  # NAVIGATION BUTTONS
  def Next_click(self, **event_args):
    if self.section == "Basics":
      status = self.button_create_model_click()
      if status == 'Congratulations, your Model was successfully created!':
        click_button('model_setup?section=Reference_Artists', event_args)
      
    elif self.section == 'Reference_Artists':
      artist_id = anvil.server.call('get_next_artist_id', self.model_id_in_creation)
      if artist_id is not None:
        click_button('model_setup?section=Level_of_Pop', event_args)
      else:        
        alert(title='Not enough References', content="Please add additional Reference Artists!")

  def Back_click(self, **event_args):
    if self.section == "Level_of_Pop":
      click_button('model_setup?section=Reference_Artists', event_args)
    elif self.section == 'Reference_Artists':
      click_button('model_setup?section=Basics', event_args)

  def Discovering_click(self, **event_args):
    artist_id = anvil.server.call('get_next_artist_id', load_var('model_id'))
    click_button(f'artists?artist_id={artist_id}', event_args)

  # ---------------
  # BASICS FUNCTIONS
  def button_create_model_click(self, **event_args):
    if self.text_box_access_token.text == '':
      alert(title='Missing Access Token',
        content="Please add an Access Token!")
      status = 'Missing Access Token'
      
    elif self.text_box_model_name.text == '':
      alert(title='Missing Model Name',
        content="Please add a Model Name!")
      status = 'Missing Model Name'

    elif self.model_id_in_creation is not None:
      print("creation in progress!")
      status = 'Congratulations, your Model was successfully created!'

      print("ADD MODEL UPDATE!!")
    
    else:
      status = anvil.server.call('create_model',
                                 user["user_id"],
                                 self.text_box_model_name.text,
                                 self.text_box_description.text,
                                 self.text_box_access_token.text)
      if (status == 'Congratulations, your Model was successfully created!'):
        # refresh model_id
        model_id = anvil.server.call('get_model_id',  user["user_id"])
        anvil.server.call('update_model_usage', user["user_id"], model_id)
        save_var('model_id', model_id)
        save_var('model_id_in_creation', model_id)

        # save name & description
        save_var('model_name_txt', self.text_box_model_name.text)
        save_var('model_description_txt', self.text_box_description.text)
    
        # refresh models components
        get_open_form().refresh_models_components()
        get_open_form().change_nav_visibility(status=True)
        
      else:
        alert(title='Error..', content=status)

    return status

  def text_box_model_name_lost_focus(self, **event_args):
    self.text_box_description.focus()

  def text_box_description_lost_focus(self, **event_args):
    self.text_box_access_token.focus()

  def text_box_change(self, **event_args):
    if self.text_box_model_name.text != '' and self.text_box_access_token.text != '':
      self.Next.role = 'call-to-action-button'
    else:
      self.Next.role = ''
