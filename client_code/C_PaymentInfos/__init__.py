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
import datetime


def ensure_stripe_js_loaded():
  """
  1. Ensures Stripe.js is loaded only once in the client
  2. Provides detailed logging of the loading process
  3. Returns the Stripe public key
  
  This function manages the single loading of Stripe.js
  across the application to prevent duplicate loading issues.
  
  Returns:
    str: The Stripe public key to use for initialization
  """
  # Stripe public key
  pk_key = 'pk_test_51RDoXJQTBcqmUQgt9CqdDXQjtHKkEkEBuXSs7EqVjwkzqcWP66EgCu8jjYArvbioeYpzvS5wSvbrUsKUtjXi0gGq00M9CzHJTa'
  
  # Check if Stripe.js is already loaded or loading
  stripe_status = anvil.js.call('eval', """
    (function() {
      if (window._stripeLoadStatus === 'loaded') {
        console.log("[STRIPE_LOADER] " + new Date().toISOString() + " - Stripe already loaded");
        return 'loaded';
      } else if (window._stripeLoadStatus === 'loading') {
        console.log("[STRIPE_LOADER] " + new Date().toISOString() + " - Stripe is currently loading");
        return 'loading';
      }
      return 'not_loaded';
    })();
  """)
  
  # If already loaded or loading, return
  if stripe_status in ['loaded', 'loading']:
    return pk_key
    
  # Set status to loading
  anvil.js.call('eval', "window._stripeLoadStatus = 'loading';")
  
  # Load Stripe.js
  anvil.js.call('eval', f"""
    (function() {{
      console.log("[STRIPE_LOADER] " + new Date().toISOString() + " - Starting to load Stripe.js");
      
      // Record start time
      window._stripeLoadStart = new Date();
      
      // Create the script element
      var script = document.createElement('script');
      script.src = 'https://js.stripe.com/v3/';
      script.async = true;
      
      // Set up onload handler
      script.onload = function() {{
        var loadTime = new Date() - window._stripeLoadStart;
        console.log("[STRIPE_LOADER] " + new Date().toISOString() + " - Stripe.js loaded in " + loadTime + "ms");
        window._stripeLoadStatus = 'loaded';
        window._stripeLoadTime = loadTime;
        
        // Track when Stripe is actually ready to use
        var checkStartTime = new Date();
        var stripeReadyInterval = setInterval(function() {{
          try {{
            if (typeof Stripe === 'function') {{
              var test = Stripe('{pk_key}');
              if (test) {{
                var readyTime = new Date() - checkStartTime;
                console.log("[STRIPE_LOADER] " + new Date().toISOString() + " - Stripe function initialized after " + readyTime + "ms");
                window._stripeReadyTime = readyTime;
                clearInterval(stripeReadyInterval);
                
                // Monitor when card elements are fully ready
                try {{
                  var elementsCheckStart = new Date();
                  var elements = test.elements();
                  var card = elements.create('card', {{}});
                  if (card) {{
                    var elementsTime = new Date() - elementsCheckStart;
                    console.log("[STRIPE_LOADER] " + new Date().toISOString() + " - Stripe Elements initialization took " + elementsTime + "ms");
                    window._stripeElementsTime = elementsTime;
                  }}
                }} catch (elemErr) {{
                  console.log("[STRIPE_LOADER] " + new Date().toISOString() + " - Could not initialize Elements: " + elemErr.message);
                }}
              }}
            }}
          }} catch (e) {{
            // Ignore errors during testing
          }}
        }}, 100);
        
        // Timeout after 15 seconds
        setTimeout(function() {{
          clearInterval(stripeReadyInterval);
          console.log("[STRIPE_LOADER] " + new Date().toISOString() + " - Timed out waiting for Stripe initialization");
        }}, 15000);
      }};
      
      // Set up error handler
      script.onerror = function() {{
        console.error("[STRIPE_LOADER] " + new Date().toISOString() + " - Failed to load Stripe.js");
        window._stripeLoadStatus = 'error';
      }};
      
      // Append to document head
      document.head.appendChild(script);
    }})();
  """)
  
  return pk_key


class C_PaymentInfos(C_PaymentInfosTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - C_PaymentInfos.__init__ started")
    global user
    user = anvil.users.get_user()
    print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Got user: {user['user_id']}")
    
    # Get subscription email
    print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Calling get_settings_subscription2")
    base_data = anvil.server.call('get_settings_subscription2', user["user_id"])
    print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Received settings data: {base_data is not None}")
    if base_data is not None:
      base_data = json.loads(base_data)[0]
      self.sub_email = base_data['mail'] if 'mail' in base_data else None
      print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Using subscription email: {self.sub_email}")
    else:
      self.sub_email = user['email']
      print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Using user email: {self.sub_email}")
    
    # Get the Stripe SetupIntent client_secret from the server
    print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Calling create_setup_intent")
    client_secret = anvil.server.call('create_setup_intent')
    print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Received client_secret: {client_secret[:10]}...")
    
    # Get customer info for billing_details
    print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Calling get_stripe_customer with email {self.sub_email}")
    customer = anvil.server.call('get_stripe_customer', self.sub_email)
    print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Received customer data: {bool(customer)}")
    customer_email = customer.get('email', '')
    customer_address = customer.get('address', {})
    address_line1 = customer_address.get('line1', '')
    address_line2 = customer_address.get('line2', '')
    city = customer_address.get('city', '')
    postal_code = customer_address.get('postal_code', '')
    state = customer_address.get('state', '')
    country = customer_address.get('country', '')
    print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Parsed customer details: email={customer_email}, country={country}")

    # Get Stripe public key using the local loader
    print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Calling local ensure_stripe_js_loaded")
    stripe_pk = ensure_stripe_js_loaded()
    print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Got stripe_pk: {stripe_pk[:10]}...")
    
    # html
    print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Starting to build HTML template")
    self.html = f"""
    <script>
    window.stripe_setup_intent_client_secret = '{client_secret}';
    </script>

    <!-- 1. Note: Stripe.js is now loaded by the centralized system -->

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
    
    // 3. Initialize Stripe and Elements (using the public key from the centralized loader)
    var stripe = Stripe('{stripe_pk}');
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

    print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - HTML template built, length: {len(self.html)}")
    
    # Add JS logging
    anvil.js.call('eval', '''
      console.log("[STRIPE_DEBUG_JS] " + new Date().toISOString() + " - Starting to load Stripe component");
      
      // Monitor when Stripe.js is loaded
      var stripeScriptLoaded = false;
      document.addEventListener("DOMContentLoaded", function() {
        console.log("[STRIPE_DEBUG_JS] " + new Date().toISOString() + " - DOM content loaded");
        
        // Check if Stripe is already in the global namespace
        if (typeof Stripe !== 'undefined') {
          console.log("[STRIPE_DEBUG_JS] " + new Date().toISOString() + " - Stripe already loaded at DOMContentLoaded");
          stripeScriptLoaded = true;
        }
        
        // Monitor script loading
        var scripts = document.getElementsByTagName('script');
        console.log("[STRIPE_DEBUG_JS] " + new Date().toISOString() + " - Found " + scripts.length + " script tags");
        
        for (var i = 0; i < scripts.length; i++) {
          if (scripts[i].src && scripts[i].src.indexOf('stripe') > -1) {
            console.log("[STRIPE_DEBUG_JS] " + new Date().toISOString() + " - Found Stripe script: " + scripts[i].src);
            scripts[i].addEventListener('load', function() {
              console.log("[STRIPE_DEBUG_JS] " + new Date().toISOString() + " - Stripe script loaded");
              stripeScriptLoaded = true;
            });
          }
        }
        
        // Monitor card element rendering
        var cardElementCheck = setInterval(function() {
          var cardElement = document.getElementById('card-element');
          if (cardElement) {
            console.log("[STRIPE_DEBUG_JS] " + new Date().toISOString() + " - Card element found");
            // Check for children to see if it's been populated by Stripe
            if (cardElement.children.length > 0) {
              console.log("[STRIPE_DEBUG_JS] " + new Date().toISOString() + " - Card element has " + cardElement.children.length + " children");
              clearInterval(cardElementCheck);
            }
          }
        }, 500);
      });
      
      // Monitor Stripe variable
      var originalStripeCheck = setInterval(function() {
        if (typeof Stripe !== 'undefined' && !stripeScriptLoaded) {
          console.log("[STRIPE_DEBUG_JS] " + new Date().toISOString() + " - Stripe object detected in global scope");
          stripeScriptLoaded = true;
          clearInterval(originalStripeCheck);
        }
      }, 500);
      
      // Log when elements are created
      var originalCreateElement = Element.prototype.createElement;
      Element.prototype.createElement = function(tagName) {
        var element = originalCreateElement.call(this, tagName);
        if (this.id === 'card-element') {
          console.log("[STRIPE_DEBUG_JS] " + new Date().toISOString() + " - Element created inside card-element");
        }
        return element;
      };
    ''');

    # Register the payment_method_ready and close_alert functions on window for JS to call
    print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Registering JS callback functions")
    anvil.js.window.payment_method_ready = self._payment_method_ready
    anvil.js.window.close_alert = self._close_alert
    print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - C_PaymentInfos.__init__ completed")


  def _close_alert(self):
    """Close the alert dialog from JS."""
    print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - _close_alert called")
    self.raise_event('x-close-alert')


  def _payment_method_ready(self, payment_method_id: str):
    """Called from JS after successful Stripe setup. Handles server calls from Python."""
    print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - _payment_method_ready called with payment_method_id: {payment_method_id[:5]}...")
    try:
        # 1. Get customer info
        print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Looking up Stripe customer for email={self.sub_email}")
        customer = anvil.server.call('get_stripe_customer', self.sub_email)
        print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Got customer response: {bool(customer)}")
        if customer and customer.get('id'):
            print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Found customer {customer['id']}, attaching payment method")
            
            # 2. Attach payment method to customer
            print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Calling attach_payment_method_to_customer")
            updated_customer = anvil.server.call('attach_payment_method_to_customer', 
                                                customer['id'], 
                                                payment_method_id)
            print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Payment method attached successfully")
            Notification("", title="Payment method created!", style="success").show()
          
            # 3. Return success to close the form
            print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Raising x-close-alert event with success value")
            self.raise_event("x-close-alert", value="success")
          
        else:
            # If no customer found, show error
            print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - No customer found, cannot attach payment method")
            Notification("", title="Could not add payment method!", style="error").show()
            return
          
    except Exception as err:
        print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - ERROR: {err}")
        Notification("", title="Could not add payment method!", style="error").show()