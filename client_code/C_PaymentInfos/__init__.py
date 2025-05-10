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
    
    # Initialize variables for async loading
    print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Initializing with default empty values")
    self.client_secret = None
    self.customer = {}
    self.customer_email = self.sub_email  # Default to subscription email
    self.customer_address = {}
    self.address_line1 = ''
    self.address_line2 = ''
    self.city = ''
    self.postal_code = ''
    self.state = ''
    self.country = ''
    
    # Flag to track when data is loaded
    self.stripe_data_loaded = False
    
    # Start loading Stripe.js immediately without waiting for server calls
    print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Starting Stripe.js loading early")
    # Get Stripe public key using the local loader
    print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Calling local ensure_stripe_js_loaded")
    self.stripe_pk = ensure_stripe_js_loaded()
    print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Got stripe_pk: {self.stripe_pk[:10]}...")
    
    # Schedule server calls to run in the background
    def load_stripe_data():
      try:
        # Get the Stripe SetupIntent client_secret from the server
        print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Calling create_setup_intent")
        self.client_secret = anvil.server.call('create_setup_intent')
        print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Received client_secret: {self.client_secret[:10]}...")
        
        # Get customer info for billing_details
        print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Calling get_stripe_customer with email {self.sub_email}")
        self.customer = anvil.server.call('get_stripe_customer', self.sub_email)
        print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Received customer data: {bool(self.customer)}")
        self.customer_email = self.customer.get('email', self.sub_email)
        self.customer_address = self.customer.get('address', {})
        self.address_line1 = self.customer_address.get('line1', '')
        self.address_line2 = self.customer_address.get('line2', '')
        self.city = self.customer_address.get('city', '')
        self.postal_code = self.customer_address.get('postal_code', '')
        self.state = self.customer_address.get('state', '')
        self.country = self.customer_address.get('country', '')
        print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Parsed customer details: email={self.customer_email}, country={self.country}")
        
        # Update form with loaded data
        self.stripe_data_loaded = True
        self.update_form_with_data()
      except Exception as e:
        print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Error loading stripe data: {str(e)}")
        
  def update_form_with_data(self):
    """
    1. Updates the payment form with loaded data 
    2. Shows the form and hides the loading indicator
    3. Updates the client secret for the Stripe form
    
    This method is called when async data loading is complete.
    """
    print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Updating form with loaded data")
    
    # Rebuild the HTML with the loaded data
    self.build_payment_form()
    
    # Use JavaScript to update the form state
    if self.client_secret:
      js_update = f"""
      (function() {{
        console.log("[STRIPE_UPDATE] " + new Date().toISOString() + " - Updating payment form with data");
        
        // Update client secret
        window.stripe_setup_intent_client_secret = '{self.client_secret}';
        
        // Hide loading indicator
        var loadingIndicator = document.getElementById('loading-indicator');
        if (loadingIndicator) loadingIndicator.style.display = 'none';
        
        // Show payment form
        var paymentForm = document.getElementById('payment-form');
        if (paymentForm) paymentForm.style.display = 'block';
        
        console.log("[STRIPE_UPDATE] " + new Date().toISOString() + " - Payment form updated");
      }})();
      """
      
      # Execute the JavaScript to update the form
      anvil.js.call('eval', js_update)
      print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Form updated via JavaScript")
    else:
      print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - No client secret available, form not updated")
    
    # Start loading data in background
    anvil.server.call_s(load_stripe_data)
    
    # Create initial HTML with loading state
    self.build_payment_form()
    
    # Register the payment_method_ready and close_alert functions on window for JS to call
    print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Registering JS callback functions")
    anvil.js.window.payment_method_ready = self._payment_method_ready
    anvil.js.window.close_alert = self._close_alert
    print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - C_PaymentInfos.__init__ completed")

  def build_payment_form(self):
    """
    1. Builds the payment form HTML with or without loaded data
    2. Shows a loading indicator if data is still being fetched
    3. Sets up Stripe.js loading and initialization
    
    This creates the initial HTML structure that will be updated
    once the Stripe data is fully loaded.
    """
    print(f"[STRIPE_DEBUG] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Starting to build HTML template")
    
    # Set the display style for loading indicator and form based on data load status
    loading_display = 'block' if not self.stripe_data_loaded else 'none'
    form_display = 'none' if not self.stripe_data_loaded else 'block'
    
    # Set the client secret JS initialization
    if self.client_secret:
      client_secret_js = f"'{self.client_secret}'"
    else:
      client_secret_js = "null"
      
    self.html = f"""
    <!-- 1. Optional client secret, Stripe public key, and customer details -->
    <script>
    window.stripe_setup_intent_client_secret = {client_secret_js};
    var stripe_pk = "{self.stripe_pk}";
    
    // Customer billing details
    var customer_email = "{self.customer_email}";
    var address_line1 = "{self.address_line1}";
    var address_line2 = "{self.address_line2}";
    var city = "{self.city}";
    var postal_code = "{self.postal_code}";
    var state = "{self.state}";
    var country = "{self.country}";
    </script>

    <!-- 2. Payment Form Container -->
    <div id="payment-form-container">    
        <!-- 2.1 Title and instructions -->
        <h2>Add payment details</h2>
        <div class="payment-info-text">Add your credit card details below. This card will be saved to your account and can be removed at any time.</div>
        
        <!-- 2.2 Loading indicator (shown until data is loaded) -->
        <div id="loading-indicator" style="display: {loading_display}">
            <div class="spinner" style="margin: 20px auto; border: 4px solid #f3f3f3; border-top: 4px solid #FF7A00; border-radius: 50%; width: 30px; height: 30px; animation: spin 1s linear infinite;"></div>
            <p style="text-align: center;">Loading payment form...</p>
        </div>
        <style>
            @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        </style>
        
        <!-- 2.3 Custom payment form (hidden until data is loaded) -->
        <form id="payment-form" style="display: {form_display}">
            <!-- 2.3.1 Card information section -->
            <div class="form-section">                
                <h3>Card information</h3>
                <div id="card-element"></div>
            </div>

            <!-- 2.3.2 Name on card field -->
            <div class="form-section">                
                <h3>Name on card</h3>
                <input id="name-on-card" name="name-on-card" type="text" autocomplete="cc-name" required placeholder="Name on card">
            </div>

            <!-- 2.3.3 Error display and buttons -->
            <div id="card-errors" role="alert"></div>
            <div class="button-row">                
                <button type="button" id="cancel-btn">Cancel</button>
                <button id="submit" type="submit">Save payment details</button>
            </div>
        </form>
    </div>

    <script>
    // 1. Define variables in global scope
    var stripe, elements, cardElement, form, nameInput, submitBtn;
    var initStartTime = new Date();
    console.log("[STRIPE_TIMING] " + initStartTime.toISOString() + " - Payment form initialization started");
    
    // Function to measure elapsed time
    function logElapsedTime(label) {{
      var now = new Date();
      var elapsed = now - initStartTime;
      console.log("[STRIPE_TIMING] " + now.toISOString() + " - " + label + " (" + elapsed + "ms elapsed)");
      return now;
    }}
    
    // 2. Check if DOM is already loaded or wait for it
    function domReady(callback) {{
      if (document.readyState === 'complete' || document.readyState === 'interactive') {{
        console.log("[STRIPE_INIT] " + new Date().toISOString() + " - DOM already ready");
        logElapsedTime("DOM ready check completed");
        setTimeout(callback, 1);
      }} else {{
        console.log("[STRIPE_INIT] " + new Date().toISOString() + " - Waiting for DOM to be ready");
        document.addEventListener('DOMContentLoaded', callback);
        logElapsedTime("Added DOM ready listener");
      }}
    }}
    
    // 3. Main initialization function
    domReady(function() {{
      console.log("[STRIPE_INIT] " + new Date().toISOString() + " - DOM ready, checking for Stripe");
      logElapsedTime("Ready to check for Stripe object");
      
      // 4. Wait for Stripe to be available before initializing
      (function checkStripeAndInitialize() {{
        if (typeof Stripe === 'undefined') {{
          console.log("[STRIPE_INIT] " + new Date().toISOString() + " - Waiting for Stripe to load...");
          setTimeout(checkStripeAndInitialize, 50);
          return;
        }}
        
        console.log("[STRIPE_INIT] " + new Date().toISOString() + " - Stripe loaded, initializing Elements");
        
        try {{
          // 5. Initialize Stripe with public key
          var stripeStartTime = new Date();
          stripe = Stripe(stripe_pk); // Use the global stripe_pk variable
          var stripeInitTime = new Date() - stripeStartTime;
          console.log("[STRIPE_INIT] " + new Date().toISOString() + " - Stripe object created in " + stripeInitTime + "ms");
          logElapsedTime("Stripe object initialized");
          
          // 6. Create Stripe Elements instance
          var elementsStartTime = new Date();
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
          var elementsInitTime = new Date() - elementsStartTime;
          console.log("[STRIPE_INIT] " + new Date().toISOString() + " - Elements created in " + elementsInitTime + "ms");
          logElapsedTime("Stripe Elements instance created");
          
          // 7. Verify DOM elements before proceeding
          var cardElementContainer = document.getElementById('card-element');
          var formElement = document.getElementById('payment-form');
          var nameInputElement = document.getElementById('name-on-card');
          var submitBtnElement = document.getElementById('submit');
          
          if (!cardElementContainer) {{
            console.error("[STRIPE_INIT] " + new Date().toISOString() + " - Card element container not found");
            // Try again later
            setTimeout(checkStripeAndInitialize, 100);
            return;
          }}
          
          if (!formElement || !nameInputElement || !submitBtnElement) {{
            console.error("[STRIPE_INIT] " + new Date().toISOString() + " - Form elements not found");
            // Try again later
            setTimeout(checkStripeAndInitialize, 100);
            return;
          }}
          
          // 8. Create and mount card element
          var cardStartTime = new Date();
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
          var cardCreationTime = new Date() - cardStartTime;
          console.log("[STRIPE_INIT] " + new Date().toISOString() + " - Card element created in " + cardCreationTime + "ms, mounting to #card-element");
          logElapsedTime("Card element created");
          
          var mountStartTime = new Date();
          cardElement.mount('#card-element');
          var mountTime = new Date() - mountStartTime;
          console.log("[STRIPE_INIT] " + new Date().toISOString() + " - Card element mounted in " + mountTime + "ms");
          logElapsedTime("Card element mounted");
          
          // Start monitoring when card becomes fully interactive
          var interactivityCheckInterval = setInterval(function() {{
            try {{
              var cardIframe = document.querySelector('#card-element iframe');
              if (cardIframe && cardIframe.contentDocument) {{
                clearInterval(interactivityCheckInterval);
                logElapsedTime("Card iframe content accessible - likely interactive");
              }}
            }} catch (e) {{
              // Silent catch - cross-origin restrictions might prevent checking iframe content
            }}
          }}, 100);
          
          // 9. Assign form elements to variables
          form = formElement;
          nameInput = nameInputElement;
          submitBtn = submitBtnElement;
          logElapsedTime("Form elements assigned");
          
          // 10. Form validation function with timing measurement
          function validateForm() {{
            var validateStartTime = new Date();
            logElapsedTime("Starting form validation");
            
            var nameComplete = nameInput.value.trim().length > 0;
            var cardComplete = false;
            if (cardElement && typeof cardElement._complete !== 'undefined') {{
              cardComplete = cardElement._complete;
            }} else if (cardElement && typeof cardElement._implementation !== 'undefined' && typeof cardElement._implementation._complete !== 'undefined') {{
              cardComplete = cardElement._implementation._complete;
            }}
            var formValid = cardComplete && nameComplete;
            
            // Log card element completion status
            logElapsedTime("Card completion state: " + (cardComplete ? "complete" : "incomplete"));
            
            if (formValid) {{
              submitBtn.removeAttribute('disabled');
              submitBtn.style.backgroundColor = '#FF7A00';
              submitBtn.style.opacity = '1';
              logElapsedTime("Form valid - submit button enabled");
            }} else {{
              submitBtn.setAttribute('disabled', 'disabled');
              submitBtn.style.backgroundColor = '#ccc';
              submitBtn.style.opacity = '0.7';
            }}
            
            var validateTime = new Date() - validateStartTime;
            console.log("[STRIPE_TIMING] " + new Date().toISOString() + " - Validation completed in " + validateTime + "ms");
            return formValid;
          }}
          
          // 11. Setup event handlers with timing
          nameInput.addEventListener('input', function() {{
            logElapsedTime("Name input event triggered");
            validateForm();
          }});
          
          cardElement.on('change', function(event) {{
            logElapsedTime("Card change event: " + (event.complete ? "complete" : "incomplete"));
            
            if (event.error) {{
              document.getElementById('card-errors').textContent = event.error.message;
              logElapsedTime("Card error: " + event.error.message);
            }} else {{
              document.getElementById('card-errors').textContent = '';
            }}
            cardElement._complete = event.complete;
            validateForm();
          }});
          
          // 12. Validation on field blur with timing
          cardElement.on('blur', function(event) {{
            logElapsedTime("Card blur event triggered");
            validateForm();
          }});
          
          cardElement._complete = false;
          form.addEventListener('input', validateForm);
          
          // Initial validation
          logElapsedTime("Running initial form validation");
          validateForm();
          
          // 13. Form submission handler with timing
          form.addEventListener('submit', function(event) {{
            event.preventDefault();
            logElapsedTime("Form submission started");
            
            var nameValue = nameInput.value;
            document.getElementById('card-errors').textContent = '';
            submitBtn.disabled = true;
            var billingDetails = {{
              name: nameValue,
              email: customer_email,
              address: {{
                line1: address_line1,
                line2: address_line2,
                city: city,
                postal_code: postal_code,
                state: state,
                country: country
              }}
            }};
            logElapsedTime("Starting card setup confirmation");
            var setupStartTime = new Date();
            
            stripe.confirmCardSetup(window.stripe_setup_intent_client_secret, {{
              payment_method: {{
                card: cardElement,
                billing_details: billingDetails
              }}
            }}).then(function(result) {{
              var setupTime = new Date() - setupStartTime;
              logElapsedTime("Card setup confirmation completed in " + setupTime + "ms");
              
              if (result.error) {{
                document.getElementById('card-errors').textContent = result.error.message;
                submitBtn.disabled = false;
                logElapsedTime("Card setup failed: " + result.error.message);
              }} else {{
                logElapsedTime("Card setup successful");
                if (typeof window.payment_method_ready === 'function') {{
                  window.payment_method_ready(result.setupIntent.payment_method);
                }}
              }}
            }});
          }});
          
          // 14. Cancel button handler with timing
          var cancelBtn = document.getElementById('cancel-btn');
          if (cancelBtn) {{
            cancelBtn.onclick = function() {{ 
              logElapsedTime("Cancel button clicked");
              window.close_alert(); 
            }};
            logElapsedTime("Cancel button handler initialized");
          }}
          
          // Final initialization complete
          logElapsedTime("ALL INITIALIZATION COMPLETE - FORM SHOULD BE FULLY INTERACTIVE");
          console.log("[STRIPE_INIT] " + new Date().toISOString() + " - All Stripe elements initialized successfully");
          
          // Start a final check to monitor interactive status every second for 15 seconds
          var readyCheckCount = 0;
          var readyCheckInterval = setInterval(function() {{
            readyCheckCount++;
            logElapsedTime("Interactive check #" + readyCheckCount);
            
            // Stop after 15 checks
            if (readyCheckCount >= 15) {{
              clearInterval(readyCheckInterval);
              logElapsedTime("Interactive monitoring complete");
            }}
          }}, 1000);
          
        }} catch (error) {{
          console.error("[STRIPE_INIT] " + new Date().toISOString() + " - Error initializing Stripe: " + error.message);
          logElapsedTime("ERROR during initialization: " + error.message);
        }}
      }})();
    }});
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