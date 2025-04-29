def render_customer_view(data: dict) -> str:
    """
    Returns the HTML for the customer/company information step.
    """
    customer = data.get('customer', {})
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
    
    return f'''
    <form id="customer-form">
      <div class="form-section">
        <label>Company Name <input id="company-name" value="{name}" required></label>
        <label>Email <input id="email" type="email" value="{email}" required></label>
        <label>Address Line 1 <input id="address-line-1" value="{line1}" required></label>
        <label>Address Line 2 <input id="address-line-2" value="{line2}"></label>
        <label>City <input id="city" value="{city}" required></label>
        <label>State <input id="state" value="{state}"></label>
        <label>Postal Code <input id="postal-code" value="{postal_code}" required></label>
        <label>Country <input id="country" value="{country}" required></label>
        <label>Tax ID <input id="tax-id" value="{tax_id}"></label>
        <label>Tax Country <input id="tax-country" value="{tax_country}"></label>
        <label><input type="checkbox" id="business-checkbox" {'checked' if tax_id else ''}> Business</label>
        <div id="vat-error" style="color:red;"></div>
      </div>
    </form>
    '''

def init_customer_js(data: dict) -> None:
    """
    Optionally add JS hooks for customer form (validation, etc.)
    """
    pass
