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
import datetime
import re

from anvil_extras import routing
from ..nav import click_link, click_button, save_var, load_var

from ..C_ForgotPasswordPopup import C_ForgotPasswordPopup


@routing.route("settings", title="Settings")
class Settings(SettingsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    global user
    user = anvil.users.get_user()

    # Any code you write here will run before the form opens.
    if user is None or user == 'None':
      self.visible = False
      
    elif user['expiration_date'] is not None and (datetime.today().date() - user['expiration_date']).days > 0:
      routing.set_url_hash('no_subs', load_from_cache=False)
      get_open_form().SearchBar.visible = False
      
    else:
      self.nav_account_click()
    

  # -----------------------
  # 1. NAVIGATION ACCOUNT SETTINGS
  def nav_account_click(self, **event_args):
    self.nav_account.role = 'section_buttons_focused'
    self.nav_not.role = 'section_buttons'
    self.nav_user.role = 'section_buttons'
    self.sec_account.visible = True
    self.sec_not.visible = False
    self.sec_user.visible = False

    # reset save button
    self.profile_save.role = ['header-6', 'call-to-action-button-disabled']
    
    # load data
    acc_data = json.loads(anvil.server.call('get_settings_account', user["user_id"]))[0]
    # print(acc_data)

    # hide admin nav
    if acc_data['admin'] is None or acc_data['admin'] is False:
      self.nav_user.visible = False
    
    # a) Profile Management
    self.mail.text = acc_data['mail']
    if acc_data['first_name'] is not None:
      self.text_box_first_name.text = acc_data['first_name']
    else:      
      self.text_box_first_name.text = '-'
    if acc_data['last_name'] is not None:
      self.text_box_last_name.text = acc_data['last_name']
    else:      
      self.text_box_last_name.text = '-'
    
    # b) Subscription Status
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

  
  # -----------------------
  # 2. NAVIGATION NOTIFICATIONS
  def nav_not_click(self, **event_args):
    self.nav_account.role = 'section_buttons'
    self.nav_not.role = 'section_buttons_focused'
    self.nav_user.role = 'section_buttons'
    self.sec_account.visible = False
    self.sec_not.visible = True
    self.sec_user.visible = False

    # reset save button
    self.not_gen_save.role = ['header-6', 'call-to-action-button-disabled']
    self.not_pers_save.role = ['header-6', 'call-to-action-button-disabled']
    
    # load data
    not_data = json.loads(anvil.server.call('get_settings_notifications', user["user_id"]))[0]
    # print(not_data)

    # a) General Notifications
    self.not_general.text = not_data["not_general"]
    self.not_reminder.text = not_data["not_reminder"]
    self.not_newsletter.text = not_data["not_newsletter"]

    self.not_general.role = ['header-7', 'call-to-action-button'] if self.not_general.text == 'active' else ['header-7', 'call-to-action-button-disabled']
    self.not_reminder.role = ['header-7', 'call-to-action-button'] if self.not_reminder.text == 'active' else ['header-7', 'call-to-action-button-disabled']
    self.not_newsletter.role = ['header-7', 'call-to-action-button'] if self.not_newsletter.text == 'active' else ['header-7', 'call-to-action-button-disabled']
    
    # b) Personal Notifications
    self.not_radars.text = not_data["not_radars"]
    self.not_highlights.text = not_data["not_highlights"]
  
    self.not_radars.role = ['header-7', 'call-to-action-button'] if self.not_radars.text == 'active' else ['header-7', 'call-to-action-button-disabled']
    self.not_highlights.role = ['header-7', 'call-to-action-button'] if self.not_highlights.text == 'active' else ['header-7', 'call-to-action-button-disabled']
    

  # -----------------------
  # 3. NAVIGATION USER MANAGEMENT
  def get_data(self, **event_args):
    return anvil.server.call('get_settings_subscription', user["user_id"])
  
  def nav_user_click(self, **event_args):
    self.nav_account.role = 'section_buttons'
    self.nav_not.role = 'section_buttons'
    self.nav_user.role = 'section_buttons_focused'
    self.sec_account.visible = False
    self.sec_not.visible = False
    self.sec_user.visible = True
 
    # load data
    sub_data = self.get_data()
    # print(sub_data)
    
    # Summary
    sum_data = json.loads(sub_data['summary'])[0]
    admin_text = 'admin' if sum_data['admin_count'] == 1 else 'admins'
    self.summary.text = f"{sum_data['active_count']}/{sum_data['no_licenses']} accounts in use - {sum_data['admin_count']} {admin_text}"
    
    # a) User Roles & Permissions
    # center table header
    for component in self.users.get_components()[0].get_components():
      if component.text in ['Status', 'Admin', 'Delete']:
        component.role = ['table_header_center']

    # add data to table
    table_data = json.loads(sub_data['table'])
    table_data = [
      {
        **entry, 
        'active': 'active' if entry['active'] else 'inactive',
        'admin': 'yes' if entry['admin'] else 'no'
      }
      for entry in table_data
    ]
    # print(table_data)

    # self.users_data.items = table_data
    self.users_data.items = [{'data': item, 'settings_page': self} for item in table_data]
    
    # b) User Invite
    inv_data = json.loads(sub_data['invite'])[0]
    self.key.text = inv_data['license_key']
    self.link.text = f"app.aidar.ai/#register?license_key={inv_data['license_key']}"

  
  # ---------------------------------------------------------------------
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
  # no actions available
  
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
      anvil.users.send_password_reset_email(user["email"])
      alert(
        title="Success",
        content="A recovery email has been sent to your email address",
        large=False,
        buttons=[("OK", True)],
        role=["forgot-password-success","remove-focus"]
      )

  
  # -----------------------
  # 2. NOTIFICATIONS
  # a) General Notifications  
  def button_active_gen_click(self, **event_args):
    # change button text    
    if event_args['sender'].text == 'active':
      event_args['sender'].text = 'deactivated'
    else:
      event_args['sender'].text = 'active'
    
    # change button roles
    if event_args['sender'].role == ['header-7', 'call-to-action-button']:
      event_args['sender'].role = ['header-7', 'call-to-action-button-disabled']
    else:
      event_args['sender'].role = ['header-7', 'call-to-action-button']

    # change save button role
    self.not_gen_save.role = ['header-6', 'call-to-action-button']

  def not_gen_save_click(self, **event_args):
    if self.not_gen_save.role == ['header-6', 'call-to-action-button']:
      status = anvil.server.call('update_settings_notifications_gen',
                                user["user_id"],
                                self.not_general.text,
                                self.not_reminder.text,
                                self.not_newsletter.text
                                )
      
      if status == 'success':
        Notification("", title="Changes saved!", style="success").show()
        self.not_gen_save.role = ['header-6', 'call-to-action-button-disabled']
      else:
        Notification("", title="Error! Sorry, something went wrong..", style="warning").show()

  # b) Personal Notifications  
  def button_active_pers_click(self, element=None, **event_args):
    # copy the event_args['sender'] if added specifically
    if element is not None:
      event_args['sender'] = element
    
    # change button text    
    if event_args['sender'].text == 'active':
      event_args['sender'].text = 'deactivated'
    else:
      event_args['sender'].text = 'active'
    
    # change button roles
    if event_args['sender'].role == ['header-7', 'call-to-action-button']:
      event_args['sender'].role = ['header-7', 'call-to-action-button-disabled']
    else:
      event_args['sender'].role = ['header-7', 'call-to-action-button']

    # change save button role
    self.not_pers_save.role = ['header-6', 'call-to-action-button']
  
  # specific function for not_radars, to ensure users really want to deactivate all personal artist radars 
  def button_active_pers_click_radar(self, **event_args):
    nots = json.loads(anvil.server.call("get_notifications", user["user_id"], 'mail'))
    
    if self.not_radars.text == 'deactivated' or len(nots) == 0:
      self.button_active_pers_click(element=event_args['sender'])
    else:
      result = alert(
        title="All personal Artist Radars will be deactivated",
        content="Are you sure to deactivate all your personal Artist Radars?\n\nYou will no longer get individual notifications based on your personal AI-Agent directly into your inbox.",
        buttons=[("Cancel", "No"), ("Yes, deactivate", "Yes")],
      )
      if result == "Yes":
        for noti in nots:
          anvil.server.call(
            "update_notification",
            notification_id=noti["notification_id"],
            type=noti["type"],
            name=noti["name"],
            active=False,
            freq_1=noti["freq_1"],
            freq_2=noti["freq_2"],
            freq_3=noti["freq_3"],
            metric=noti["metric"],
            no_artists=noti["no_artists"],
            repetition_1=noti["repetition_1"],
            repetition_2=noti["repetition_2"],
            rated=noti["rated"],
            watchlist=noti["watchlist"],
            release_days=noti["release_days"],
            min_grow_fit=noti["min_grow_fit"],
            model_ids=noti["model_ids"],
            song_selection_1=noti["song_selection_1"],
            song_selection_2=noti["song_selection_2"],
          )
        self.button_active_pers_click(element=event_args['sender'])
        Notification("", title="All Artist Radars deactivated!", style="success").show()
        self.not_pers_save_click()  
  
  def not_pers_save_click(self, **event_args):
    if self.not_pers_save.role == ['header-6', 'call-to-action-button']:
      status = anvil.server.call('update_settings_notifications_pers',
                                user["user_id"],
                                self.not_radars.text,
                                self.not_highlights.text
                                )
      
      if status == 'success':
        Notification("", title="Changes saved!", style="success").show()
        self.not_pers_save.role = ['header-6', 'call-to-action-button-disabled']
      else:
        Notification("", title="Error! Sorry, something went wrong..", style="warning").show()

  
  # -----------------------
  # 3. USER MANAGEMENT
  # a) User Roles & Permissions
  def search_user_click(self, **event_args):
    sub_data = self.get_data()    
    table_data = json.loads(sub_data['table'])
    table_data = [
      {
        **entry, 
        'active': 'active' if entry['active'] else 'inactive',
        'admin': 'yes' if entry['admin'] else 'no'
      }
      for entry in table_data
    ]    
    # self.users_data.items = [entry for entry in table_data if str(entry["name"]).lower().find(str(self.search_user_box.text).lower()) != -1]
    self.users_data.items = [
      {'data': entry, 'settings_page': self}
      for entry in table_data
      if str(entry["name"]).lower().find(str(self.search_user_box.text).lower()) != -1
    ]

  def roles_save_click(self, **event_args):
    if self.roles_save.role == ['header-6', 'call-to-action-button']:
      change_list = json.loads(load_var('change_list').replace("'", '"'))
      anvil.server.call('update_settings_user_role', change_list)
      
      if self.search_user_box.text == '':
        self.nav_user_click()
      else:
        self.nav_user_click()
        self.search_user_click()
      self.roles_save.role = ['header-6', 'call-to-action-button-disabled']
      Notification("", title="Changes saved!", style="success").show()
  
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
    
  def mail_enters_change(self, **event_args):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    mails = [item.strip() for item in re.split(r'[;\n]', self.mail_enters.text) if item.strip()]

    error = False
    for mail in mails:
      if re.match(email_regex, mail) is None:
        error = True

    if error is True or self.mail_enters.text == '':
      self.sent_invite.role = ['pos-abs-bottom', 'header-6', 'call-to-action-button-disabled']
    else:      
      self.sent_invite.role = ['pos-abs-bottom', 'header-6', 'call-to-action-button']

  def sent_invite_click(self, **event_args):
    if self.sent_invite.role == ['pos-abs-bottom', 'header-6', 'call-to-action-button']:
      mails = [item.strip() for item in re.split(r'[;\n]', self.mail_enters.text) if item.strip()]

      anvil.server.call('sent_mail_invite', user["user_id"], mails)
      Notification("", title=f"{len(mails)} new user/s invited!", style="success").show()
      
      self.mail_enters.text = ''
      self.sent_invite.role = ['pos-abs-bottom', 'header-6', 'call-to-action-button-disabled']
      self.nav_user_click()


