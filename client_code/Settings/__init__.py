from ._anvil_designer import SettingsTemplate
from anvil import *
import stripe.checkout
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import random
import string
from anvil.js.window import navigator
import json
from datetime import datetime, date
import re

from anvil_extras import routing
from ..nav import click_link, click_button, save_var, load_var

from ..C_ForgotPasswordPopup import C_ForgotPasswordPopup
from ..C_PaymentInfos import C_PaymentInfos
from ..C_PaymentCustomer import C_PaymentCustomer


@routing.route("settings", url_keys=['section'], title="Settings")
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
      # section routing
      section = self.url_dict['section']
      
      if section == 'Account':
        self.nav_account_click()
      elif section == 'Notifications':
        self.nav_not_click()
      elif section == 'Subscription':
        self.nav_sub_click()
      elif section == 'UserManagement':
        self.nav_user_click()
      elif section == 'Payment':
        self.nav_pay_click()

      # Initialize customer_info as a class attribute
      self.customer_info = anvil.server.call('get_stripe_customer_with_tax_info', user['email'])

    
      
  # -----------------------
  # 0. UTILITY FUNCTIONS
  def _set_nav_section(self, section: str):
    """
    Sets navigation button styles and section visibility based on the selected section.
    Handles redirection to Account section if Payment or UserManagement are selected but no customer exists.
    
    Args:
        section: One of 'account', 'not', 'sub', 'user', 'pay'
    """
    # Check if customer exists for sections that require it
    if (section in ['pay', 'user']) and (not hasattr(self, 'customer_info') or not self.customer_info or not self.customer_info.get('id')):
      print(f"[SETTINGS] No customer info found, redirecting from {section} to account")
      section = 'account'
    
    # Reset all navigation buttons to default style
    self.nav_account.role = 'section_buttons'
    self.nav_not.role = 'section_buttons'
    self.nav_sub.role = 'section_buttons'
    self.nav_user.role = 'section_buttons'
    self.nav_pay.role = 'section_buttons'
    
    # Set the selected button to focused
    if section == 'account':
      self.nav_account.role = 'section_buttons_focused'
    elif section == 'not':
      self.nav_not.role = 'section_buttons_focused'
    elif section == 'sub':
      self.nav_sub.role = 'section_buttons_focused'
    elif section == 'user':
      self.nav_user.role = 'section_buttons_focused'
    elif section == 'pay':
      self.nav_pay.role = 'section_buttons_focused'
    
    # Hide all sections first
    self.sec_account.visible = False
    self.sec_not.visible = False
    self.sec_sub.visible = False
    self.sec_user.visible = False
    self.sec_pay.visible = False
    
    # Show only the selected section
    if section == 'account':
      self.sec_account.visible = True
    elif section == 'not':
      self.sec_not.visible = True
    elif section == 'sub':
      self.sec_sub.visible = True
    elif section == 'user':
      self.sec_user.visible = True
    elif section == 'pay':
      self.sec_pay.visible = True

  # -----------------------
  # 1. NAVIGATION ACCOUNT SETTINGS
  def nav_account_click(self, **event_args):
    self._set_nav_section('account')
    
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
    
  
  # -----------------------
  # 2. NAVIGATION NOTIFICATIONS
  def nav_not_click(self, **event_args):
    self._set_nav_section('not')

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
  def nav_sub_click(self, **event_args):
    self._set_nav_section('sub')
    
    # load data
    sub_data = anvil.server.call('get_settings_subscription', user["user_id"])
    print(sub_data)
    
    # a) Subscription Status
    if user["expiration_date"] is not None and user["expiration_date"] < date.today():
      # I. no subscription
      print("User has no subscription!")
      if sub_data is not None:
        print("But had a former subscription!")

      else:
        print("And never had a subscription!")

    
    elif sub_data is None and (user["expiration_date"] is None or user["expiration_date"] >= date.today()) and user["extended_trial"] is not True:
      # II. active test user:
      print("User is testing!")

      # a) subscription
      self.type.text = 'Free Trial'
      if user["expiration_date"] is None:
        self.end.text = 'unlimited'
      else:
        days = (user["expiration_date"] - date.today()).days
        days_left = f"{days} day left" if days == 1 else f"{days} days left"
        self.end.text = f"{user['expiration_date'].strftime('%b %d, %Y')} ({days_left})"
        
      self.orga.text = ''
      self.user.text = ''
      self.admin.text = ''

      # b) plan
      self.plan_header.text = 'Activate Subscription Plan'
      self.plan_desc.text = 'Subscribe now and your subscription will start after your free trial ends.'

    
    elif sub_data is None and (user["expiration_date"] is None or user["expiration_date"] >= date.today()) and user["extended_trial"] is True:
      # III. active extended test user:
      print("User is extended testing!")

    
    elif sub_data is not None and (user["expiration_date"] is None or user["expiration_date"] >= date.today()):
      # IV. subscribed customer:
      print("User is a subscribed customer!")
      sub_data = json.loads(sub_data)[0]
      
      self.orga.text = sub_data['name']
      if sub_data['active'] is True:
        self.user.text = 'active'
      else:
        self.user.text = 'inactive'
      if sub_data['admin'] is not None and sub_data['admin'] is True:
        self.admin.text = 'yes'
      else:
          self.admin.text = 'no'

      
    # b) Payment
    # MANUAL STRIPE INTEGRATION
    pass
    
    # # ANVIL STRIPE INTEGRATION
    # # 1st Try
        
    # # c = stripe.checkout.charge(
    # #   amount=99,  # in cents
    # #   currency="EUR",
    # #   title="Direct Payment",  # of the popup
    # #   description="First test")  # of the popup
    # # print(c)

    
    # # 2nd Try
    # # store token/ credit card information
    # token, info = stripe.checkout.get_token(amount=100, currency="EUR")
    # print(token)
    # print(info)
    # print(info['email'])

    # anvil.server.call('create_stripe_customer', token, info['email'])

    
  
  # -----------------------
  # 4. NAVIGATION USER MANAGEMENT
  def get_data(self, **event_args):
    return anvil.server.call('get_settings_user_mgmt', user["user_id"])
  
  def nav_user_click(self, **event_args):
    self._set_nav_section('user')
 
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

  # -----------------------
  # 5. PAYMENT
  def nav_pay_click(self, **event_args):
    self._set_nav_section('pay')
    
    # load data
    if self.customer_info and self.customer_info.get('id'):
        # Display customer information
        self.pay_profile_email.text = self.customer_info.get('email', '')
        self.pay_profile_name.text = self.customer_info.get('name', '')
        
        # Format address
        address = self.customer_info.get('address', {})
        address_parts = []
        if address.get('line1'):
            address_parts.append(address.get('line1', ''))
        if address.get('line2'):
            address_parts.append(address.get('line2', ''))
        if address.get('city'):
            address_parts.append(address.get('city', ''))
        if address.get('postal_code'):
            address_parts.append(address.get('postal_code', ''))
        if address.get('country'):
            country_code = address.get('country', '')
            country_name = country_code  # Default to code if no mapping exists
            # If you have country code mapping in this class, use it here
            address_parts.append(country_name)
            
        self.pay_profile_address.text = ', '.join(filter(None, address_parts))
        
        # Display tax information
        tax_id = self.customer_info.get('tax_id', '')
        tax_country = self.customer_info.get('tax_country', '')
        tax_id_type = self.customer_info.get('tax_id_type', '')
        
        if tax_id and tax_country:
            self.pay_profile_tax.text = f"{tax_country} - {tax_id} ({tax_id_type})"
        else:
            self.pay_profile_tax.text = "No tax information"
            
        # Get and display payment methods
        payment_methods = anvil.server.call('get_stripe_payment_methods', self.customer_info['id'])
        print(f"[STRIPE] Found {len(payment_methods)} payment methods for customer {self.customer_info['id']}")
        for pm in payment_methods:
            print(f"[STRIPE] Payment method: id={pm.get('id')}, type={pm.get('type')}, brand={pm.get('card', {}).get('brand')}, last4={pm.get('card', {}).get('last4')}")
    else:
        print(f"[STRIPE] No Stripe customer found for email={user['email']}")
        self.pay_profile_email.text = user['email']
        self.pay_profile_name.text = "No customer information"
        self.pay_profile_address.text = "No address information"
        self.pay_profile_tax.text = "No tax information"
  

  # ---------------------------------------------------------------------
  # 1. ACCOUNT SETTINGS
  # a) Profile Management
  def text_box_first_name_change(self, **event_args):
    self.profile_save.role = ['header-6', 'call-to-action-button']

  def text_box_last_name_change(self, **event_args):
    self.profile_save.role = ['header-6', 'call-to-action-button']

  def profile_save_click(self, **event_args):
    if self.profile_save.role == ['header-6', 'call-to-action-button']:
      
      # 1. Update user in Anvil Users table
      anvil_status = anvil.server.call('update_anvil_user',
                                      user["user_id"],
                                      self.text_box_first_name.text,
                                      self.text_box_last_name.text)
      
      # 2. Update user in backend database
      backend_status = anvil.server.call('update_settings_account',
                                        user["user_id"],
                                        self.text_box_first_name.text,
                                        self.text_box_last_name.text)
  
      if anvil_status == 'success' and backend_status == 'success':
        Notification("", title="Changes saved!", style="success").show()
        anvil.js.get_dom_node(self.text_box_last_name).blur()
        anvil.js.get_dom_node(self.text_box_first_name).blur()
        self.profile_save.role = ['header-6', 'call-to-action-button-disabled']
      else:
        Notification("", title="Error! Sorry, something went wrong..", style="warning").show()
  
  # b) Password
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
  # 3. SUBSCRIPTION
  # a) Subscription Status
  # no actions available

  
  # -----------------------
  # 4. USER MANAGEMENT
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

  # -----------------------
  # 5. PAYMENT
  # a) Payment Details
  def add_payment_details_click(self, **event_args):
    details = alert(
      content=C_PaymentInfos(),
      large=False,
      width=500,
      buttons=[],
      dismissible=True
    )
    print(details)
    

  def change_pay_profile_click(self, **event_args):
    """
    Opens the C_PaymentCustomer pop-up to edit customer profile information.
    Saves new payment method if successful and removes old ones.
    """
    # Use the centrally stored customer_info instead of making a new call
    form = C_PaymentCustomer(
        prefill_email=self.customer_info.get('email', user['email']),
        prefill_company_name=self.customer_info.get('name', ''),
        prefill_address=self.customer_info.get('address', {}),
        prefill_tax_id=self.customer_info.get('tax_id', ''),
        prefill_tax_country=self.customer_info.get('tax_country', ''),
        prefill_b2b=True
    )
    
    result = alert(
        content=form,
        large=False,
        width=500,
        buttons=[],
        dismissible=True
    )
    
    if result == 'success':
        # Refresh the payment profile section
        self.nav_pay_click()
