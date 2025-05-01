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

from ..C_PaymentCustomer import C_PaymentCustomer
from ..C_PaymentInfos import C_PaymentInfos


class C_PaymentSubscription(C_PaymentSubscriptionTemplate):
  # 0. Country code to name mapping and helper
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
  @classmethod
  def get_country_name(cls, code: str) -> str:
      return cls.COUNTRY_CODES.get(code, code or "")

  def __init__(self, plan_type: str = None, user_count: int = None, billing_period: str = None, **properties):
    # [AIDAR_SUBSCRIPTION_LOG] --- Start Subscription Form Init ---
    print("[AIDAR_SUBSCRIPTION_LOG] __init__ called. plan_type=", plan_type, "user_count=", user_count, "billing_period=", billing_period)
    
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Store passed arguments for use in the form
    self.plan_type: str = plan_type
    self.user_count: int = user_count
    self.billing_period: str = billing_period

    # Any code you write here will run before the form opens.
    global user
    try:
        user = anvil.users.get_user()
        print("[AIDAR_SUBSCRIPTION_LOG] user:", user)
    except Exception as e:
        print("[AIDAR_SUBSCRIPTION_LOG] ERROR getting user:", e)
        user = None

    # --- TAX INFO GATHERING LOGS ---
    print("[AIDAR_SUBSCRIPTION_LOG] Fetching tax info for email:", user['email'] if user else None)
    try:
        customer_info = anvil.server.call('get_stripe_customer_with_tax_info', user['email'] if user else None)
        print("[AIDAR_SUBSCRIPTION_LOG] customer_info from get_stripe_customer_with_tax_info:", customer_info)
        
        # Direct assignment from response dictionary - SAVE TAX INFO early
        self.tax_country = customer_info.get('tax_country', '')
        self.tax_id = customer_info.get('tax_id', '')
        self.tax_id_type = customer_info.get('tax_id_type', '')
        
        # Fallback for tax data in tax_ids array if direct keys are empty
        if not self.tax_country or not self.tax_id:
            tax_ids = customer_info.get('tax_ids', {}).get('data', [])
            print("[AIDAR_SUBSCRIPTION_LOG] Fallback to tax_ids array:", tax_ids)
            if tax_ids and len(tax_ids) > 0:
                first_tax = tax_ids[0]
                if not self.tax_country:
                    self.tax_country = first_tax.get('country', '')
                if not self.tax_id:
                    self.tax_id = first_tax.get('value', '')
                if not self.tax_id_type:
                    self.tax_id_type = first_tax.get('type', '')
        
        print("[AIDAR_SUBSCRIPTION_LOG] After fallback - self.tax_country:", self.tax_country)
        print("[AIDAR_SUBSCRIPTION_LOG] After fallback - self.tax_id:", self.tax_id)
        print("[AIDAR_SUBSCRIPTION_LOG] After fallback - self.tax_id_type:", self.tax_id_type)
        
    except Exception as e:
        print("[AIDAR_SUBSCRIPTION_LOG] ERROR calling get_stripe_customer_with_tax_info:", e)
        customer_info = {}
    
    # IMPORTANT: Use direct assignments from customer_info, not reset
    if not hasattr(self, 'tax_country') or not self.tax_country:
        self.tax_country = customer_info.get('tax_country', '')
    if not hasattr(self, 'tax_id') or not self.tax_id:
        self.tax_id = customer_info.get('tax_id', '')
    if not hasattr(self, 'tax_id_type') or not self.tax_id_type:
        self.tax_id_type = customer_info.get('tax_id_type', '')
        
    # CRITICAL: Force from customer_info data - as fallback method
    if 'tax_country' in customer_info and not self.tax_country:
        self.tax_country = customer_info['tax_country']
    if 'tax_id' in customer_info and not self.tax_id:
        self.tax_id = customer_info['tax_id']
        
    print("[AIDAR_SUBSCRIPTION_LOG] FINAL TAX DATA: country=", self.tax_country, "id=", self.tax_id, "type=", self.tax_id_type)
    
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
    print('price_id:', self.price_id)
    
    # Compute price string based on plan and user count
    self.price = ''
    if self.plan_type and self.billing_period:
        if self.plan_type == 'Explore' and self.billing_period == 'monthly':
            self.price = f'€29.00/mo'
        elif self.plan_type == 'Explore' and self.billing_period == 'yearly':
            self.price = f'€{26 * 12:.2f}/yr ({26:.2f}/mo)'
        elif self.plan_type == 'Professional' and self.billing_period == 'monthly':
            self.price = f'€{44 * (self.user_count or 1):.2f}/mo'
        elif self.plan_type == 'Professional' and self.billing_period == 'yearly':
            self.price = f'€{39 * 12 * (self.user_count or 1):.2f}/yr ({39 * (self.user_count or 1):.2f}/mo/user)'

    # 1. Get Stripe customer by email
    self.customer = anvil.server.call('get_stripe_customer', user['email'])
    print('customer:', self.customer)
    self.customer_id = self.customer.get('id') if self.customer else None
    print('customer_id:', self.customer_id)
    
    # Convert LiveObjectProxy to dict if needed
    if hasattr(self.customer, 'items'):
        self.customer = dict(self.customer)

    # Fetch and structure company/customer details for summary
    self.company_email = customer_info.get('email', user['email'] if user else '')
    self.company_name = customer_info.get('name', '')
    self.company_address = self._format_address(customer_info.get('address', {}))
    print("[AIDAR_SUBSCRIPTION_LOG] self.company_email:", self.company_email)
    print("[AIDAR_SUBSCRIPTION_LOG] self.company_name:", self.company_name)
    print("[AIDAR_SUBSCRIPTION_LOG] self.company_address:", self.company_address)
    
    address_lines = []
    if self.customer.get('address', {}):
        line1 = self.customer.get('address', {}).get('line1', '')
        line2 = self.customer.get('address', {}).get('line2', '')
        city = self.customer.get('address', {}).get('city', '')
        state = self.customer.get('address', {}).get('state', '')
        postal_code = self.customer.get('address', {}).get('postal_code', '')
        country = self.customer.get('address', {}).get('country', '')
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
    address_formatted = ", ".join([line for line in address_lines if line])

    # Get default payment method summary (if any)
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

    # Ensure payment_method_summary is always set before HTML rendering
    if not hasattr(self, 'payment_method_summary'):
        self.payment_method_summary = "No payment method on file."

    # [AIDAR_SUBSCRIPTION_LOG] --- DEBUG: Print all key variables before rendering HTML ---
    print("[AIDAR_SUBSCRIPTION_LOG] DEBUG: self.tax_country=", repr(self.tax_country), "self.tax_id=", repr(self.tax_id), "self.tax_id_type=", repr(self.tax_id_type))
    print("[AIDAR_SUBSCRIPTION_LOG] DEBUG: customer_info=", repr(customer_info))
    print("[AIDAR_SUBSCRIPTION_LOG] DEBUG: user=", repr(user))
    print("[AIDAR_SUBSCRIPTION_LOG] DEBUG: self.company_email=", repr(self.company_email), "self.company_name=", repr(self.company_name), "self.company_address=", repr(self.company_address))
    print("[AIDAR_SUBSCRIPTION_LOG] DEBUG: About to render HTML with above values.")

    # Define instance methods
    self._edit_company_click = self.__class__._edit_company_click.__get__(self)
    self._edit_payment_click = self.__class__._edit_payment_click.__get__(self)
    self._cancel_btn_click = self.__class__._cancel_btn_click.__get__(self)
    self._confirm_subscription_click = self.__class__._confirm_subscription_click.__get__(self)

    # Register JS-callable methods
    anvil.js.window.edit_company_click = self._edit_company_click
    anvil.js.window.edit_payment_click = self._edit_payment_click
    anvil.js.window.cancel_btn_click = self._cancel_btn_click
    anvil.js.window.confirm_subscription_click = self._confirm_subscription_click

    # Instance methods for Python compatibility
    self.edit_company_click = self._edit_company_click
    self.edit_payment_click = self._edit_payment_click
    self.cancel_btn_click = self._cancel_btn_click
    self.confirm_subscription_click = self._confirm_subscription_click

    # --- CANCEL BUTTON LOGS ---
    print("[AIDAR_SUBSCRIPTION_LOG] Registering JS cancel_btn_click handler...")
    anvil.js.window.cancel_btn_click = self._cancel_btn_click
    print("[AIDAR_SUBSCRIPTION_LOG] Registered JS cancel_btn_click handler:", anvil.js.window.cancel_btn_click)

    # --- TAX INFO LOG: Show in summary HTML ---
    print("[AIDAR_SUBSCRIPTION_LOG] Rendering tax info in HTML. self.tax_country=", self.tax_country, "self.tax_id=", self.tax_id, "self.tax_id_type=", self.tax_id_type)
    self.html = f"""
    <div id='payment-form-container'>
      <h2>Confirm Subscription</h2>
      <div class='payment-info-text'>Please review your subscription details before confirming.</div>
      <form id='subscription-summary-form'>
        <!-- Company Profile Summary -->
        <div class='form-section'>
          <h3 style='display:inline;'>Company Details</h3>
          <span id='edit-company' style='cursor:pointer;margin-left:8px;' title='Edit Company Details'>✏️</span>
          <div class='stripe-text'><b>Email:</b> {self.company_email}</div>
          <div class='stripe-text'><b>Name:</b> {self.company_name}</div>
          <div class='stripe-text'><b>Address:</b> {self.company_address}</div>
          <div class='stripe-text'><b>Tax Country:</b> {self.get_country_name(self.tax_country)}</div>
          <div class='stripe-text'><b>Tax ID:</b> {self.tax_id}</div>
          <div class='stripe-text'><b>Tax ID Type:</b> {self.tax_id_type}</div>
        </div>
        <!-- Payment Method Summary -->
        <div class='form-section'>
          <h3 style='display:inline;'>Payment Method</h3>
          <span id='edit-payment' style='cursor:pointer;margin-left:8px;' title='Edit Payment Method'>✏️</span>
          <div class='stripe-text'>{self.payment_method_summary}</div>
        </div>
        <!-- Plan Summary -->
        <div class='form-section'>
          <h3>Subscription Plan</h3>
          <div class='stripe-text'><b>Plan:</b> {self.plan_type}</div>
          <div class='stripe-text'><b>User count:</b> {self.user_count}</div>
          <div class='field-row'><b>Billing period:</b> {self.billing_period}</div>
          <div class='field-row'><b>Price:</b> {self.price}</div>
        </div>
      </form>
      <div class="button-row">
        <button type="button" id="cancel-btn">Cancel</button>
        <button id="submit" type="submit">Book Subscription now ({self.price})</button>
      </div>
      <script>
        console.log('[AIDAR_SUBSCRIPTION_LOG] Setting up cancel button JS handler');
        
        // Direct method to properly close the modal from JS
        window.cancel_btn_click = function() {{
            console.log('[AIDAR_SUBSCRIPTION_LOG] JS window.cancel_btn_click fired');
            try {{
                console.log('[AIDAR_SUBSCRIPTION_LOG] Trying to close dialog');
                // This works in Anvil to close an alert - call the x-close-alert event directly
                document.dispatchEvent(new CustomEvent('x-close-alert'));
            }} catch(e) {{
                console.log('[AIDAR_SUBSCRIPTION_LOG] Error closing modal:', e);
                // Try several other methods
                try {{ 
                    document.querySelector('.anvil-alert-dismiss-btn').click();
                }} catch(e) {{
                    console.log('No dismiss button found:', e);
                }}
            }}
        }};
        
        document.getElementById('edit-company').onclick = function() {{ window.edit_company_click && window.edit_company_click(); }};
        document.getElementById('edit-payment').onclick = function() {{ window.edit_payment_click && window.edit_payment_click(); }};
        document.getElementById('cancel-btn').onclick = function() {{
            console.log('[AIDAR_SUBSCRIPTION_LOG] Cancel button clicked');
            window.cancel_btn_click && window.cancel_btn_click();
        }};
        document.getElementById('submit').onclick = function() {{ window.confirm_subscription_click && window.confirm_subscription_click(); }};
      </script>
    </div>
    """
    print("[AIDAR_SUBSCRIPTION_LOG] HTML rendered. Tax info should be visible in summary.")

    # Robust Cancel button system: always set cancel handler on window and in JS after each dialog open
    anvil.js.window.cancel_btn_click = self._cancel_btn_click

  def _edit_company_click(self, **event_args):
      """Opens the C_PaymentCustomer pop-up with prefilled data for editing, including country and tax info."""
      customer_info = anvil.server.call('get_stripe_customer_with_tax_info', self.company_email)
      form = C_PaymentCustomer(
          prefill_email=customer_info.get('email', self.company_email),
          prefill_company_name=customer_info.get('name', self.company_name),
          prefill_address=customer_info.get('address', {}),
          prefill_tax_id=customer_info.get('tax_id', self.tax_id),
          prefill_tax_country=customer_info.get('tax_country', self.tax_country),
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
          self._handle_customer_form_result(form)

  def _edit_payment_click(self, **event_args):
      """Opens the C_PaymentInfos pop-up to update payment method."""
      form = C_PaymentInfos()
      result = alert(
          content=form,
          large=False,
          width=500,
          buttons=[],
          dismissible=True
      )
      if result == 'success':
          self.__init__(plan_type=self.plan_type, user_count=self.user_count, billing_period=self.billing_period)

  def _cancel_btn_click(self, **event_args):
      """Closes the modal popup when the Cancel button is clicked."""
      print("[AIDAR_SUBSCRIPTION_LOG] _cancel_btn_click called. Closing modal.")
      import traceback
      print("[AIDAR_SUBSCRIPTION_LOG] _cancel_btn_click STACKTRACE:\n" + traceback.format_exc())
      self.raise_event("x-close-alert")

  def _confirm_subscription_click(self, **event_args):
      """Creates the subscription and redirects."""
      if not self.customer_id:
        alert('No Stripe customer found. Please add a payment method first.', title='Error')
        return
      if not self.price_id:
        alert('No Stripe price selected. Please select a valid plan.', title='Error')
        return
      try:
        subscription = anvil.server.call('create_stripe_subscription', self.customer_id, self.price_id, self.plan_type, self.user_count)
        alert(f"Subscription created! Status: {subscription.get('status')}", title="Success")
        anvil.js.window.location.replace("/#settings?section=Subscription")
        self.raise_event("x-close-alert", value="success")
      except Exception as e:
        alert(f"Failed to create subscription: {e}", title="Error")

  def _handle_customer_form_result(self, form):
    """
    1. Process the result from the customer form
    2. Update Stripe customer data
    3. Refresh display with new information
    """
    # Get updated values from the form using a method or attribute that returns the data
    # Assume form.get_customer_data() returns a dict with the fields: name, email, address, tax_id, tax_id_type
    if hasattr(form, 'get_customer_data'):
        data = form.get_customer_data()
        updated_name = data.get('name')
        updated_email = data.get('email')
        updated_address = data.get('address')
        updated_tax_id = data.get('tax_id')
        tax_id_type = data.get('tax_id_type')
    else:
        # fallback: try to get from public attributes if get_customer_data is not implemented
        updated_name = getattr(form, 'company_name', None)
        updated_email = getattr(form, 'company_email', anvil.users.get_user()['email'])
        updated_address = getattr(form, 'address', {})
        updated_tax_id = getattr(form, 'tax_id', None)
        tax_id_type = getattr(form, 'tax_id_type', None)
    # Update customer info in Stripe
    anvil.server.call(
        'update_stripe_customer',
        self.customer_id,
        updated_name,
        updated_email,
        updated_address
    )
    # Update tax info if provided
    if updated_tax_id and tax_id_type:
        anvil.server.call(
            'update_stripe_customer_tax_id',
            self.customer_id,
            updated_tax_id,
            tax_id_type
        )
    # Re-fetch customer data and rerender summary by reinitializing
    self.__init__(plan_type=self.plan_type, user_count=self.user_count, billing_period=self.billing_period)

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
