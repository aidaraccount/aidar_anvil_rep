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

    <!-- 1. Performance optimization: DNS Preconnect for Stripe domains -->
    <link rel="preconnect" href="https://js.stripe.com" crossorigin>
    <link rel="preconnect" href="https://api.stripe.com" crossorigin>
    <link rel="preconnect" href="https://m.stripe.network" crossorigin>
    <link rel="preconnect" href="https://b.stripecdn.com" crossorigin>
    
    <!-- 2. CSS for loading state -->
    <style>
      #stripe-loading-overlay {{
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(24, 24, 24, 0.8);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        z-index: 1000;
        color: white;
      }}
      
      .stripe-spinner {{
        width: 40px;
        height: 40px;
        border: 4px solid rgba(255, 122, 0, 0.3);
        border-radius: 50%;
        border-top-color: #FF7A00;
        animation: stripe-spin 1s linear infinite;
        margin-bottom: 15px;
      }}
      
      @keyframes stripe-spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
      }}
      
      #payment-form-container {{
        position: relative;
        min-height: 300px;
      }}
      
      #card-element {{
        background-color: #333;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 10px;
      }}
    </style>
    
    <!-- 3. Stripe.js script with optimized loading strategy -->
    <script>
    // Define messages only if not already defined
    if (typeof window.STRIPE_MESSAGES === 'undefined') {{
      window.STRIPE_MESSAGES = {{
        cardError: 'There was an error processing your card. Please check your card details and try again.',
        success: 'Your card has been saved successfully!',
        processing: 'Processing your card...',
        serverError: 'There was a server error. Please try again later.',
        loading: 'Loading payment form...'
      }};
    }}
    
    // Debug utilities for tracking UI performance and blocking
    if (typeof window.STRIPE_DEBUG === 'undefined') {{
      window.STRIPE_DEBUG = {{
        // Flag to enable periodic interval checking (for Anvil/Stripe specific issues)
        enablePeriodicCheck: true,
        // Track frame rate and main thread blocking
        frameTimeLog: [],
        lastFrameTime: performance.now(),
        inputEventCount: 0,
        blockingEvents: [],
        isMonitoring: false,
        longTaskObserver: null,
        blockThreshold: 100, // ms threshold to consider UI blocked
        
        // Start monitoring performance
        startMonitoring: function() {{
          const debug = this;
          
          // Special Anvil-specific check for periodic blocking
          if (this.enablePeriodicCheck) {{
            // Check for periodic blocking patterns every 250ms
            this.periodicCheckInterval = setInterval(function() {{
              const now = performance.now();
              const inputField = document.querySelector('#card-element iframe');
              
              if (inputField) {{
                // Test if input field is responding
                try {{
                  // Create a MutationObserver to watch for iframe style changes
                  // which might indicate blocking
                  if (!debug.mutationObserver) {{
                    debug.mutationObserver = new MutationObserver(function(mutations) {{
                      mutations.forEach(function(mutation) {{
                        if (mutation.type === 'attributes' && mutation.attributeName === 'style') {{
                          debug.blockingEvents.push({{
                            timestamp: performance.now(),
                            type: 'iframe-style-change',
                            target: mutation.target.id || 'stripe-iframe',
                            oldValue: mutation.oldValue,
                            newValue: mutation.target.style.cssText
                          }});
                          console.warn('[Stripe Debug] Iframe style changed', mutation);
                        }}
                      }});
                    }});
                    
                    // Observe all style attribute changes on the iframe
                    debug.mutationObserver.observe(inputField, {{
                      attributes: true,
                      attributeFilter: ['style'],
                      attributeOldValue: true
                    }});
                    
                    console.log('[Stripe Debug] Started monitoring iframe style changes');
                  }}
                }} catch (e) {{
                  console.warn('[Stripe Debug] Error setting up iframe monitoring:', e);
                }}
              }}
            }}, 250);
          }}
          if (this.isMonitoring) return;
          
          console.log('[Stripe Debug] Starting performance monitoring');
          this.isMonitoring = true;
          this.frameTimeLog = [];
          this.blockingEvents = [];
          this.lastFrameTime = performance.now();
          
          // Set up frame rate monitoring
          const debug = this;
          this.frameId = requestAnimationFrame(function frameLogger() {{
            const now = performance.now();
            const frameDelta = now - debug.lastFrameTime;
            
            // Log frames that took too long (potential blocking)
            if (frameDelta > debug.blockThreshold) {{
              debug.blockingEvents.push({{
                timestamp: now,
                duration: frameDelta,
                type: 'frame-drop',
                stack: new Error().stack
              }});
              console.warn(`[Stripe Debug] UI blocked for ${{frameDelta.toFixed(2)}}ms`);
            }}
            
            debug.frameTimeLog.push(frameDelta);
            if (debug.frameTimeLog.length > 100) debug.frameTimeLog.shift();
            debug.lastFrameTime = now;
            
            // Continue monitoring
            if (debug.isMonitoring) {{
              debug.frameId = requestAnimationFrame(frameLogger);
            }}
          }});
          
          // Monitor long tasks using the Long Tasks API if available
          if (window.PerformanceObserver && window.PerformanceLongTaskTiming) {{
            try {{
              this.longTaskObserver = new PerformanceObserver((entries) => {{
                entries.getEntries().forEach((entry) => {{
                  debug.blockingEvents.push({{
                    timestamp: performance.now(),
                    duration: entry.duration,
                    type: 'long-task',
                    attribution: entry.attribution,
                    detail: entry
                  }});
                  console.warn(`[Stripe Debug] Long task detected: ${{entry.duration.toFixed(2)}}ms`, entry);
                }});
              }});
              this.longTaskObserver.observe({{ entryTypes: ['longtask'] }});
            }} catch (e) {{
              console.warn('[Stripe Debug] Long Tasks API not supported', e);
            }}
          }}
          
          // Track input events to detect responsiveness
          this.inputHandler = function(e) {{
            debug.inputEventCount++;
            // Check if input is in the card element iframe
            if (e.target && e.target.tagName === 'IFRAME' && e.target.closest('#card-element')) {{
              // Record the input time to analyze if blocking occurs after input
              debug.blockingEvents.push({{
                timestamp: performance.now(),
                type: 'input-event',
                target: e.target.id || 'iframe'
              }});
            }}
          }}
          
          document.addEventListener('keydown', this.inputHandler, true);
          document.addEventListener('mousedown', this.inputHandler, true);
          
          // Monitor network activity
          if (window.performance && window.performance.getEntriesByType) {{
            setInterval(() => {{
              const resources = window.performance.getEntriesByType('resource');
              const stripeResources = resources.filter(r => 
                r.name.includes('stripe.com') || 
                r.name.includes('stripecdn.com') || 
                r.name.includes('stripe.network')
              );
              
              // Log slow resources
              stripeResources.forEach(r => {{
                if (r.duration > 500) {{
                  console.warn(`[Stripe Debug] Slow resource: ${{r.name}} (${{r.duration.toFixed(2)}}ms)`);
                  debug.blockingEvents.push({{
                    timestamp: performance.now(),
                    duration: r.duration,
                    type: 'network',
                    resource: r.name
                  }});
                }}
              }});
            }}, 2000);
          }}
        }},
        
        // Stop monitoring
        stopMonitoring: function() {{
          if (!this.isMonitoring) return;
          
          this.isMonitoring = false;
          cancelAnimationFrame(this.frameId);
          
          if (this.longTaskObserver) {{
            this.longTaskObserver.disconnect();
          }}
          
          if (this.mutationObserver) {{
            this.mutationObserver.disconnect();
          }}
          
          if (this.periodicCheckInterval) {{
            clearInterval(this.periodicCheckInterval);
          }}
          
          document.removeEventListener('keydown', this.inputHandler, true);
          document.removeEventListener('mousedown', this.inputHandler, true);
          
          console.log('[Stripe Debug] Stopped monitoring');
        }},
        
        // Get a summary of blocking events
        getBlockingSummary: function() {{
          if (this.blockingEvents.length === 0) {{
            return 'No blocking events detected';
          }}
          
          const typeCount = this.blockingEvents.reduce((acc, event) => {{
            acc[event.type] = (acc[event.type] || 0) + 1;
            return acc;
          }}, {{}});
          
          const avgDuration = this.blockingEvents
            .filter(e => e.duration)
            .reduce((sum, e) => sum + e.duration, 0) / 
            this.blockingEvents.filter(e => e.duration).length;
          
          return `Detected ${{this.blockingEvents.length}} blocking events: ` + 
                 Object.entries(typeCount).map(([type, count]) => 
                   `${{type}}: ${{count}}`
                 ).join(', ') + 
                 `. Average duration: ${{avgDuration ? avgDuration.toFixed(2) : 0}}ms`;
        }}
      }};
    }}
    
    // Initialize Stripe loading with improved loading strategy
    function loadStripeJS() {{
      return new Promise(function(resolve) {{
        function checkStripeLoaded() {{
          if (typeof window.Stripe !== 'undefined') {{
            resolve(window.Stripe);
            return true;
          }}
          return false;
        }}
        
        // Check if already loaded
        if (checkStripeLoaded()) return;
        
        // Create script element with high priority loading
        var stripeScript = document.createElement('script');
        stripeScript.src = 'https://js.stripe.com/v3/';
        stripeScript.setAttribute('importance', 'high');
        stripeScript.async = true;
        stripeScript.onload = function() {{
          // Check again after the script loads
          checkStripeLoaded();
        }};
        
        // Insert at the beginning of head for higher priority
        if (document.head.firstChild) {{
          document.head.insertBefore(stripeScript, document.head.firstChild);
        }} else {{
          document.head.appendChild(stripeScript);
        }}
        
        // Fallback check in case the onload event doesn't fire
        var checkInterval = setInterval(function() {{
          if (checkStripeLoaded()) {{
            clearInterval(checkInterval);
          }}
        }}, 100);
      }});
    }}
    </script>

    <!-- 4. Payment Form Container -->
    <div id="payment-form-container">    
        <!-- 4.1 Loading overlay -->
        <div id="stripe-loading-overlay">
            <div class="stripe-spinner"></div>
            <div id="loading-message">Loading payment form...</div>
        </div>
        
        <!-- 4.2 Title and instructions -->
        <h2>Add payment details</h2>
        <div class="payment-info-text">Add your credit card details below. This card will be saved to your account and can be removed at any time.</div>
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
    
    // Show loading state
    document.getElementById('loading-message').textContent = window.STRIPE_MESSAGES.loading;
    
    // Automatically start performance monitoring
    window.STRIPE_DEBUG.startMonitoring();
    console.log('[Stripe Debug] You can check the performance data with window.STRIPE_DEBUG.getBlockingSummary() in browser console');
    console.log('[Stripe Debug] To see all collected blocking events: console.table(window.STRIPE_DEBUG.blockingEvents);');
    
    // Initialize the form only after Stripe.js is fully loaded
    loadStripeJS().then(function(StripeJS) {{
      // Small delay to ensure browser resources are available
      setTimeout(function() {{
        try {{
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
          
          // Hide loading overlay once the card element is ready
          cardElement.on('ready', function() {{
            document.getElementById('stripe-loading-overlay').style.display = 'none';
          }});

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
        }} catch(e) {{
          console.error('Error initializing Stripe:', e);
          document.getElementById('loading-message').textContent = 'Error loading payment form';
        }}
      }}, 100); // Small delay for browser to settle
    
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