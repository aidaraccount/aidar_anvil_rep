def render_subscription_view(data: dict) -> str:
    """
    Returns the HTML for the subscription confirmation step.
    """
    customer = data.get('customer', {})
    plan = data.get('plan', {})
    pm = data.get('payment_method', {})
    name = customer.get('name', '')
    email = customer.get('email', '')
    address = customer.get('address', {})
    tax_id = customer.get('tax_id', '')
    tax_country = customer.get('tax_country', '')
    line1 = address.get('line1', '')
    line2 = address.get('line2', '')
    city = address.get('city', '')
    state = address.get('state', '')
    postal_code = address.get('postal_code', '')
    country = address.get('country', '')
    address_str = ', '.join([x for x in [line1, line2, city, state, postal_code, country] if x])
    pm_summary = f"{pm.get('brand','').title()} **** **** **** {pm.get('last4','')} (exp {pm.get('exp_month','')}/{pm.get('exp_year','')})" if pm else "No payment method on file."
    return f'''
    <div class='form-section'>
      <h3>Company Details <span id="edit-customer" style="cursor:pointer;">✏️</span></h3>
      <div><b>Email:</b> {email}</div>
      <div><b>Name:</b> {name}</div>
      <div><b>Address:</b> {address_str}</div>
      <div><b>Tax:</b> {tax_country} {tax_id}</div>
    </div>
    <div class='form-section'>
      <h3>Payment Method <span id="edit-payment" style="cursor:pointer;">✏️</span></h3>
      <div>{pm_summary}</div>
    </div>
    <div class='form-section'>
      <h3>Plan</h3>
      <div>{plan.get('type','')}</div>
      <div>User count: {plan.get('user_count','')}</div>
      <div>Billing period: {plan.get('billing_period','')}</div>
    </div>
    '''

def init_subscription_js(data: dict) -> None:
    """
    Optionally add JS hooks for the subscription summary view (edit buttons, etc.)
    """
    pass
