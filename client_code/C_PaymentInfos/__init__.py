from ._anvil_designer import C_PaymentInfosTemplate
from anvil import *
import anvil.server
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.js

class C_PaymentInfos(C_PaymentInfosTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    
    # Get the Stripe SetupIntent client_secret from the server
    client_secret = anvil.server.call('create_setup_intent')
    self.html = f"""
    <script>
    window.stripe_setup_intent_client_secret = '{client_secret}';
    </script>
    <!-- 1. Stripe.js script -->
    <script src=\"https://js.stripe.com/v3/\"></script>
    <div id=\"payment-form-container\">
        <!-- 2. Title and instructions -->
        <h2>Add payment details</h2>
        <div class=\"payment-info-text\">Add your credit card details below. This card will be saved to your account and can be removed at any time.</div>
        <!-- 3. Custom payment form -->
        <form id=\"payment-form\">
            <!-- Customer email -->
            <div class=\"form-section\">
                <h3>Customer email</h3>
                <input id=\"email\" name=\"email\" type=\"email\" autocomplete=\"email\" required placeholder=\"Email\" value=\"{user['email']}\">
            </div>
            <!-- Name on card -->
            <div class=\"form-section\">
                <h3>Name on card</h3>
                <input id=\"name-on-card\" name=\"name-on-card\" type=\"text\" autocomplete=\"cc-name\" required placeholder=\"Name on card\">
            </div>
            <!-- Card information section -->
            <div class=\"form-section\">
                <h3>Card information</h3>
                <div id=\"card-element\"></div>
            </div>
            <!-- Billing address section -->
            <div class=\"form-section\">
                <h3>Billing address</h3>
                <div class=\"field-row\">
                    <select id=\"country\" name=\"country\" placeholder=\"Country\">
                        <option value=\"DE\">Germany</option>
                        <option value=\"FR\">France</option>
                        <option value=\"IT\">Italy</option>
                        <option value=\"ES\">Spain</option>
                        <option value=\"GB\">United Kingdom</option>
                        <option value=\"US\">United States</option>
                        <option value=\"NL\">Netherlands</option>
                        <option value=\"PL\">Poland</option>
                        <option value=\"CH\">Switzerland</option>
                    </select>
                </div>
                <div class=\"field-row\">
                    <input id=\"address-line-1\" name=\"address-line-1\" type=\"text\" placeholder=\"Address line 1\">
                </div>
                <div class=\"field-row\">
                    <input id=\"address-line-2\" name=\"address-line-2\" type=\"text\" placeholder=\"Address line 2\">
                </div>
                <div class=\"two-column\">
                    <div class=\"field-row\">
                        <input id=\"city\" name=\"city\" type=\"text\" placeholder=\"City\">
                    </div>
                    <div class=\"field-row\">
                        <input id=\"postal-code\" name=\"postal-code\" type=\"text\" placeholder=\"Postal code\">
                    </div>
                </div>
                <div class=\"field-row\">
                    <input id=\"state\" name=\"state\" type=\"text\" placeholder=\"State, county, province, or region\">
                </div>
            </div>
            <!-- Business details section -->
            <div class=\"form-section\">
                <h3>Business details</h3>
                <div class=\"field-row inline-fields\">
                    <select id=\"tax-country\" name=\"tax-country\" placeholder=\"Country\">
                        <option value=\"\">VAT country</option>
                        <option value=\"DE\">Germany</option>
                        <option value=\"FR\">France</option>
                        <option value=\"IT\">Italy</option>
                        <option value=\"ES\">Spain</option>
                        <option value=\"GB\">United Kingdom</option>
                        <option value=\"US\">United States</option>
                        <option value=\"NL\">Netherlands</option>
                        <option value=\"PL\">Poland</option>
                        <option value=\"SE\">Sweden</option>
                        <option value=\"CH\">Switzerland</option>
                    </select>
                    <input id=\"tax-id\" name=\"tax-id\" type=\"text\" maxlength=\"32\" autocomplete=\"off\" placeholder=\"VAT/Tax ID\">
                </div>
                <div class=\"checkbox-container\">
                    <input type=\"checkbox\" id=\"business-checkbox\" name=\"business-checkbox\">
                    <label for=\"business-checkbox\">I confirm to purchase as a business</label>
                </div>
            </div>
            <div id=\"card-errors\" role=\"alert\"></div>
            <div class=\"button-row\">
                <button type=\"button\" id=\"cancel-btn\">Cancel</button>
                <button id=\"submit-payment\" type=\"submit\">Save payment details</button>
            </div>
        </form>
    </div>
    <script>
    // Initialize Stripe
    var stripe = Stripe('pk_test_51RDoXJQTBcqmUQgt9CqdDXQjtHKkEkEBuXSs7EqVjwkzqcWP66EgCu8jjYArvbioeYpzvS5wSvbrUsKUtjXi0gGq00M9CzHJTa');
    // Create a Stripe client side instance
    var elements = stripe.elements({{
        appearance: {{
            theme: 'flat',
            variables: {{
                colorPrimary: '#FF7A00',
                colorBackground: '#181818',
                colorText: '#ffffff',
                colorDanger: '#FF5A36',
                fontFamily: 'Inter, "Segoe UI", sans-serif',
                borderRadius: '8px',
                colorTextPlaceholder: '#aaaaaa'
            }}
        }}
    }});
    // Create Card Element and mount it
    var cardElement = elements.create('card', {{
        style: {{
            base: {{
                color: '#ffffff',
                fontFamily: 'Inter, "Segoe UI", sans-serif',
                fontSize: '16px',
                iconColor: '#ffffff',
                '::placeholder': {{ color: '#aaaaaa' }}
            }},
            invalid: {{
                color: '#FF5A36',
                iconColor: '#FF5A36'
            }}
        }},
        hidePostalCode: true
    }});
    cardElement.mount('#card-element');
    var form = document.getElementById('payment-form');
    var nameInput = document.getElementById('name-on-card');
    var businessCheckbox = document.getElementById('business-checkbox');
    var taxIdInput = document.getElementById('tax-id');
    var taxCountryInput = document.getElementById('tax-country');
    var submitBtn = document.getElementById('submit-payment');
    // Required field references
    var countryInput = document.getElementById('country');
    var addressLine1Input = document.getElementById('address-line-1');
    var cityInput = document.getElementById('city');
    var postalCodeInput = document.getElementById('postal-code');
    var stateInput = document.getElementById('state');
    // Form validation
    function validateForm() {{
        var nameComplete = nameInput.value.trim().length > 0;
        var addressComplete = (
            addressLine1Input.value.trim().length > 0 &&
            cityInput.value.trim().length > 0 &&
            postalCodeInput.value.trim().length > 0 &&
            stateInput.value.trim().length > 0
        );
        var businessChecked = businessCheckbox.checked;
        var taxIdValid = taxIdInput.value.trim().length > 3;
        var taxCountryValid = taxCountryInput.value.length === 2;
        var businessComplete = businessChecked && taxIdValid && taxCountryValid;
        var cardComplete = cardElement._complete || false;
        var formValid = cardComplete && nameComplete && addressComplete && businessComplete;
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
    [nameInput, addressLine1Input, cityInput, postalCodeInput, stateInput, taxIdInput, taxCountryInput].forEach(function(input) {{
        input.addEventListener('input', validateForm);
    }});
    cardElement.on('change', function(event) {{
        if (event.error) {{
            document.getElementById('card-errors').textContent = event.error.message;
        }} else {{
            document.getElementById('card-errors').textContent = '';
        }}
        cardElement._complete = event.complete;
        validateForm();
    }});
    businessCheckbox.addEventListener('change', validateForm);
    cardElement._complete = false;
    validateForm();
    form.addEventListener('submit', function(event) {{
        event.preventDefault();
        var nameValue = nameInput.value;
        var business = businessCheckbox.checked;
        var taxId = taxIdInput.value.trim();
        var taxCountry = taxCountryInput.value;
        if (!(business && taxId.length > 3 && taxCountry.length === 2)) {{
            document.getElementById('card-errors').textContent = 'Please enter a valid VAT/Tax ID and country, and tick the business checkbox.';
            return;
        }}
        document.getElementById('card-errors').textContent = '';
        submitBtn.disabled = true;
        var billingDetails = {{
            name: nameValue,
            address: {{
                country: countryInput.value,
                line1: addressLine1Input.value,
                line2: document.getElementById('address-line-2').value,
                city: cityInput.value,
                postal_code: postalCodeInput.value,
                state: stateInput.value
            }}
        }};
        var metadata = {{
            business: 'yes',
            tax_id: taxId,
            tax_country: taxCountry
        }};
        stripe.confirmCardSetup(window.stripe_setup_intent_client_secret, {{
            payment_method: {{
                card: cardElement,
                billing_details: billingDetails,
                metadata: metadata
            }}
        }}).then(function(result) {{
            if (result.error) {{
                document.getElementById('card-errors').textContent = result.error.message;
                submitBtn.disabled = false;
            }} else {{
                var emailValue = document.getElementById('email').value;
                alert('Payment method saved successfully with id: ' + result.setupIntent.payment_method + ' and email: ' + emailValue);
                window.payment_method_ready(result.setupIntent.payment_method, emailValue);
            }}
        }});
    }});
    document.getElementById('cancel-btn').onclick = function() {{ window.close_alert(); }};
    </script>
    """
    # Register the payment_method_ready and close_alert functions on window for JS to call
    anvil.js.window.payment_method_ready = self._on_payment_method_ready
    anvil.js.window.close_alert = self._close_alert

  def _on_payment_method_ready(self, token: str, email: str, **event_args) -> None:
    """Handle payment method ready event from JS and call server to create customer."""
    try:
      customer_result = anvil.server.call('create_stripe_customer', token, email)
      alert('Payment method saved and customer created!')
    except Exception as err:
      alert(f'Error creating customer: {err}')

  def _close_alert(self):
    """Close the alert dialog from JS."""
    alert.close_alert()