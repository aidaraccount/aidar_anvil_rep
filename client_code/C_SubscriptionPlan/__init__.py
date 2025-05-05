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

    # Store the current plan and licenses
    self.active_plan = plan
    self.active_licenses = no_licenses if no_licenses else 1
    self.billing_period = plan_type

    # 1. HTML content
    self.html = """
    <!-- 1. Pricing Toggle -->
    <div class='pricing-toggle-container'>
        <div class='pricing-toggle'>
            <button id='pricing-toggle-monthly' class='pricing-toggle-btn """ + ('selected' if self.billing_period == "monthly" else '') + """' type='button'>Monthly</button>
            <button id='pricing-toggle-yearly' class='pricing-toggle-btn """ + ('selected' if self.billing_period == "yearly" else '') + """' type='button'>Yearly <span class='discount'>-10%</span></button>
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
                    <input id='user-count' class='user-count-value-input' type='text' value='""" + str(self.active_licenses) + """' maxlength='3' />
                    <span> User<span id='user-count-plural' style='display:""" + ('none' if self.active_licenses == 1 else '') + """;'>s</span></span>
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
    var userCount = """ + str(self.active_licenses) + """;
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
    if ('""" + self.billing_period + """' === 'yearly') {
      setYearly();
    } else {
      setMonthly();
    }
    </script>
    """

    # Initialize JS with the current billing period
    self.current_billing_period = self.billing_period
    
    # Initialize with the correct pricing based on billing period
    anvil.js.window.setTimeout("""
      try {
        // Set initial pricing toggle based on current billing period
        if ('""" + self.billing_period + """' === 'yearly') {
          setYearly();
        } else {
          setMonthly();
        }
      } catch(e) {
        console.error("Error setting initial pricing:", e);
      }
    """, 100)

    # 2. Add Anvil Buttons for plan selection
    self.explore_btn = Button(text="Choose Plan", role="cta-button", tag={"plan_type": "Explore"})
    self.professional_btn = Button(text="Choose Plan", role="cta-button", tag={"plan_type": "Professional"})
    
    # Set button event handlers and appearance based on current plan
    self.update_button_state()
    
    # Add buttons to appropriate slots
    self.add_component(self.explore_btn, slot="explore-plan-button")
    self.add_component(self.professional_btn, slot="professional-plan-button")
    
    # Set up JS listeners for billing toggle and user count changes
    anvil.js.window.setTimeout("""
      try {
        // Store a reference to the Python component
        window.pyComponent = _this;
        
        // Set up billing toggle listeners
        var monthlyBtn = document.getElementById('pricing-toggle-monthly');
        var yearlyBtn = document.getElementById('pricing-toggle-yearly');
        
        if (monthlyBtn) {
          monthlyBtn.addEventListener('click', function() {
            if (window.pyComponent && window.pyComponent.update_button_state) {
              window.pyComponent.update_button_state();
            }
          });
        }
        
        if (yearlyBtn) {
          yearlyBtn.addEventListener('click', function() {
            if (window.pyComponent && window.pyComponent.update_button_state) {
              window.pyComponent.update_button_state();
            }
          });
        }
        
        // Set up user count change listener
        var userCountInput = document.getElementById('user-count');
        if (userCountInput) {
          userCountInput.addEventListener('input', function() {
            var val = parseInt(userCountInput.value);
            if (isNaN(val) || val < 1) val = 1;
            
            if (window.pyComponent && window.pyComponent.update_button_state) {
              window.pyComponent.update_button_state();
            }
          });
          
          // Also listen for +/- button clicks
          var minusBtn = document.getElementById('user-minus');
          var plusBtn = document.getElementById('user-plus');
          
          if (minusBtn) {
            minusBtn.addEventListener('click', function() {
              if (window.pyComponent && window.pyComponent.update_button_state) {
                setTimeout(function() {
                  window.pyComponent.update_button_state();
                }, 50);
              }
            });
          }
          
          if (plusBtn) {
            plusBtn.addEventListener('click', function() {
              if (window.pyComponent && window.pyComponent.update_button_state) {
                setTimeout(function() {
                  window.pyComponent.update_button_state();
                }, 50);
              }
            });
          }
        }
      } catch(e) {
        console.error("Error setting up Python-JS bridge:", e);
      }
    """, 500)

  def update_button_state(self):
    """
    1. Updates button appearance and event handlers based on the active subscription plan
    2. Configures text, styling, and click behavior for both the Explore and Professional buttons
    3. Considers billing period (monthly/yearly) preference when determining upgrade/downgrade status
    """
    # Get user count from JS input field
    user_count_input = document.getElementById('user-count')
    user_count = 1
    if user_count_input is not None:
        try:
            user_count = int(user_count_input.value)
        except Exception:
            user_count = 1
                
    # Determine active billing period from JS toggle state
    monthly_btn = document.getElementById('pricing-toggle-monthly')
    yearly_btn = document.getElementById('pricing-toggle-yearly')
    
    if monthly_btn and yearly_btn:
        is_yearly = yearly_btn.classList.contains('selected')
        self.billing_period = "yearly" if is_yearly else "monthly"
        
    active_plan = self.active_plan
    active_licenses = self.active_licenses
        
    # 1. EXPLORE BUTTON LOGIC
    if active_plan in ["Trial", "Extended Trial", None]:
        # For Trial/Extended Trial: Orange "Choose Plan"
        self.explore_btn.text = "Choose Plan"
        self.explore_btn.role = "cta-button"
        self.explore_btn.set_event_handler('click', self.choose_plan_click)
    elif active_plan == "Explore":
        # For Explore: Grey "Cancel Plan"
        self.explore_btn.text = "Cancel Plan"
        self.explore_btn.role = "secondary-button"
        self.explore_btn.set_event_handler('click', self.cancel_subscription)
    elif active_plan == "Professional":
        # For Professional: Grey "Downgrade Plan"
        self.explore_btn.text = "Downgrade Plan"
        self.explore_btn.role = "secondary-button"
        self.explore_btn.set_event_handler('click', self.update_subscription)
        self.explore_btn.tag["target_plan"] = "Explore"
        self.explore_btn.tag["user_count"] = 1  # Explore always has 1 user
            
    # 2. PROFESSIONAL BUTTON LOGIC
    if active_plan in ["Trial", "Extended Trial", None]:
        # For Trial/Extended Trial: Orange "Choose Plan"
        self.professional_btn.text = "Choose Plan"
        self.professional_btn.role = "cta-button"
        self.professional_btn.set_event_handler('click', self.choose_plan_click)
    elif active_plan == "Professional":
        # For Professional: Check for changes
        if user_count == active_licenses and self.billing_period == getattr(self, 'current_billing_period', self.billing_period):
            # No change: Grey "Cancel Plan"
            self.professional_btn.text = "Cancel Plan"
            self.professional_btn.role = "secondary-button"
            self.professional_btn.set_event_handler('click', self.cancel_subscription)
        else:
            # Is this an upgrade or downgrade?
            is_upgrade = (user_count > active_licenses) or (getattr(self, 'current_billing_period', 'monthly') == 'monthly' and self.billing_period == 'yearly')
            
            if is_upgrade:
                # Orange "Upgrade Plan"
                self.professional_btn.text = "Upgrade Plan"
                self.professional_btn.role = "cta-button"
            else:
                # Grey "Downgrade Plan"
                self.professional_btn.text = "Downgrade Plan" 
                self.professional_btn.role = "secondary-button"
            
            self.professional_btn.set_event_handler('click', self.update_subscription)
    elif active_plan == "Explore":
        # For Explore: Orange "Upgrade Plan"
        self.professional_btn.text = "Upgrade Plan"
        self.professional_btn.role = "cta-button"
        self.professional_btn.set_event_handler('click', self.choose_plan_click)
            
    # 3. HANDLE BILLING PERIOD CHANGES EXPLICITLY
    if active_plan not in ["Trial", "Extended Trial", None]:
        # Only for paid plans, check for billing period changes
        current_billing = getattr(self, 'current_billing_period', self.billing_period)
        
        if current_billing != self.billing_period:
            if self.billing_period == "yearly" and current_billing == "monthly":
                # Upgrading to yearly - orange
                self.professional_btn.text = "Upgrade to Yearly"
                self.professional_btn.role = "cta-button"
                self.professional_btn.set_event_handler('click', self.update_subscription)
            elif self.billing_period == "monthly" and current_billing == "yearly":
                # Downgrading to monthly - grey
                self.professional_btn.text = "Downgrade to Monthly"
                self.professional_btn.role = "secondary-button"
                self.professional_btn.set_event_handler('click', self.update_subscription)
            
    # 4. STORE TAG DATA FOR BOTH BUTTONS
    # For professional button, always store user count and billing period
    self.professional_btn.tag["user_count"] = user_count
    self.professional_btn.tag["billing_period"] = self.billing_period
    self.professional_btn.tag["plan_type"] = "Professional"
        
    # For explore button, always store relevant data
    self.explore_btn.tag["user_count"] = 1  # Explore always has 1 user
    self.explore_btn.tag["billing_period"] = self.billing_period
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
    user_count = 1
    if user_count_input is not None:
        try:
            user_count = int(user_count_input.value)
        except Exception:
            user_count = 1
    
    # Get billing period from toggle state
    self.update_button_state()  # Ensure billing period is current
    billing_period = self.billing_period
    
    # Open subscription checkout flow with the collected info
    self.open_subscription(plan_type=plan_type, user_count=user_count, billing_period=billing_period)

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
      f"Are you sure you want to cancel your {self.active_plan} subscription?",
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
    current_plan: str = self.active_plan
    target_plan: str = sender.tag.get("target_plan", current_plan)
    
    # Get the user count for Professional plan
    user_count: int = sender.tag.get("user_count", 1)
    if not user_count:
        user_count_input = document.getElementById('user-count')
        if user_count_input is not None:
            try:
                user_count = int(user_count_input.value)
            except Exception:
                user_count = 1
    
    # Get billing period info
    billing_period: str = sender.tag.get("billing_period", self.billing_period)
    
    # Determine update type
    if target_plan != current_plan:
        operation_type = "downgrade" if current_plan == "Professional" else "upgrade"
        confirmation_message = f"Are you sure you want to {operation_type} from {current_plan} to {target_plan}?"
    elif billing_period != getattr(self, 'current_billing_period', self.billing_period):
        if billing_period == "yearly":
            operation_type = "upgrade"
            confirmation_message = f"Are you sure you want to upgrade from monthly to yearly billing?"
        else:
            operation_type = "downgrade"
            confirmation_message = f"Are you sure you want to change from yearly to monthly billing?"
    else:
        if user_count > self.active_licenses:
            operation_type = "upgrade"
            confirmation_message = f"Are you sure you want to increase your user count from {self.active_licenses} to {user_count}?"
        else:
            operation_type = "downgrade"
            confirmation_message = f"Are you sure you want to decrease your user count from {self.active_licenses} to {user_count}?"

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
          user_count=user_count, 
          billing_period=billing_period
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
    user_count = event_args.get('user_count')
    billing_period = event_args.get('billing_period', 'monthly')
    if not plan_type or not user_count:
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
      user_count=user_count,
      billing_period=billing_period
    )
    subscription_result = alert(
      content=subscription_form,
      large=False,
      width=600,
      buttons=[],
      dismissible=True
    )
    #   # 7. If subscription was created successfully, refresh the page
    #   if subscription_result == 'success':
    #       anvil.js.window.location.reload()
