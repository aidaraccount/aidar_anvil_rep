from ._anvil_designer import C_ForgotPasswordPopupTemplate
from anvil import *
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
      try:
        # Use the built-in function to send the password reset email
        anvil.users.send_password_reset_email(email)
        alert("A password reset email has been sent to " + email + ".")
        self.remove_from_parent()  # Close the popup after sending
        print("THE RESET EMAIL HAS BEEN SENT")
      except anvil.users.UserNotFound:
        alert("User not found. Please check the email address.")
    else:
      alert("Please enter an email address.")