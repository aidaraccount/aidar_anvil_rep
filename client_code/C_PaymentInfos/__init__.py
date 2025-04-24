from ._anvil_designer import C_PaymentInfosTemplate
from anvil import *
import anvil.server
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


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
    window.stripe_setup_intent_client_secret = \"{client_secret}\";
    </script>
    <!-- 1. Stripe.js script -->
    <script src=\"https://js.stripe.com/v3/\"></script>
    <div id=\"payment-form-container\">
        <!-- 2. Title and instructions -->
        <h2>Add payment details</h2>
        <div class=\"payment-info-text\">Add your credit card details below. This card will be saved to your account and can be removed at any time.</div>
        <!-- 3. Stripe Payment Element form -->
        <form id=\"payment-form\">
            <!-- Card information section -->
            <div class=\"form-section\">
                <h3>Card information</h3>
                <div id=\"payment-element\"></div>
            </div>
            
            <!-- Name on card -->
            <div class=\"form-section\">
                <label for=\"name-on-card\">Name on card</label>
                <input id=\"name-on-card\" name=\"name-on-card\" type=\"text\" autocomplete=\"cc-name\" required>
            </div>
            
            <!-- Billing address section -->
            <div class=\"form-section\">
                <h3>Billing address</h3>
                <label for=\"country\">Country</label>
                <select id=\"country\" name=\"country\">
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
                
                <label for=\"address-line-1\">Address line 1</label>
                <input id=\"address-line-1\" name=\"address-line-1\" type=\"text\">
                
                <label for=\"address-line-2\">Address line 2</label>
                <input id=\"address-line-2\" name=\"address-line-2\" type=\"text\">
                
                <div class=\"two-column\">
                    <div>
                        <label for=\"city\">City</label>
                        <input id=\"city\" name=\"city\" type=\"text\">
                    </div>
                    <div>
                        <label for=\"postal-code\">Postal code</label>
                        <input id=\"postal-code\" name=\"postal-code\" type=\"text\">
                    </div>
                </div>
                
                <label for=\"state\">State, county, province, or region</label>
                <input id=\"state\" name=\"state\" type=\"text\">
            </div>
            
            <!-- Business checkbox -->
            <div class=\"form-section\">
                <div class=\"checkbox-container\">
                    <input type=\"checkbox\" id=\"business-checkbox\" name=\"business-checkbox\">
                    <label for=\"business-checkbox\">Purchasing as a business</label>
                </div>
            </div>
            
            <!-- VAT/Business Tax ID row (hidden unless business) -->
            <div id=\"tax-id-row\" style=\"display:none;\">
                <label for=\"tax-country\" style=\"margin-right:5px;\">Country</label>
                <select id=\"tax-country\" name=\"tax-country\" style=\"margin-right:10px;\">
                    <option value=\"\">Select</option>
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
                <label for=\"tax-id\" style=\"margin-right:5px;\">VAT/Tax ID</label>
                <input id=\"tax-id\" name=\"tax-id\" type=\"text\" maxlength=\"32\" autocomplete=\"off\">
            </div>
            
            <div id=\"card-errors\" role=\"alert\"></div>
            <div class=\"button-row\">
                <button type=\"button\" id=\"cancel-btn\">Cancel</button>
                <button id=\"submit-payment\" type=\"submit\">Continue</button>
            </div>
        </form>
    </div>
    <script>
    // 4. Initialize Stripe
    var stripe = Stripe('pk_test_51RDoXJQTBcqmUQgt9CqdDXQjtHKkEkEBuXSs7EqVjwkzqcWP66EgCu8jjYArvbioeYpzvS5wSvbrUsKUtjXi0gGq00M9CzHJTa');
    var elements = stripe.elements({{
        // When using clientSecret, do not specify mode (it's inferred from the clientSecret)
        currency: 'eur',
        appearance: {{ theme: 'flat' }},
        clientSecret: window.stripe_setup_intent_client_secret
    }});
    
    // Create just the card element without other payment methods
    var paymentElement = elements.create('payment', {{ 
        defaultValues: {{
            billingDetails: {{
                address: {{
                    country: 'DE',
                }}
            }}
        }},
        fields: {{
            billingDetails: 'never'  // We'll collect billing details with our custom form
        }},
        wallets: {{
            applePay: 'never',
            googlePay: 'never'
        }},
        paymentMethodOrder: ['card'], // Only show card
        paymentMethodTypes: ['card']  // Only use card payment method
    }});
    paymentElement.mount('#payment-element');

    // Business logic for VAT/Tax ID fields
    var businessCheckbox = document.getElementById('business-checkbox');
    var taxIdRow = document.getElementById('tax-id-row');
    var submitBtn = document.getElementById('submit-payment');
    var taxIdInput = document.getElementById('tax-id');
    var taxCountryInput = document.getElementById('tax-country');

    function validateBusinessFields() {{
        if (!businessCheckbox.checked) {{
            taxIdRow.style.display = 'none';
            submitBtn.disabled = false;
            return true;
        }}
        taxIdRow.style.display = 'flex';
        var taxId = taxIdInput.value.trim();
        var taxCountry = taxCountryInput.value;
        var valid = taxId.length > 3 && taxCountry.length === 2;
        submitBtn.disabled = !valid;
        return valid;
    }}
    businessCheckbox.addEventListener('change', validateBusinessFields);
    taxIdInput.addEventListener('input', validateBusinessFields);
    taxCountryInput.addEventListener('change', validateBusinessFields);
    // Initialize state
    validateBusinessFields();

    // 5. Handle form submission
    var form = document.getElementById('payment-form');
    form.addEventListener('submit', function(event) {{
        event.preventDefault();
        var name = document.getElementById('name-on-card').value;
        var business = businessCheckbox.checked;
        var taxId = taxIdInput.value.trim();
        var taxCountry = taxCountryInput.value;
        if (business) {{
            if (!(taxId.length > 3 && taxCountry.length === 2)) {{
                document.getElementById('card-errors').textContent = 'Please enter a valid VAT/Tax ID and country.';
                return;
            }}
        }}
        stripe.confirmSetup({{
            elements: elements,
            confirmParams: {{
                payment_method_data: {{
                    billing_details: {{
                        name: name,
                        address: {{
                            country: document.getElementById('country').value,
                            line1: document.getElementById('address-line-1').value,
                            line2: document.getElementById('address-line-2').value,
                            city: document.getElementById('city').value,
                            postal_code: document.getElementById('postal-code').value,
                            state: document.getElementById('state').value
                        }}
                    }},
                    metadata: Object.assign({{}},
                        business ? {{
                            business: 'yes',
                            tax_id: taxId,
                            tax_country: taxCountry
                        }} : {{}}
                    )
                }}
            }},
            redirect: 'if_required'
        }}).then(function(result) {{
            var errorDiv = document.getElementById('card-errors');
            if (result.error) {{
                errorDiv.textContent = result.error.message;
            }} else {{
                errorDiv.textContent = '';
                // TODO: Send result.setupIntent.payment_method to server via anvil.call() or anvil.server.call()
                alert('Payment method saved with id: ' + result.setupIntent.payment_method);
            }}
        }});
    }});
    // Optional: Cancel button closes the popup
    document.getElementById('cancel-btn').onclick = function() {{ anvil.call('close_alert'); }};
    </script>
    """