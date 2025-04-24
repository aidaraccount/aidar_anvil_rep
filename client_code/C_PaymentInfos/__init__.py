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
            <!-- Name on card -->
            <label for=\"name-on-card\">Name on card</label>
            <input id=\"name-on-card\" name=\"name-on-card\" type=\"text\" autocomplete=\"cc-name\" required style=\"width:100%;margin-bottom:10px\">
            <!-- PaymentElement (handles card + billing address) -->
            <div id=\"payment-element\"></div>
            <!-- Business checkbox -->
            <div style=\"margin:10px 0\">
                <input type=\"checkbox\" id=\"business-checkbox\" name=\"business-checkbox\">
                <label for=\"business-checkbox\">I confirm to purchase as a business</label>
            </div>
            <!-- VAT/Business Tax ID row (hidden unless business) -->
            <div id=\"tax-id-row\" style=\"display:none; margin-bottom:10px; align-items:center; gap:8px;\">
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
                    <!-- Add more as needed -->
                </select>
                <label for=\"tax-id\" style=\"margin-right:5px;\">VAT/Tax ID</label>
                <input id=\"tax-id\" name=\"tax-id\" type=\"text\" style=\"width:180px\" maxlength=\"32\" autocomplete=\"off\">
            </div>
            <div id=\"card-errors\" role=\"alert\"></div>
            <div style=\"display:flex;justify-content:flex-end;gap:10px;margin-top:20px\">
                <button type=\"button\" id=\"cancel-btn\">Cancel</button>
                <button id=\"submit-payment\" type=\"submit\">Save Payment Method</button>
            </div>
        </form>
    </div>
    <script>
    // 4. Initialize Stripe
    var stripe = Stripe('pk_test_51RDoXJQTBcqmUQgt9CqdDXQjtHKkEkEBuXSs7EqVjwkzqcWP66EgCu8jjYArvbioeYpzvS5wSvbrUsKUtjXi0gGq00M9CzHJTa');
    var elements = stripe.elements({{
        mode: 'setup',
        appearance: {{ theme: 'flat' }},
        clientSecret: window.stripe_setup_intent_client_secret
    }});
    var paymentElement = elements.create('payment', {{ 
      currency: 'eur',
      fields: {{ billingDetails: {{ address: 'auto' }} }}
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