from ._anvil_designer import C_SubModelContributionTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json

import plotly.graph_objects as go

from ..nav import click_link, click_button, logout, save_var, load_var


class C_SubModelContribution(C_SubModelContributionTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.model_id_view = load_var("model_id_view")
    
    infos = json.loads(anvil.server.call("get_model_stats", self.model_id_view))[0]
    self.slider_1.value = infos['model_1_cont'] * 100
    self.slider_2.value = infos['model_4_cont'] * 100
    self.slider_3.value = infos['model_3_cont'] * 100

    save_var('artist_career_fit', self.slider_1.value)
    save_var('musical_fit', self.slider_2.value)
    save_var('growth_imp_fit', self.slider_3.value)

  
  def slider_1_change(self, **event_args):
    save_var('artist_career_fit', self.slider_1.value)

  def slider_2_change(self, **event_args):
    save_var('musical_fit', self.slider_2.value)
    
  def slider_3_change(self, **event_args):
    save_var('growth_imp_fit', self.slider_3.value)

  
  def slider_1_button_reset_click(self, **event_args):
    self.slider_1.reset()
    save_var('artist_career_fit', self.slider_1.value)
  
  def slider_2_button_reset_click(self, **event_args):
    self.slider_2.reset()
    save_var('musical_fit', self.slider_2.value)
    
  def slider_3_button_reset_click(self, **event_args):
    self.slider_3.reset()
    save_var('growth_imp_fit', self.slider_3.value)
