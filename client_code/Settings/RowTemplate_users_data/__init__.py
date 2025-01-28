from ._anvil_designer import RowTemplate_users_dataTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

import json

from ...nav import click_link, click_button, save_var, load_var


class RowTemplate_users_data(RowTemplate_users_dataTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    save_var('change_list', [])
    
    # Any code you write here will run before the form opens.
    pass

    
  def button_active_click(self, **event_args):
    # change button text
    if self.button_active.text == 'active':
      self.button_active.text = 'inactive'
    else:
      self.button_active.text = 'active'
    
    # update change_list
    new_list = {'user_id': self.item['user_id'], 'customer_id': self.item['customer_id'], 'active': self.button_active.text, 'admin': self.button_admin.text}
    change_list = load_var('change_list')
    for index, item in enumerate(change_list):
      if item['user_id'] == new_list['user_id']:
        change_list[index] = new_list
        break
    else:
      change_list.append(new_list)
    save_var('change_list', change_list)

    # change button roles
    if self.button_active.role == ['header-7', 'call-to-action-button']:
      self.button_active.role = ['header-7', 'call-to-action-button-disabled']
    else:
      self.button_active.role = ['header-7', 'call-to-action-button']

    # change save button role
    self.parent.parent.parent.parent.parent.parent.roles_save.role = ['header-6', 'call-to-action-button']
    
  def button_admin_click(self, **event_args):
    # change button text
    if self.button_admin.text == 'yes':
      self.button_admin.text = 'no'
    else:
      self.button_admin.text = 'yes'
    
    # update change_list
    new_list = {"user_id": self.item["user_id"], "customer_id": self.item["customer_id"], "active": self.button_active.text, "admin": self.button_admin.text}
    # print("New item:", new_list)
    
    change_list = load_var('change_list')
    # print("Loaded change_list:", change_list)
    # print("Type of change_list:", type(change_list))

    if change_list is None or change_list == '':
      change_list = []
    else:
      change_list = change_list.replace("'", '"')
      change_list = json.loads(change_list)
      # change_list = json.loads(change_list)
    # print(change_list)
    
    for index, item in enumerate(change_list):
      if item['user_id'] == new_list['user_id']:
        change_list[index] = new_list
        break
    else:
      change_list.append(new_list)
        
    save_var('change_list', str(change_list))
    # print("Updated change_list saved:", change_list)
    # print("Updated change_list saved - type:", type(change_list))
    # print("-----------")
    
    # change button roles
    if self.button_admin.role == ['header-7', 'call-to-action-button']:
      self.button_admin.role = ['header-7', 'call-to-action-button-disabled']
    else:
      self.button_admin.role = ['header-7', 'call-to-action-button']
    
    # change save button role
    self.parent.parent.parent.parent.parent.parent.roles_save.role = ['header-6', 'call-to-action-button']
    