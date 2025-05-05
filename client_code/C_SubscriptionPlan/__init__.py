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

from ..C_PaymentSubscription import C_PaymentSubscription
from ..C_PaymentCustomer import C_PaymentCustomer
from ..C_PaymentInfos import C_PaymentInfos


class C_SubscriptionPlan(C_SubscriptionPlanTemplate):
  def __init__(self, plan, no_licenses, plan_type, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
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
    
    print(f"INIT DETAILS - Subscribed: Plan={self.subscribed_plan}, Licenses={self.subscribed_licenses}, Billing={self.subscribed_billing}")
    print(f"INIT DETAILS - Selected: Plan={self.selected_plan}, Licenses={self.selected_licenses}, Billing={self.selected_billing}")

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
        <div class='pricing-plan left'>
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
        <div class='pricing-plan recommended'>
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
    
    # We'll move the JS initialization code to after the script is loaded
    # This ensures the functions are defined before we try to call them
    anvil.js.window.setTimeout("""
      try {
        // First set the correct pricing toggle
        if ('""" + self.subscribed_billing + """' === 'yearly') {
          // Check if function exists before calling
          if (typeof setYearly === 'function') {
            setYearly();
          } else {
            console.log("setYearly function not found yet");
            // Manually set the toggle classes
            if (document.getElementById('pricing-toggle-yearly')) {
              document.getElementById('pricing-toggle-yearly').classList.add('selected');
              document.getElementById('pricing-toggle-monthly').classList.remove('selected');
            }
          }
        } else {
          // Check if function exists before calling
          if (typeof setMonthly === 'function') {
            setMonthly();
          } else {
            console.log("setMonthly function not found yet");
            // Manually set the toggle classes
            if (document.getElementById('pricing-toggle-monthly')) {
              document.getElementById('pricing-toggle-monthly').classList.add('selected');
              document.getElementById('pricing-toggle-yearly').classList.remove('selected');
            }
          }
        }
        console.log("Initial pricing setup completed");
      } catch(e) {
        console.error("Error setting initial pricing:", e);
      }
    """, 200)

    # 2. Add Anvil Buttons for plan selection
    self.explore_btn = Button(text="Choose Plan", role="cta-button", tag={"plan_type": "Explore"})
    self.professional_btn = Button(text="Choose Plan", role="cta-button", tag={"plan_type": "Professional"})
    
    # Set button event handlers and appearance based on current plan
    self.update_button_state()
    
    # Add buttons to appropriate slots
    self.add_component(self.explore_btn, slot="explore-plan-button")
    self.add_component(self.professional_btn, slot="professional-plan-button")
    
    # Register this form to make it callable from JavaScript
    anvil.js.window.pythonComponent = self
    
    # Use the simplest, most reliable approach to add event listeners
    anvil.js.call('eval', """
    function setupEvents() {
      console.log("Setting up event listeners");
      
      // 1. Set up billing toggle listeners
      var monthlyBtn = document.getElementById('pricing-toggle-monthly');
      if (monthlyBtn) {
        monthlyBtn.onclick = function() {
          console.log("Monthly clicked");
          // Direct window method call
          window.pythonComponent.js_update_button_state();
        };
      }
      
      var yearlyBtn = document.getElementById('pricing-toggle-yearly');
      if (yearlyBtn) {
        yearlyBtn.onclick = function() {
          console.log("Yearly clicked");
          // Direct window method call
          window.pythonComponent.js_update_button_state();
        };
      }
      
      // 2. Set up user count listeners
      var userInput = document.getElementById('user-count');
      if (userInput) {
        userInput.oninput = function() {
          console.log("User input changed");
          // Direct window method call
          window.pythonComponent.js_update_button_state();
        };
      }
      
      // 3. Set up plus/minus buttons
      var minusBtn = document.getElementById('user-minus');
      if (minusBtn) {
        minusBtn.onclick = function() {
          console.log("Minus clicked");
          setTimeout(function() {
            // Direct window method call
            window.pythonComponent.js_update_button_state();
          }, 100);
        };
      }
      
      var plusBtn = document.getElementById('user-plus');
      if (plusBtn) {
        plusBtn.onclick = function() {
          console.log("Plus clicked");
          setTimeout(function() {
            // Direct window method call
            window.pythonComponent.js_update_button_state();
          }, 100);
        };
      }
    }
    
    // Run setup now
    setupEvents();
    
    // Also run after a short delay to ensure DOM is loaded
    setTimeout(setupEvents, 500);
    """)

  def form_show(self, **event_args):
    """Called when the form becomes visible - perfect time to set up JS handlers"""
    # 1. Set up JS event handlers once the DOM is fully loaded
    anvil.js.call('eval', """
    (function() {
      // 1.1 Setup monthly toggle
      var monthlyBtn = document.getElementById('pricing-toggle-monthly');
      if (monthlyBtn) {
        monthlyBtn.addEventListener('click', function() {
          console.log('Monthly clicked');
          if (typeof anvil !== 'undefined') {
            anvil.call('js_update_button_state');
          }
        });
      }
      
      // 1.2 Setup yearly toggle
      var yearlyBtn = document.getElementById('pricing-toggle-yearly');
      if (yearlyBtn) {
        yearlyBtn.addEventListener('click', function() {
          console.log('Yearly clicked');
          if (typeof anvil !== 'undefined') {
            anvil.call('js_update_button_state');
          }
        });
      }
      
      // 1.3 Setup user count input
      var userInput = document.getElementById('user-count');
      if (userInput) {
        userInput.addEventListener('input', function() {
          console.log('User count changed');
          if (typeof anvil !== 'undefined') {
            anvil.call('js_update_button_state');
          }
        });
      }
      
      // 1.4 Setup plus and minus buttons
      var plusBtn = document.getElementById('user-plus');
      var minusBtn = document.getElementById('user-minus');
      
      if (plusBtn) {
        plusBtn.addEventListener('click', function() {
          console.log('Plus clicked');
          setTimeout(function() {
            if (typeof anvil !== 'undefined') {
              anvil.call('js_update_button_state');
            }
          }, 100);
        });
      }
      
      if (minusBtn) {
        minusBtn.addEventListener('click', function() {
          console.log('Minus clicked');
          setTimeout(function() {
            if (typeof anvil !== 'undefined') {
              anvil.call('js_update_button_state');
            }
          }, 100);
        });
      }
      
      console.log('Event handlers setup complete');
    })();
    """)

  # 1. Create a reliable JS-to-Python call method
  def js_update_button_state(self, **event_args):
    """
    1. Called reliably from JavaScript through Anvil's built-in event system
    2. Acts as a bridge between JavaScript UI events and Python button state updates
    3. Ensures changes to user inputs are reflected in button appearance
    """
    # Force a direct call to update_button_state to refresh UI state
    anvil.js.report_callback_exception = self.handle_callback_error  # Add error handling
    self.update_button_state()
    
  def handle_callback_error(self, exception, stacktrace):
    """
    1. Handles errors in JavaScript callbacks
    2. Reports errors to console for troubleshooting
    """
    print(f"ERROR in JavaScript callback: {exception}")
    print(f"Stack trace: {stacktrace}")
    # This helps diagnose JS-Python communication issues

  def update_button_state(self):
    """
    1. Updates button appearance and event handlers based on the subscribed plan
    2. Configures text, styling, and click behavior for both the Explore and Professional buttons
    3. Considers billing period (monthly/yearly) preference when determining upgrade/downgrade status
    """
    # Add a timestamp and message to confirm method is being called
    import datetime
    print(f"UPDATE_BUTTON_STATE CALLED at {datetime.datetime.now()}")
    
    # Get user count from JS input field - Update self.selected_licenses
    user_count_input = document.getElementById('user-count')
    if user_count_input is not None:
        try:
            self.selected_licenses = int(user_count_input.value)
        except Exception:
            pass  # Keep existing value if there's an error
                
    # Determine active billing period from JS toggle state - Update self.selected_billing
    monthly_btn = document.getElementById('pricing-toggle-monthly')
    yearly_btn = document.getElementById('pricing-toggle-yearly')
    
    if monthly_btn and yearly_btn:
        is_yearly = yearly_btn.classList.contains('selected')
        self.selected_billing = "yearly" if is_yearly else "monthly"
        
    print(f"DEBUG - Comparison: subscribed_plan={self.subscribed_plan}, subscribed_licenses={self.subscribed_licenses}, subscribed_billing={self.subscribed_billing}")
    print(f"DEBUG - Comparison:   selected_plan={self.selected_plan},   selected_licenses={self.selected_licenses},   selected_billing={self.selected_billing}")
        
    # 1. EXPLORE BUTTON LOGIC
    if self.subscribed_plan in ["Trial", "Extended Trial", None]:
        # For Trial/Extended Trial: Orange "Choose Plan"
        self.explore_btn.text = "Choose Plan"
        self.explore_btn.role = "cta-button"
        self.explore_btn.set_event_handler('click', self.choose_plan_click)
    elif self.subscribed_plan == "Explore":
        # For Explore: Grey "Cancel Plan"
        self.explore_btn.text = "Cancel Plan"
        self.explore_btn.role = "secondary-button"
        self.explore_btn.set_event_handler('click', self.cancel_subscription)
    elif self.subscribed_plan == "Professional":
        # For Professional: Grey "Downgrade Plan"
        self.explore_btn.text = "Downgrade Plan"
        self.explore_btn.role = "secondary-button"
        self.explore_btn.set_event_handler('click', self.update_subscription)
        self.explore_btn.tag["target_plan"] = "Explore"
        self.explore_btn.tag["user_count"] = 1  # Explore always has 1 user
            
    # 2. PROFESSIONAL BUTTON LOGIC
    if self.subscribed_plan in ["Trial", "Extended Trial", None]:
        # For Trial/Extended Trial: Orange "Choose Plan"
        self.professional_btn.text = "Choose Plan"
        self.professional_btn.role = "cta-button"
        self.professional_btn.set_event_handler('click', self.choose_plan_click)
    elif self.subscribed_plan == "Explore":
        # For Explore: Orange "Upgrade Plan"
        self.professional_btn.text = "Upgrade Plan"
        self.professional_btn.role = "cta-button"
        self.professional_btn.set_event_handler('click', self.choose_plan_click)
    elif self.subscribed_plan == "Professional":
        # Check if selected options match current subscription
        is_same_subscription = (self.selected_licenses == self.subscribed_licenses and self.selected_billing == self.subscribed_billing and self.subscribed_plan == "Professional")
        
        if is_same_subscription:
            # No change: Grey "Cancel Plan"
            self.professional_btn.text = "Cancel Plan"
            self.professional_btn.role = "secondary-button"
            self.professional_btn.set_event_handler('click', self.cancel_subscription)
        else:
            # Is this an upgrade or downgrade?
            is_upgrade = (self.selected_licenses > self.subscribed_licenses) or (self.subscribed_billing == 'monthly' and self.selected_billing == 'yearly')
            
            if is_upgrade:
                # Orange "Upgrade Plan"
                self.professional_btn.text = "Upgrade Plan"
                self.professional_btn.role = "cta-button"
            else:
                # Grey "Downgrade Plan"
                self.professional_btn.text = "Downgrade Plan" 
                self.professional_btn.role = "secondary-button"
            
            self.professional_btn.set_event_handler('click', self.update_subscription)
            
    # 3. HANDLE BILLING PERIOD CHANGES EXPLICITLY
    if self.subscribed_plan not in ["Trial", "Extended Trial", None]:
        # Only for paid plans, check for billing period changes
        if self.subscribed_billing != self.selected_billing:
            if self.selected_billing == "yearly" and self.subscribed_billing == "monthly":
                # Upgrading to yearly - orange
                self.professional_btn.text = "Upgrade to Yearly"
                self.professional_btn.role = "cta-button"
                self.professional_btn.set_event_handler('click', self.update_subscription)
            elif self.selected_billing == "monthly" and self.subscribed_billing == "yearly":
                # Downgrading to monthly - grey
                self.professional_btn.text = "Downgrade to Monthly"
                self.professional_btn.role = "secondary-button"
                self.professional_btn.set_event_handler('click', self.update_subscription)
            
    # 4. STORE TAG DATA FOR BOTH BUTTONS
    # For professional button, always store user count and billing period
    self.professional_btn.tag["user_count"] = self.selected_licenses
    self.professional_btn.tag["billing_period"] = self.selected_billing
    self.professional_btn.tag["plan_type"] = "Professional"
        
    # For explore button, always store relevant data
    self.explore_btn.tag["user_count"] = 1  # Explore always has 1 user
    self.explore_btn.tag["billing_period"] = self.selected_billing
    self.explore_btn.tag["plan_type"] = "Explore"

  # 3. Handle Anvil Button clicks
  def choose_plan_click(self, sender, **event_args):
    """
    1. Handles clicks on the Explore and Professional plan buttons.
    2. Determines plan type, user count, and billing period, then opens checkout.
    
    Parameters:
        sender: The button that was clicked
        event_args (dict): Event arguments from the button click
    """
    plan_type = sender.tag.get("plan_type", "")
    # Get user count from JS input field
    user_count_input = document.getElementById('user-count')
    selected_user_count = 1
    if user_count_input is not None:
        try:
            selected_user_count = int(user_count_input.value)
        except Exception:
            selected_user_count = 1
    
    # Get billing period from toggle state
    self.update_button_state()  # Ensure billing period is current
    selected_billing_period = self.selected_billing
    
    # Open subscription checkout flow with the collected info
    self.open_subscription(plan_type=plan_type, user_count=selected_user_count, billing_period=selected_billing_period)

  def cancel_subscription(self, sender, **event_args) -> None:
    """
    1. Handles the cancellation of a subscription
    2. Calls the server function to cancel the subscription in Stripe
    
    Parameters:
        sender: The button that was clicked
        event_args (dict): Event arguments from the button click
    """
    plan_type: str = sender.tag.get("plan_type", "")
    # Get confirmation from user
    confirmation = alert(
      f"Are you sure you want to cancel your {self.subscribed_plan} subscription?",
      title="Cancel Subscription",
      buttons=["Yes, Cancel", "No, Keep Subscription"],
      large=False
    )

    if confirmation == "Yes, Cancel":
      # Call server function to cancel subscription
      try:
        result = anvil.server.call('cancel_subscription')
        if result and result.get('success'):
          alert("Your subscription has been successfully cancelled.", title="Success")
          # Refresh the page to reflect the changes
          anvil.js.window.location.reload()
        else:
          alert("There was a problem cancelling your subscription. Please try again or contact support.", title="Error")
      except Exception as e:
        print(f"Error in cancel_subscription: {e}")
        alert("There was a problem processing your request. Please try again later.", title="Error")

  def update_subscription(self, sender, **event_args) -> None:
    """
    1. Handles updating a subscription (upgrading, downgrading, or changing user count)
    2. Calls the server function to update the subscription in Stripe
    
    Parameters:
        sender: The button that was clicked
        event_args (dict): Event arguments from the button click
    """
    # Use subscribed_* variables consistently throughout the code
    current_plan: str = self.subscribed_plan
    target_plan: str = sender.tag.get("target_plan", current_plan)
    
    # Get the user count for Professional plan
    selected_user_count: int = sender.tag.get("user_count", 1)
    if not selected_user_count:
        user_count_input = document.getElementById('user-count')
        if user_count_input is not None:
            try:
                selected_user_count = int(user_count_input.value)
            except Exception:
                selected_user_count = 1
    
    # Get billing period info
    selected_billing_period: str = sender.tag.get("billing_period", self.selected_billing)
    
    # Determine update type
    if target_plan != current_plan:
        operation_type = "downgrade" if current_plan == "Professional" else "upgrade"
        confirmation_message = f"Are you sure you want to {operation_type} from {current_plan} to {target_plan}?"
    elif selected_billing_period != self.subscribed_billing:
        if selected_billing_period == "yearly":
            operation_type = "upgrade"
            confirmation_message = f"Are you sure you want to upgrade from monthly to yearly billing?"
        else:
            operation_type = "downgrade"
            confirmation_message = f"Are you sure you want to change from yearly to monthly billing?"
    else:
        if selected_user_count > self.subscribed_licenses:
            operation_type = "upgrade"
            confirmation_message = f"Are you sure you want to increase your user count from {self.subscribed_licenses} to {selected_user_count}?"
        else:
            operation_type = "downgrade"
            confirmation_message = f"Are you sure you want to decrease your user count from {self.subscribed_licenses} to {selected_user_count}?"

    # Get confirmation from user
    confirmation = alert(
      confirmation_message,
      title=f"{operation_type.capitalize()} Subscription",
      buttons=[f"Yes, {operation_type.capitalize()}", "No, Cancel"],
      large=False
    )

    if confirmation.startswith("Yes"):
      # Call server function to update subscription
      try:
        result = anvil.server.call(
          'update_subscription', 
          target_plan=target_plan, 
          user_count=selected_user_count, 
          billing_period=selected_billing_period
        )
        if result and result.get('success'):
          alert(f"Your subscription has been successfully updated.", title="Success")
          # Refresh the page to reflect the changes
          anvil.js.window.location.reload()
        else:
          alert("There was a problem updating your subscription. Please try again or contact support.", title="Error")
      except Exception as e:
        print(f"Error in update_subscription: {e}")
        alert("There was a problem processing your request. Please try again later.", title="Error")

  # 4. Handle the full checkout process
  def open_subscription(self, **event_args):
    """
    1. Opens the subscription workflow
    2. Handles navigation between components based on data availability
    3. Only proceeds to next step if previous data is available
    """
    # 1. Get the current subscription plan and billing period
    plan_type = event_args.get('plan_type')
    selected_user_count = event_args.get('user_count')
    selected_billing_period = event_args.get('billing_period', 'monthly')
    if not plan_type or not selected_user_count:
      alert("Please select a plan and specify the number of users.", title="Missing Information")
      return
    # 2. Check if customer data exists
    customer = anvil.server.call('get_stripe_customer', anvil.users.get_user()['email'])
    customer_exists = bool(customer and customer.get('id'))
    # 3. If no customer data, start with C_PaymentCustomer
    if not customer_exists:
      customer_form = C_PaymentCustomer()
      customer_result = alert(
        content=customer_form,
        large=False,
        width=500,
        buttons=[],
        dismissible=True
      )
      # Only continue if customer data was successfully submitted
      if customer_result != 'success':
        return
      # Refresh customer data
      customer = anvil.server.call('get_stripe_customer', anvil.users.get_user()['email'])
    # 4. Check if payment method exists
    payment_methods = []
    if customer and customer.get('id'):
      payment_methods = anvil.server.call('get_stripe_payment_methods', customer['id'])
    # 5. If no payment method, open C_PaymentInfos
    if not payment_methods:
      payment_form = C_PaymentInfos()
      payment_result = alert(
        content=payment_form,
        large=False,
        width=500,
        buttons=[],
        dismissible=True
      )
      # Only continue if payment method was successfully added
      if payment_result != 'success':
        return
      # Refresh payment methods
      if customer and customer.get('id'):
        payment_methods = anvil.server.call('get_stripe_payment_methods', customer['id'])
    # 6. Finally, open subscription confirmation
    subscription_form = C_PaymentSubscription(
      plan_type=plan_type,
      user_count=selected_user_count,
      billing_period=selected_billing_period
    )
    subscription_result = alert(
      content=subscription_form,
      large=False,
      width=600,
      buttons=[],
      dismissible=True
    )
