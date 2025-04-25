from ._anvil_designer import C_PaymentSubscriptionTemplate
from anvil import *
import anvil.server
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class C_PaymentSubscription(C_PaymentSubscriptionTemplate):
  def __init__(self, plan_type: str = None, user_count: int = None, billing_period: str = None, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Store passed arguments for use in the form
    self.plan_type: str = plan_type
    self.user_count: int = user_count
    self.billing_period: str = billing_period

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    
    # Display the selected plan details for debugging/demo
    self.html = f"""
    <div id='payment-form-container'>
      <h2>Subscription Details</h2>
      <div class='payment-info-text'>Please review your subscription details before proceeding.</div>
      <form id='subscription-summary-form'>
        <div class='form-section'>
          <h3>Plan</h3>
          <div class='field-row'>{self.plan_type}</div>
        </div>
        <div class='form-section'>
          <h3>User count</h3>
          <div class='field-row'>{self.user_count}</div>
        </div>
        <div class='form-section'>
          <h3>Billing period</h3>
          <div class='field-row'>{self.billing_period}</div>
        </div>
      </form>
    </div>
    """
