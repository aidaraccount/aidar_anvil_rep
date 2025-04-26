from ._anvil_designer import C_PaymentCustomerTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class C_PaymentCustomer(C_PaymentCustomerTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()

    # create html
    # 1. Company Profile Form Modal
    self.html = f'''
    <div id="payment-form-container">
        <!-- 1.1 Title and instructions -->
        <h2>Create company profile</h2>
        <div class="payment-info-text">The provided email is also used as the billing email address.</div>
        <!-- 1.2 Custom payment form -->
        <form id="payment-form">
            <!-- 1.2.1 Customer email -->
            <div class="form-section">
                <h3>Customer email</h3>
                <input id="email" name="email" type="email" autocomplete="email" required placeholder="Email" value="{user['email']}">
            </div>
            <!-- 1.2.2 Company Name -->
            <div class="form-section">
                <h3>Company name</h3>
                <input id="company-name" name="company-name" type="text" required placeholder="Company name">
            </div>
            <!-- 1.2.3 Company & Billing address section -->
            <div class="form-section">
                <h3>Company & Billing address</h3>
                <div class="field-row">
                    <input id="address-line-1" name="address-line-1" type="text" placeholder="Address line 1">
                </div>
                <div class="field-row">
                    <input id="address-line-2" name="address-line-2" type="text" placeholder="Address line 2">
                </div>
                <div class="two-column">
                    <div class="field-row">
                        <input id="city" name="city" type="text" placeholder="City">
                    </div>
                    <div class="field-row">
                        <input id="state" name="state" type="text" placeholder="State, county, province, or region">
                    </div>
                    <div class="field-row">
                        <input id="postal-code" name="postal-code" type="text" placeholder="Postal code">
                    </div>
                </div>
                <div class="field-row">
                    <select id="country" name="country" placeholder="Country">
                        <option value="">Country</option>
                        <option value="AU">Australia</option><option value="AT">Austria</option><option value="BE">Belgium</option><option value="BR">Brazil</option><option value="BG">Bulgaria</option><option value="CA">Canada</option><option value="CN">China</option><option value="HR">Croatia</option><option value="CY">Cyprus</option><option value="CZ">Czech Republic</option><option value="DK">Denmark</option><option value="EE">Estonia</option><option value="FI">Finland</option><option value="FR">France</option><option value="DE">Germany</option><option value="GR">Greece</option><option value="HK">Hong Kong</option><option value="HU">Hungary</option><option value="IS">Iceland</option><option value="IN">India</option><option value="IE">Ireland</option><option value="IT">Italy</option><option value="JP">Japan</option><option value="LI">Liechtenstein</option><option value="LT">Lithuania</option><option value="LU">Luxembourg</option><option value="LV">Latvia</option><option value="MT">Malta</option><option value="MX">Mexico</option><option value="NL">Netherlands</option><option value="NZ">New Zealand</option><option value="NO">Norway</option><option value="PL">Poland</option><option value="PT">Portugal</option><option value="RO">Romania</option><option value="SG">Singapore</option><option value="SK">Slovakia</option><option value="SI">Slovenia</option><option value="ZA">South Africa</option><option value="ES">Spain</option><option value="SE">Sweden</option><option value="CH">Switzerland</option><option value="GB">United Kingdom</option><option value="US">United States</option>
                    </select>
                </div>
            </div>
            <!-- 1.2.4 Business details section -->
            <div class="form-section">
                <h3>Business details</h3>
                <div class="field-row inline-fields">
                    <select id="tax-country" name="tax-country" placeholder="Country">
                        <option value="">VAT country</option>
                        <option value="AU">Australia</option><option value="AT">Austria</option><option value="BE">Belgium</option><option value="BR">Brazil</option><option value="BG">Bulgaria</option><option value="CA">Canada</option><option value="CN">China</option><option value="HR">Croatia</option><option value="CY">Cyprus</option><option value="CZ">Czech Republic</option><option value="DK">Denmark</option><option value="EE">Estonia</option><option value="FI">Finland</option><option value="FR">France</option><option value="DE">Germany</option><option value="GR">Greece</option><option value="HK">Hong Kong</option><option value="HU">Hungary</option><option value="IS">Iceland</option><option value="IN">India</option><option value="IE">Ireland</option><option value="IT">Italy</option><option value="JP">Japan</option><option value="LI">Liechtenstein</option><option value="LT">Lithuania</option><option value="LU">Luxembourg</option><option value="LV">Latvia</option><option value="MT">Malta</option><option value="MX">Mexico</option><option value="NL">Netherlands</option><option value="NZ">New Zealand</option><option value="NO">Norway</option><option value="PL">Poland</option><option value="PT">Portugal</option><option value="RO">Romania</option><option value="SG">Singapore</option><option value="SK">Slovakia</option><option value="SI">Slovenia</option><option value="ZA">South Africa</option><option value="ES">Spain</option><option value="SE">Sweden</option><option value="CH">Switzerland</option><option value="GB">United Kingdom</option><option value="US">United States</option>
                    </select>
                    <input id="tax-id" name="tax-id" type="text" maxlength="32" autocomplete="off" placeholder="VAT/Tax ID">
                </div>
                <div class="checkbox-container">
                    <input type="checkbox" id="business-checkbox" name="business-checkbox">
                    <label for="business-checkbox">I confirm to purchase as a business</label>
                </div>
            </div>
            <!-- 1.2.5 Error and button row -->
            <div id="form-errors" role="alert"></div>
            <div class="button-row">
                <button type="button" id="cancel-btn">Cancel</button>
                <button id="submit-customer" type="submit">Save company profile</button>
            </div>
        </form>
    </div>
    <script>
    // 2. Form JS logic
    // 2.1 Setup input references
    var companyNameInput = document.getElementById('company-name');
    var emailInput = document.getElementById('email');
    var addressLine1Input = document.getElementById('address-line-1');
    var addressLine2Input = document.getElementById('address-line-2');
    var cityInput = document.getElementById('city');
    var stateInput = document.getElementById('state');
    var postalCodeInput = document.getElementById('postal-code');
    var countryInput = document.getElementById('country');
    var taxIdInput = document.getElementById('tax-id');
    var taxCountryInput = document.getElementById('tax-country');
    var businessCheckbox = document.getElementById('business-checkbox');
    var submitBtn = document.getElementById('submit-customer');
    // 2.2 Form validation
    function validateForm() {
        var companyNameComplete = companyNameInput.value.trim().length > 0;
        var emailComplete = emailInput.value.trim().length > 0;
        var addressComplete = (
            addressLine1Input.value.trim().length > 0 &&
            cityInput.value.trim().length > 0 &&
            postalCodeInput.value.trim().length > 0
        );
        var businessChecked = businessCheckbox.checked;
        var taxIdValid = taxIdInput.value.trim().length > 3;
        var taxCountryValid = taxCountryInput.value.length === 2;
        var businessComplete = businessChecked && taxIdValid && taxCountryValid;
        var formValid = companyNameComplete && emailComplete && addressComplete && businessComplete;
        submitBtn.disabled = !formValid;
        if (formValid) {
            submitBtn.style.backgroundColor = 'var(--Orange, #FF7A00)';
            submitBtn.style.opacity = '1';
        } else {
            submitBtn.style.backgroundColor = '#ccc';
            submitBtn.style.opacity = '0.7';
        }
        return formValid;
    }
    [companyNameInput, emailInput, addressLine1Input, cityInput, postalCodeInput, stateInput, taxIdInput, taxCountryInput].forEach(function(input) {
        input.addEventListener('input', validateForm);
    });
    businessCheckbox.addEventListener('change', validateForm);
    validateForm();
    // 2.3 Submit handler
    document.getElementById('payment-form').addEventListener('submit', function(event) {
        event.preventDefault();
        var companyName = companyNameInput.value;
        var email = emailInput.value;
        var address = {
            line1: addressLine1Input.value,
            line2: addressLine2Input.value,
            city: cityInput.value,
            state: stateInput.value,
            postal_code: postalCodeInput.value,
            country: countryInput.value
        };
        var taxId = taxIdInput.value.trim();
        var taxCountry = taxCountryInput.value;
        var business = businessCheckbox.checked;
        if (!(business && taxId.length > 3 && taxCountry.length === 2)) {
            document.getElementById('form-errors').textContent = 'Please enter a valid VAT/Tax ID and country, and tick the business checkbox.';
            return;
        }
        document.getElementById('form-errors').textContent = '';
        submitBtn.disabled = true;
        // Call Python handler
        if (typeof window.customer_ready === 'function') {
            window.customer_ready(companyName, email, address, taxId, taxCountry);
        } else {
            document.getElementById('form-errors').textContent = 'Internal error: callback not found.';
        }
    });
    // 2.4 Cancel button handler
    document.getElementById('cancel-btn').onclick = function() { window.close_alert(); };
    </script>
    '''

    # Register the customer_ready and close_alert functions on window for JS to call
    anvil.js.window.customer_ready = self._customer_ready
    anvil.js.window.close_alert = self._close_alert

  def _customer_ready(self, company_name: str, email: str, address: dict, tax_id: str, tax_country: str):
    """Called from JS after successful form submit. Handles server calls from Python."""
    try:
        print(f"[STRIPE] Python: Looking up Stripe customer for email={email}")
        customer = anvil.server.call('get_stripe_customer', email)
        if customer and customer.get('id'):
            print(f"[STRIPE] Python: Found customer {customer['id']}, not creating new.")
        else:
            print(f"[STRIPE] Python: No customer found, creating new for email={email}")
            customer = anvil.server.call('create_stripe_customer', email, company_name, address)
            # c) add customer tax id
            if tax_id and tax_country:
                tax_id_type_map = {
                    'AT': 'eu_vat', 'BE': 'eu_vat', 'BG': 'eu_vat', 'CY': 'eu_vat', 'CZ': 'eu_vat',
                    'DE': 'eu_vat', 'DK': 'eu_vat', 'EE': 'eu_vat', 'ES': 'eu_vat', 'FI': 'eu_vat', 'FR': 'eu_vat',
                    'GR': 'eu_vat', 'HR': 'eu_vat', 'HU': 'eu_vat', 'IE': 'eu_vat', 'IT': 'eu_vat', 'LT': 'eu_vat',
                    'LU': 'eu_vat', 'LV': 'eu_vat', 'MT': 'eu_vat', 'NL': 'eu_vat', 'PL': 'eu_vat', 'PT': 'eu_vat',
                    'RO': 'eu_vat', 'SE': 'eu_vat', 'SI': 'eu_vat', 'SK': 'eu_vat',
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
                tax_id_type = tax_id_type_map.get(tax_country, 'unknown')
                if tax_id_type != 'unknown':
                    anvil.server.call('add_stripe_customer_tax_id', customer['id'], tax_id, tax_id_type)
                else:
                    print(f"[STRIPE] WARNING: No Stripe tax_id_type for country {tax_country}. Not adding tax ID.")

    except Exception as err:
        print(f"[STRIPE] Python ERROR: {err}")
        alert(f'[STRIPE] Error: {err}')

  def _close_alert(self):
    """Close the alert dialog from JS."""
    self.raise_event('x-close-alert')