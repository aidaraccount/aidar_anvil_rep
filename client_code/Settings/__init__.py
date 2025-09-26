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
from ..C_SubscriptionPlan import C_SubscriptionPlan


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
      
    else:
      # Initialize customer_info as a class attribute
      base_data = anvil.server.call('get_settings_subscription', user["user_id"])
      if base_data is not None:
        base_data = json.loads(base_data)[0]
      
        self.sub_email = base_data['mail'] if 'mail' in base_data else None
  
        if self.sub_email is not None:
          self.customer_info = anvil.server.call('get_stripe_customer_with_tax_info', self.sub_email)
        else:
          self.customer_info = None
      
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
    
      
  # -----------------------
  # 0. UTILITY FUNCTIONS
  def _set_nav_section(self, section: str):
    """
    Sets navigation button styles and section visibility based on the selected section.
    Handles redirection to Account section if Payment or UserManagement are selected but no customer exists.
    
    Args:
        section: One of 'account', 'not', 'sub', 'user', 'pay'
    """
    # # Check if customer exists for sections that require it
    # if (section in ['pay', 'user']) and ((not hasattr(self, 'customer_info') or not self.customer_info or not self.customer_info.get('id')) or user['admin'] is not True):
    #   print(f"[SETTINGS] No customer info/ admin found, redirecting from {section} to account")
    #   section = 'account'
    
    # Hide Subscription when not beeing an admin
    if user['admin'] is not True:
      self.nav_sub.visible = False

    # Hide Billing when there is no Customer yet OR its not an admin OR plan is Contract
    if user['customer_id'] is None or user['admin'] is not True or user['plan'] == 'Contract':
      self.nav_pay.visible = False

    # Hide User Management when there not Professional/Contract OR its not an admin
    if user['plan'] not in ['Professional', 'Contract'] or user['admin'] is not True:  
      self.nav_user.visible = False

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
  # 1. INIT - NAVIGATION ACCOUNT SETTINGS
  def nav_account_click(self, **event_args):
    self._set_nav_section('account')
    
    # reset save button
    self.profile_save.role = ['header-6', 'call-to-action-button-disabled']
    
    # load data
    # present in user
    
    # a) Profile Management
    self.mail.text = user['email']
    if user['first_name'] is not None:
      self.text_box_first_name.text = user['first_name']
    else:      
      self.text_box_first_name.text = '-'
    if user['last_name'] is not None:
      self.text_box_last_name.text = user['last_name']
    else:      
      self.text_box_last_name.text = '-'

    # b) Time Zone - Load countries and set up timezone selection
    acc_data = json.loads(anvil.server.call('get_settings_account', user["user_id"]))[0]
    user_timezone = acc_data["timezone"]
    
    # Load all countries
    countries = anvil.server.call('get_countries')
    self.country_drop_down.items = [(country['name'], country['code']) for country in countries]
    
    # Find and set user's country based on timezone
    if user_timezone:
      user_country = anvil.server.call('get_country_for_timezone', user_timezone)
      if user_country:
        self.country_drop_down.selected_value = user_country
        # Load timezones for the user's country
        timezones = anvil.server.call('get_timezones_for_country', user_country)
        self.time_zone_drop_down.items = [(tz['display_name'], tz['timezone']) for tz in timezones]
        self.time_zone_drop_down.selected_value = user_timezone
        self.time_zone_drop_down.visible = True
      else:
        # If country not found (e.g., UTC), show UTC option and leave country unselected
        self.time_zone_drop_down.items = [('UTC (Coordinated Universal Time)', 'UTC')]
        self.time_zone_drop_down.selected_value = 'UTC'
        self.time_zone_drop_down.visible = True
        # Leave country_drop_down with placeholder showing
        self.country_drop_down.selected_value = None
    else:
      # Hide timezone dropdown until country is selected
      self.time_zone_drop_down.visible = False
  
  # -----------------------
  # 2. INIT - NAVIGATION NOTIFICATIONS
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
    self.not_agents.text = not_data["not_agents"]
    self.slider_agents.value = not_data["not_agents_freq"]
    self.not_watchlist.text = not_data["not_watchlist"]
    self.slider_wl.value = not_data["not_watchlist_freq"]
    self.not_highlights.text = not_data["not_highlights"]
  
    self.not_agents.role = ['header-7', 'call-to-action-button'] if self.not_agents.text == 'active' else ['header-7', 'call-to-action-button-disabled']
    self.not_watchlist.role = ['header-7', 'call-to-action-button'] if self.not_watchlist.text == 'active' else ['header-7', 'call-to-action-button-disabled']
    self.not_highlights.role = ['header-7', 'call-to-action-button'] if self.not_highlights.text == 'active' else ['header-7', 'call-to-action-button-disabled']
    

  # -----------------------
  # 3. INIT - NAVIGATION SUBSCRIPTION
  def nav_sub_click(self, **event_args):
    self._set_nav_section('sub')
    
    # a) Subscription Status
    if user["expiration_date"] is not None and user["expiration_date"] < date.today():
      # I. no subscription
      print("I. no subscription!")
      
      # a) subscription
      self.type.text = 'No valid subscription'
      
      self.label_end.visible = False
      self.end.visible = False
      self.label_orga.visible = False
      self.orga.visible = False
      self.label_user.visible = False
      self.user.visible = False
      self.label_admin.visible = False
      self.admin.visible = False

      # b) plan
      self.plan_header.text = 'Activate Subscription Plan'
      self.plan_desc.text = 'Subscribe now and start discovering right away!'
      self.sub_plan.clear()
      self.sub_plan.add_component(C_SubscriptionPlan(plan=None, no_licenses=None, frequency=None, expiration_date=user["expiration_date"]))

    
    elif user["plan"] in ['Trial', 'Extended Trial'] and (user["expiration_date"] is None or user["expiration_date"] >= date.today()):
      # II. active test user:
      print(f"II. active test user - {user['plan']}!")

      # a) subscription
      if user["plan"] == 'Extended Trial':
        self.type.text = 'Extended Free Trial'
      else:
        self.type.text = 'Free Trial'
      if user["expiration_date"] is None:
        self.end.text = 'unlimited'
      else:
        days = (user["expiration_date"] - date.today()).days
        days_left = f"{days} day left" if days == 1 else f"{days} days left"
        self.end.text = f"{user['expiration_date'].strftime('%b %d, %Y')} ({days_left})"

      self.label_orga.visible = False
      self.orga.visible = False
      self.label_user.visible = False
      self.user.visible = False
      self.label_admin.visible = False
      self.admin.visible = False

      # b) plan
      self.plan_header.text = 'Activate Subscription Plan'
      self.plan_desc.text = 'Subscribe now and your subscription will start after your free trial ends.'
      self.sub_plan.clear()
      self.sub_plan.add_component(C_SubscriptionPlan(plan=user["plan"], no_licenses=None, frequency=None, expiration_date=user["expiration_date"]))

    
    elif user["plan"] in ['Explore', 'Professional'] and (user["expiration_date"] is None or user["expiration_date"] >= date.today()):
      # III. subscribed customer:
      print(f"III. subscribed customer! - {user['plan']}")

      # a) subscription
      self.type.text = 'Paid Subscription'
      if user["expiration_date"] is None:
        self.label_end.visible = False
        self.end.visible = False
      else:
        days = (user["expiration_date"] - date.today()).days
        days_left = f"{days} day left" if days == 1 else f"{days} days left"
        self.end.text = f"{user['expiration_date'].strftime('%b %d, %Y')} ({days_left})"
      
      self.orga.text = user['customer_name']
      if user['active'] is True:
        self.user.text = 'active'
      else:
        self.user.text = 'inactive'
      if user['admin'] is not None and user['admin'] is True:
        self.admin.text = 'yes'
      else:
        self.admin.text = 'no'

      # b) plan
      # load data
      sub_data = json.loads(anvil.server.call('get_settings_subscription', user["user_id"]))[0]
      no_licenses = sub_data['no_licenses'] if 'no_licenses' in sub_data else None
      frequency = sub_data['frequency'] if 'frequency' in sub_data else None
      if 'expiration_date' in sub_data and sub_data['expiration_date'] is not None:
        expiration_date = date.fromtimestamp(sub_data['expiration_date']/1000)
      else:
        expiration_date = None
      
      # add component
      self.sub_plan.clear()
      self.sub_plan.add_component(C_SubscriptionPlan(plan=user["plan"], no_licenses=no_licenses, frequency=frequency, expiration_date=expiration_date))


    elif user["plan"] in ['Contract'] and (user["expiration_date"] is None or user["expiration_date"] >= date.today()):
      # IV. ccontract customer:
      print(f"IV. contract customer! - {user['plan']}")

      # a) subscription
      self.type.text = 'Indiv. Contract'
      if user["expiration_date"] is None:
        self.label_end.visible = False
        self.end.visible = False
      else:
        days = (user["expiration_date"] - date.today()).days
        days_left = f"{days} day left" if days == 1 else f"{days} days left"
        self.end.text = f"{user['expiration_date'].strftime('%b %d, %Y')} ({days_left})"

      self.orga.text = user['customer_name']
      if user['active'] is True:
        self.user.text = 'active'
      else:
        self.user.text = 'inactive'
      if user['admin'] is not None and user['admin'] is True:
        self.admin.text = 'yes'
      else:
        self.admin.text = 'no'

      # b) plan
      self.plan_desc.text = 'To manage your individual contract, pleace get in touch with us directly or send an email to team@aidar.ai'

    
  # -----------------------
  # 4. INIT - NAVIGATION USER MANAGEMENT
  def nav_user_click(self, **event_args):
    self._set_nav_section('user')
 
    # 1. Load server data
    summary_data = json.loads(anvil.server.call('get_settings_user_mgmt', user["customer_id"]))[0]
    license_key = summary_data['license_key'] if 'license_key' in summary_data else None
    no_licenses = summary_data['no_licenses'] if 'no_licenses' in summary_data else None
    
    # 2. Get user data from the Users table
    user_data = anvil.server.call('get_anvil_users', user['customer_id'])
    
    # 3. Summary - calculate user statistics
    if user_data:
      active_users = sum(1 for u in user_data if u['active'])
      admin_count = sum(1 for u in user_data if u['admin'])
      admin_text = 'admin' if admin_count == 1 else 'admins'
      self.summary.text = f"{active_users}/{no_licenses} accounts in use - {admin_count} {admin_text}"
      
    # 4. User Roles & Permissions
    # Center table header
    for component in self.users.get_components()[0].get_components():
      if component.text in ['Status', 'Admin', 'Delete']:
        component.role = ['table_header_center']

    # 5. Format user data for the table - simplified as server now returns pre-formatted data
    table_data = []
    for u in user_data:
      # Just format the display values that need to be shown as text
      user_dict = dict(u)  # Make a copy of the user data
      user_dict['active'] = 'active' if u['active'] else 'inactive'
      user_dict['admin'] = 'yes' if u['admin'] else 'no'
      table_data.append(user_dict)
    
    self.users_data.items = [{'data': item, 'settings_page': self} for item in table_data]
    
    # 6. User Invite
    self.key.text = license_key
    self.link.text = f"app.aidar.ai/#register?license_key={license_key}"
  

  # -----------------------
  # 5. INIT - PAYMENT
  def nav_pay_click(self, **event_args):
    self._set_nav_section('pay')
    
    # a) Company Profile
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
    
    else:
      print(f"[STRIPE] No Stripe customer found for email={self.sub_email}")
      self.pay_profile_email.text = self.sub_email
      self.pay_profile_name.text = "No customer information"
      self.pay_profile_address.text = "No address information"
      self.pay_profile_tax.text = "No tax information"

    # b) Payment Details
    if self.customer_info and self.customer_info.get('id'):
      payment_methods = anvil.server.call('get_stripe_payment_methods', self.customer_info['id'])
      
      if payment_methods and len(payment_methods) > 0:
        # Show payment info
        self.no_payment.visible = False
        self.yes_payment.visible = True

        # Get first payment method
        pm = payment_methods[0]
        print(f"[STRIPE] Payment method: id={pm.get('id')}, type={pm.get('type')}, brand={pm.get('card', {}).get('brand')}, last4={pm.get('card', {}).get('last4')}")
    
        # Set contact info (email) and card info
        self.pay_contact.text = pm.get('billing_details', {}).get('name', '')
        brand = pm.get('card', {}).get('brand', '')
        last4 = pm.get('card', {}).get('last4', '')
        exp_month = pm.get('card', {}).get('exp_month', '')
        exp_year = pm.get('card', {}).get('exp_year', '')
        self.pay_card.text = f"{brand.title()} **** **** **** {last4} (exp {exp_month}/{exp_year})"
      else:
        # No payment method on file
        self.no_payment.visible = True
        self.yes_payment.visible = False
        self.pay_contact.text = ''
        self.pay_card.text = ''
    else:
      self.no_payment.visible = True
      self.yes_payment.visible = False
      self.pay_contact.text = ''
      self.pay_card.text = ''
  

  # ---------------------------------------------------------------------
  # 1. ACTIONS - ACCOUNT SETTINGS
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

  # b) Country and Time Zone
  def country_drop_down_change(self, **event_args):
    """When country is selected, load its timezones"""
    country_code = self.country_drop_down.selected_value
    if country_code:
      # Load timezones for selected country
      timezones = anvil.server.call('get_timezones_for_country', country_code)
      self.time_zone_drop_down.items = [(tz['display_name'], tz['timezone']) for tz in timezones]
      self.time_zone_drop_down.visible = True
      # Auto-select first timezone to avoid invalid value
      if timezones:
        self.time_zone_drop_down.selected_value = timezones[0]['timezone']
      # Enable save button
      self.time_zone_save.role = ['header-6', 'call-to-action-button']
    else:
      # Hide timezone dropdown if no country selected
      self.time_zone_drop_down.visible = False

  def time_zone_drop_down_change(self, **event_args):
    self.time_zone_save.role = ['header-6', 'call-to-action-button']

  def time_zone_save_click(self, **event_args):
    if self.time_zone_save.role == ['header-6', 'call-to-action-button']:
      # 1. Update user in backend database with IANA timezone
      backend_status = anvil.server.call('update_settings_account_time_zone',
                                         user["user_id"],
                                         self.time_zone_drop_down.selected_value)

      if backend_status == 'success':
        Notification("", title="Changes saved!", style="success").show()
        self.time_zone_save.role = ['header-6', 'call-to-action-button-disabled']
      else:
        Notification("", title="Error! Sorry, something went wrong..", style="warning").show()
  
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
  # 2. ACTIONS - NOTIFICATIONS
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
  
  # specific function for not_agents, to ensure users really want to deactivate all personal artist radars
  def button_active_pers_click_radar(self, **event_args):
    nots = json.loads(anvil.server.call("get_notifications", user["user_id"], 'mail'))
    
    if self.not_agents.text == 'deactivated' or len(nots) == 0:
      self.button_active_pers_click(element=event_args['sender'])
    else:
      result = alert(
        title="All personal Agent Notifications will be deactivated",
        content="Are you sure to deactivate all your personal Agent Notifications?\n\nYou will no longer get individual notifications based on your personal AI-Agent directly into your inbox.",
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
        Notification("", title="All Agent Notifications deactivated!", style="success").show()
        self.not_pers_save_click()  
  
  def not_pers_save_click(self, **event_args):
    if self.not_pers_save.role == ['header-6', 'call-to-action-button']:
      status = anvil.server.call('update_settings_notifications_pers',
                                user["user_id"],
                                self.not_agents.text,
                                self.slider_agents.value,
                                self.not_watchlist.text,
                                self.slider_wl.value,
                                self.not_highlights.text
                                )
      
      if status == 'success':
        Notification("", title="Changes saved!", style="success").show()
        self.not_pers_save.role = ['header-6', 'call-to-action-button-disabled']
      else:
        Notification("", title="Error! Sorry, something went wrong..", style="warning").show()


  # -----------------------
  # 3. ACTIONS - SUBSCRIPTION
  # a) Subscription Status
  # no actions available

  
  # -----------------------
  # 4. ACTIONS - USER MANAGEMENT
  # a) User Roles & Permissions
  def search_user_click(self, **event_args):
    # 1. Get user data from the Users table
    user_data = anvil.server.call('get_anvil_users', user['customer_id'])
    
    # 2. Format user data for the table - simplified as server now returns pre-formatted data
    table_data = []
    for u in user_data:
      # Just format the display values that need to be shown as text
      user_dict = dict(u)  # Make a copy of the user data
      user_dict['active'] = 'active' if u['active'] else 'inactive'
      user_dict['admin'] = 'yes' if u['admin'] else 'no'
      table_data.append(user_dict)
    
    # 3. Filter by search term and update table
    self.users_data.items = [
      {'data': entry, 'settings_page': self}
      for entry in table_data
      if str(entry["name"]).lower().find(str(self.search_user_box.text).lower()) != -1
    ]

  def roles_save_click(self, **event_args):
    if self.roles_save.role == ['header-6', 'call-to-action-button']:
      change_list = json.loads(load_var('change_list').replace("'", '"'))
      print('change_list:', change_list)
      
      # update user roles
      anvil.server.call('update_user_role', change_list)

      # reload
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
  # 5. ACTIONS - PAYMENT
  # a) Payment Details
  def add_payment_details_click(self, **event_args):
    details = alert(
      content=C_PaymentInfos(),
      large=False,
      width=500,
      buttons=[],
      dismissible=True
    )
    # refresh page to see new subscription
    anvil.js.window.location.replace("/#settings?section=Payment")


  def change_payment_details_click(self, **event_args):
    # add new payment method
    result = alert(
      content=C_PaymentInfos(),
      large=False,
      width=500,
      buttons=[],
      dismissible=True
    )

    # on success reload payment details
    if result == 'success':
      anvil.js.window.location.replace("/#settings?section=Payment")

  
  def change_customer_click(self, **event_args):
    """
    Opens the C_PaymentCustomer pop-up to edit customer profile information.
    Saves new payment method if successful and removes old ones.
    """
    # Use the centrally stored customer_info instead of making a new call
    form = C_PaymentCustomer(
        prefill_email=self.customer_info.get('email', ''),
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
      anvil.js.window.location.replace("/#settings?section=Payment")

  
  def sliders_slide(self, handle, **event_args):
    # change save button role
    self.not_pers_save.role = ['header-6', 'call-to-action-button']
