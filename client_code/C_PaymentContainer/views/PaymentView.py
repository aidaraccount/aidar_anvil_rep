def render_payment_view(data: dict) -> str:
    """
    Returns the HTML for the payment method step.
    """
    pm = data.get('payment_method', {})
    brand = pm.get('brand', '')
    last4 = pm.get('last4', '')
    exp_month = pm.get('exp_month', '')
    exp_year = pm.get('exp_year', '')
    summary = f"{brand.title()} **** **** **** {last4} (exp {exp_month}/{exp_year})" if brand and last4 else "No payment method on file."
    return f'''
    <form id="payment-form">
      <div class="form-section">
        <div>Current Payment Method: {summary}</div>
        <label>Name on Card <input id="name-on-card" required></label>
        <div id="card-element"></div>
        <div id="card-errors" style="color:red;"></div>
      </div>
    </form>
    '''

def init_payment_js(data: dict) -> None:
    """
    Optionally add JS hooks for payment form (Stripe.js, etc.)
    """
    pass
