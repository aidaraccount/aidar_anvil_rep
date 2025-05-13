from ._anvil_designer import C_PaymentCustomerTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json


class C_PaymentCustomer(C_PaymentCustomerTemplate):
  def __init__(self, prefill_email=None, prefill_company_name=None, prefill_address=None, prefill_tax_id=None, prefill_tax_country=None, prefill_b2b=None, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()

    self.prefill_email = prefill_email
    
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
    
    def get_country_name(code: str) -> str:
        return COUNTRY_CODES.get(code, code or "")

    # create html
    # 1. Company Profile Form Modal
    self.html = f"""
    <div id="payment-form-container">
        <!-- 1.1 Title and instructions -->
        <h2>Create company profile</h2>
        <div class="payment-info-text">The provided email is also used as the billing email address.</div>
        <!-- 1.2 Custom company profile form -->
        <form id="payment-form">
            <!-- Subscription email -->
            <div class="form-section">
                <h3>Subscription email</h3>
                <div class="stripe-text">
                    {prefill_email}
                </div>
            </div>
            <!-- Company Name -->
            <div class="form-section">
                <h3>Company name</h3>
                <input id="company-name" name="company-name" type="text" required placeholder="Company name" value="{prefill_company_name if prefill_company_name else ''}">
            </div>
            <!-- Billing address section -->
            <div class="form-section">
                <h3>Billing address</h3>
                <div class="field-row">
                    <input id="address-line-1" name="address-line-1" type="text" required placeholder="Street and number" value="{prefill_address.get('line1', '') if prefill_address else ''}">
                </div>
                <div class="field-row">
                    <input id="address-line-2" name="address-line-2" type="text" placeholder="Apartment, suite, etc." value="{prefill_address.get('line2', '') if prefill_address else ''}">
                </div>
                <div class="two-column">
                    <div class="field-row">
                        <input id="city" name="city" type="text" required placeholder="City" value="{prefill_address.get('city', '') if prefill_address else ''}">
                    </div>
                    <div class="field-row">
                        <input id="postal-code" name="postal-code" type="text" required placeholder="Postal code" value="{prefill_address.get('postal_code', '') if prefill_address else ''}">
                    </div>
                </div>
                <div class="field-row">
                    <input id="state" name="state" type="text" placeholder="State/Province" value="{prefill_address.get('state', '') if prefill_address else ''}">
                </div>    
                <div class="field-row">
                    <select id="country" name="country" required>
                        <option value="">Country</option>
                        {f'<option value="{prefill_address["country"]}" selected>{get_country_name(prefill_address["country"])}</option>' if prefill_address and prefill_address.get('country') else ''}
                        {''.join([f'<option value="{code}">{get_country_name(code)}</option>' for code in COUNTRY_CODES.keys()])}
                    </select>
                </div>
            </div>
            <!-- Tax details section -->
            <div class="form-section">
                <h3>Tax details</h3>
                <div class="field-row inline-fields">
                    <select id="tax-country" name="tax-country" placeholder="Country" value="{prefill_tax_country if prefill_tax_country else ''}">
                        <option value="">Tax/VAT country</option>
                        {f'<option value="{prefill_tax_country}" selected>{get_country_name(prefill_tax_country)}</option>' if prefill_tax_country else ''}
                        {''.join([f'<option value="{code}">{get_country_name(code)}</option>' for code in COUNTRY_CODES.keys()])}
                    </select>
                    <input id="tax-id" name="tax-id" type="text" maxlength="32" autocomplete="off" placeholder="Tax/VAT ID" value="{prefill_tax_id if prefill_tax_id else ''}">
                </div>
                <div id="vat-error" class="error-message" style="color:#FF5A36;margin-top:4px;"></div>
                <div class="checkbox-container">
                    <input type="checkbox" id="business-checkbox" name="business-checkbox" {'checked' if prefill_b2b else ''}>
                    <label for="business-checkbox">I confirm to purchase as a business</label>
                </div>
            </div>
            <div id="form-errors" role="alert"></div>
            <div class="button-row">
                <button type="button" id="cancel-btn">Cancel</button>
                <button id="submit" type="submit">Save company profile</button>
            </div>
        </form>
    </div>
    <script>
    
    // 1. Setup input references
    var companyNameInput = document.getElementById('company-name');
    var addressLine1Input = document.getElementById('address-line-1');
    var addressLine2Input = document.getElementById('address-line-2');
    var cityInput = document.getElementById('city');
    var stateInput = document.getElementById('state');
    var postalCodeInput = document.getElementById('postal-code');
    var countryInput = document.getElementById('country');
    var taxIdInput = document.getElementById('tax-id');
    var taxCountryInput = document.getElementById('tax-country');
    var businessCheckbox = document.getElementById('business-checkbox');
    var submitBtn = document.getElementById('submit');
    var vatError = document.getElementById('vat-error');
    
    // 2. VAT prefix mapping
    var vatPrefixes = {{
        'AT': 'ATU', 'BE': 'BE', 'BG': 'BG', 'CY': 'CY', 'CZ': 'CZ', 'DE': 'DE', 'DK': 'DK', 'EE': 'EE',
        'EL': 'EL', 'ES': 'ES', 'FI': 'FI', 'FR': 'FR', 'GB': 'GB', 'GR': 'EL', 'HR': 'HR', 'HU': 'HU',
        'IE': 'IE', 'IT': 'IT', 'LT': 'LT', 'LU': 'LU', 'LV': 'LV', 'MT': 'MT', 'NL': 'NL', 'PL': 'PL',
        'PT': 'PT', 'RO': 'RO', 'SE': 'SE', 'SI': 'SI', 'SK': 'SK', 'EE': 'EE', 'HR': 'HR', 'LV': 'LV',
        'LT': 'LT', 'LU': 'LU', 'MT': 'MT', 'NL': 'NL', 'PL': 'PL', 'PT': 'PT', 'RO': 'RO', 'SE': 'SE',
        'SI': 'SI', 'SK': 'SK', 'XI': 'XI'
    }};
    
    // 3. Auto-prefix VAT ID on country change
    taxCountryInput.addEventListener('change', function() {{
        var country = taxCountryInput.value;
        var prefix = vatPrefixes[country];
        if (prefix) {{
            if (!taxIdInput.value.startsWith(prefix)) {{
                taxIdInput.value = prefix;
            }}
        }}
    }});
    
    // 4. Form validation
    function validateForm() {{
        var companyNameComplete = companyNameInput.value.trim().length > 0;
        var addressComplete = (
            addressLine1Input.value.trim().length > 0 &&
            cityInput.value.trim().length > 0 &&
            postalCodeInput.value.trim().length > 0
        );
        var businessChecked = businessCheckbox.checked;
        var taxIdValid = taxIdInput.value.trim().length > 3;
        var taxCountryValid = taxCountryInput.value.length === 2;
        var businessComplete = businessChecked && taxIdValid && taxCountryValid;
        var formValid = companyNameComplete && addressComplete && businessComplete;
        submitBtn.disabled = !formValid;
        if (formValid) {{
            submitBtn.style.backgroundColor = 'var(--Orange, #FF7A00)';
            submitBtn.style.opacity = '1';
        }} else {{
            submitBtn.style.backgroundColor = '#ccc';
            submitBtn.style.opacity = '0.7';
        }}
        return formValid;
    }}
    [companyNameInput, addressLine1Input, cityInput, postalCodeInput, stateInput, taxIdInput, taxCountryInput].forEach(function(input) {{
        input.addEventListener('input', validateForm);
    }});
    businessCheckbox.addEventListener('change', validateForm);
    validateForm();
    document.getElementById('payment-form').addEventListener('submit', function(event) {{
        event.preventDefault();
        var companyName = companyNameInput.value;
        var address = {{
            line1: addressLine1Input.value,
            line2: addressLine2Input.value,
            city: cityInput.value,
            state: stateInput.value,
            postal_code: postalCodeInput.value,
            country: (countryInput.value && countryInput.value !== 'Country') ? countryInput.value : ''
        }};
        var taxId = taxIdInput.value.trim();
        var taxCountry = taxCountryInput.value;
        var business = businessCheckbox.checked;
        vatError.textContent = '';
        if (!(business && taxId.length > 3 && taxCountry.length === 2)) {{
            vatError.textContent = 'Please enter a valid VAT/Tax ID and country, and tick the business checkbox.';
            return;
        }}
        document.getElementById('form-errors').textContent = '';
        submitBtn.disabled = true;
        // Call Python handler
        if (typeof window.customer_ready === 'function') {{
            window.customer_ready(companyName, address, taxId, taxCountry);
        }} else {{
            document.getElementById('form-errors').textContent = 'Internal error: callback not found.';
        }}
    }});

    document.getElementById('cancel-btn').onclick = function() {{ window.close_alert(); }};
    </script>
    """

    # Register the customer_ready and close_alert functions on window for JS to call
    anvil.js.window.customer_ready = self._customer_ready
    anvil.js.window.close_alert = self._close_alert
    

  def _close_alert(self):
    """Close the alert dialog from JS."""
    self.raise_event('x-close-alert')

  def _validate_eu_vat(self, tax_id: str, tax_country: str) -> bool:
    """
    1. Validates an EU VAT number based on format requirements
    2. Returns True if valid, False otherwise
    3. Displays appropriate error messages in the UI
    """
    # Dictionary of expected formats for EU countries
    expected_formats = {
        'DE': 'Format: DE123456789',
        'AT': 'Format: ATU12345678',
        'BE': 'Format: BE0123456789',
        'FR': 'Format: FRXX123456789',
        'IT': 'Format: IT12345678901',
        'ES': 'Format: ESX1234567X',
        'NL': 'Format: NL123456789B01',
        'PL': 'Format: PL1234567890',
        'SE': 'Format: SE123456789012',
        'DK': 'Format: DK12345678',
        'FI': 'Format: FI12345678',
        'IE': 'Format: IE1234567X',
        'PT': 'Format: PT123456789',
        'GR': 'Format: EL123456789',
        'LU': 'Format: LU12345678',
        'LT': 'Format: LT123456789',
        'LV': 'Format: LV12345678901',
        'CZ': 'Format: CZ12345678',
        'SK': 'Format: SK1234567890',
        'HU': 'Format: HU12345678',
        'SI': 'Format: SI12345678',
        'EE': 'Format: EE123456789',
        'HR': 'Format: HR12345678901',
        'BG': 'Format: BG123456789',
        'RO': 'Format: RO1234567890',
        'CY': 'Format: CY12345678X',
        'MT': 'Format: MT12345678',
    }
    
    # Basic format validation
    valid = True
    if tax_country in expected_formats:
      # Check if tax_id starts with country code (or EL for GR)
      expected_prefix = 'EL' if tax_country == 'GR' else tax_country
      if not tax_id.upper().startswith(expected_prefix):
        valid = False
      
      # Check minimum length (country code + at least 7 chars)
      if len(tax_id) < 9:
        valid = False
    
    if not valid:
      # Display error message with expected format
      format_hint = expected_formats.get(tax_country, '')
      error_msg = f"""
      var vatError = document.getElementById('vat-error');
      if (vatError) {{
          vatError.textContent = 'Invalid VAT format for {tax_country}. {format_hint}';
      }}
      """
      anvil.js.call_js('eval', error_msg)
      return False
    
    # If validation passes, clear any errors
    clear_msg = """
    var vatError = document.getElementById('vat-error');
    if (vatError) {
        vatError.textContent = '';
    }
    """
    anvil.js.call_js('eval', clear_msg)
    return True

  def _customer_ready(self, company_name: str, address: dict, tax_id: str, tax_country: str):
    """
    Called from JS after successful form submit. Handles server calls from Python.
    """
    try:
        print(f"[STRIPE] Python: Looking up Stripe customer for email={self.prefill_email}")
        customer = anvil.server.call('get_stripe_customer', self.prefill_email)
        
        # 1. Check if customer exists already
        if customer and customer.get('id'):
            # 2. Update customer data
            anvil.server.call('update_stripe_customer', 
                              customer['id'], 
                              company_name,
                              address)
        else:
            # 3. Create new customer if needed
            customer = anvil.server.call('create_stripe_customer', self.prefill_email, company_name, address)
            if customer:
                Notification("", title="Company profile created!", style="success").show()
            else:
                Notification("", title="Error: Could not create the company profile!", style="error").show()
          
        # 4. Get updated customer ID for tax operations
        customer_id = customer.get('id') if customer else None
        if not customer_id:
            raise Exception("Failed to create or update customer")
        
        # 5. Handle tax ID if provided
        if tax_id and tax_country:
            # Determine tax ID type based on country
            eu_countries = [
                'AT', 'BE', 'BG', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GR', 'HR', 'HU', 'IE',
                'IT', 'LT', 'LU', 'LV', 'MT', 'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK'
            ]
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
            
            # Set tax ID type based on country
            if tax_country in eu_countries:
                tax_id_type = 'eu_vat'
            else:
                tax_id_type = tax_id_type_map.get(tax_country)
                
            # EU VAT validation
            if tax_id_type == 'eu_vat':
                if not self._validate_eu_vat(tax_id, tax_country):
                    return
            
            # Update/create tax ID
            if tax_id_type:
                try:
                    anvil.server.call('update_stripe_customer_tax_id',
                                    customer_id,
                                    tax_id,
                                    tax_id_type)
                except Exception as e:
                    Notification("", title="Error: Could not add the tax ID!", style="error").show()
                    print(f"[STRIPE] Error setting tax ID: {e}")
        
        # 6. Close the form and return success
        print("[STRIPE] Python: Customer data saved successfully")
        self.raise_event("x-close-alert", value="success")

        return "success"
        
    except Exception as e:
        print(f"[STRIPE] Python ERROR: {e}")