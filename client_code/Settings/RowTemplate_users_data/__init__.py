from ._anvil_designer import RowTemplate_users_dataTemplate
from anvil import *
import stripe.checkout
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

    # Access the parent (Settings page) and allocate data
    self.settings_page = self.item.get('settings_page', None)
    self.item = self.item.get('data', None)

    # initiate change_list
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
    new_list = {"user_id": self.item["user_id"], "customer_id": self.item["customer_id"], "active": self.button_active.text, "admin": self.button_admin.text}
    change_list = load_var('change_list')
    
    if change_list is None or change_list == '':
      change_list = []
    else:
      change_list = change_list.replace("'", '"')
      change_list = json.loads(change_list)
    
    for index, item in enumerate(change_list):
      if item['user_id'] == new_list['user_id']:
        change_list[index] = new_list
        break
    else:
      change_list.append(new_list)
        
    save_var('change_list', str(change_list))

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
    change_list = load_var('change_list')
    
    if change_list is None or change_list == '':
      change_list = []
    else:
      change_list = change_list.replace("'", '"')
      change_list = json.loads(change_list)
    
    for index, item in enumerate(change_list):
      if item['user_id'] == new_list['user_id']:
        change_list[index] = new_list
        break
    else:
      change_list.append(new_list)
        
    save_var('change_list', str(change_list))
    
    # change button roles
    if self.button_admin.role == ['header-7', 'call-to-action-button']:
      self.button_admin.role = ['header-7', 'call-to-action-button-disabled']
    else:
      self.button_admin.role = ['header-7', 'call-to-action-button']
    
    # change save button role
    self.parent.parent.parent.parent.parent.parent.roles_save.role = ['header-6', 'call-to-action-button']

  
  def button_delete_click(self, **event_args):    
    res = alert(
      title='Do you want to remove this user from your subscription?',
      content="The user will no longer be able to log in to AIDAR.",
      buttons=[
        ("Cancel", "NO"),
        ("Yes, remove", "YES")
      ],
      role=["forgot-password-success","remove-focus"]
    )
    if res == 'YES':
      # remove user from users_customers
      anvil.server.call('update_settings_delete_user', self.item["user_id"], self.item["customer_id"])
      Notification("", title="User removed!", style="success").show()

      # remove row from table      
      for component in self.parent.get_components():
        if component.item['user_id'] == self.item['user_id']:
          component.remove_from_parent()
      
      # remove from change_list      
      change_list = load_var('change_list')
      
      if change_list is not None and change_list != '':
        change_list = change_list.replace("'", '"')
        change_list = json.loads(change_list)
      
        for index, item in enumerate(change_list):
          if item['user_id'] == self.item['user_id']:
            del change_list[index]
            break
            
        save_var('change_list', str(change_list))

      # refresh summary and filter data if filterd before
      if self.settings_page.search_user_box.text == '':
        self.settings_page.nav_user_click()
      else:
        self.settings_page.nav_user_click()
        self.settings_page.search_user_click()
