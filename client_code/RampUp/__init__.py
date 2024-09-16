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

from anvil_extras import routing
from ..nav import click_link, click_button, load_var, save_var

from anvil import js
import anvil.js
import anvil.js.window


@routing.route("model_setup", url_keys=['model_id', 'section'], title="Model Setup")
class RampUp(RampUpTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    
    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()

    # initial variable defenition
    self.model_id_view = self.url_dict['model_id']
    save_var("model_id_view", self.model_id_view)
    print(f"RampUp model_id_view: {self.model_id_view}")
    
    section = self.url_dict["section"]
    self.section = section
    print(f"RampUp section: {section}")
    
    # ---------------
    # EXISTING MODEL?
    # fill header and test fields
    if self.model_id_view != 'None':
      self.column_panel_header.visible = True
      model_stats = json.loads(anvil.server.call('get_model_stats', self.model_id_view))[0]
      self.model_name.text = model_stats["model_name"]
      self.text_box_model_name.text = model_stats["model_name"]
      self.model_description.text = model_stats["description"]
      self.text_box_description.text = model_stats["description"]
    else:
      self.column_panel_header.visible = False

    # ---------------
    # SECTION ROUTING
    if section == "Basics":
      self.nav_Basics_load()
      self.Back.visible = False
      self.Next.visible = True
      self.next_role(section)
      self.Discovering.visible = False
    elif section == "Reference_Artists":
      self.nav_References_load()
      self.Back.visible = True
      self.Next.visible = True
      self.next_role(section)
      self.Discovering.visible = False
    elif section == "Level_of_Pop":
      self.nav_Level_Pop_load()
      self.Back.visible = True
      self.Next.visible = False
      self.Discovering.visible = True

  # # ---------------
  # # NAVIGATION BAR
  # def nav_Basics_click(self, **event_args):
  #   if self.model_id:
  #     click_link(self.nav_Basics, f'model_setup?model_id={self.model_id}&section=Basics', event_args)
  #   else:
  #     click_link(self.nav_Basics, 'model_setup?model_id=None&section=Basics', event_args)

  # def nav_References_click(self, **event_args):
  #   # status = self.button_create_model_click()
  #   # if status == 'Congratulations, your Model was successfully created!':
  #   if self.model_id:
  #     click_link(self.nav_References, f'model_setup?model_id={self.model_id}&section=Reference_Artists', event_args)
  #   else:
  #     click_link(self.nav_References, 'model_setup?model_id=None&section=Reference_Artists', event_args)

  # def nav_Level_Pop_click(self, **event_args):
  #   # artist_id = anvil.server.call('get_next_artist_id', self.model_id_in_creation)
  #   # if artist_id is not None:
  #   #   click_button(f'model_setup?model_id={self.model_id}&section=Level_of_Pop', event_args)
  #   # else:        
  #   #   alert(title='Not enough References', content="Please add additional Reference Artists!")
  #   if self.model_id:
  #     click_link(self.nav_Level_Pop, f'model_setup?model_id={self.model_id}&section=Level_of_Pop', event_args)
  #   else:
  #     click_link(self.nav_Level_Pop, 'model_setup?model_id=None&section=Level_of_Pop', event_args)
    
  # ---------------
  # NAVIGATION BUTTONS
  def Next_click(self, **event_args):
    # Basics
    if self.section == "Basics":
      if self.text_box_model_name.text == '':        
        alert(title='Model Name required', content="Please add a name for the model!")
        
      else:
        # save changes
        print("1", self.model_id_view)
        if self.model_id_view != 'None':
          print("model_id_view is!")
          status = anvil.server.call('update_model_stats',
                                    self.model_id_view,
                                    self.text_box_model_name.text,
                                    self.text_box_description.text)
          if status == 'success':
            status = 'Congratulations, your Model was successfully created!'
        else:
          access_token = f"{''.join(random.choice((string.ascii_letters + string.digits)) for _ in range(3))}-{''.join(random.choice((string.ascii_letters + string.digits)) for _ in range(3))}-{''.join(random.choice((string.ascii_letters + string.digits)) for _ in range(3))}"
          status = anvil.server.call('create_model',
                                     user["user_id"],
                                     self.text_box_model_name.text,
                                     self.text_box_description.text,
                                     access_token)
          
          if status == 'Congratulations, your Model was successfully created!':
            # refresh model_id_view
            self.model_id_view = anvil.server.call('get_model_id', user["user_id"])
            print("2", self.model_id_view)
            anvil.server.call('update_model_usage', user["user_id"], self.model_id_view)
            save_var('model_id', self.model_id_view)
            self.model_id = self.model_id_view
            save_var('model_id_view', self.model_id_view)
            self.model_id_view = self.model_id_view
    
            # refresh models components
            get_open_form().refresh_models_components()
            get_open_form().change_nav_visibility(status=True)
            
        # check
        if status == 'Congratulations, your Model was successfully created!':
          
          # routing
          click_button(f'model_setup?model_id={self.model_id_view}&section=Reference_Artists', event_args)
        
    # Reference_Artists
    elif self.section == 'Reference_Artists':
      artist_id = anvil.server.call('get_next_artist_id', self.model_id_view)
      if artist_id is not None:
        click_button(f'model_setup?model_id={self.model_id_view}&section=Level_of_Pop', event_args)
      else:
        alert(title='Not enough References', content="Please add additional Reference Artists!")
            
  def Back_click(self, **event_args):
    if self.section == "Level_of_Pop":
      click_button(f'model_setup?model_id={self.model_id_view}&section=Reference_Artists', event_args)
    elif self.section == 'Reference_Artists':
      click_button(f'model_setup?model_id={self.model_id_view}&section=Basics', event_args)

  def Discovering_click(self, **event_args):
    artist_id = anvil.server.call('get_next_artist_id', load_var('model_id_view'))
    click_button(f'artists?artist_id={artist_id}', event_args)

  # ---------------
  # LOAD SECTIONS
  def nav_Basics_load(self, **event_args):
    self.nav_Basics.role = "section_buttons_focused"
    self.nav_References.role = "section_buttons"
    self.nav_Level_Pop.role = "section_buttons"
    self.sec_Basics.visible = True
    self.sec_Reference_Artists.visible = False
    self.sec_Level_of_Pop.visible = False
    
  def nav_References_load(self, **event_args):
    self.nav_Basics.role = "section_buttons"
    self.nav_References.role = "section_buttons_focused"
    self.nav_Level_Pop.role = "section_buttons"
    self.sec_Basics.visible = False
    self.sec_Reference_Artists.visible = True
    self.sec_Level_of_Pop.visible = False
    self.sec_Reference_Artists.clear()
    self.sec_Reference_Artists.add_component(C_RefArtistsSettings())

  def nav_Level_Pop_load(self, **event_args):
    self.nav_Basics.role = "section_buttons"
    self.nav_References.role = "section_buttons"
    self.nav_Level_Pop.role = "section_buttons_focused"
    self.sec_Basics.visible = False
    self.sec_Reference_Artists.visible = False
    self.sec_Level_of_Pop.visible = True
    self.sec_Level_of_Pop.clear()
    # self.sec_Reference_Artists.add_component(C_RefArtistsSettings())

  # ---------------
  # BASICS FUNCTIONS
  # def button_create_model_click(self, **event_args):
  #   if self.model_id_in_creation is not None:
  #     status = anvil.server.call('update_model_stats',
  #                                self.model_id_in_creation,
  #                                self.text_box_model_name.text,
  #                                self.text_box_description.text)
  #     if status == 'success':
  #       status = 'Congratulations, your Model was successfully created!'  
  #       save_var('model_name_txt', self.text_box_model_name.text)
  #       save_var('model_description_txt', self.text_box_description.text)
    
  #   else:
  #     access_token = f"{''.join(random.choice((string.ascii_letters + string.digits)) for _ in range(3))}-{''.join(random.choice((string.ascii_letters + string.digits)) for _ in range(3))}-{''.join(random.choice((string.ascii_letters + string.digits)) for _ in range(3))}"
  #     status = anvil.server.call('create_model',
  #                                user["user_id"],
  #                                self.text_box_model_name.text,
  #                                self.text_box_description.text,
  #                                access_token)
  #     if (status == 'Congratulations, your Model was successfully created!'):
  #       # refresh model_id
  #       model_id = anvil.server.call('get_model_id',  user["user_id"])
  #       anvil.server.call('update_model_usage', user["user_id"], model_id)
  #       save_var('model_id', model_id)
  #       save_var('model_id_in_creation', model_id)

  #       # save name & description
  #       save_var('model_name_txt', self.text_box_model_name.text)
  #       save_var('model_description_txt', self.text_box_description.text)
    
  #       # refresh models components
  #       get_open_form().refresh_models_components()
  #       get_open_form().change_nav_visibility(status=True)
        
  #     else:
  #       alert(title='Error..', content=status)

  #   return status

  def text_box_model_name_lost_focus(self, **event_args):
    self.text_box_description.focus()

  def delete_click(self, ask=True, **event_args):
    print("DELETE COMPLETE MODEL")
    print("ON MODEL VIEW GO TO RAMP UP (add a bool to models table)")
    result = ''
    if ask:
      result = alert(title='Do you want to delete this model setup?',
            content="Are you sure to delete this model setup?",
            buttons=[
              ("Cancel", "Cancel"),
              ("Delete", "Delete")
            ])
    
    if result == 'Delete' or ask is False:
      save_var('model_id_in_creation', None)
      save_var('model_name_txt', None)
      save_var('model_description_txt', None)
      
      if ask:
        Notification("",
          title="Model deleted!",
          style="success").show()
        click_button('home', event_args)
        get_open_form().refresh_models_components()
        get_open_form().refresh_models_underline()

  def next_role(self, section='Basics', **event_args):
    if section == 'Basics' and self.text_box_model_name.text != '':
      self.Next.role = 'call-to-action-button'
    elif section == 'Reference_Artists':
      artist_id = anvil.server.call('get_next_artist_id', self.model_id_view)          
      if artist_id is not None:
        self.Next.role = 'call-to-action-button'
      else:
        self.Next.role = ''
    else:
      self.Next.role = ''
