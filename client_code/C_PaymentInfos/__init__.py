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
    # Get customer info for billing_details
    customer = anvil.server.call('get_stripe_customer', user['email'])
    customer_email = customer.get('email', '')
    customer_name = customer.get('name', '')
    customer_address = customer.get('address', {})
    address_line1 = customer_address.get('line1', '')
    address_line2 = customer_address.get('line2', '')
    city = customer_address.get('city', '')
    postal_code = customer_address.get('postal_code', '')
    state = customer_address.get('state', '')
    country = customer_address.get('country', '')

    # create html
    self.html = f"""
    <script>
    window.stripe_setup_intent_client_secret = '{client_secret}';
    </script>

    <!-- 1. Stripe.js script: Load Stripe library -->
    <script src=\"https://js.stripe.com/v3/\"></script>

    <!-- 2. Payment Form Container -->
    <div id=\"payment-form-container\">    
        <!-- 2.1 Title and instructions -->
        <h2>Add payment details</h2>
        <div class=\"payment-info-text\">Add your credit card details below. This card will be saved to your account and can be removed at any time.</div>
        <!-- 2.2 Custom payment form -->
        <form id=\"payment-form\">            
            <!-- 2.2.1 Card information section -->
            <div class=\"form-section\">                
                <h3>Card information</h3>
                <div id=\"card-element\"></div>
            </div>

            <!-- 2.2.2 Name on card field -->
            <div class=\"form-section\">                
                <h3>Name on card</h3>
                <input id=\"name-on-card\" name=\"name-on-card\" type=\"text\" autocomplete=\"cc-name\" required placeholder=\"Name on card\" value=\"{customer_name}\">
            </div>

            <!-- 2.2.3 Error display and buttons -->
            <div id=\"card-errors\" role=\"alert\"></div>
            <div class=\"button-row\">                
                <button type=\"button\" id=\"cancel-btn\">Cancel</button>
                <button id=\"submit\" type=\"submit\">Save payment details</button>
            </div>
        </form>
    </div>

    <script>
    // 3. Initialize Stripe and Elements
    var stripe = Stripe('pk_test_51RDoXJQTBcqmUQgt9CqdDXQjtHKkEkEBuXSs7EqVjwkzqcWP66EgCu8jjYArvbioeYpzvS5wSvbrUsKUtjXi0gGq00M9CzHJTa');
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

    // 4. Create and mount Card Element
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

    // 5. Form and field references
    var form = document.getElementById('payment-form');
    var nameInput = document.getElementById('name-on-card');
    var submitBtn = document.getElementById('submit');

    // 6. Form validation logic
    function validateForm() {{
        var nameComplete = nameInput.value.trim().length > 0;
        var cardComplete = false;
        if (cardElement && typeof cardElement._complete !== 'undefined') {{
            cardComplete = cardElement._complete;
        }} else if (cardElement && typeof cardElement._implementation !== 'undefined' && typeof cardElement._implementation._complete !== 'undefined') {{
            cardComplete = cardElement._implementation._complete;
        }}
        var formValid = cardComplete && nameComplete;
        if (formValid) {{
            submitBtn.removeAttribute('disabled');
            submitBtn.style.backgroundColor = '#FF7A00';
            submitBtn.style.opacity = '1';
        }} else {{
            submitBtn.setAttribute('disabled', 'disabled');
            submitBtn.style.backgroundColor = '#ccc';
            submitBtn.style.opacity = '0.7';
        }}
        return formValid;
    }}
    nameInput.addEventListener('input', validateForm);
    cardElement.on('change', function(event) {{
        if (event.error) {{
            document.getElementById('card-errors').textContent = event.error.message;
        }} else {{
            document.getElementById('card-errors').textContent = '';
        }}
        cardElement._complete = event.complete;
        validateForm();
    }});
    // Ensure validation after leaving card field (e.g. after CVC entry)
    cardElement.on('blur', function(event) {{
        validateForm();
    }});
    cardElement._complete = false;
    form.addEventListener('input', validateForm);
    validateForm();

    // 7. Form submission handler
    form.addEventListener('submit', function(event) {{
        event.preventDefault();
        var nameValue = nameInput.value;
        document.getElementById('card-errors').textContent = '';
        submitBtn.disabled = true;
        var billingDetails = {{
            name: nameValue,
            email: '{customer_email}',
            address: {{
                line1: '{address_line1}',
                line2: '{address_line2}',
                city: '{city}',
                postal_code: '{postal_code}',
                state: '{state}',
                country: '{country}'
            }}
        }};
        stripe.confirmCardSetup(window.stripe_setup_intent_client_secret, {{
            payment_method: {{
                card: cardElement,
                billing_details: billingDetails
            }}
        }}).then(function(result) {{
            if (result.error) {{
                document.getElementById('card-errors').textContent = result.error.message;
                submitBtn.disabled = false;
            }} else {{
                if (typeof window.payment_method_ready === 'function') {{
                    window.payment_method_ready(result.setupIntent.payment_method);
                }}
            }}
        }});
    }});

    // 8. Cancel button closes the modal
    document.getElementById('cancel-btn').onclick = function() {{ window.close_alert(); }};
    </script>
    """

    # Register the payment_method_ready and close_alert functions on window for JS to call
    anvil.js.window.payment_method_ready = self._payment_method_ready
    anvil.js.window.close_alert = self._close_alert

  def _payment_method_ready(self, payment_method_id: str):
    """Called from JS after successful Stripe setup. Handles server calls from Python."""
    try:
        # 1. Get form data
        import anvil.js
        name = anvil.js.window.document.getElementById('name-on-card').value
        # 2. lookup customer
        # a) check if customer exists
        print(f"[STRIPE] Python: Looking up Stripe customer for email={user['email']}")
        customer = anvil.server.call('get_stripe_customer', user['email'])
        if customer and customer.get('id'):
            print(f"[STRIPE] Python: Found customer {customer['id']}, attaching payment method.")
        else:
            # b) if not -> error
            print(f"[STRIPE] Python: No customer found, cannot attach payment method.")
            return
            
        # 3. attach payment method to customer
        updated_customer = anvil.server.call('attach_payment_method_to_customer', customer['id'], payment_method_id)
        print(f"[STRIPE] Python: Payment method attached. Updated customer: {updated_customer}")

    except Exception as err:
        print(f"[STRIPE] Python ERROR: {err}")
        alert(f'[STRIPE] Error: {err}')

  def _close_alert(self):
    """Close the alert dialog from JS."""
    self.raise_event('x-close-alert')