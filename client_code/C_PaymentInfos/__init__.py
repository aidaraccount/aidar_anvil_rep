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
        
        # 1. Get user data and setup Stripe
        # 1.1 Get subscription email
        base_data = anvil.server.call('get_settings_subscription2', user["user_id"])
        if base_data is not None:
            base_data = json.loads(base_data)[0]
            self.sub_email = base_data['mail'] if 'mail' in base_data else None
        else:
            self.sub_email = user['email']
        
        # 1.2 Get the Stripe publishable key from the server
        stripe_publishable_key = anvil.server.call('get_stripe_publishable_key')
        
        # 1.3 Get the Stripe SetupIntent client_secret
        client_secret = anvil.server.call('create_setup_intent', self.sub_email)
        
        # 1.4 Get customer info for billing_details
        customer = anvil.server.call('get_stripe_customer', self.sub_email)
        customer_email = customer.get('email', '')
        customer_address = customer.get('address', {})
        address_line1 = customer_address.get('line1', '')
        address_line2 = customer_address.get('line2', '')
        city = customer_address.get('city', '')
        postal_code = customer_address.get('postal_code', '')
        state = customer_address.get('state', '')
        country = customer_address.get('country', '')
        
        # 2. Register JS callbacks
        anvil.js.window.payment_method_ready = self._payment_method_ready
        anvil.js.window.close_alert = self._close_alert
        
        # 3. Create HTML template for optimized Stripe integration with proper escaping
        html_template = f"""
<!DOCTYPE html>
<html>
    <script>
      // Store configuration securely
      const STRIPE_CONFIG = {{
        clientSecret: '{client_secret}',
        publishableKey: '{stripe_publishable_key}',
        customerEmail: '{customer_email}',
        address: {{
          line1: '{address_line1}',
          line2: '{address_line2}',
          city: '{city}',
          postal_code: '{postal_code}',
          state: '{state}',
          country: '{country}'
        }}
      }};
    </script>

    <!-- 1. DNS optimization -->
    <link rel="preconnect" href="https://js.stripe.com" crossorigin>
    <link rel="preconnect" href="https://api.stripe.com" crossorigin>
    
    <!-- 2. CSS styles -->
    <style>
      /* 2.1 Payment form container */
      #payment-form-container {{
        position: relative;
        font-family: Inter, "Segoe UI", sans-serif;
        color: #ffffff;
        padding: 10px 0;
      }}
      
      /* 2.2 Loading spinner */
      #loading-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100px;
        margin: 20px 0;
      }}
      
      .spinner {{
        width: 40px;
        height: 40px;
        border: 4px solid rgba(255, 122, 0, 0.3);
        border-radius: 50%;
        border-top-color: #FF7A00;
        animation: spin 1s linear infinite;
      }}
      
      @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
      }}
      
      /* 2.3 Form elements */
      #payment-form {{
        margin-top: 20px;
      }}
      
      .form-section {{
        margin-bottom: 20px;
      }}
      
      .form-section h3 {{
        margin-bottom: 8px;
        font-size: 16px;
        font-weight: 500;
      }}
      
      #card-element {{
        background-color: #292929;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 16px;
      }}
      
      #name-on-card {{
        width: 100%;
        padding: 12px;
        background-color: #292929;
        border: none;
        border-radius: 8px;
        color: #ffffff;
        font-size: 16px;
        font-family: inherit;
      }}
      
      /* 2.4 Feedback and controls */
      #card-errors {{
        color: #FF5A36;
        margin-bottom: 16px;
        min-height: 20px;
      }}
      
      .button-row {{
        display: flex;
        justify-content: space-between;
        margin-top: 20px;
      }}
      
      button {{
        padding: 12px 24px;
        border: none;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 500;
        cursor: pointer;
      }}
      
      #cancel-btn {{
        background-color: transparent;
        color: #ffffff;
        border: 1px solid #555555;
      }}
      
      #submit {{
        background-color: #FF7A00;
        color: #ffffff;
      }}
      
      #submit:disabled {{
        background-color: #cccccc;
        opacity: 0.7;
        cursor: not-allowed;
      }}
      
      .success-message {{
        color: #00C853;
      }}
    </style>
    
    <!-- 3. Payment form structure -->
    <div id="payment-form-container">
      <!-- 3.1 Loading state -->
      <div id="loading-container">
        <div class="spinner"></div>
      </div>
      
      <!-- 3.2 Form content (hidden until loaded) -->
      <div id="form-content" style="display: none;">
        <h2>Add payment details</h2>
        <div class="payment-info-text">Add your credit card details below. This card will be saved to your account and can be removed at any time.</div>
        
        <form id="payment-form">
          <!-- Card element section -->
          <div class="form-section">
            <h3>Card information</h3>
            <div id="card-element"></div>
          </div>
          
          <!-- Name field section -->
          <div class="form-section">
            <h3>Name on card</h3>
            <input id="name-on-card" name="name-on-card" type="text" autocomplete="cc-name" required placeholder="Name on card">
          </div>
          
          <!-- Feedback and controls -->
          <div id="card-errors" role="alert"></div>
          <div class="button-row">
            <button type="button" id="cancel-btn">Cancel</button>
            <button id="submit" type="submit" disabled>Save payment details</button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- 4. Stripe integration script -->
    <script src="https://js.stripe.com/v3/"></script>
    
    <!-- 5. Payment processing logic -->
    <script>
      // 5.1 Performance monitoring utilities
      const STRIPE_DEBUG = {
        // Configuration
        enabled: true,
        blockThreshold: 100, // ms threshold to consider UI blocked
        
        // State tracking
        frameTimeLog: [],
        lastFrameTime: performance.now(),
        inputEventCount: 0,
        blockingEvents: [],
        isMonitoring: false,
        longTaskObserver: null,
        mutationObserver: null,
        
        // Start monitoring performance
        startMonitoring: function() {
          if (this.isMonitoring) return;
          
          // Store 'this' reference for closures
          const self = this;
          
          console.log('[Stripe Debug] Starting performance monitoring');
          this.isMonitoring = true;
          this.frameTimeLog = [];
          this.blockingEvents = [];
          this.lastFrameTime = performance.now();
          
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
                  if (!self.mutationObserver) {{
                    self.mutationObserver = new MutationObserver(function(mutations) {{
                      mutations.forEach(function(mutation) {{
                        if (mutation.type === 'attributes' && mutation.attributeName === 'style') {{
                          self.blockingEvents.push({{
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
                    self.mutationObserver.observe(inputField, {{
                      attributes: true,
                      attributeFilter: ['style'],
                      attributeOldValue: true
                    }});
                    
                    console.log('[Stripe Debug] Started monitoring iframe style changes');
            
            // Log significant frame time (potential stutter)
            if (frameTime > self.blockThreshold) {
              self.blockingEvents.push({
                type: 'frame_drop',
                duration: frameTime,
                timestamp: timestamp
              });
              console.warn(`Stripe UI: Frame drop detected - ${frameTime.toFixed(2)}ms`);
            }
            
            self.frameTimeLog.push(frameTime);
            // Keep log size reasonable
            if (self.frameTimeLog.length > 300) {
              self.frameTimeLog.shift();
            }
            
            self.lastFrameTime = timestamp;
            
            // Continue monitoring
            if (self.isMonitoring) {
              requestAnimationFrame(frameRateCheck);
            }
          }
          
          // 2. Track long tasks with PerformanceObserver
          if (window.PerformanceObserver && PerformanceObserver.supportedEntryTypes && 
              PerformanceObserver.supportedEntryTypes.includes('longtask')) {
              
            this.longTaskObserver = new PerformanceObserver((entryList) => {
              for (const entry of entryList.getEntries()) {
                self.blockingEvents.push({
                  type: 'long_task',
                  duration: entry.duration,
                  timestamp: performance.now(),
                  attribution: entry.attribution && entry.attribution[0] ? 
                               entry.attribution[0].name : 'unknown'
                });
                console.warn(`Stripe UI: Long task detected - ${entry.duration.toFixed(2)}ms`);
              }
            });
            
            try {
              this.longTaskObserver.observe({ entryTypes: ['longtask'] });
            } catch (e) {
              console.error('Error setting up longtask observer:', e);
            }
          }
          
          // 3. Track user input events
          const cardElement = document.getElementById('card-element');
          if (cardElement) {
            const inputHandler = function(event) {
              self.inputEventCount++;
              // Track when last input was received
              self.lastInputTime = performance.now();
            };
            
            const inputEvents = ['keydown', 'keyup', 'input', 'change', 'focus', 'blur'];
            
            inputEvents.forEach(eventType => {
              cardElement.addEventListener(eventType, inputHandler);
            });
            
            // Track Stripe iframe style changes which might indicate blocking
            const stripeIframes = document.querySelectorAll('#card-element iframe');
            if (stripeIframes.length > 0 && window.MutationObserver) {
              this.mutationObserver = new MutationObserver((mutations) => {
                for (const mutation of mutations) {
                  if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                    self.blockingEvents.push({
                      type: 'iframe_style_change',
                      timestamp: performance.now(),
                      element: mutation.target.outerHTML.substring(0, 100) + '...'
                    });
                    console.log('Stripe iframe style changed:', mutation);
                  }
                }
              });
              
              stripeIframes.forEach(iframe => {
                try {
                  this.mutationObserver.observe(iframe, {
                    attributes: true,
                    attributeFilter: ['style']
                  });
                } catch (e) {
                  console.error('Error setting up mutation observer:', e);
                }
              });
            }
          }
          
          // Mark as monitoring
          this.isMonitoring = true;
          requestAnimationFrame(frameRateCheck);
          console.log('Stripe UI monitoring started');
        },
        
        // Stop monitoring performance
        stopMonitoring: function() {
          this.isMonitoring = false;
          
          if (this.longTaskObserver) {
            this.longTaskObserver.disconnect();
          }
          
          if (this.mutationObserver) {
            this.mutationObserver.disconnect();
          }
          
          console.log('Stripe UI monitoring stopped');
        },
        
        // Get a summary of blocking events
        getBlockingSummary: function() {
          const frameTimes = this.frameTimeLog.filter(time => time > this.blockThreshold);
          const avgBlockingFrameTime = frameTimes.length ? 
                frameTimes.reduce((sum, time) => sum + time, 0) / frameTimes.length : 0;
          
          return {
            totalBlockingEvents: this.blockingEvents.length,
            avgBlockingFrameTime: avgBlockingFrameTime.toFixed(2),
            blockingFramesCount: frameTimes.length,
            inputEventCount: this.inputEventCount,
            events: this.blockingEvents
          };
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

  // Load Stripe.js
  function loadStripeJS() {
    return new Promise(function(resolve) {
      function checkStripeLoaded() {
        if (typeof window.Stripe !== 'undefined') {
          resolve(window.Stripe);
          return true;
        }
        return false;
      }

      // Check if already loaded
      if (checkStripeLoaded()) return;

      // Create script element with high priority loading
      var stripeScript = document.createElement('script');
      stripeScript.src = 'https://js.stripe.com/v3/';
      stripeScript.setAttribute('importance', 'high');
      stripeScript.async = true;
      stripeScript.onload = function() {
        // Check again after the script loads
        checkStripeLoaded();
      };

      // Insert at the beginning of head for higher priority
      if (document.head.firstChild) {
        document.head.insertBefore(stripeScript, document.head.firstChild);
      } else {
        document.head.appendChild(stripeScript);
      }
    // 3. Initialize Stripe and Elements
    // Wait for Stripe to load first, then initialize
    const stripePublishableKey = window.ANVIL_STRIPE_PUBLISHABLE_KEY || 'pk_test_51RDoXJQTBcqmUQgt9CqdDXQjtHKkEkEBuXSs7EqVjwkzqcWP66EgCu8jjYArvbioeYpzvS5wSvbrUsKUtjXi0gGq00M9CzHJTa';
    var stripe, elements, cardElement;
    
    // Show loading state
    document.getElementById('loading-message').textContent = window.STRIPE_MESSAGES.loading;
    
    // Set up initialization in a safe way with a small delay
    setTimeout(function() {{
      try {{
        // Show loading state
        if (STRIPE_DEBUG.enabled) {
          STRIPE_DEBUG.startMonitoring();
        }
        
        // Mount card element and handle UI
        cardElement.mount('#card-element');
        
        // Handle ready state
        cardElement.on('ready', function() {
          // Hide loading state, show form
          loadingContainer.style.display = 'none';
          formContent.style.display = 'block';
          
          // Enable submit button when input is complete
          submitButton.disabled = false;
        });
        
        // Handle card validation errors
        cardElement.on('change', function(event) {
          if (event.error) {
            cardErrors.textContent = event.error.message;
          } else {
            cardErrors.textContent = '';
          }
        });
        
        // Handle form submission
        form.addEventListener('submit', function(event) {
          event.preventDefault();
          
          // Disable submit button during processing
          submitButton.disabled = true;
          submitButton.textContent = MESSAGES.processing;
          
          // Get name input value
          const nameInput = document.getElementById('name-on-card');
          const cardholderName = nameInput.value;
          
          // Get billing details from config
          const billingDetails = {
            name: cardholderName,
            email: STRIPE_CONFIG.customerEmail,
            address: STRIPE_CONFIG.address
          };
          
          // Confirm card setup
          stripe.confirmCardSetup(STRIPE_CONFIG.clientSecret, {
            payment_method: {
              card: cardElement,
              billing_details: billingDetails
            }
          }).then(function(result) {
            if (result.error) {
              // Show error message
              cardErrors.textContent = result.error.message || MESSAGES.cardError;
              submitButton.disabled = false;
              submitButton.textContent = 'Save payment details';
            } else {
              // Success - card setup complete
              cardErrors.textContent = MESSAGES.success;
              cardErrors.className = 'success-message';
              submitButton.textContent = 'Saved';
              
              // Notify Anvil that setup was successful
              if (typeof anvil !== 'undefined') {
                anvil.call('stripe_setup_complete', result.setupIntent.payment_method);
              }
              
              // Close form after short delay
              setTimeout(function() {
                if (typeof anvil !== 'undefined') {
                  anvil.closeForm();
                }
              }, 1500);
            }
          });
        });
        
        // Handle cancel button
        document.getElementById('cancel-btn').addEventListener('click', function() {
          if (typeof anvil !== 'undefined') {
            anvil.closeForm();
          }
        });
      }} catch (err) {{
        console.error('[Stripe Debug] Error during initialization:', err);
      }}
{{ ... }}
          cardElement.on('blur', function(event) {{
        validateForm();
    }});
          cardElement._complete = false;
          form.addEventListener('input', validateForm);
          validateForm()
      
      // 5.2 User messages
      const MESSAGES = {
        cardError: 'There was an error processing your card. Please check your card details and try again.',
        success: 'Your card has been saved successfully!',
        processing: 'Processing your card...',
        serverError: 'There was a server error. Please try again later.',
        loading: 'Loading payment form...'
      };
      
      // 5.3 Main initialization function
      document.addEventListener('DOMContentLoaded', function() {
        // References to DOM elements
        const loadingContainer = document.getElementById('loading-container');
        const formContent = document.getElementById('form-content');
        const form = document.getElementById('payment-form');
        const submitButton = document.getElementById('submit');
        const cardErrors = document.getElementById('card-errors');
        
        // Initialize Stripe with publishable key
        const stripe = Stripe(STRIPE_CONFIG.publishableKey);
        const elements = stripe.elements();

        // Create card element
        const cardElement = elements.create('card', {
          style: {
            base: {
              color: '#ffffff',
              fontFamily: 'Inter, "Segoe UI", sans-serif',
              fontSmoothing: 'antialiased',
              fontSize: '16px',
              '::placeholder': {
                color: '#aab7c4'
              }
            },
  
  // 5.2 User messages
  const MESSAGES = {
    cardError: 'There was an error processing your card. Please check your card details and try again.',
        }
      });
    });

    // Handle cancel button
    document.getElementById('cancel-btn').addEventListener('click', function() {
      if (typeof anvil !== 'undefined') {
        anvil.closeForm();
      }
    });
  } catch (err) {
    console.error('[Stripe Debug] Error during initialization:', err);
  }
});

// 5.2 User messages
const MESSAGES = {
  cardError: 'There was an error processing your card. Please check your card details and try again.',
  success: 'Your card has been saved successfully!',
  processing: 'Processing your card...',
  serverError: 'There was a server error. Please try again later.',
  loading: 'Loading payment form...'
};

// 5.3 Main initialization function
document.addEventListener('DOMContentLoaded', function() {
  // References to DOM elements
  const loadingContainer = document.getElementById('loading-container');
  const formContent = document.getElementById('form-content');
  const form = document.getElementById('payment-form');
  const submitButton = document.getElementById('submit');
  const cardErrors = document.getElementById('card-errors');

  // Initialize Stripe with publishable key
  const stripe = Stripe(STRIPE_CONFIG.publishableKey);
  const elements = stripe.elements();

  // Create card element
  const cardElement = elements.create('card', {
    style: {
      base: {
        color: '#ffffff',
        fontFamily: 'Inter, "Segoe UI", sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        '::placeholder': {
          color: '#aab7c4'
        }
      },
      invalid: {
        color: '#FF5A36',
        iconColor: '#FF5A36'
      }
    }
  });

  cardElement.on('blur', function(event) {
    validateForm();
  });
  cardElement._complete = false;
  form.addEventListener('input', validateForm);
  validateForm();

def _close_alert(self):
  """Close the alert dialog from JS."""
  self.raise_event('x-close-alert')

def _payment_method_ready(self, payment_method_id: str):
  """Called from JS after successful Stripe setup. Handles server calls from Python."""
  try:
    # 1. Get customer info
    customer = anvil.server.call('get_stripe_customer', self.sub_email)
    if customer and customer.get('id'):
      print(f"[STRIPE] Python: Found customer {customer['id']}, attaching payment method.")
      
      # 2. Attach payment method to customer and save to database
      anvil.server.call('save_payment_method', self.sub_email, payment_method_id)
      
      # 3. Close the form
      self.raise_event('x-close-alert')
    else:
      print("[STRIPE] Error: No customer found")
      Notification("No customer found", title="Could not add payment method!", style="error").show()
  except Exception as e:
    print(f"[STRIPE] Error in payment_method_ready: {str(e)}")
    Notification(str(e), title="Error processing payment method", style="error").show()

self.html = """
<!-- DNS optimization for improved loading performance -->
<link rel="preconnect" href="https://js.stripe.com" crossorigin>
<link rel="preconnect" href="https://api.stripe.com" crossorigin>

<!-- CSS styles with numbered sections for organization -->
<style>
  /* 1. Container styles */
  #payment-form-container {
    position: relative;
    font-family: Inter, "Segoe UI", sans-serif;
    color: #ffffff;
    padding: 10px 0;
  }
  
  /* 2. Loading indicator */
  #loading-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100px;
    margin: 20px 0;
  }
  
  .spinner {
    width: 40px;
    height: 40px;
    border: 4px solid rgba(255, 122, 0, 0.3);
    border-radius: 50%;
    border-top-color: #FF7A00;
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  /* 3. Form elements */
  #payment-form {
    margin-top: 20px;
  }
  
  .form-section {
    margin-bottom: 20px;
  }
  
  .form-section h3 {
    margin-bottom: 8px;
    font-size: 16px;
    font-weight: 500;
  }
  
  #card-element {
    background-color: #292929;
    padding: 16px;
    border-radius: 8px;
    margin-bottom: 16px;
  }
  
  #name-on-card {
    width: 100%;
    padding: 12px;
    background-color: #292929;
    border: none;
    border-radius: 8px;
    color: #ffffff;
    font-size: 16px;
    font-family: inherit;
  }
  
  /* 4. Feedback and controls */
  #card-errors {
    color: #FF5A36;
    margin-bottom: 16px;
    min-height: 20px;
  }
  
  .button-row {
    display: flex;
    justify-content: space-between;
    margin-top: 20px;
  }
  
  button {
    padding: 12px 24px;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
  }
  
  #cancel-btn {
    background-color: transparent;
    color: #ffffff;
    border: 1px solid #555555;
  }
  
  #submit {
    background-color: #FF7A00;
    color: #ffffff;
  }
  
  #submit:disabled {
    background-color: #cccccc;
    opacity: 0.7;
    cursor: not-allowed;
  }
  
  .success-message {
    color: #00C853;
  }
</style>

<!-- Payment form HTML structure -->
<div id="payment-form-container">
  <!-- Loading state -->
  <div id="loading-container">
    <div class="spinner"></div>
  </div>
  
  <!-- Form content (hidden until loaded) -->
  <div id="form-content" style="display: none;">
    <h2>Add payment details</h2>
    <div class="payment-info-text">Add your credit card details below. This card will be saved to your account and can be removed at any time.</div>
    
    <form id="payment-form">
      <!-- Card element section -->
      <div class="form-section">
        <h3>Card information</h3>
        <div id="card-element"></div>
      </div>
      
      <!-- Name field section -->
      <div class="form-section">
        <h3>Name on card</h3>
        <input id="name-on-card" name="name-on-card" type="text" autocomplete="cc-name" required placeholder="Name on card">
      </div>
      
      <!-- Feedback and controls -->
      <div id="card-errors" role="alert"></div>
      <div class="button-row">
        <button type="button" id="cancel-btn">Cancel</button>
        <button id="submit" type="submit" disabled>Save payment details</button>
      </div>
    </form>
  </div>
</div>

<!-- Load Stripe.js with optimal performance -->
<script src="https://js.stripe.com/v3/"></script>
            Notification("", title="Could not add payment method!", style="error").show()
            return
          
    except Exception as err:
        print(f"[STRIPE] Python ERROR: {err}")
        Notification("", title="Could not add payment method!", style="error").show()