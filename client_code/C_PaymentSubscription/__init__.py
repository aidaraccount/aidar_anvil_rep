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
    print('price_id:', self.price_id)
    
    # 1. Get Stripe customer by email
    self.customer = anvil.server.call('get_stripe_customer', user['email'])
    print('customer:', self.customer)
    self.customer_id = self.customer['id']
    print('customer_id:', self.customer_id)
    
    # Convert LiveObjectProxy to dict if needed
    if hasattr(self.customer, 'items'):
        self.customer = dict(self.customer)
    self.customer_id = self.customer.get('id') if self.customer else None

    # Fetch and structure company/customer details for summary
    company_name = self.customer.get('name', '')
    email = self.customer.get('email', '')
    address = self.customer.get('address', {})
    tax_ids = self.customer.get('tax_ids', [])
    tax_id = ''
    tax_country = ''
    if tax_ids:
        tax_id_obj = tax_ids[0] # Use the first tax ID for summary
        tax_id = tax_id_obj.get('value', '')
        tax_country = tax_id_obj.get('country', '')
    address_lines = []
    if address:
        line1 = address.get('line1', '')
        line2 = address.get('line2', '')
        city = address.get('city', '')
        state = address.get('state', '')
        postal_code = address.get('postal_code', '')
        country = address.get('country', '')
        if line1:
            address_lines.append(line1)
        if line2:
            address_lines.append(line2)
        address_lines.append(f"{postal_code} {city}")
        if state:
            address_lines.append(state)
        if country:
            address_lines.append(country)
    address_str = ", ".join([x for x in address_lines if x and x.strip()])
    self.company_name = company_name
    self.company_email = email
    self.company_address = address_str
    self.tax_id = tax_id
    self.tax_country = tax_country

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

    # Ensure payment_method_summary is always set before HTML rendering
    if not hasattr(self, 'payment_method_summary'):
        self.payment_method_summary = "No payment method on file."

    # Render summary with edit icon
    self.html = f"""
    <div id='payment-form-container'>
      <h2>Confirm Subscription</h2>
      <div class='payment-info-text'>Please review your subscription details before confirming.</div>
      <form id='subscription-summary-form'>
        <!-- Company Profile Summary -->
        <div class='form-section'>
          <h3 style='display:inline;'>Company Details</h3>
          <span id='edit-company' style='cursor:pointer;margin-left:8px;' title='Edit'>✏️</span>
          <div class='field-row'><b>Email:</b> {self.company_email}</div>
          <div class='field-row'><b>Name:</b> {self.company_name}</div>
          <div class='field-row'><b>Address:</b> {self.company_address}</div>
          <div class='field-row'><b>Tax:</b> {self.tax_country} {self.tax_id}</div>
        </div>
        <!-- Payment Method Summary -->
        <div class='form-section'>
          <h3>Payment Method</h3>
          <div class='field-row'>{self.payment_method_summary}</div>
        </div>
        <!-- Plan Summary -->
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
      <div class="button-row">
        <button type="button" id="cancel-btn">Cancel</button>
        <button id="submit" type="submit">Book Subscription now</button>
      </div>
      <script>
        document.getElementById('edit-company').onclick = function() {{ anvil.call(this, 'edit_company_click'); }};
        document.getElementById('cancel-btn').onclick = function() {{ anvil.call(this, 'cancel_btn_click'); }};
        document.getElementById('submit').onclick = function() {{ anvil.call(this, 'confirm_subscription_click'); }};
      </script>
    </div>
    """

    # --- Section 5: Anvil event bindings ---
    # Ensure all event handlers are bound to the instance
    # This is critical for Anvil to expose methods to JS (for use in self.html script)
    self.edit_company_click = self.edit_company_click.__get__(self)
    self.cancel_btn_click = self.cancel_btn_click.__get__(self)
    self.confirm_subscription_click = self.confirm_subscription_click.__get__(self)

    # 4. Button handler for subscription confirmation
    def confirm_subscription_click(self, **event_args):
      if not self.customer_id:
        alert('No Stripe customer found. Please add a payment method first.', title='Error')
        return
      if not self.price_id:
        alert('No Stripe price selected. Please select a valid plan.', title='Error')
        return
      try:
        subscription = anvil.server.call('create_stripe_subscription', self.customer_id, self.price_id, self.user_count)
        alert(f"Subscription created! Status: {subscription.get('status')}", title="Success")
        import anvil.js
        anvil.js.window.location.replace("/#settings?section=Subscription")
        self.raise_event("x-close-alert", value="success")
      except Exception as e:
        alert(f"Failed to create subscription: {e}", title="Error")

    def cancel_btn_click(self, **event_args):
      """
      1. Handles the Cancel button click.
      2. Closes the modal popup.
      """
      self.raise_event("x-close-alert")

    def edit_company_click(self, **event_args):
      """
      1. Opens the C_PaymentCustomer pop-up with all customer fields pre-filled for editing.
      2. On save, updates the Stripe customer and reloads the subscription summary.
      """
      from ..C_PaymentCustomer import C_PaymentCustomer
      import anvil.server
      # Pass current customer data (including tax info) to the form for pre-filling
      form = C_PaymentCustomer(
          prefill_email=self.company_email,
          prefill_company_name=self.company_name,
          prefill_address=self.customer.get('address', {}),
          prefill_tax_id=self.tax_id,
          prefill_tax_country=self.tax_country,
          prefill_b2b=True if self.tax_id else False
      )
      result = alert(
          content=form,
          large=False,
          width=500,
          buttons=[],
          dismissible=True
      )
      if result == 'success':
        # Collect updated values from the form
        updated_name = form.company_name_box.text
        import anvil.users
        updated_email = anvil.users.get_user()['email']
        updated_address = {
            'line1': form.address_line1_box.text,
            'line2': form.address_line2_box.text,
            'city': form.city_box.text,
            'state': form.state_box.text,
            'postal_code': form.postal_code_box.text,
            'country': form.country_box.selected_value
        }
        updated_tax_id = form.tax_id_box.text
        updated_tax_country = form.tax_country_box.selected_value
        b2b_checked = form.business_checkbox.checked
        tax_id_type_map = {
            'GB': 'gb_vat',
            'US': 'us_ein',
            'CA': 'ca_bn',
            'AU': 'au_abn',
            'CH': 'ch_vat',
            'NO': 'no_vat',
            'IS': 'is_vat',
            'LI': 'li_uid',
            'IN': 'in_gst',
            'JP': 'jp_cn',
            'CN': 'cn_tin',
            'BR': 'br_cnpj',
            'MX': 'mx_rfc',
            'SG': 'sg_gst',
            'HK': 'hk_br',
            'NZ': 'nz_gst',
            'ZA': 'za_vat',
        }
        eu_countries = [
            'AT', 'BE', 'BG', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GR', 'HR', 'HU', 'IE',
            'IT', 'LT', 'LU', 'LV', 'MT', 'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK'
        ]
        if updated_tax_country in eu_countries:
            tax_id_type = 'eu_vat'
        else:
            tax_id_type = tax_id_type_map.get(updated_tax_country, None)
        # Update customer info
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
        # Re-fetch customer data and rerender summary
        self.customer = anvil.server.call('get_stripe_customer', updated_email)
        self.payment_method_summary = "No payment method on file."
        self.default_payment_method = None
        if self.customer_id:
            payment_methods = anvil.server.call('get_stripe_payment_methods', self.customer_id)
            if payment_methods:
                pm = payment_methods[0]
                brand = pm.get('card', {}).get('brand', '')
                last4 = pm.get('card', {}).get('last4', '')
                exp_month = pm.get('card', {}).get('exp_month', '')
                exp_year = pm.get('card', {}).get('exp_year', '')
                self.default_payment_method = pm.get('id')
                self.payment_method_summary = f"{brand.title()} **** **** **** {last4} (exp {exp_month}/{exp_year})"
        self.__init__(plan_type=self.plan_type, user_count=self.user_count, billing_period=self.billing_period)
