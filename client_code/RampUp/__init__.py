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
from ..C_CreateModel import C_CreateModel

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

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()

    # initial visibile settings
    self.nav_Basics.role = "section_buttons_focused"
    self.sec_Reference_Artists.visible = False
    self.sec_Level_of_Pop.visible = False

    # ---------------
    # HEADER LEFT
    # model name and description text and text boxes

    # secction routing
    if section == "Basics":
      self.nav_Basics_click()
    elif section == "Reference_Artists":
      self.nav_References_click()
    elif section == "Level_of_Pop":
      self.nav_Level_Pop_click()

  def nav_Basics_click(self, **event_args):
    self.nav_Basics.role = "section_buttons_focused"
    self.nav_References.role = "section_buttons"
    self.nav_Level_Pop.role = "section_buttons"
    
    self.sec_Basics.visible = True
    self.sec_Reference_Artists.visible = False
    self.sec_Level_of_Pop.visible = False

    self.sec_Basics.clear()
    self.sec_Basics.add_component(C_CreateModel())

  def nav_References_click(self, **event_args):
    self.nav_Basics.role = "section_buttons"
    self.nav_References.role = "section_buttons_focused"
    self.nav_Level_Pop.role = "section_buttons"
    
    self.sec_Basics.visible = False
    self.sec_Reference_Artists.visible = True
    self.sec_Level_of_Pop.visible = False

    self.sec_Reference_Artists.clear()
    self.sec_Reference_Artists.add_component(C_RefArtistsSettings(model_id=2))

  def nav_Level_Pop_click(self, **event_args):
    self.nav_Basics.role = "section_buttons"
    self.nav_References.role = "section_buttons"
    self.nav_Level_Pop.role = "section_buttons_focused"
    
    self.sec_Basics.visible = False
    self.sec_Reference_Artists.visible = False
    self.sec_Level_of_Pop.visible = True

    self.sec_Level_of_Pop.clear()
    # self.sec_Reference_Artists.add_component(C_RefArtistsSettings(self.model_id_view))


