from ._anvil_designer import Notifications_RowTemplateTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json
from datetime import datetime
from anvil.js.window import observeFitLikelihoodCircle

from anvil_extras import routing
from ...nav import click_link, click_button, logout, login_check, load_var


class Notifications_RowTemplate(Notifications_RowTemplateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    if self.item["type"] == 'mail':
      # visibility
      self.p_name.visible = False
      self.m_name.visible = True

      # content
      self.m_name.text = self.item["name"]

    elif self.item["type"] == 'playlist':
      # visibility
      self.p_name.visible = True
      self.m_name.visible = False

      # content
      self.p_name.text = self.item["name"]
