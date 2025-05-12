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
from datetime import date, datetime
import json

from ..C_PaymentSubscription import C_PaymentSubscription
from ..C_PaymentCustomer import C_PaymentCustomer
from ..C_PaymentInfos import C_PaymentInfos


class C_SubscriptionPlan(C_SubscriptionPlanTemplate):
  def __init__(self, plan, no_licenses, frequency, expiration_date, **properties):
    """
    1. Initialize the subscription plan component with default values
    2. Set up instance variables for plan details and button elements
    
    Parameters:
        plan: The plan type (Trial, Extended Trial, Explore, Professional)
        no_licenses: The number of licenses (for Professional plan)
        frequency: The billing frequency (monthly/yearly)
        expiration_date: The expiration date of the subscription
    """
    # Initialize the component
    self.init_components(**properties)
    
    global user
    user = anvil.users.get_user()

    # Initialize the subscribed values (what the user is currently subscribed to)
    self.subscribed_plan = "Trial" if plan is None else plan  # Current plan type (Explore/Professional)
    self.subscribed_licenses = 1 if no_licenses is None else no_licenses  # Current number of licenses
    self.subscribed_frequency = "monthly" if frequency is None else frequency  # Billing period (monthly/yearly)
    self.subscribed_expiration_date = expiration_date  # Expiration date of the subscription

    print('C_SubscriptionPlan subscribed_expiration_date:', self.subscribed_expiration_date)
    
    if self.subscribed_expiration_date is not None and self.subscribed_expiration_date > date.today():
      self.trial_end = (self.subscribed_expiration_date - date.today()).days
    else:
      self.trial_end = 0
    print('C_SubscriptionPlan trial_end:', self.trial_end)
    
    # Initialize the selected values (what the user is currently selecting in the UI)
    # Initially these are the same as the subscription values
    self.selected_plan = self.subscribed_plan
    self.selected_licenses = self.subscribed_licenses
    self.selected_frequency = self.subscribed_frequency
    
    # Save CSS for direct application via JavaScript
    self.explore_highlight_css = "0 0 20px rgba(0, 0, 0, 0.25)"
    self.professional_highlight_css = "0 0 20px rgba(0, 0, 0, 0.25)"

    # 1. HTML content
    self.html = """
    <!-- 1. Pricing Toggle -->
    <div class='pricing-toggle-container'>
        <div class='pricing-toggle'>
            <button id='pricing-toggle-monthly' class='pricing-toggle-btn """ + ('selected' if self.subscribed_frequency == "monthly" else '') + """' type='button'>Monthly</button>
            <button id='pricing-toggle-yearly' class='pricing-toggle-btn """ + ('selected' if self.subscribed_frequency == "yearly" else '') + """' type='button'>Yearly <span class='discount'>-10%</span></button>
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
    if ('""" + self.subscribed_frequency + """' === 'yearly') {
      setYearly();
    } else {
      setMonthly();
    }
    </script>
    """
    
    # 2. Add Anvil Buttons for plan selection
    self.explore_plan_btn = Button(text="Choose Plan", role="cta-button")
    self.professional_plan_btn = Button(text="Choose Plan", role="cta-button")
    
    # Set button event handlers and appearance based on current plan
    self.update_button_state()
    
    # Add buttons to appropriate slots
    self.add_component(self.explore_plan_btn, slot="explore-plan-button")
    self.add_component(self.professional_plan_btn, slot="professional-plan-button")
    
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
    
    # Initialize JS environment and setup custom JavaScript
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


  def js_update_button_state(self, **event_args):
    """
    1. Called reliably from JavaScript through Anvil's built-in event system
    2. Acts as a bridge between JavaScript UI events and Python button state updates
    3. Ensures changes to user inputs are reflected in button appearance
    """
    # Force a direct call to update_button_state to refresh UI state
    self.update_button_state()
    self.apply_plan_highlighting()


  def choose_plan_click(self, sender, **event_args):
    """
    1. Handles clicks on the Explore and Professional plan buttons
    2. Determines plan type, user count, and billing period, then opens checkout
    
    Parameters:
        sender: The button that was clicked
        event_args (dict): Event arguments from the button click
    """
    # Update the selected plan based on which button was clicked
    if sender == self.explore_plan_btn:
        self.selected_plan = "Explore"
    elif sender == self.professional_plan_btn:
        self.selected_plan = "Professional"
    
    # Ensure state is up-to-date
    self.update_button_state()
    
    # Open subscription checkout flow with the collected info
    self.open_subscription(
        selected_plan=self.selected_plan, 
        selected_licenses=self.selected_licenses, 
        selected_frequency=self.selected_frequency,
        trial_end=self.trial_end
    )


  def open_subscription(self, selected_plan: str, selected_licenses: int, selected_frequency: str, trial_end: int):
    """
    1. Opens the subscription workflow
    2. Handles navigation between components based on data availability
    3. Only proceeds to next step if previous data is available
    
    Parameters:
        selected_plan: The subscription plan (Explore/Professional)
        selected_licenses: Number of user licenses 
        selected_frequency: Billing frequency (monthly/yearly)
        trial_end: The trial end date of the subscription
    """
    # 1. Get the current subscription plan and billing period
    if not selected_plan or not selected_licenses:
      alert("Please select a plan and specify the number of users.", title="Missing Information")
      return
    
    # 2. Get subscription email
    base_data = anvil.server.call('get_settings_subscription2', user["user_id"])
    if base_data is not None:
      base_data = json.loads(base_data)[0]
      sub_email = base_data['mail'] if 'mail' in base_data else None
    else:
      sub_email = user['email']      
    
    # 3. Check if customer data exists
    customer = anvil.server.call('get_stripe_customer', sub_email)
    customer_exists = bool(customer and customer.get('id'))
    
    # 4. If no customer data, start with C_PaymentCustomer
    if not customer_exists:
      customer_form = C_PaymentCustomer(
        prefill_email=sub_email,
      )

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
      customer = anvil.server.call('get_stripe_customer', sub_email)
    
    # 5. Check if payment method exists
    payment_methods = []
    if customer and customer.get('id'):
      payment_methods = anvil.server.call('get_stripe_payment_methods', customer['id'])
    
    # 6. If no payment method, open C_PaymentInfos
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
    
    # 7. Finally, open subscription confirmation
    subscription_form = C_PaymentSubscription(
      plan=selected_plan,
      no_licenses=selected_licenses,
      frequency=selected_frequency,
      trial_end=trial_end
    )
    subscription_result = alert(
      content=subscription_form,
      large=False,
      width=600,
      buttons=[],
      dismissible=True
    )


  def update_subscription(self, **event_args) -> None:
    """
    1. Handles updating a subscription (upgrading, downgrading, or changing user count)
    2. Calls the server function to update the subscription in Stripe
    
    Parameters:
        event_args (dict): Event arguments from the button click
    """
    
    # Define operation type for user-friendly message
    operation_type = "update"
    confirmation_message = ""
    
    # Determine update type
    if self.selected_plan != self.subscribed_plan:
      # Plan change
      operation_type = "upgrade" if self.selected_plan == "Professional" else "downgrade"
      confirmation_message = f"Are you sure you want to {operation_type} from {self.subscribed_plan} to {self.selected_plan}?"
    elif self.selected_frequency != self.subscribed_frequency:
      # Billing period change
      if self.selected_frequency == "yearly":
        operation_type = "upgrade"
        confirmation_message = f"Are you sure you want to upgrade from monthly to yearly billing?"
      else:
        operation_type = "downgrade"
        confirmation_message = f"Are you sure you want to downgrade from yearly to monthly billing?"
    elif self.selected_licenses != self.subscribed_licenses:
      # User count change
      if self.selected_licenses > self.subscribed_licenses:
        operation_type = "increase"
        confirmation_message = f"Are you sure you want to increase your license count from {self.subscribed_licenses} to {self.selected_licenses}?"
      else:
        operation_type = "decrease"
        confirmation_message = f"Are you sure you want to reduce your license count from {self.subscribed_licenses} to {self.selected_licenses}?"
    elif self.subscribed_expiration_date is not None:
      # reactivate subscription
      operation_type = "reactivate"
      confirmation_message = "Are you sure you want to reactivate your subscription?"
    else:
      # No change detected
      alert("No changes to your subscription were detected.", buttons=["OK"], dismissible=False)
      return
    
    # Confirm with user
    confirmation = alert(
      confirmation_message,
      buttons=["Yes", "No"],
      dismissible=True
    )
    
    # If confirmed, make the API call to update subscription
    if confirmation == "Yes":
      try:
        result = anvil.server.call(
          'update_stripe_subscription',
          self.selected_plan,
          self.selected_licenses,
          self.selected_frequency,
          self.trial_end,
          self.subscribed_plan,
          self.subscribed_frequency
        )
        
        if result["success"]:
          # Subscription updated, show success message
          alert(f"Your subscription has been updated! {result.get('message', '')}", buttons=["OK"])
          
          # # Update UI to reflect changes (could redirect to another page or reload this component)
          # self.raise_event("x-subscription-updated")
        else:
          # Error occurred
          alert(f"Failed to update subscription: {result.get('message', 'An unknown error occurred.')}", buttons=["OK"])
      except Exception as e:
        # Handle any other errors
        alert(f"An error occurred: {str(e)}", buttons=["OK"])
        print(f"[SUBSCRIPTION_DEBUG] Error updating subscription: {e}")


  def cancel_subscription(self, **event_args) -> None:
    """
    1. Handles the cancellation of a subscription
    2. Calls the server function to cancel the subscription in Stripe
    
    Parameters:
        event_args (dict): Event arguments from the button click
    """
    # Get confirmation from user
    confirmation = alert(
      f"Are you sure you want to cancel your {self.subscribed_plan} subscription?",
      title="Cancel Subscription",
      buttons=["Yes, Cancel Subscription", "No, Keep Subscription"],
      large=False
    )

    if confirmation.startswith("Yes"):
      # Call server function to cancel subscription
      try:
        result = anvil.server.call('cancel_stripe_subscription')
        if result and result.get('success'):
          alert(f"Your subscription has been cancelled and will end on {result.get('expiration_date')}.", title="Subscription Cancelled")
          # Refresh the page to reflect the changes
          anvil.js.window.location.reload()
        else:
          alert("There was a problem cancelling your subscription. Please try again or contact support at team@aidar.ai.", title="Error")
      except Exception as e:
        print(f"[SUBSCRIPTION_DEBUG] Error in cancel_stripe_subscription: {e}")
        alert("There was a problem processing your request. Please try again or contact support at team@aidar.ai.", title="Error")


  def reactivate_stripe_subscription(self):
    """
    1. Reactivates a cancelled subscription in Stripe
    2. Calls the server function to reactivate the subscription
    """
    try:
      result = anvil.server.call('reactivate_stripe_subscription')
      if result and result.get('success'):
        alert("Your subscription has been reactivated.", title="Subscription Reactivated")
        # Refresh the page to reflect the changes
        anvil.js.window.location.reload()
      else:
        alert("There was a problem reactivating your subscription. Please try again or contact support at team@aidar.ai.", title="Error")
    except Exception as e:
      print(f"[SUBSCRIPTION_DEBUG] Error in reactivate_stripe_subscription: {e}")
      alert("There was a problem processing your request. Please try again or contact support at team@aidar.ai.", title="Error")


  def update_button_state(self):
    """
    1. Updates button appearance and event handlers based on the subscribed plan
    2. Configures text, styling, and click behavior for both the Explore and Professional buttons
    3. Considers billing period (monthly/yearly) preference when determining upgrade/downgrade status
    """
    # First get the selected user count from the DOM - we need this for proper button behavior
    user_count_input = document.getElementById('user-count')
    if user_count_input is not None:
      try:
        self.selected_licenses = int(user_count_input.value)
      except Exception:
        pass  # Keep existing value if there's an error
    
    # Determine active billing period from JS toggle state - Update self.selected_frequency
    monthly_btn = document.getElementById('pricing-toggle-monthly')
    yearly_btn = document.getElementById('pricing-toggle-yearly')
    
    if monthly_btn and yearly_btn:
      is_yearly = yearly_btn.classList.contains('selected')
      self.selected_frequency = "yearly" if is_yearly else "monthly"
        
    # 1. LEFT EXPLORE BUTTON LOGIC
    if self.subscribed_plan in ["Trial", "Extended Trial", None]:
      # If not subscribed yet, just show basic "Choose Plan" button
      self.explore_plan_btn.text = "Choose Plan"
      self.explore_plan_btn.role = "cta-button"
      self.explore_plan_btn.set_event_handler('click', self.choose_plan_click)
    
    elif self.subscribed_plan == "Explore":
      # If already on Explore plan, check frequency
      if self.selected_frequency == self.subscribed_frequency:
        if self.subscribed_expiration_date is None:
          # Same plan, same frequency - show Cancel Subscription button
          self.explore_plan_btn.text = "Cancel Subscription"
          self.explore_plan_btn.role = "secondary-button"
          self.explore_plan_btn.set_event_handler('click', self.cancel_subscription)
        else:
          # Same plan, same frequency - show Renew Subscription button
          self.explore_plan_btn.text = "Renew Subscription"
          self.explore_plan_btn.role = "cta-button"
          self.explore_plan_btn.set_event_handler('click', self.reactivate_stripe_subscription)
      else:
        # Same plan but different frequency - allow change
        if self.selected_frequency == "yearly":
          # Monthly to Yearly is upgrade
          self.explore_plan_btn.text = "Upgrade to Yearly"
          self.explore_plan_btn.role = "cta-button"
        else:
          # Yearly to Monthly is downgrade
          self.explore_plan_btn.text = "Downgrade to Monthly"
          self.explore_plan_btn.role = "secondary-button"
        self.explore_plan_btn.set_event_handler('click', self.update_subscription)
    
    elif self.subscribed_plan == "Professional":
      # If on Professional plan, allow downgrade
      self.explore_plan_btn.text = "Downgrade to Explore"
      self.explore_plan_btn.role = "secondary-button"
      self.explore_plan_btn.set_event_handler('click', self.update_subscription)
    
    # 2. RIGHT PROFESSIONAL BUTTON LOGIC
    if self.subscribed_plan in ["Trial", "Extended Trial", None]:
      # If not subscribed yet, just show basic "Choose Plan" button
      self.professional_plan_btn.text = "Choose Plan"
      self.professional_plan_btn.role = "cta-button"
      self.professional_plan_btn.set_event_handler('click', self.choose_plan_click)
        
    elif self.subscribed_plan == "Explore":
      # If on Explore plan, allow upgrade to Professional
      self.professional_plan_btn.text = "Upgrade to Professional"
      self.professional_plan_btn.role = "cta-button"
      self.professional_plan_btn.set_event_handler('click', self.update_subscription)
        
    elif self.subscribed_plan == "Professional":
      # Check if this is the exact same subscription or a change
      is_same_subscription = (self.selected_licenses == self.subscribed_licenses and 
                            self.selected_frequency == self.subscribed_frequency and 
                            self.subscribed_plan == "Professional")
      
      if is_same_subscription:
        if self.subscribed_expiration_date is None:
          # Exact same plan - show Current Plan + Cancel option
          self.professional_plan_btn.text = "Cancel Subscription"
          self.professional_plan_btn.role = "secondary-button"
          self.professional_plan_btn.set_event_handler('click', self.cancel_subscription)
        else:
          # Exact same plan - show Current Plan + Cancel option
          self.professional_plan_btn.text = "Renew Subscription"
          self.professional_plan_btn.role = "cta-button"
          self.professional_plan_btn.set_event_handler('click', self.reactivate_stripe_subscription)
      else:
        # Is this an upgrade or downgrade?
        is_upgrade = (self.selected_licenses > self.subscribed_licenses) or (self.subscribed_frequency == 'monthly' and self.selected_frequency == 'yearly')
        
        if is_upgrade:
          # Orange "Upgrade Plan"
          self.professional_plan_btn.text = "Upgrade Plan"
          self.professional_plan_btn.role = "cta-button"
        else:
          # Grey "Downgrade Plan"
          self.professional_plan_btn.text = "Downgrade Plan"
          self.professional_plan_btn.role = "secondary-button"
            
        self.professional_plan_btn.set_event_handler('click', self.update_subscription)
    
    # 3. HANDLE BILLING PERIOD CHANGES EXPLICITLY
    if self.subscribed_plan not in ["Trial", "Extended Trial", None]:
      # Only for paid plans, check for billing period changes
      if self.subscribed_frequency != self.selected_frequency:
        if self.selected_frequency == "yearly" and self.subscribed_frequency == "monthly":
          # Upgrading to yearly - orange
          self.explore_plan_btn.text = "Upgrade to Yearly"
          self.explore_plan_btn.role = "cta-button"
          self.explore_plan_btn.set_event_handler('click', self.update_subscription)
          self.professional_plan_btn.text = "Upgrade to Yearly"
          self.professional_plan_btn.role = "cta-button"
          self.professional_plan_btn.set_event_handler('click', self.update_subscription)
        elif self.selected_frequency == "monthly" and self.subscribed_frequency == "yearly":
          # Downgrading to monthly - grey
          self.explore_plan_btn.text = "Downgrade to Monthly"
          self.explore_plan_btn.role = "secondary-button"
          self.explore_plan_btn.set_event_handler('click', self.update_subscription)
          self.professional_plan_btn.text = "Downgrade to Monthly"
          self.professional_plan_btn.role = "secondary-button"
          self.professional_plan_btn.set_event_handler('click', self.update_subscription)
    
    # Apply highlighting
    self.apply_plan_highlighting()


  def apply_plan_highlighting(self):
    """
    1. Applies highlighting to the appropriate plan box based on subscription plan
    2. Uses subtle box-shadow and indicator label for current plan
    """
    print(f"[SUBSCRIPTION_DEBUG] Applying plan highlighting for plan: {self.subscribed_plan}")
    
    # Check if all parameters match current subscription
    should_highlight = False
    if self.subscribed_plan == "Explore" and self.selected_plan == "Explore":
        # For Explore, only check billing period
        should_highlight = (self.subscribed_frequency == self.selected_frequency)
        print(f"[SUBSCRIPTION_DEBUG] Explore highlight check: frequency={self.subscribed_frequency == self.selected_frequency}")
    elif self.subscribed_plan == "Professional" and self.selected_plan == "Professional":
        # For Professional, check licenses and billing period
        should_highlight = (self.subscribed_licenses == self.selected_licenses and 
                            self.subscribed_frequency == self.selected_frequency)
        print(f"[SUBSCRIPTION_DEBUG] Professional highlight check: licenses={self.subscribed_licenses == self.selected_licenses}, frequency={self.subscribed_frequency == self.selected_frequency}")
    
    # Create the JavaScript to apply highlighting 
    anvil.js.call('eval', f"""
    try {{
      console.log("[SUBSCRIPTION_DEBUG] Applying discreet highlight ({self.subscribed_plan}) - should highlight: {should_highlight}");
      
      // Clear any existing interval to prevent multiple calls
      if (window.highlightInterval) {{
          clearInterval(window.highlightInterval);
          window.highlightInterval = null;
      }}
      
      // 1. Clean up any existing highlights first
      function removeAllHighlights() {{
        // Remove existing markers and labels
        document.querySelectorAll('.current-plan-label').forEach(function(el) {{
          el.parentNode.removeChild(el);
        }});
        
        // Reset any box-shadows
        document.querySelectorAll('.pricing-plan.left, .pricing-plan.recommended').forEach(function(box) {{
          box.style.boxShadow = '';
        }});
        
        // Always show recommended tag for non-Professional subscribers
        if ('{self.subscribed_plan}' !== 'Professional') {{
          // Find all recommended boxes and make sure the ribbon is visible
          document.querySelectorAll('.pricing-plan.recommended').forEach(function(box) {{
            // Find and show the ribbon element if it exists
            var ribbons = box.querySelectorAll('.ribbon');
            ribbons.forEach(function(ribbon) {{
              ribbon.style.display = 'block';
            }});
            
            // Find and show the recommended tag
            var recommendedTags = box.querySelectorAll('.recommended-tag');
            recommendedTags.forEach(function(tag) {{
              tag.style.display = 'block';
            }});
          }});
        }}
      }}
      
      // 2. Function to apply the highlighting
      function applyHighlight() {{
        // First clean up any existing highlights
        removeAllHighlights();
        
        // Only highlight if parameters match
        if (!{str(should_highlight).lower()}) {{
          console.log('[SUBSCRIPTION_DEBUG] Not highlighting - parameter mismatch');
          return;
        }}
        
        // Determine which plan box to highlight
        var targetSelector = '{self.subscribed_plan}' === 'Explore' ? 
                          '.pricing-plan.left' : 
                          '.pricing-plan.recommended';
                          
        var boxColor = '{self.subscribed_plan}' === 'Explore' ? 
                     'var(--PurpleFocus, rgb(130, 39, 118))' : 
                     'var(--Orange, #FF6400)';
        
        // Find all matching boxes
        var boxes = document.querySelectorAll(targetSelector);
        console.log('[SUBSCRIPTION_DEBUG] Found ' + boxes.length + ' plan boxes to highlight');
        
        // Apply subtle highlight to each box
        boxes.forEach(function(box) {{
          // Apply box-shadow only
          box.style.boxShadow = '8px 8px 10px ' + boxColor;
          console.log('[SUBSCRIPTION_DEBUG] Applied box-shadow to plan');
          
          // Hide recommended ribbon and tag if this is the Professional plan
          if ('{self.subscribed_plan}' === 'Professional') {{
            // Hide ribbon elements
            var ribbons = box.querySelectorAll('.ribbon');
            ribbons.forEach(function(ribbon) {{
              ribbon.style.display = 'none';
            }});
            
            // Hide recommended tag
            var recommendedTags = box.querySelectorAll('.recommended-tag');
            recommendedTags.forEach(function(tag) {{
              tag.style.display = 'none';
            }});
          }}
          
          // Add the "CURRENT PLAN" label in the upper right
          var label = document.createElement('div');
          label.className = 'current-plan-label';
          label.textContent = 'CURRENT PLAN';
          label.style.backgroundColor = boxColor;
          label.style.color = 'white';
          label.style.fontWeight = 'bold';
          label.style.padding = '4px 8px';
          label.style.position = 'absolute';
          label.style.top = '10px';
          label.style.right = '10px';
          label.style.zIndex = '999';
          label.style.borderRadius = '4px';
          label.style.fontSize = '11px';
          
          // Make sure the box has relative positioning for the absolute label
          if (window.getComputedStyle(box).position === 'static') {{
            box.style.position = 'relative';
          }}
          
          box.appendChild(label);
          console.log('[SUBSCRIPTION_DEBUG] Added "CURRENT PLAN" label');
        }});
      }}
      
      // 3. Apply only once initially
      applyHighlight();
      
      // 4. Set up MutationObserver for dynamic changes
      var observer = new MutationObserver(function(mutations) {{
        var shouldCheck = false;
        
        for(var mutation of mutations) {{
          if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {{
            for(var node of mutation.addedNodes) {{
              if (node.nodeType === 1) {{ // Element node
                if ((node.classList && 
                    (node.classList.contains('pricing-plan') || 
                     node.classList.contains('recommended') ||
                     node.classList.contains('left'))) ||
                    (node.querySelector && 
                     (node.querySelector('.pricing-plan') ||
                      node.querySelector('.recommended') ||
                      node.querySelector('.left')))) {{
                  shouldCheck = true;
                  break;
                }}
              }}
            }}
          }}
          
          if (shouldCheck) break;
        }}
        
        // Use debounce pattern to prevent multiple rapid calls
        if (shouldCheck) {{
          console.log('[SUBSCRIPTION_DEBUG] Detected pricing plan changes, scheduling highlight update');
          if (window.highlightTimeout) {{
            clearTimeout(window.highlightTimeout);
          }}
          window.highlightTimeout = setTimeout(applyHighlight, 100);
        }}
      }});
      
      observer.observe(document.body, {{ childList: true, subtree: true }});
      console.log('[SUBSCRIPTION_DEBUG] Set up MutationObserver to watch for DOM changes');
      
      // 5. Apply when toggle buttons are clicked - with debounce
      var toggles = document.querySelectorAll('#pricing-toggle-monthly, #pricing-toggle-yearly');
      toggles.forEach(function(toggle) {{
        // Remove any existing listeners first
        toggle.removeEventListener('click', toggle.highlightListener);
        
        // Add new listener with debounce
        toggle.highlightListener = function() {{
          console.log('[SUBSCRIPTION_DEBUG] Pricing toggle clicked, scheduling highlight update');
          if (window.highlightTimeout) {{
            clearTimeout(window.highlightTimeout);
          }}
          window.highlightTimeout = setTimeout(applyHighlight, 200);
        }};
        
        toggle.addEventListener('click', toggle.highlightListener);
      }});
      
    }} catch (e) {{
      console.error("[SUBSCRIPTION_DEBUG] Error applying plan highlighting:", e);
      console.error("[SUBSCRIPTION_DEBUG] Error details:", e.message, e.stack);
    }}
    """)
