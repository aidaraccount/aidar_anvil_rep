from ._anvil_designer import SettingsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import random
import string
from anvil.js.window import navigator
import json

from anvil_extras import routing
from ..nav import click_link, click_button, save_var

from ..C_ForgotPasswordPopup import C_ForgotPasswordPopup


@routing.route("settings", title="Settings")
class Settings(SettingsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()

    self.nav_account_click()
    

  # -----------------------
  # NAVIGATION
  def nav_account_click(self, **event_args):
    self.nav_account.role = 'section_buttons_focused'
    self.nav_user.role = 'section_buttons'
    self.sec_account.visible = True
    self.sec_user.visible = False

    # reset save button
    self.profile_save.role = ['header-6', 'call-to-action-button-disabled']
    
    # load data
    acc_data = json.loads(anvil.server.call('get_settings_account', user["user_id"]))[0]
    print(acc_data)

    # hide admin nav
    if acc_data['admin'] is None or acc_data['admin'] is False:
      self.nav_user.visible = False
    
    # Profile Management
    self.mail.text = acc_data['mail']
    if acc_data['first_name'] is not None:
      self.text_box_first_name.text = acc_data['first_name']
    else:      
      self.text_box_first_name.text = '-'
    if acc_data['last_name'] is not None:
      self.text_box_last_name.text = acc_data['last_name']
    else:      
      self.text_box_last_name.text = '-'
    # Subscription Status
    if acc_data['name'] is not None:
      self.orga.text = acc_data['name']
    else:      
      self.orga.text = 'ADIAR Test Account'
    if acc_data['active'] is not None:
      if acc_data['active'] is True:
        self.user.text = 'active'
      else:
        self.user.text = 'inactive'
    else:
      self.user.text = 'limited access'
    if acc_data['admin'] is not None and acc_data['admin'] is True:
      self.admin.text = 'yes'
    else:
        self.admin.text = 'no'
    
    
  def nav_user_click(self, **event_args):
    self.nav_account.role = 'section_buttons'
    self.nav_user.role = 'section_buttons_focused'
    self.sec_account.visible = False
    self.sec_user.visible = True

    # load data
    sub_data = anvil.server.call('get_settings_subscription', user["user_id"])
    # print(sub_data)

    # User Roles & Permissions
    sum_data = json.loads(sub_data['summary'])[0]
    self.summary.text = f"{sum_data['active_count']}/{sum_data['no_licenses']} account/s in use - {sum_data['admin_count']} admin/s"

    table_data = json.loads(sub_data['table'])[0]
    
    # User Invite
    inv_data = json.loads(sub_data['invite'])[0]
    self.key.text = inv_data['license_key']
    self.link.text = f"app.aidar.ai/#register?license_key={inv_data['license_key']}"

    
  # -----------------------
  # 1. ACCOUNT SETTINGS
  # a) Profile Management
  def text_box_first_name_change(self, **event_args):
    self.profile_save.role = ['header-6', 'call-to-action-button']

  def text_box_last_name_change(self, **event_args):
    self.profile_save.role = ['header-6', 'call-to-action-button']

  def profile_save_click(self, **event_args):
    if self.profile_save.role == ['header-6', 'call-to-action-button']:
      status = anvil.server.call('update_settings_account',
                                user["user_id"],
                                self.text_box_first_name.text,
                                self.text_box_last_name.text
                                )
  
      if status == 'success':
        Notification("", title="Changes saved!", style="success").show()
        anvil.js.get_dom_node(self.text_box_last_name).blur()
        anvil.js.get_dom_node(self.text_box_first_name).blur()
        self.profile_save.role = ['header-6', 'call-to-action-button-disabled']
      else:
        Notification("", title="Error! Sorry, something went wrong..", style="warning").show()
    
  
  # b) Subscription Status

  
  # c) Password
  def reset_pw_click(self, **event_args):
    res = alert(
      title='Do you want to reset your password?',
      content="Are you sure to reset your password?",
      buttons=[
        ("Cancel", "NO"),
        ("Yes, reset password", "YES")
      ],
      role=["forgot-password-success","remove-focus"]
    )
    if res == 'YES':
      anvil.users.send_password_reset_email('janek-meyn@web.de')  # ATTENTION !!!
      alert(
        title="Success",
        content="A recovery email has been sent to your email address",
        large=False,
        buttons=[("OK", True)],
        role=["forgot-password-success","remove-focus"]
      )

  
  # -----------------------
  # 2. USER MANAGEMENT
  # a) User Roles & Permissions

  
  # b) User Invite
  def refresh_key_click(self, **event_args):
    res = alert(
      title='Do you want to reset your company license key?',
      content="All pending invitations are no longer able to register.",
      buttons=[
        ("Cancel", "NO"),
        ("Yes, reset key", "YES")
      ],
      role=["forgot-password-success","remove-focus"]
    )
    if res == 'YES':
      new_key = anvil.server.call('update_settings_license_key', user["user_id"])
      alert(
        title="Your new Company License Key is...",
        content=f'New Key: {new_key}',
        large=False,
        buttons=[("OK", True)],
        role=["forgot-password-success","remove-focus"]
      )
    self.nav_user_click()
    
  def copy_click(self, **event_args):
    navigator.clipboard.writeText(f'https://{self.link.text}')
    Notification("", title="Link copied!", style="success").show()

