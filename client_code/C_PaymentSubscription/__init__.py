import anvil
from ._anvil_designer import C_PaymentSubscriptionTemplate
from anvil import *
import anvil.server
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.js
import json

from ..C_PaymentCustomer import C_PaymentCustomer
from ..C_PaymentInfos import C_PaymentInfos


class C_PaymentSubscription(C_PaymentSubscriptionTemplate):
  def __init__(self, plan: str = None, no_licenses: int = None, frequency: str = None, trial_end: int = 0, **properties):
    
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()

    # Get subscription email
    base_data = anvil.server.call('get_settings_subscription2', user["user_id"])
    if base_data is not None:
      base_data = json.loads(base_data)[0]
      self.sub_email = base_data['mail'] if 'mail' in base_data else None
    else:
      self.sub_email = user['email']

    self.plan: str = plan
    self.no_licenses: int = no_licenses
    self.frequency: str = frequency
    print('C_PaymentSubscription trial_end:', trial_end)
    self.trial_end: int = trial_end

    # --- 1. GET CUSTOMER INFO ---
    try:
        self.stripe_customer = anvil.server.call('get_stripe_customer_with_tax_info', self.sub_email)
    except Exception as e:
        print("[AIDAR_SUBSCRIPTION_LOG] ERROR calling get_stripe_customer_with_tax_info:", e)
        self.stripe_customer = {}

    self.stripe_customer_id = self.stripe_customer.get('id') if self.stripe_customer else None

    # Fetch and structure company/customer details for summary
    self.company_email = self.stripe_customer.get('email', self.sub_email)
    self.company_name = self.stripe_customer.get('name', '')
    self.company_address = self._format_address(self.stripe_customer.get('address', {}))
    
    address_lines = []
    if self.stripe_customer.get('address', {}):
        line1 = self.stripe_customer.get('address', {}).get('line1', '')
        line2 = self.stripe_customer.get('address', {}).get('line2', '')
        city = self.stripe_customer.get('address', {}).get('city', '')
        state = self.stripe_customer.get('address', {}).get('state', '')
        postal_code = self.stripe_customer.get('address', {}).get('postal_code', '')
        country = self.stripe_customer.get('address', {}).get('country', '')
        if line1:
            address_lines.append(line1)
        if line2:
            address_lines.append(line2)
        if city and postal_code:
            address_lines.append(f"{city}, {postal_code}")
        elif city:
            address_lines.append(city)
        if state:
            address_lines.append(state)
        if country:
            address_lines.append(country)


    # --- 2. GET TAX INFO ---        
    # Direct assignment from response dictionary - SAVE TAX INFO early
    self.tax_country = self.stripe_customer.get('tax_country', '')
    self.tax_id = self.stripe_customer.get('tax_id', '')
    self.tax_id_type = self.stripe_customer.get('tax_id_type', '')
    

    # --- 3. GET PRICE INFO ---
    # Get the Stripe Price ID based on plan type and frequency
    self.price_id = None
    if self.plan == "Explore" and self.frequency == "monthly":
        self.price_id = "price_1RE3tSQTBcqmUQgtoNyD0LgB"
    elif self.plan == "Explore" and self.frequency == "yearly":
        self.price_id = "price_1REVjKQTBcqmUQgt4Z47P00s"
    elif self.plan == "Professional" and self.frequency == "monthly":
        self.price_id = "price_1REVwmQTBcqmUQgtiBBLNZaD"
    elif self.plan == "Professional" and self.frequency == "yearly":
        self.price_id = "price_1REVzZQTBcqmUQgtpyBz8Gky"
    
    # Compute price string based on plan and user count
    self.price = ''
    if self.plan and self.frequency:
        if self.plan == 'Explore' and self.frequency == 'monthly':
            self.price = f'€29.00/mo'
        elif self.plan == 'Explore' and self.frequency == 'yearly':
            self.price = f'€{26 * 12:.2f}/yr ({26:.2f}/mo)'
        elif self.plan == 'Professional' and self.frequency == 'monthly':
            self.price = f'€{44 * (self.no_licenses or 1):.2f}/mo'
        elif self.plan == 'Professional' and self.frequency == 'yearly':
            self.price = f'€{39 * 12 * (self.no_licenses or 1):.2f}/yr ({39 * (self.no_licenses or 1):.2f}/mo/user)'

    if self.frequency == 'yearly':
        self.price_submit = self.price.split(' (')[0]
    else:
        self.price_submit = self.price

    # Get default payment method summary (if any)
    self.payment_method_summary = "No payment method on file."
    self.default_payment_method = None
    if self.stripe_customer_id:
        payment_methods = anvil.server.call('get_stripe_payment_methods', self.stripe_customer_id)
        if payment_methods:
            pm = payment_methods[0]  # Assume first is default for simplicity
            brand = pm.get('card', {}).get('brand', '')
            last4 = pm.get('card', {}).get('last4', '')
            exp_month = pm.get('card', {}).get('exp_month', '')
            exp_year = pm.get('card', {}).get('exp_year', '')
            self.default_payment_method = pm.get('id')
            self.payment_method_summary = f"{brand.title()} **** **** **** {last4} (exp {exp_month}/{exp_year})"

    # Ensure payment_method_summary is always set before HTML rendering
    if not hasattr(self, 'payment_method_summary'):
        self.payment_method_summary = "No payment method on file."

    # --- 4. HTML ---
    self.html = f"""
    <div id='payment-form-container'>
      <h2>Confirm Subscription</h2>
      <div class='payment-info-text'>Please review your subscription details before confirming.</div>
      <form id='subscription-summary-form'>
        <!-- Company Profile Summary -->
        <div class='form-section'>
          <h3 style='display:inline;'>Company Details</h3>
          <!--<span id='edit-company' style='cursor:pointer;margin-left:8px;' title='Edit Company Details'>✏️</span>-->
          <div class='stripe-text'><b>Email:</b> {self.company_email}</div>
          <div class='stripe-text'><b>Name:</b> {self.company_name}</div>
          <div class='stripe-text'><b>Address:</b> {self.company_address}</div>
          <div class='stripe-text'><b>Tax:</b> {self.get_country_name(self.tax_country)} - {self.tax_id}</div>
        </div>
        <!-- Payment Method Summary -->
        <div class='form-section'>
          <h3 style='display:inline;'>Payment Method</h3>
          <!--<span id='edit-payment' style='cursor:pointer;margin-left:8px;' title='Edit Payment Method'>✏️</span>-->
          <div class='stripe-text'>{self.payment_method_summary}</div>
        </div>
        <!-- Plan Summary -->
        <div class='form-section'>
          <h3>Subscription Plan</h3>
          <div class='stripe-text'><b>Plan:</b> {self.plan}</div>
          <div class='stripe-text'><b>User count:</b> {self.no_licenses}</div>
          <div class='stripe-text'><b>Billing period:</b> {self.frequency}</div>
          <div class='stripe-text'><b>Price:</b> {self.price}</div>
        </div>
      </form>
      <div class="button-row">
        <button type="button" id="cancel-btn">Cancel</button>
        <button id="submit" type="submit">{"Start Subscription now" if self.trial_end == 0 else f"Start Subscription in {self.trial_end} days"} ({self.price_submit})</button>
      </div>
      <script>        
        <!--document.getElementById('edit-company').onclick = function() {{ window.edit_company_click && window.edit_company_click(); }};-->
        <!--document.getElementById('edit-payment').onclick = function() {{ window.edit_payment_click && window.edit_payment_click(); }};-->
        document.getElementById('cancel-btn').onclick = function() {{ window.close_alert(); }};
        document.getElementById('submit').onclick = function() {{ window.confirm_subscription_click && window.confirm_subscription_click(); }};
      </script>
    </div>
    """


    # --- 5. REGISTER JS-CALLABLE METHODS ---
    # anvil.js.window.edit_company_click = self._edit_company_click
    # anvil.js.window.edit_payment_click = self._edit_payment_click
    anvil.js.window.confirm_subscription_click = self._confirm_subscription_click
    anvil.js.window.close_alert = self._close_alert
    

  def _close_alert(self):
    """Close the alert dialog from JS."""
    self.raise_event('x-close-alert')


#   def _edit_company_click(self, **event_args):
#       """Opens the C_PaymentCustomer pop-up with prefilled data for editing, including country and tax info."""
#       customer_info = anvil.server.call('get_stripe_customer_with_tax_info', self.company_email)
#       form = C_PaymentCustomer(
#           prefill_email=customer_info.get('email', self.company_email),
#           prefill_company_name=customer_info.get('name', self.company_name),
#           prefill_address=customer_info.get('address', {}),
#           prefill_tax_id=customer_info.get('tax_id', self.tax_id),
#           prefill_tax_country=customer_info.get('tax_country', self.tax_country),
#           prefill_b2b=True
#       )
#       result = alert(
#           content=form,
#           large=False,
#           width=500,
#           buttons=[],
#           dismissible=True
#       )
#       if result == 'success':
#           self._handle_customer_form_result(form)


#   def _edit_payment_click(self, **event_args):
#       """Opens the C_PaymentInfos pop-up to update payment method."""
#       form = C_PaymentInfos()
#       result = alert(
#           content=form,
#           large=False,
#           width=500,
#           buttons=[],
#           dismissible=True
#       )
#       if result == 'success':
#           self.__init__(plan=self.plan, no_licenses=self.no_licenses, frequency=self.frequency)


  def _confirm_subscription_click(self, **event_args):
      """Creates the subscription and redirects."""
      if not self.stripe_customer_id:
        alert('No Stripe customer found. Please add a payment method first.', title='Error')
        return
      if not self.price_id:
        alert('No Stripe price selected. Please select a valid plan.', title='Error')
        return
      try:
        subscription = anvil.server.call('create_stripe_subscription',
          customer_id=self.stripe_customer_id,
          price_id=self.price_id,
          plan_type=self.plan,
          frequency=self.frequency,
          user_count=self.no_licenses,
          trial_end=self.trial_end)
        self.raise_event("x-close-alert", value="success")

        # success alert
        alert_res = alert(
          "We're happy to have you on board - have fun discovering!",
          title="Congratulations!",
          buttons=[("OK", False), ("CREATE AGENT", True)],
          role=["payment-form-container"]
        )
        if alert_res is True:
          # navigate to create agent page
          anvil.js.window.location.replace("/#model_setup?model_id=None&section=Basics")
        else:
          # refresh page to see new subscription
          anvil.js.window.location.replace("/#settings?section=Subscription")
        
      except Exception as e:
        alert(f"Failed to create subscription: {e}", title="Error")


#   def _handle_customer_form_result(self, form):
#     """
#     1. Process the result from the customer form
#     2. Update Stripe customer data
#     3. Refresh display with new information
#     """
#     # Get updated values from the form using a method or attribute that returns the data
#     # Assume form.get_customer_data() returns a dict with the fields: name, email, address, tax_id, tax_id_type
#     if hasattr(form, 'get_customer_data'):
#         data = form.get_customer_data()
#         updated_name = data.get('name')
#         updated_email = data.get('email')
#         updated_address = data.get('address')
#         updated_tax_id = data.get('tax_id')
#         tax_id_type = data.get('tax_id_type')
#     else:
#         # fallback: try to get from public attributes if get_customer_data is not implemented
#         updated_name = getattr(form, 'company_name', None)
#         updated_email = getattr(form, 'company_email', anvil.users.get_user()['email'])
#         updated_address = getattr(form, 'address', {})
#         updated_tax_id = getattr(form, 'tax_id', None)
#         tax_id_type = getattr(form, 'tax_id_type', None)
#     # Update customer info in Stripe
#     anvil.server.call(
#         'update_stripe_customer',
#         self.stripe_customer_id,
#         updated_name,
#         updated_address
#     )
#     # Update tax info if provided
#     if updated_tax_id and tax_id_type:
#         anvil.server.call(
#             'update_stripe_customer_tax_id',
#             self.stripe_customer_id,
#             updated_tax_id,
#             tax_id_type
#         )
#     # Re-fetch customer data and rerender summary by reinitializing
#     self.__init__(plan=self.plan, no_licenses=self.no_licenses, frequency=self.frequency)


  def get_country_name(self, code: str) -> str:
    COUNTRY_CODES = {
    'AU': 'Australia', 'AT': 'Austria', 'BE': 'Belgium', 'BR': 'Brazil', 'BG': 'Bulgaria', 'CA': 'Canada',
    'CN': 'China', 'HR': 'Croatia', 'CY': 'Cyprus', 'CZ': 'Czech Republic', 'DK': 'Denmark', 'EE': 'Estonia',
    'FI': 'Finland', 'FR': 'France', 'DE': 'Germany', 'GR': 'Greece', 'HK': 'Hong Kong', 'HU': 'Hungary',
    'IS': 'Iceland', 'IN': 'India', 'IE': 'Ireland', 'IT': 'Italy', 'JP': 'Japan', 'LI': 'Liechtenstein',
    'LT': 'Lithuania', 'LU': 'Luxembourg', 'LV': 'Latvia', 'MT': 'Malta', 'MX': 'Mexico', 'NL': 'Netherlands',
    'NZ': 'New Zealand', 'NO': 'Norway', 'PL': 'Poland', 'PT': 'Portugal', 'RO': 'Romania', 'SG': 'Singapore',
    'SK': 'Slovakia', 'SI': 'Slovenia', 'ZA': 'South Africa', 'ES': 'Spain', 'SE': 'Sweden', 'CH': 'Switzerland',
    'GB': 'United Kingdom', 'US': 'United States'
    }

    return COUNTRY_CODES.get(code, code or "")


  def _format_address(self, address: dict) -> str:
    """Format address dict as string for display."""
    if not address:
        return ""
    parts = [
        address.get('line1', ''),
        address.get('line2', ''),
        address.get('city', ''),
        address.get('state', ''),
        address.get('postal_code', ''),
        self.get_country_name(address.get('country', ''))
    ]
    return ', '.join([p for p in parts if p])
