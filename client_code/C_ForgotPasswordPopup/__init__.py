from ._anvil_designer import C_ForgotPasswordPopupTemplate
from anvil import *
import stripe.checkout
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class C_ForgotPasswordPopup(C_ForgotPasswordPopupTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

  def submit_button_click(self, **event_args):
    """This method is called when the submit button is clicked"""    
    email = self.email_field.text  # Get the email from the input field
    if email:
      # Call the server function to check if the user exists
      user_exists = anvil.server.call('check_user_exists', email)
      
      if user_exists:
        # Use the built-in function to send the password reset email
        anvil.users.send_password_reset_email(email)
        alert(
          "A recovery email has been sent to the provided email address",
          title="Success",
          large=False,
          buttons=[("OK", True)],
          role=["forgot-password-success","remove-focus"]
        )
        self.remove_from_parent()  # Close the popup after sending
      else:
        alert(
          "Please enter a valid email address.",
          title="User not found.",
          large=False,
          buttons=[("Go Back", True)],
          role=["forgot-password-success","remove-focus"]
        )
    else:
      alert(
          "Please enter a valid email address.",
          title="User not found",
          large=False,
          buttons=[("Go Back", True)],
          role=["forgot-password-success","remove-focus"]
        )

  def email_field_pressed_enter(self, **event_args):
    """This method is called when the user presses Enter in this text box"""
    pass
