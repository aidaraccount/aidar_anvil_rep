import anvil
from ._anvil_designer import C_PaymentInfosTemplate
from anvil import *
import anvil.server
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.js
import json


class C_PaymentInfos(C_PaymentInfosTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    
    # Get subscription email
    base_data = anvil.server.call('get_settings_subscription2', user["user_id"])
    if base_data is not None:
      base_data = json.loads(base_data)[0]
      self.sub_email = base_data['mail'] if 'mail' in base_data else None
    else:
      self.sub_email = user['email']
    
    # Get the Stripe publishable key from the server
    stripe_publishable_key = anvil.server.call('get_stripe_publishable_key')
    
    # Get the Stripe SetupIntent client_secret from the server
    # Pass the user's email to associate with the customer
    client_secret = anvil.server.call('create_setup_intent', self.sub_email)
    
    # Get customer info for billing_details
    customer = anvil.server.call('get_stripe_customer', self.sub_email)
    customer_email = customer.get('email', '')
    customer_address = customer.get('address', {})
    address_line1 = customer_address.get('line1', '')
    address_line2 = customer_address.get('line2', '')
    city = customer_address.get('city', '')
    postal_code = customer_address.get('postal_code', '')
    state = customer_address.get('state', '')
    country = customer_address.get('country', '')

    # html
    self.html = f"""
    <script>
    window.stripe_setup_intent_client_secret = '{client_secret}';
    window.ANVIL_STRIPE_PUBLISHABLE_KEY = '{stripe_publishable_key}';
    </script>

    <!-- 1. Stripe.js script: Load Stripe library with guard against duplicate loading -->
    <script>
    // Define messages only if not already defined
    if (typeof window.STRIPE_MESSAGES === 'undefined') {{
      window.STRIPE_MESSAGES = {{
        cardError: 'There was an error processing your card. Please check your card details and try again.',
        success: 'Your card has been saved successfully!',
        processing: 'Processing your card...',
        serverError: 'There was a server error. Please try again later.'
      }};
    }}
    
    // Initialize Stripe loading
    function loadStripeJS() {{
      return new Promise(function(resolve) {{
        if (typeof window.Stripe !== 'undefined') {{
          // Stripe is already loaded
          resolve(window.Stripe);
        }} else {{
          // Create script element programmatically
          var stripeScript = document.createElement('script');
          stripeScript.src = 'https://js.stripe.com/v3/';
          stripeScript.onload = function() {{
            resolve(window.Stripe);
          }};
          document.head.appendChild(stripeScript);
        }}
      }});
    }}
    </script>

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
                <input id=\"name-on-card\" name=\"name-on-card\" type=\"text\" autocomplete=\"cc-name\" required placeholder=\"Name on card\">
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
    // Wait for Stripe to load first, then initialize
    const stripePublishableKey = window.ANVIL_STRIPE_PUBLISHABLE_KEY || 'pk_test_51RDoXJQTBcqmUQgt9CqdDXQjtHKkEkEBuXSs7EqVjwkzqcWP66EgCu8jjYArvbioeYpzvS5wSvbrUsKUtjXi0gGq00M9CzHJTa';
    var stripe, elements, cardElement;
    
    // Initialize the form only after Stripe.js is fully loaded
    loadStripeJS().then(function(StripeJS) {{
      stripe = StripeJS(stripePublishableKey);
      elements = stripe.elements({{
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
      cardElement = elements.create('card', {{
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
        // Display processing message
        document.getElementById('card-errors').textContent = window.STRIPE_MESSAGES.processing;
        document.getElementById('card-errors').style.color = '#FF7A00';
        
        stripe.confirmCardSetup(window.stripe_setup_intent_client_secret, {{
            payment_method: {{
                card: cardElement,
                billing_details: billingDetails
            }}
        }}).then(function(result) {{
            if (result.error) {{
                // Show error in card-errors div
                document.getElementById('card-errors').textContent = result.error.message || window.STRIPE_MESSAGES.cardError;
                document.getElementById('card-errors').style.color = '#FF5A36';
                submitBtn.disabled = false;
            }} else {{
                // Call our server-side function to handle the successful setup
                // and properly attach the payment method to the customer
                anvil.server.call('handle_setup_intent_success', 
                                 result.setupIntent.id,
                                 result.setupIntent.payment_method)
                  .then(function(response) {{
                    if (response.success) {{
                      // Show success message
                      document.getElementById('card-errors').textContent = window.STRIPE_MESSAGES.success;
                      document.getElementById('card-errors').style.color = '#00C853';
                      
                      // Call the callback if it exists
                      if (typeof window.payment_method_ready === 'function') {{
                          window.payment_method_ready(result.setupIntent.payment_method);
                      }}
                      
                      // Add a small delay before potentially closing the form
                      setTimeout(function() {{
                        if (typeof window.close_alert === 'function') {{
                          window.close_alert();
                        }}
                      }}, 1500);
                    }} else {{
                      // Show server error
                      document.getElementById('card-errors').textContent = response.message || window.STRIPE_MESSAGES.serverError;
                      document.getElementById('card-errors').style.color = '#FF5A36';
                      submitBtn.disabled = false;
                    }}
                  }})
                  .catch(function(err) {{
                    // Handle any server call errors
                    document.getElementById('card-errors').textContent = window.STRIPE_MESSAGES.serverError;
                    document.getElementById('card-errors').style.color = '#FF5A36';
                    submitBtn.disabled = false;
                    console.error('Server error:', err);
                  }});
            }}
        }});
    }});

    // 8. Cancel button closes the modal
    document.getElementById('cancel-btn').onclick = function() {{ window.close_alert(); }};
    
    }}).catch(function(error) {{
      console.error('Failed to load Stripe.js:', error);
      document.getElementById('card-errors').textContent = window.STRIPE_MESSAGES.serverError;
      document.getElementById('card-errors').style.color = '#FF5A36';
    }});
    </script>
    """

    # Register the payment_method_ready and close_alert functions on window for JS to call
    anvil.js.window.payment_method_ready = self._payment_method_ready
    anvil.js.window.close_alert = self._close_alert


  def _close_alert(self):
    """Close the alert dialog from JS."""
    self.raise_event('x-close-alert')


  def _payment_method_ready(self, payment_method_id: str):
    """Called from JS after successful Stripe setup. Handles server calls from Python."""
    try:
        # 1. Get customer info
        print(f"[STRIPE] Python: Looking up Stripe customer for email={self.sub_email}")
        customer = anvil.server.call('get_stripe_customer', self.sub_email)
        if customer and customer.get('id'):
            print(f"[STRIPE] Python: Found customer {customer['id']}, attaching payment method.")
            
            # 2. Attach payment method to customer
            updated_customer = anvil.server.call('attach_payment_method_to_customer', 
                                                customer['id'], 
                                                payment_method_id)
            print(f"[STRIPE] Python: Payment method attached. Updated customer: {updated_customer}")
            Notification("", title="Payment method created!", style="success").show()
          
            # 3. Return success to close the form
            self.raise_event("x-close-alert", value="success")
          
        else:
            # If no customer found, show error
            print("[STRIPE] Python: No customer found, cannot attach payment method.")
            Notification("", title="Could not add payment method!", style="error").show()
            return
          
    except Exception as err:
        print(f"[STRIPE] Python ERROR: {err}")
        Notification("", title="Could not add payment method!", style="error").show()