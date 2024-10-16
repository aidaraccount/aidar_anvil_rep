from ._anvil_designer import C_GrowthImportanceTemplate
from ..C_RefPopupTable import C_RefPopupTable
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json

import plotly.graph_objects as go

from ..nav import click_link, click_button, logout, save_var, load_var


class C_GrowthImportance(C_GrowthImportanceTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.model_id_view = load_var("model_id_view")

    # Need to replace "min_pop" with the field that Janek provides in the get_model_stats
    # then need to replicate for slider for Musical Fit importance and Growth Importance
    
    infos = json.loads(anvil.server.call("get_model_stats", self.model_id_view))[0]
    print(infos)
    if infos["min_pop"] is None:
      save_var("min_pop", 1)
    else:
      self.slider_1.values = infos["min_pop"]
      save_var("min_pop", infos["min_pop"])

  def slider_1_change(self, handle, **event_args):
    save_var("min_pop", self.slider_1.formatted_values[0])
  
  # def set_slider_text_boxes(self):
  #   self.text_box_left.text, self.text_box_right.text = self.slider_1.formatted_values

  # def slider_1_slide(self, handle, **event_args):
  #   self.set_slider_text_boxes()
  
  # def slider_1_textbox_enter(self, **event_args):
  #   self.slider_1.values = self.text_box_left.text, self.text_box_right.text
  #   self.set_slider_text_boxes()

  def slider_1_button_reset_click(self, **event_args):
    self.slider_1.reset()
    save_var("min_pop", 20)
    save_var("max_pop", 50)
    # self.set_slider_text_boxes()
