from ._anvil_designer import Main_OutTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import datetime
import re
from ..Main_In import Main_In
from ..Imprint import Imprint


class Main_Out(Main_OutTemplate):
  def __init__(self, **properties):    
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    check_log_status(self)

  
  def link_login_click(self, **event_args):
    anvil.users.login_with_form(allow_cancel=True, remember_by_default=True)
    print(f"{datetime.datetime.now()}: Main_Out - link_login_click - 1", flush=True)
    check_log_status(self)
    print(f"{datetime.datetime.now()}: Main_Out - link_login_click - 2", flush=True)
    user = anvil.users.get_user()
    print(f"{datetime.datetime.now()}: Main_Out - link_login_click - 3", flush=True)
    if user is not None:
      try:
        anvil.server.call("server_transfer_user_id")
        print(f"{datetime.datetime.now()}: Main_Out - link_login_click - 4", flush=True)
        user = anvil.users.get_user()
        print(f"{datetime.datetime.now()}: Main_Out - link_login_click - 5", flush=True)
        open_form(
          "Main_In",
          model_id=None,
          temp_artist_id=None,
          target=None,
          user_id=user["user_id"],
          value=None,
        )
        print(f"{datetime.datetime.now()}: Main_Out - link_login_click - 6", flush=True)
      except:
        pass
        #alert(
        #  title="Unveiling New Features!",
        #  content="Apologies for any inconvenience caused.\n\nWe are presently integrating new features and will have the site accessible again shortly.\n\nFeel free to contact us via email at info@aidar.ai.\n\nThank you,\nYour AIDAR Team",
        #)

  def button_login_click(self, **event_args):
    try:
      user = anvil.users.login_with_email(self.login_email.text,self.login_pw.text)
      print(f"User: {user}")
      check_log_status(self)
      user = anvil.users.get_user()
      if user is not None:
        try:
          anvil.server.call("server_transfer_user_id")
          user = anvil.users.get_user()
          open_form(
            "Main_In",
            model_id=None,
            temp_artist_id=None,
            target=None,
            user_id=user["user_id"],
            value=None,
          )
        except:
          pass
          #alert(
          #  title="Unveiling New Features!",
          #  content="Apologies for any inconvenience caused.\n\nWe are presently integrating new features and will have the site accessible again shortly.\n\nFeel free to contact us via email at info@aidar.ai.\n\nThank you,\nYour AIDAR Team",
          #)
    except:
      print("ERROR!!")
      Notification("",
        title="Authentification failed!",
        style="danger").show()
  
  def link_logout_click(self, **event_args):
    anvil.users.logout()
    check_log_status(self)

  def button_signup_click(self, **event_args):
    anvil.users.signup_with_form(allow_cancel=True)

  def link_home_click(self, **event_args):
    user = anvil.users.get_user()
    if user is not None:
      anvil.server.call("check_user_presence", mail=user["email"])
      open_form(
        "Main_In", model_id=None, temp_artist_id=None, target=None, user_id=user["user_id"], value=None
      )

  def linkedin_click(self, **event_args):
    self.linkedin_link.url = "https://www.linkedin.com/company/aidar-insights/"

  def instagram_click(self, **event_args):
    self.instagram_link.url = "https://www.instagram.com/aidar_insights/"

  def call2action_text_box_click(self, **event_args):
    ## 1. Option: add_waiter by Anvil and Anvils Waiters table
    try:
      if re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", self.call2action_text_box.text):
        app_tables.waiters.add_row(
          Date=datetime.datetime.now(), Mail=self.call2action_text_box.text
        )
        self.call2action_text_box.text = ""
        self.label_c2a_header.visible = False
        self.column_panel_call2action.visible = False
        self.label_confirmation.visible = True
        alert(
          title="Thanks for joining our Waiting List!",
          content="We appreciate your interest in our service and will get back to you as soon as we have the capacity available.\n\nBest regards\nYour AIDAR Team",
        )
      else:
        alert(
          title="No valid Email..",
          content="The Email you entered is not a valid Email - please retry or send us a message to info@aidar.ai\n\nThank you,\nYour AIDAR Team",
        )
    except:
      alert(
        title="Error..",
        content="Apologies for the inconvenience caused.\n\nIf the error persists, kindly reach out to us via email at info@aidar.ai.\n\nThank you,\nYour AIDAR Team",
      )

  def imprint_link_click(self, **event_args):
    open_form("Imprint")

  def image_partner3_mouse_enter(self, x, y, **event_args):
    self.image_partner3.source = "_/theme/pics/Partner3_original.png"

  def image_partner3_mouse_leave(self, x, y, **event_args):
    self.image_partner3.source = "_/theme/pics/Partner3_grey.png"


def check_log_status(self, **event_args):
  if anvil.users.get_user() is None:
    self.link_login.visible = True
    # self.link_register.visible = True
    self.link_logout.visible = False
    self.link_home.visible = False
  else:
    self.link_login.visible = False
    # self.link_register.visible = False
    self.link_logout.visible = True
    self.link_home.visible = True
  if self.updates_sign.visible is True:
    self.link_login.visible = False
    self.link_register.visible = False
    self.link_logout.visible = False
    self.link_home.visible = False
