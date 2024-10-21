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
from ..C_LevelOfPopularity import C_LevelOfPopularity
from ..C_SubModelContribution import C_SubModelContribution

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

    self.Discovering.role = ['call-to-action-button','header-5','opacity-100', '150px-width']  # needs to be individualized!!!
    
    # ---------------
    # EXISTING MODEL? (fill header and test fields)
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
      self.Next.visible = True
      self.next_role(section)
      self.Discovering.visible = False
    elif section == "Sub_Model_Contribution":
      self.nav_SubModelContribution_load()
      self.Back.visible = True
      self.Next.visible = False
      self.Discovering.visible = True

  # ---------------
  # NAVIGATION BUTTONS
  def Next_click(self, **event_args):
    # Basics
    if self.section == "Basics":
      if self.text_box_model_name.text == '':        
        alert(title='Model Name required', content="Please add a name for the model!")  
      else:
        # save changes
        if self.model_id_view != 'None':
          status = anvil.server.call('update_model_stats',
                                    self.model_id_view,
                                    self.text_box_model_name.text,
                                    self.text_box_description.text,
                                    True)
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
            anvil.server.call('update_model_usage', user["user_id"], self.model_id_view)
            save_var('model_id', self.model_id_view)
            self.model_id = self.model_id_view
            save_var('model_id_view', self.model_id_view)
            self.model_id_view = self.model_id_view
    
        # refresh models components
        get_open_form().refresh_models_components()
        get_open_form().refresh_models_underline()
        
        # refresh watchlists components
        watchlist_id = anvil.server.call("get_watchlist_id", user["user_id"])
        anvil.server.call("update_watchlist_usage", user["user_id"], watchlist_id)
        save_var("watchlist_id", watchlist_id)
        get_open_form().refresh_watchlists_components()
        get_open_form().refresh_watchlists_underline()

        # refresh visibility
        get_open_form().change_nav_visibility(status=True)
            
        # check & routing
        if status == 'Congratulations, your Model was successfully created!':
          click_button(f'model_setup?model_id={self.model_id_view}&section=Reference_Artists', event_args)
        
    # Reference_Artists
    elif self.section == 'Reference_Artists':
      artist_id = anvil.server.call('get_next_artist_id', self.model_id_view)
      if artist_id is not None:
        click_button(f'model_setup?model_id={self.model_id_view}&section=Level_of_Pop', event_args)
      else:
        alert(title='Not enough References', content="Please add additional Reference Artists!")

    # Level_of_Pop
    elif self.section == "Level_of_Pop":
      # save popularity min and max
      anvil.server.call('update_model_popularity_range',
                        int(self.model_id_view),
                        load_var('min_pop'),
                        load_var('max_pop'))
      
      click_button(f'model_setup?model_id={self.model_id_view}&section=Sub_Model_Contribution', event_args)

  def Back_click(self, **event_args):
    if self.section == "Sub_Model_Contribution":
      click_button(f'model_setup?model_id={self.model_id_view}&section=Level_of_Pop', event_args)
    elif self.section == "Level_of_Pop":
      click_button(f'model_setup?model_id={self.model_id_view}&section=Reference_Artists', event_args)
    elif self.section == 'Reference_Artists':
      click_button(f'model_setup?model_id={self.model_id_view}&section=Basics', event_args)

  def Discovering_click(self, **event_args):  
    # end ramp-up
    anvil.server.call('update_model_stats',
                      self.model_id_view,
                      self.text_box_model_name.text,
                      self.text_box_description.text,
                      False)

    # load artist
    artist_id = anvil.server.call('get_next_artist_id', load_var('model_id_view'))
    click_button(f'artists?artist_id={artist_id}', event_args)
    
    # add search bar, if missing due to inital model setup
    get_open_form().SearchBar.visible = True

  # ---------------
  # LOAD SECTIONS
  def nav_Basics_load(self, **event_args):
    self.nav_Basics.role = "rampup-labels_focused"
    self.nav_References.role = "rampup-labels"
    self.nav_Level_Pop.role = "rampup-labels"
    self.nav_SubModelContribution.role = "rampup-labels"
    self.sec_Basics.visible = True
    self.sec_Reference_Artists.visible = False
    self.sec_Level_of_Pop.visible = False
    self.sec_SubModelContribution.visible = False

  def nav_References_load(self, **event_args):
    self.nav_Basics.role = "rampup-labels"
    self.nav_References.role = "rampup-labels_focused"
    self.nav_Level_Pop.role = "rampup-labels"
    self.nav_SubModelContribution.role = "rampup-labels"
    self.sec_Basics.visible = False
    self.sec_Reference_Artists.visible = True
    self.sec_Level_of_Pop.visible = False
    self.sec_Reference_Artists.clear()
    self.sec_Reference_Artists_title.visible = True
    self.sec_Reference_Artists.add_component(C_RefArtistsSettings())
    self.sec_SubModelContribution.visible = False

  def nav_Level_Pop_load(self, **event_args):
    self.nav_Basics.role = "rampup-labels"
    self.nav_References.role = "rampup-labels"
    self.nav_Level_Pop.role = "rampup-labels_focused"
    self.nav_SubModelContribution.role = "rampup-labels"
    self.sec_Basics.visible = False
    self.sec_Reference_Artists.visible = False
    self.sec_Level_of_Pop.visible = True
    self.sec_Level_of_Pop.clear()
    self.sec_Level_of_Pop_title.visible = True
    self.sec_pop = self.sec_Level_of_Pop.add_component(C_LevelOfPopularity())
    self.sec_SubModelContribution.visible = False

  def nav_SubModelContribution_load(self, **event_args):
    self.nav_Basics.role = "rampup-labels"
    self.nav_References.role = "rampup-labels"
    self.nav_Level_Pop.role = "rampup-labels"
    self.nav_SubModelContribution.role = "rampup-labels_focused"
    self.sec_Basics.visible = False
    self.sec_Reference_Artists.visible = False
    self.sec_Level_of_Pop.visible = False
    self.sec_SubModelContribution.clear()
    self.sec_SubModelContribution_title.visible = True
    self.sec_SubModelContribution.visible = True
    self.sec_pop = self.sec_SubModelContribution.add_component(C_SubModelContribution())

  # ---------------
  # OTHER FUNCTIONS
  def text_box_model_name_lost_focus(self, **event_args):
    self.text_box_description.focus()

  def text_box_description_pressed_enter(self, **event_args):
    self.Next_click()

  def delete_click(self, ask=True, **event_args):
    result = alert(title='Do you want to delete this model setup?',
          content="Are you sure to delete this model setup?",
          buttons=[
            ("Cancel", "Cancel"),
            ("Delete", "Delete")
          ])
    if result == 'Delete':
      res = anvil.server.call('delete_model', self.model_id_view)
      if res == 'success':
        Notification("",
          title="Model deleted!",
          style="success").show()
        click_button('home', event_args)
        get_open_form().refresh_models_components()
        get_open_form().refresh_models_underline()

  def next_role(self, section='Basics', **event_args):
    if section == 'Basics' and self.text_box_model_name.text != '':
      self.Next.role = ['call-to-action-button','header-5','opacity-100']
    elif section == 'Reference_Artists':
      artist_id = anvil.server.call('get_next_artist_id', self.model_id_view)          
      if artist_id is not None:
        self.Next.role = ['call-to-action-button','header-5','opacity-100']
      else:
        self.Next.role = ['call-to-action-button', 'header-5', 'opacity-25']
    elif section == 'Level_of_Pop':
      # artist_id = anvil.server.call('get_next_artist_id', self.model_id_view)          
      # if artist_id is not None:
      print("THIS ROLE SHOULD BE KICKING IN RN")
      self.Next.role = ['call-to-action-button','header-5','opacity-100']
    else:
      self.Next.role = ['call-to-action-button', 'header-5', 'opacity-25']
