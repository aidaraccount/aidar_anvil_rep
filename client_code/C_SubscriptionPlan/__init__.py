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
from ..C_PaymentInfos import C_PaymentInfos#


class C_SubscriptionPlan(C_SubscriptionPlanTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()

    # 1. HTML content
    self.html = """
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
        <div class='pricing-plan left'>
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
                    <input id='user-count' class='user-count-value-input' type='text' value='1' maxlength='3' />
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
    var userCount = 1;
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
        var val = parseInt(userCountInput.value.replace(/\D/g, ''));
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
    });
    userCountInput.addEventListener('blur', function() {
        if (!userCountInput.value || parseInt(userCountInput.value) < 1) {
            userCount = 1;
            userCountInput.value = 1;
            userCountPlural.style.display = 'none';
            setProfessionalPrice();
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
        }
    });
    document.getElementById('pricing-toggle-monthly').addEventListener('click', setMonthly);
    document.getElementById('pricing-toggle-yearly').addEventListener('click', setYearly);
    setMonthly();
    </script>
    """


    # 2. Add Anvil Buttons for plan selection
    self.explore_btn = Button(text="Choose Plan", role="cta-button", tag={"plan_type": "Explore"})
    self.professional_btn = Button(text="Choose Plan", role="cta-button", tag={"plan_type": "Professional"})
    self.explore_btn.set_event_handler('click', self.choose_plan_click)
    self.professional_btn.set_event_handler('click', self.choose_plan_click)
    self.add_component(self.explore_btn, slot="explore-plan-button")
    self.add_component(self.professional_btn, slot="professional-plan-button")

  # 3. Handle Anvil Button clicks
  def choose_plan_click(self, sender, **event_args):
      """
      1. Handles clicks on the Explore and Professional plan buttons.
      2. Determines plan type, user count, and billing period, then opens checkout.
      """
      plan_type = sender.tag.get("plan_type")
      # Get user count from JS input field
      user_count_input = document.getElementById('user-count')
      user_count = 1
      if user_count_input is not None:
          try:
              user_count = int(user_count_input.value)
          except Exception:
              user_count = 1
      # Determine billing period from JS button state
      monthly_btn = document.getElementById('pricing-toggle-monthly')
      billing_period = "monthly"
      if monthly_btn and not monthly_btn.classList.contains('selected'):
          billing_period = "yearly"
      self.open_subscription(plan_type=plan_type, user_count=user_count, billing_period=billing_period)

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
      # 7. If subscription was created successfully, refresh the page
      if subscription_result == 'success':
          anvil.js.window.location.reload()
