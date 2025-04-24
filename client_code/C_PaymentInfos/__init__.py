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
        
        <!-- 3. Custom payment form -->
        <form id=\"payment-form\">
            <!-- Card information section -->
            <div class=\"form-section\">
                <h3>Card information</h3>
                <div id=\"card-element\"></div>
            </div>
            
            <!-- Name on card -->
            <div class=\"form-section\">
                <h3>Name on card</h3>
                <input id=\"name-on-card\" name=\"name-on-card\" type=\"text\" autocomplete=\"cc-name\" required placeholder=\"Name on card\">
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
                        <option value=\"\">Select country</option>
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
                <button id=\"submit-payment\" type=\"submit\">Continue</button>
            </div>
        </form>
    </div>
    <script>
    // Initialize Stripe
    var stripe = Stripe('pk_test_51RDoXJQTBcqmUQgt9CqdDXQjtHKkEkEBuXSs7EqVjwkzqcWP66EgCu8jjYArvbioeYpzvS5wSvbrUsKUtjXi0gGq00M9CzHJTa');
    
    // Create a Stripe client side instance
    var elements = stripe.elements({{
        clientSecret: window.stripe_setup_intent_client_secret,
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

    // Create card Element and mount it
    var cardElement = elements.create('card', {{
        style: {{
            base: {{
                color: '#ffffff',
                fontFamily: 'Inter, "Segoe UI", sans-serif',
                fontSize: '16px',
                iconColor: '#ffffff',
                '::placeholder': {{
                    color: '#aaaaaa'
                }}
            }},
            invalid: {{
                color: '#FF5A36',
                iconColor: '#FF5A36'
            }}
        }},
        hidePostalCode: true
    }});
    cardElement.mount('#card-element');

    // Handle form submission
    var form = document.getElementById('payment-form');
    var name = document.getElementById('name-on-card');
    var businessCheckbox = document.getElementById('business-checkbox');
    var taxIdInput = document.getElementById('tax-id');
    var taxCountryInput = document.getElementById('tax-country');
    var submitBtn = document.getElementById('submit-payment');
    
    // Show/hide tax ID fields based on business checkbox
    function validateBusinessFields() {{
        var taxId = taxIdInput.value.trim();
        var taxCountry = taxCountryInput.value;
        var valid = !businessCheckbox.checked || (taxId.length > 3 && taxCountry.length === 2);
        submitBtn.disabled = !valid;
        return valid;
    }}
    
    // Attach event listeners
    businessCheckbox.addEventListener('change', validateBusinessFields);
    taxIdInput.addEventListener('input', validateBusinessFields);
    taxCountryInput.addEventListener('change', validateBusinessFields);
    validateBusinessFields();
    
    // Handle form submission
    form.addEventListener('submit', function(event) {{
        event.preventDefault();
        
        var nameValue = name.value;
        var business = businessCheckbox.checked;
        var taxId = taxIdInput.value.trim();
        var taxCountry = taxCountryInput.value;
        
        if (business && !(taxId.length > 3 && taxCountry.length === 2)) {{
            document.getElementById('card-errors').textContent = 'Please enter a valid VAT/Tax ID and country.';
            return;
        }}
        
        document.getElementById('card-errors').textContent = '';
        submitBtn.disabled = true;
        submitBtn.textContent = 'Processing...';
        
        // Collect billing address data
        var billingDetails = {{
            name: nameValue,
            address: {{
                country: document.getElementById('country').value,
                line1: document.getElementById('address-line-1').value,
                line2: document.getElementById('address-line-2').value,
                city: document.getElementById('city').value,
                postal_code: document.getElementById('postal-code').value,
                state: document.getElementById('state').value
            }}
        }};
        
        // Business data as metadata
        var metadata = business ? {{
            business: 'yes',
            tax_id: taxId,
            tax_country: taxCountry
        }} : {{
            business: 'no'
        }};
        
        // Create a Payment Method and confirm setup
        stripe.confirmSetup({{
            elements,
            confirmParams: {{
                return_url: window.location.href,
                payment_method_data: {{
                    billing_details: billingDetails,
                    metadata: metadata
                }}
            }},
            redirect: 'if_required'
        }})
        .then(function(result) {{
            if (result.error) {{
                document.getElementById('card-errors').textContent = result.error.message;
                submitBtn.disabled = false;
                submitBtn.textContent = 'Continue';
            }} else {{
                // The setup has succeeded. Display a success message to your customer.
                alert('Payment method saved successfully with id: ' + result.setupIntent.payment_method);
                // Here you would typically send the payment method ID to your server
                // anvil.server.call('save_payment_method', result.setupIntent.payment_method);
            }}
        }});
    }});
    
    // Cancel button
    document.getElementById('cancel-btn').onclick = function() {{ anvil.call('close_alert'); }};
    </script>
    """