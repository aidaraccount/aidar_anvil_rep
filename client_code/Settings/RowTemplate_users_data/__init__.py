from ._anvil_designer import RowTemplate_users_dataTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class RowTemplate_users_data(RowTemplate_users_dataTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    pass

    
  def button_active_click(self, **event_args):
    if self.button_active.role == ['header-7', 'call-to-action-button']:
      self.button_active.role = ['header-7', 'call-to-action-button-disabled']
    else:
      self.button_active.role = ['header-7', 'call-to-action-button']
          
    if self.button_active.text == 'active':
      self.button_active.text = 'inactive'
    else:
      self.button_active.text = 'active'

    self.parent.parent.parent.parent.parent.parent.roles_save.role = ['header-6', 'call-to-action-button']
    
  def button_admin_click(self, **event_args):
    if self.button_admin.role == ['header-7', 'call-to-action-button']:
      self.button_admin.role = ['header-7', 'call-to-action-button-disabled']
    else:
      self.button_admin.role = ['header-7', 'call-to-action-button']
    
    if self.button_admin.text == 'yes':
      self.button_admin.text = 'no'
    else:
      self.button_admin.text = 'yes'
      
    self.parent.parent.parent.parent.parent.parent.roles_save.role = ['header-6', 'call-to-action-button']
    