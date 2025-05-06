from ._anvil_designer import C_SubscriptionPlanTemplate
from anvil import *
import anvil.server
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil import Button, alert
import anvil.js
from anvil.js.window import document
import datetime

from ..C_PaymentSubscription import C_PaymentSubscription
from ..C_PaymentCustomer import C_PaymentCustomer
from ..C_PaymentInfos import C_PaymentInfos


class C_SubscriptionPlan(C_SubscriptionPlanTemplate):
  def __init__(self, plan, no_licenses, plan_type, **properties):
    """
    1. Initialize the subscription plan component with default values
    2. Set up instance variables for plan details and button elements
    """
    # Initialize the component
    self.init_components(**properties)
    
    # Set up instance variables with default values
    self.selected_plan = None
    self.selected_licenses = 1
    self.selected_billing = "monthly"
    
    self.subscribed_plan = None
    self.subscribed_licenses = 0
    self.subscribed_billing = "monthly"
    
    # Store the plan info that was set via data bindings
    self.plan = properties.get('plan', None)
    self.no_licenses = properties.get('no_licenses', 0)
    self.plan_type = properties.get('plan_type', "monthly")
    
    # Map display text to actual plan names
    self.plan_name_map = {
      "Professional": "Professional",
      "Pro": "Professional",
      "Explore": "Explore"
    }
    
    # Reference to button components for easy access
    self.explore_btn = self.explore_plan_btn
    self.professional_btn = self.professional_plan_btn
    
    # Save CSS for direct application via JavaScript
    self.explore_highlight_css = "0 0 20px rgba(0, 0, 0, 0.25)"
    self.professional_highlight_css = "0 0 20px rgba(0, 0, 0, 0.25)"

    # Set Form properties and Data Bindings.
    global user
    user = anvil.users.get_user()

    print('plan:', plan)
    print('no_licenses:', no_licenses)
    print('plan_type:', plan_type)

    # Store the current SUBSCRIPTION details (what the user is currently subscribed to)
    self.subscribed_plan = plan  # Current plan user is subscribed to (Explore/Professional)
    self.subscribed_licenses = no_licenses if no_licenses else 1  # Current number of licenses
    self.subscribed_billing = plan_type  # Current billing period (monthly/yearly)

    # Store the SELECTED values (what the user is currently selecting in the UI)
    # These will be updated as user interacts with the component
    self.selected_plan = plan  # Initially same as subscription
    self.selected_licenses = self.subscribed_licenses  # Initially same as subscription
    self.selected_billing = plan_type  # Initially same as subscription

    print(f"[SUBSCRIPTION_DEBUG] INIT DETAILS - Subscribed: Plan={self.subscribed_plan}, Licenses={self.subscribed_licenses}, Billing={self.subscribed_billing}")
    print(f"[SUBSCRIPTION_DEBUG] INIT DETAILS - Selected: Plan={self.selected_plan}, Licenses={self.selected_licenses}, Billing={self.selected_billing}")

    # 1. HTML content
    self.html = """
    <!-- 1. Pricing Toggle -->
    <div class='pricing-toggle-container'>
        <div class='pricing-toggle'>
            <button id='pricing-toggle-monthly' class='pricing-toggle-btn """ + ('selected' if self.subscribed_billing == "monthly" else '') + """' type='button'>Monthly</button>
            <button id='pricing-toggle-yearly' class='pricing-toggle-btn """ + ('selected' if self.subscribed_billing == "yearly" else '') + """' type='button'>Yearly <span class='discount'>-10%</span></button>
        </div>
    </div>
    <!-- 2. Pricing Plans -->
    <div class='pricing-plans'>
        <!-- Explore Plan -->
        <div id='explore-plan-box' class='pricing-plan left'>
            <h2 class='plan-name'>Explore</h2>
            <p class='plan-description'>Best for solo scouts exploring AI-powered artist discovery.</p>
            <div class='plan-price-container'>
                <div class='discount-badge'>25%<br>Launch Disc.</div>
                <span class='original-price'><span class='euro-symbol'>€</span><span class='price-number'>38</span></span>
                <span class='plan-price'><span class='euro-symbol'>€</span>27</span>
                <span class='price-period'>/month</span>
            </div>
            <ul class='plan-features plan-features-orange'>
                <li>1 user</li>
                <li>100 Artist Profiles per month</li>
                <li>1 AI-scouting-agent</li>
                <li>1 Watchlist</li>
                <li>E-Mail Support</li>
            </ul>
            <div anvil-slot="explore-plan-button"></div>
        </div>
        <!-- Professional Plan -->
        <div id='professional-plan-box' class='pricing-plan recommended'>
            <div class='recommended-tag'>Recommended</div>
            <h2 class='plan-name'>Professional</h2>
            <p class='plan-description'>For individuals or teams who want to unlock full AI-powered scouting.</p>
            <div class='plan-price-container'>
                <div class='discount-badge'>25%<br>Launch Disc.</div>
                <span class='original-price'><span class='euro-symbol'>€</span><span class='price-number'>58</span></span>
                <span class='plan-price'><span class='euro-symbol'>€</span>41</span>
                <span class='price-period'>/user & month</span>
            </div>
            <ul class='plan-features plan-features-orange'>
                <li>Collaborate in teams. Pay per the number of users in your team.</li>
                <li>Unlimited Artist Profiles</li>
                <li>Unlimited AI-scouting-agents</li>
                <li>Unlimited Watchlists</li>
                <li>Premium Support</li>
            </ul>
            <!-- User selector -->
            <div class='user-count-selector'>
                <button type='button' class='user-count-btn' id='user-minus'>−</button>
                <span class='user-count-label'>
                    <input id='user-count' class='user-count-value-input' type='text' value='""" + str(self.subscribed_licenses) + """' maxlength='3' />
                    <span> User<span id='user-count-plural' style='display:""" + ('none' if self.subscribed_licenses == 1 else '') + """;'>s</span></span>
                </span>
                <button type='button' class='user-count-btn' id='user-plus'>+</button>
            </div>
            <div anvil-slot="professional-plan-button"></div>
        </div>
    </div>
    <!-- 3. Pricing Toggle JS -->
    <script>
    // Pricing toggle JS
    function setMonthly() {
        document.getElementById('pricing-toggle-monthly').classList.add('selected');
        document.getElementById('pricing-toggle-yearly').classList.remove('selected');
        document.querySelector('.pricing-plan.left .original-price').innerHTML = '<span class="euro-symbol">€</span><span class="price-number">39</span>';
        document.querySelector('.pricing-plan.left .plan-price').innerHTML = '<span class="euro-symbol">€</span>29';
        document.querySelector('.pricing-plan.left .price-period').textContent = '/month';
        setProfessionalPrice();
    }
    function setYearly() {
        document.getElementById('pricing-toggle-monthly').classList.remove('selected');
        document.getElementById('pricing-toggle-yearly').classList.add('selected');
        document.querySelector('.pricing-plan.left .original-price').innerHTML = '<span class="euro-symbol">€</span><span class="price-number">35</span>';
        document.querySelector('.pricing-plan.left .plan-price').innerHTML = '<span class="euro-symbol">€</span>26';
        document.querySelector('.pricing-plan.left .price-period').textContent = '/month';
        setProfessionalPrice();
    }

    // --- Professional Plan Pricing Logic ---
    var userCount = """ + str(self.subscribed_licenses) + """;
    var userCountInput = document.getElementById('user-count');
    var userCountPlural = document.getElementById('user-count-plural');
    var profOriginalPrice = document.querySelector('.pricing-plan.recommended .original-price .price-number');
    var profPlanPrice = document.querySelector('.pricing-plan.recommended .plan-price');
    var profPricePeriod = document.querySelector('.pricing-plan.recommended .price-period');

    // Monthly and yearly price per user
    var monthlyOriginalPerUser = 59;
    var monthlyDiscountedPerUser = 44;
    var yearlyOriginalPerUser = 53;
    var yearlyDiscountedPerUser = 39;

    function setProfessionalPrice() {
        var isMonthly = document.getElementById('pricing-toggle-monthly').classList.contains('selected');
        var orig = isMonthly ? monthlyOriginalPerUser : yearlyOriginalPerUser;
        var disc = isMonthly ? monthlyDiscountedPerUser : yearlyDiscountedPerUser;
        profOriginalPrice.textContent = orig * userCount;
        profPlanPrice.innerHTML = '<span class="euro-symbol">€</span>' + (disc * userCount);
        if (userCount === 1) {
            profPricePeriod.textContent = '/user & month';
        } else {
            profPricePeriod.textContent = 'for ' + userCount + ' users / month';
        }
    }

    userCountInput.addEventListener('input', function() {
        var val = parseInt(userCountInput.value.replace(/\\D/g, ''));
        if (isNaN(val) || val < 1) val = 1;
        if (val > 100) val = 100;
        userCount = val;
        userCountInput.value = userCount;
        if (userCount === 1) {
            userCountPlural.style.display = 'none';
        } else {
            userCountPlural.style.display = '';
        }
        setProfessionalPrice();
        // Update button state
        if (window.pyComponent && window.pyComponent.update_button_state) {
            window.pyComponent.update_button_state();
        }
    });
    userCountInput.addEventListener('blur', function() {
        if (!userCountInput.value || parseInt(userCountInput.value) < 1) {
            userCount = 1;
            userCountInput.value = 1;
            userCountPlural.style.display = 'none';
            setProfessionalPrice();
            // Update button state
            if (window.pyComponent && window.pyComponent.update_button_state) {
                window.pyComponent.update_button_state();
            }
        }
    });
    document.getElementById('user-minus').addEventListener('click', function() {
        if (userCount > 1) {
            userCount--;
            userCountInput.value = userCount;
            if (userCount === 1) {
                userCountPlural.style.display = 'none';
            }
            setProfessionalPrice();
            // Update button state
            if (window.pyComponent && window.pyComponent.update_button_state) {
                window.pyComponent.update_button_state();
            }
        }
    });
    document.getElementById('user-plus').addEventListener('click', function() {
        if (userCount < 100) {
            userCount++;
            userCountInput.value = userCount;
            if (userCount > 1) {
                userCountPlural.style.display = '';
            }
            setProfessionalPrice();
            // Update button state
            if (window.pyComponent && window.pyComponent.update_button_state) {
                window.pyComponent.update_button_state();
            }
        }
    });
    document.getElementById('pricing-toggle-monthly').addEventListener('click', function() {
        setMonthly();
        // Update button state
        if (window.pyComponent && window.pyComponent.update_button_state) {
            window.pyComponent.update_button_state();
        }
    });
    document.getElementById('pricing-toggle-yearly').addEventListener('click', function() {
        setYearly();
        // Update button state
        if (window.pyComponent && window.pyComponent.update_button_state) {
            window.pyComponent.update_button_state();
        }
    });
    
    // Initialize JS with the current billing period
    if ('""" + self.subscribed_billing + """' === 'yearly') {
      setYearly();
    } else {
      setMonthly();
    }
    </script>
    """

    # Initialize JS with the current billing period
    self.current_billing_period = self.subscribed_billing
    
    # 2. Add Anvil Buttons for plan selection
    self.explore_btn = Button(text="Choose Plan", role="cta-button", tag={"plan_type": "Explore"})
    self.professional_btn = Button(text="Choose Plan", role="cta-button", tag={"plan_type": "Professional"})
    
    # Set button event handlers and appearance based on current plan
    self.update_button_state()
    
    # Add buttons to appropriate slots
    self.add_component(self.explore_btn, slot="explore-plan-button")
    self.add_component(self.professional_btn, slot="professional-plan-button")
    
    # 3. Update existing event handlers
    # Make our update_button_state method available to the existing JS event handlers
    anvil.js.window.update_subscription_buttons = self.update_button_state
    
    anvil.js.call('eval', """
    // Make the Python update_button_state method available for existing event handlers
    console.log("[SUBSCRIPTION_DEBUG] Setting up window.pyComponent for existing event handlers");
    window.pyComponent = {};
    window.pyComponent.update_button_state = function() {
      console.log("[SUBSCRIPTION_DEBUG] Called update_button_state from existing JS event handlers");
      try {
        if (window.update_subscription_buttons) {
          window.update_subscription_buttons();
          console.log("[SUBSCRIPTION_DEBUG] Successfully called Python update_button_state");
        } else {
          console.error("[SUBSCRIPTION_DEBUG] window.update_subscription_buttons is not defined");
        }
      } catch (e) {
        console.error("[SUBSCRIPTION_DEBUG] Error calling Python:", e);
      }
    };
    """)

    self.apply_plan_highlighting()

  def form_show(self):
    """
    1. Initializes form UI when the component is first shown
    2. Updates UI elements based on current subscription plan
    3. Sets up event handlers for interactive elements
    """
    print(f"[SUBSCRIPTION_DEBUG] FORM_SHOW CALLED at {datetime.datetime.now()}")
    
    # 1. Log initial details for debugging
    print(f"[SUBSCRIPTION_DEBUG] INIT DETAILS - Subscribed: Plan={self.subscribed_plan}, Licenses={self.subscribed_licenses}, Billing={self.subscribed_billing}")
    print(f"[SUBSCRIPTION_DEBUG] INIT DETAILS - Selected: Plan={self.selected_plan}, Licenses={self.selected_licenses}, Billing={self.selected_billing}")
    
    # 2. Initialize JS environment and setup custom JavaScript
    anvil.js.call('eval', """
    // Set up window.pyComponent for existing event handlers
    console.log("[SUBSCRIPTION_DEBUG] Setting up window.pyComponent for existing event handlers");
    
    if (typeof window.pyComponent === 'undefined') {
      window.pyComponent = {};
    }
    
    if (typeof window.update_subscription_buttons === 'undefined') {
      window.update_subscription_buttons = function() {
        if (typeof anvil !== 'undefined') {
          anvil.call('js_update_button_state');
        }
      };
    }
    
    window.pyComponent.update_button_state = window.update_subscription_buttons;
    """)

  def apply_plan_highlighting(self):
    """
    1. Applies highlighting to the appropriate plan box based on subscription plan
    2. Uses different strategies to ensure highlighting works despite DOM access issues
    """
    print(f"[SUBSCRIPTION_DEBUG] Applying plan highlighting for plan: {self.subscribed_plan}")
    
    # Define highlight styles
    explore_style = "0 0 20px rgba(0, 0, 0, 0.25)"
    professional_style = "0 0 20px rgba(0, 0, 0, 0.25)"
    
    # Create the JavaScript to apply highlighting through direct style injection
    anvil.js.call('eval', f"""
    try {{
      console.log("[SUBSCRIPTION_DEBUG] Trying to apply highlighting via style overrides");
      
      // 1. Since we can't find plan boxes directly, inject a style tag with CSS
      function injectCSS() {{
        var styleId = 'plan-highlights-style';
        var existingStyle = document.getElementById(styleId);
        
        if (existingStyle) {{
          existingStyle.remove();  // Remove existing style if present
        }}
        
        var style = document.createElement('style');
        style.id = styleId;
        
        // Clear any existing highlights
        style.textContent = '.pricing-plan.left, .pricing-plan.recommended {{ box-shadow: none !important; }}';
        
        // Apply highlight based on current plan
        if ('{self.subscribed_plan}' === 'Explore') {{
          console.log('[SUBSCRIPTION_DEBUG] Adding Explore highlight rule to CSS');
          style.textContent += '\\n.pricing-plan.left {{ box-shadow: {explore_style} !important; }}';
        }} else if ('{self.subscribed_plan}' === 'Professional') {{
          console.log('[SUBSCRIPTION_DEBUG] Adding Professional highlight rule to CSS');
          style.textContent += '\\n.pricing-plan.recommended {{ box-shadow: {professional_style} !important; }}';
        }}
        
        document.head.appendChild(style);
        console.log('[SUBSCRIPTION_DEBUG] Applied highlighting via CSS injection', style.textContent);
      }}
      
      // First attempt immediately
      injectCSS();
      
      // Second attempt after a delay to ensure DOM is ready
      setTimeout(injectCSS, 1000);
      
      // Third attempt using MutationObserver to detect DOM changes
      var observer = new MutationObserver(function(mutations) {{
        for(var mutation of mutations) {{
          if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {{
            // Check if any pricing-plan elements have been added
            for(var node of mutation.addedNodes) {{
              if (node.nodeType === 1) {{ // Element node
                if (node.querySelector && (
                    node.querySelector('.pricing-plan') || 
                    node.classList && node.classList.contains('pricing-plan'))) {{
                  console.log('[SUBSCRIPTION_DEBUG] Detected pricing-plan added to DOM, applying highlight');
                  injectCSS();
                  break;
                }}
              }}
            }}
          }}
        }}
      }});
      
      // Start observing the document for changes
      observer.observe(document.body, {{ childList: true, subtree: true }});
      console.log('[SUBSCRIPTION_DEBUG] Set up MutationObserver to watch for DOM changes');
      
      // Also inject when toggle buttons are clicked
      var monthlyBtn = document.getElementById('pricing-toggle-monthly');
      var yearlyBtn = document.getElementById('pricing-toggle-yearly');
      
      if (monthlyBtn) {{
        monthlyBtn.addEventListener('click', function() {{
          console.log('[SUBSCRIPTION_DEBUG] Monthly toggle clicked, triggering highlight');
          setTimeout(injectCSS, 200);
        }});
      }}
      
      if (yearlyBtn) {{
        yearlyBtn.addEventListener('click', function() {{
          console.log('[SUBSCRIPTION_DEBUG] Yearly toggle clicked, triggering highlight');
          setTimeout(injectCSS, 200);
        }});
      }}
      
    }} catch (e) {{
      console.error("[SUBSCRIPTION_DEBUG] Error applying plan highlighting:", e);
      console.error("[SUBSCRIPTION_DEBUG] Error details:", e.message, e.stack);
    }}
    """)

  def js_update_button_state(self, **event_args):
    """
    1. Called reliably from JavaScript through Anvil's built-in event system
    2. Acts as a bridge between JavaScript UI events and Python button state updates
    3. Ensures changes to user inputs are reflected in button appearance
    """
    # Force a direct call to update_button_state to refresh UI state
    anvil.js.report_callback_exception = self.handle_callback_error  # Add error handling
    self.update_button_state()
    # Also apply plan highlighting
    self.apply_plan_highlighting()

  def handle_callback_error(self, exception, stacktrace):
    """
    1. Handles errors in JavaScript callbacks
    2. Reports errors to console for troubleshooting
    """
    print(f"[SUBSCRIPTION_DEBUG] ERROR in JavaScript callback: {exception}")
    print(f"[SUBSCRIPTION_DEBUG] Stack trace: {stacktrace}")

  # ... rest of the code remains the same ...
