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
    
    # Get the Stripe Price ID based on plan type and billing period
    self.price_id = None
    if self.plan_type == "Explore" and self.billing_period == "monthly":
        self.price_id = "price_1RE3tSQTBcqmUQgtoNyD0LgB"
    elif self.plan_type == "Explore" and self.billing_period == "yearly":
        self.price_id = "price_1REVjKQTBcqmUQgt4Z47P00s"
    elif self.plan_type == "Professional" and self.billing_period == "monthly":
        self.price_id = "price_1REVwmQTBcqmUQgtiBBLNZaD"
    elif self.plan_type == "Professional" and self.billing_period == "yearly":
        self.price_id = "price_1REVzZQTBcqmUQgtpyBz8Gky"

    # 1. Get Stripe customer by email
    self.customer = anvil.server.call('get_stripe_customer', user['email']) if user and user.get('email') else None
    self.customer_id = self.customer.get('id') if self.customer else None

    # 2. Get default payment method summary (if any)
    self.payment_method_summary = "No payment method on file."
    self.default_payment_method = None
    if self.customer_id:
        payment_methods = anvil.server.call('get_stripe_payment_methods', self.customer_id)
        if payment_methods:
            pm = payment_methods[0]  # Assume first is default for simplicity
            brand = pm.get('card', {}).get('brand', '')
            last4 = pm.get('card', {}).get('last4', '')
            exp_month = pm.get('card', {}).get('exp_month', '')
            exp_year = pm.get('card', {}).get('exp_year', '')
            self.default_payment_method = pm.get('id')
            self.payment_method_summary = f"{brand.title()} **** **** **** {last4} (exp {exp_month}/{exp_year})"

    # 3. Display the selected plan and payment details
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
        <div class='form-section'>
          <h3>Default payment method</h3>
          <div class='field-row'>{self.payment_method_summary}</div>
        </div>
      </form>
      <button id='confirm-subscription-btn' class='cta-button cta-primary' style='width:100%;margin-top:16px;'>Confirm Subscription</button>
    </div>
    <script>
      document.getElementById('confirm-subscription-btn').onclick = function() {{ anvil.call(this, 'confirm_subscription_click'); }};
    </script>
    """

  # 4. Button handler for subscription confirmation
  def confirm_subscription_click(self, **event_args):
    if not self.customer_id:
      alert('No Stripe customer found. Please add a payment method first.', title='Error')
      return
    if not self.price_id:
      alert('No Stripe price selected. Please select a valid plan.', title='Error')
      return
    try:
      subscription = anvil.server.call('create_stripe_subscription', self.customer_id, self.price_id)
      alert(f"Subscription created! Status: {subscription.get('status')}", title="Success")
    except Exception as e:
      alert(f"Failed to create subscription: {e}", title="Error")
