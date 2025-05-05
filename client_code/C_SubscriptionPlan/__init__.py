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
  def __init__(self, plan, no_licenses, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()

    print('plan:', plan)
    print('no_licenses:', no_licenses)

    # Determine which plan to highlight
    self.active_plan = None
    self.active_licenses = None
    if plan not in ["Trial", "Extended Trial"]:
        if plan == "Explore":
            self.active_plan = "explore"
        elif plan == "Professional":
            self.active_plan = "professional"
            self.active_licenses = no_licenses

    # 1. HTML content
    self.html = f"""
    <!-- 1. Pricing Toggle -->
    <div class='pricing-toggle-container'>
        <div class='pricing-toggle'>
            <button id='pricing-toggle-monthly' class='pricing-toggle-btn selected' type='button'>Monthly</button>
            <button id='pricing-toggle-yearly' class='pricing-toggle-btn' type='button'>Yearly <span class='discount'>-10%</span></button>
        </div>
    </div>
    <!-- 2. Pricing Plans -->
    <div class='pricing-plans'>
        <!-- Explore Plan -->
        <div class='pricing-plan left{' active' if self.active_plan == 'explore' else ''}'>
            <h2 class='plan-name'>Explore</h2>
            <p class='plan-description'>Best for solo scouts exploring AI-powered artist discovery.</p>
            <div class='plan-price-container'>
                <div class='discount-badge'>25%<br>Launch Disc.</div>
                <span class='original-price'><span class='euro-symbol'>€</span><span class='price-number'>38</span></span>
                <span class='plan-price'><span class='euro-symbol'>€</span>27</span>
                <span class='price-period'>/month</span>
            </div>
            <ul class='plan-features'>
                <li>1 user</li>
                <li>100 Artist Profiles per month</li>
                <li>1 AI-scouting-agent</li>
                <li>1 Watchlist</li>
                <li>E-Mail Support</li>
            </ul>
            <div anvil-slot="explore-plan-button"></div>
        </div>
        <!-- Professional Plan -->
        <div class='pricing-plan recommended{' active' if self.active_plan == 'professional' else ''}'>
            <div class='recommended-tag'>Recommended</div>
            <h2 class='plan-name'>Professional</h2>
            <p class='plan-description'>For individuals or teams who want to unlock full AI-powered scouting.</p>
            <div class='plan-price-container'>
                <div class='discount-badge'>25%<br>Launch Disc.</div>
                <span class='original-price'><span class='euro-symbol'>€</span><span class='price-number'>58</span></span>
                <span class='plan-price'><span class='euro-symbol'>€</span>41</span>
                <span class='price-period'>/user & month</span>
            </div>
            <ul class='plan-features'>
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
                    <input id='user-count' class='user-count-value-input' type='text' value='{self.active_licenses if self.active_licenses else 1}' maxlength='3' />
                    <span> User<span id='user-count-plural' style='display:none;'>s</span></span>
                </span>
                <button type='button' class='user-count-btn' id='user-plus'>+</button>
            </div>
            <div anvil-slot="professional-plan-button"></div>
        </div>
    </div>
    
    <!-- 3. Pricing Toggle JS -->
    <script>
    // Pricing toggle JS
    function setMonthly() {{
        var origPrice = document.querySelector('.pricing-plan.left .original-price');
        if (origPrice) origPrice.innerHTML = '<span class=\"euro-symbol\">€</span><span class=\"price-number\">39</span>';
        var planPrice = document.querySelector('.pricing-plan.left .plan-price');
        if (planPrice) planPrice.innerHTML = '<span class=\"euro-symbol\">€</span>29';
        var pricePeriod = document.querySelector('.pricing-plan.left .price-period');
        if (pricePeriod) pricePeriod.textContent = '/month';
        var monthlyBtn = document.getElementById('pricing-toggle-monthly');
        var yearlyBtn = document.getElementById('pricing-toggle-yearly');
        if (monthlyBtn) monthlyBtn.classList.add('selected');
        if (yearlyBtn) yearlyBtn.classList.remove('selected');
        updateProfessionalPrice();
    }}
    function setYearly() {{
        var origPrice = document.querySelector('.pricing-plan.left .original-price');
        if (origPrice) origPrice.innerHTML = '<span class=\"euro-symbol\">€</span><span class=\"price-number\">35</span>';
        var planPrice = document.querySelector('.pricing-plan.left .plan-price');
        if (planPrice) planPrice.innerHTML = '<span class=\"euro-symbol\">€</span>25';
        var pricePeriod = document.querySelector('.pricing-plan.left .price-period');
        if (pricePeriod) pricePeriod.textContent = '/month (billed yearly)';
        var monthlyBtn = document.getElementById('pricing-toggle-monthly');
        var yearlyBtn = document.getElementById('pricing-toggle-yearly');
        if (monthlyBtn) monthlyBtn.classList.remove('selected');
        if (yearlyBtn) yearlyBtn.classList.add('selected');
        updateProfessionalPrice();
    }}
        
        // Updated Professional pricing function
        function updateProfessionalPrice() {{
            try {{
                var userCountInput = document.getElementById('user-count');
                if (!userCountInput) return;
                
                var userCount = parseInt(userCountInput.value);
                if (isNaN(userCount) || userCount < 1) userCount = 1;
                
                var isYearly = false;
                var yearlyBtn = document.getElementById('pricing-toggle-yearly');
                if (yearlyBtn) isYearly = yearlyBtn.classList.contains('selected');
                
                var origPrice = document.querySelector('.pricing-plan.recommended .original-price');
                var planPrice = document.querySelector('.pricing-plan.recommended .plan-price');
                var pricePeriod = document.querySelector('.pricing-plan.recommended .price-period');
                
                // Pricing per user
                var origPricePerUser = isYearly ? 52 : 58;
                var discountPricePerUser = isYearly ? 37 : 41;
                
                // Update prices based on user count
                if (origPrice) {{
                    origPrice.innerHTML = '<span class=\"euro-symbol\">€</span><span class=\"price-number\">' + (origPricePerUser * userCount) + '</span>';
                }}
                
                if (planPrice) {{
                    planPrice.innerHTML = '<span class=\"euro-symbol\">€</span>' + (discountPricePerUser * userCount);
                }}
                
                if (pricePeriod) {{
                    if (isYearly) {{
                        pricePeriod.textContent = userCount > 1 ? 
                            'for ' + userCount + ' users/month (billed yearly)' : 
                            '/user & month (billed yearly)';
                    }} else {{
                        pricePeriod.textContent = userCount > 1 ? 
                            'for ' + userCount + ' users/month' : 
                            '/user & month';
                    }}
                }}
                
                // Update the plural display on the user count
                var pluralSpan = document.getElementById('user-count-plural');
                if (pluralSpan) {{
                    pluralSpan.style.display = (userCount > 1) ? '' : 'none';
                }}
            }} catch(e) {{
                console.error("Error updating professional price:", e);
            }}
        }}
        
        document.addEventListener('DOMContentLoaded', function() {{
            var monthlyBtn = document.getElementById('pricing-toggle-monthly');
            var yearlyBtn = document.getElementById('pricing-toggle-yearly');
            if (monthlyBtn) monthlyBtn.addEventListener('click', setMonthly);
            if (yearlyBtn) yearlyBtn.addEventListener('click', setYearly);
            
            // User count selector logic
            var userCountInput = document.getElementById('user-count');
            var minusBtn = document.getElementById('user-minus');
            var plusBtn = document.getElementById('user-plus');
            
            function handleUserCountChange() {{
                try {{
                    if (!userCountInput) return;
                    
                    var val = parseInt(userCountInput.value.replace(/\\D/g, ''));
                    if (isNaN(val) || val < 1) val = 1;
                    userCountInput.value = val;
                    
                    // Update pricing based on user count
                    updateProfessionalPrice();
                    
                    // Notify Python that the user count has changed
                    try {{
                        var pyComponent = window.pyComponent;
                        if (pyComponent && pyComponent.user_count_changed) {{
                            pyComponent.user_count_changed(val);
                        }}
                    }} catch(e) {{
                        console.log('Error notifying Python:', e);
                    }}
                }} catch(e) {{
                    console.error("Error in handleUserCountChange:", e);
                }}
            }}
            
            // Directly attach click events with proper functionality
            if (minusBtn) {{
                minusBtn.addEventListener('click', function() {{
                    try {{
                        if (!userCountInput) return;
                        
                        var val = parseInt(userCountInput.value);
                        if (isNaN(val) || val <= 1) val = 2;
                        userCountInput.value = val - 1;
                        
                        handleUserCountChange();
                    }} catch(e) {{
                        console.error("Error in minus button click:", e);
                    }}
                }});
            }}
            
            if (plusBtn) {{
                plusBtn.addEventListener('click', function() {{
                    try {{
                        if (!userCountInput) return;
                        
                        var val = parseInt(userCountInput.value);
                        if (isNaN(val)) val = 0;
                        userCountInput.value = val + 1;
                        // Trigger change event
                        userCountInput.dispatchEvent(new Event('input'));
                    }} catch(e) {{
                        console.error("Error in plus button click:", e);
                    }}
                }});
            }}
            
            if (userCountInput) {{
                userCountInput.addEventListener('input', handleUserCountChange);
                userCountInput.addEventListener('change', handleUserCountChange);
                
                // Initialize
                handleUserCountChange();
            }}
            
            // Set initial prices
            setMonthly();
            
            // Store reference to the Python component for callbacks
            window.pyComponent = null;
            try {{
                // This will be set by Python after the HTML is rendered
                window.setPyComponent = function(component) {{
                    window.pyComponent = component;
                    console.log("Python component reference set");
                }};
            }} catch(e) {{
                console.log('Error setting up Python bridge:', e);
            }}
        }});
    """

    # 2. Set up JavaScript-Python bridge for user count changes
    from anvil.js.window import document
    
    # 2.1 Configure button appearance and behaviors
    self.explore_btn = Button(text="Choose Plan", role="cta-button", tag={"plan_type": "Explore"})
    self.professional_btn = Button(text="Choose Plan", role="cta-button", tag={"plan_type": "Professional"})
    
    # 2.2 Set up event handlers
    self.explore_btn.set_event_handler('click', self.choose_plan_click)
    self.professional_btn.set_event_handler('click', self.choose_plan_click)
    
    # 2.3 Add buttons to appropriate slots
    self.add_component(self.explore_btn, slot="explore-plan-button")
    self.add_component(self.professional_btn, slot="professional-plan-button")
    
    # 2.4 Set up JavaScript-Python communication for user count changes
    anvil.js.call_js('setTimeout', """
    function() {
      try {
        // Get user count input element
        var userCountInput = document.getElementById('user-count');
        
        // Add JS event listener that will call our Python method
        if (userCountInput) {
          userCountInput.addEventListener('input', function() {
            var val = parseInt(userCountInput.value);
            if (isNaN(val) || val < 1) val = 1;
            
            // This directly calls the Python method
            _this.user_count_changed(val);
          });
          
          // Setup plus/minus buttons
          var minusBtn = document.getElementById('user-minus');
          var plusBtn = document.getElementById('user-plus');
          
          if (minusBtn) {
            minusBtn.addEventListener('click', function() {
              if (!userCountInput) return;
              var val = parseInt(userCountInput.value);
              if (isNaN(val) || val <= 1) val = 2;
              userCountInput.value = val - 1;
              
              // Trigger change event
              userCountInput.dispatchEvent(new Event('input'));
            });
          }
          
          if (plusBtn) {
            plusBtn.addEventListener('click', function() {
              if (!userCountInput) return;
              var val = parseInt(userCountInput.value);
              if (isNaN(val)) val = 0;
              userCountInput.value = val + 1;
                            // Trigger change event
              userCountInput.dispatchEvent(new Event('input'));
            });
          }
        }
      } catch(e) {
        console.error("Error setting up Python-JS bridge:", e);
      }
    }
    """, 500)  # 500ms delay to ensure DOM is ready
    
    # 2.5 Initialize button states based on current plan
    self.update_plan_buttons()

  def choose_plan_click(self, **event_args) -> None:
    """
    1. Handles the click event for the 'Choose Plan' button.
    2. Initiates the subscription process for the selected plan.
    
    Parameters:
        event_args (dict): Event arguments from the button click
    """
    plan_type: str = self.sender.tag.get("plan_type", "")
    user_count: int = self.professional_btn.tag.get("user_count", 1)
    # TODO: Implement subscription logic for each plan type
    alert(f"Plan chosen: {plan_type}, Users: {user_count}")

  def cancel_subscription(self, **event_args) -> None:
    """
    1. Handles the click event for the 'Cancel Plan' or 'Downgrade Plan' button.
    2. Initiates the cancellation or downgrade process for the subscription.
    
    Parameters:
        event_args (dict): Event arguments from the button click
    """
    plan_type: str = self.sender.tag.get("plan_type", "")
    # TODO: Implement cancellation logic for each plan type
    alert(f"Cancel/Downgrade requested for plan: {plan_type}")

  def user_count_changed(self, new_count: int) -> None:
    """
    1. Called by JavaScript when the user count input changes
    2. Updates the professional plan button state accordingly
    
    Args:
        new_count (int): The new number of users selected
    """
    try:
        current_licenses = self.active_licenses if self.active_licenses else 1
        
        # Save the current count for future reference
        self.professional_btn.tag["user_count"] = new_count
        
        # Update the button text and role based on the plan and count
        self.update_plan_buttons()
        
        # Update the price display in JavaScript
        anvil.js.call_js("""
        function() {
          try {
            var userCount = arguments[0];
            if (userCount < 1) userCount = 1;
            
            var isYearly = document.getElementById('pricing-toggle-yearly') &&
                          document.getElementById('pricing-toggle-yearly').classList.contains('selected');
            
            var origPrice = document.querySelector('.pricing-plan.recommended .original-price');
            var planPrice = document.querySelector('.pricing-plan.recommended .plan-price');
            var pricePeriod = document.querySelector('.pricing-plan.recommended .price-period');
            
            // Pricing per user
            var origPricePerUser = isYearly ? 52 : 58;
            var discountPricePerUser = isYearly ? 37 : 41;
            
            // Update prices based on user count
            if (origPrice) {
                origPrice.innerHTML = '<span class="euro-symbol">€</span><span class="price-number">' + 
                                    (origPricePerUser * userCount) + '</span>';
            }
            
            if (planPrice) {
                planPrice.innerHTML = '<span class="euro-symbol">€</span>' + (discountPricePerUser * userCount);
            }
            
            if (pricePeriod) {
                if (isYearly) {
                    pricePeriod.textContent = userCount > 1 ? 
                        'for ' + userCount + ' users/month (billed yearly)' : 
                        '/user & month (billed yearly)';
                } else {
                    pricePeriod.textContent = userCount > 1 ? 
                        'for ' + userCount + ' users/month' : 
                        '/user & month';
                }
            }
            
            // Update the plural display on the user count
            var pluralSpan = document.getElementById('user-count-plural');
            if (pluralSpan) {
                pluralSpan.style.display = (userCount > 1) ? '' : 'none';
            }
          } catch(e) {
            console.error("Error updating professional price:", e);
          }
        }
        """, new_count)
        
    except Exception as e:
        print("Error in user_count_changed:", e)

  def update_plan_buttons(self) -> None:
    """
    1. Updates the text, role, and handlers for both plan buttons based on active plan
    2. Sets the appropriate button state: Choose, Cancel, or Update
    """
    # Get current user count if available
    user_count = 1
    try:
        user_count_input = self.get_user_count_input()
        if user_count_input:
            user_count = int(user_count_input.value)
    except:
        pass
    
    current_licenses = self.active_licenses if self.active_licenses else 1
    self.professional_btn.tag["user_count"] = user_count
    
    # For Trial or Extended Trial: both "Choose Plan" buttons should be orange
    if self.active_plan in ["Trial", "Extended Trial", None]:
        # Configure Explore button
        self.explore_btn.text = "Choose Plan"
        self.explore_btn.role = "cta-button"
        self.explore_btn.set_event_handler('click', self.choose_plan_click)
        
        # Configure Professional button
        self.professional_btn.text = "Choose Plan"
        self.professional_btn.role = "cta-button"
        self.professional_btn.set_event_handler('click', self.choose_plan_click)
    
    # For Explore plan
    elif self.active_plan == "explore":
        # Configure Explore button - Cancel (grey)
        self.explore_btn.text = "Cancel Plan"
        self.explore_btn.role = "secondary-button"
        self.explore_btn.set_event_handler('click', self.cancel_subscription)
        
        # Configure Professional button - Upgrade (orange)
        self.professional_btn.text = "Upgrade Plan"
        self.professional_btn.role = "cta-button"
        self.professional_btn.set_event_handler('click', self.choose_plan_click)
    
    # For Professional plan
    elif self.active_plan == "professional":
        # Configure Explore button - Downgrade (grey)
        self.explore_btn.text = "Downgrade Plan"
        self.explore_btn.role = "secondary-button"
        self.explore_btn.set_event_handler('click', self.choose_plan_click)
        
        # Configure Professional button based on user count vs. current licenses
        if user_count > current_licenses:
            # Upgrade (orange)
            self.professional_btn.text = "Upgrade Subscription"
            self.professional_btn.role = "cta-button"
            self.professional_btn.set_event_handler('click', self.update_subscription)
        elif user_count < current_licenses:
            # Downgrade (grey)
            self.professional_btn.text = "Downgrade Subscription"
            self.professional_btn.role = "secondary-button"
            self.professional_btn.set_event_handler('click', self.update_subscription)
        else:
            # Cancel (grey)
            self.professional_btn.text = "Cancel Plan"
            self.professional_btn.role = "secondary-button"
            self.professional_btn.set_event_handler('click', self.cancel_subscription)
