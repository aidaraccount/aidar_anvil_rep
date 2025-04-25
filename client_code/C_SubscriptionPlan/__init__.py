from ._anvil_designer import C_SubscriptionPlanTemplate
from anvil import *
import anvil.server
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..C_PaymentSubscription import C_PaymentSubscription
from anvil import Button, alert

class C_SubscriptionPlan(C_SubscriptionPlanTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()

    self.replace_choose_plan_buttons()

    self.html = """
    <!-- 2. Pricing Toggle -->
    <div class='pricing-toggle-container'>
        <div class='pricing-toggle'>
            <button id='pricing-toggle-monthly' class='pricing-toggle-btn selected' type='button'>Monthly</button>
            <button id='pricing-toggle-yearly' class='pricing-toggle-btn' type='button'>Yearly <span class='discount'>-10%</span></button>
        </div>
    </div>
    <!-- 3. Pricing Plans -->
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
    <!-- 5. Pricing Toggle JS -->
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
    from anvil import Button
    self.explore_btn = Button(text="Choose Plan", role="cta-button cta-primary center", tag={"plan_type": "Explore"})
    self.professional_btn = Button(text="Choose Plan", role="cta-button cta-primary center", tag={"plan_type": "Professional"})
    self.explore_btn.set_event_handler('click', self.choose_plan_click)
    self.professional_btn.set_event_handler('click', self.choose_plan_click)
    self.add_component(self.explore_btn, slot="explore-plan-button")
    self.add_component(self.professional_btn, slot="professional-plan-button")

  # 3. Handle Anvil Button clicks
  def choose_plan_click(self, sender, **event_args):
      """
      1. Handles clicks on the Explore and Professional plan buttons.
      2. Determines plan type and user count, then opens checkout.
      """
      plan_type: str = sender.tag.get("plan_type", "Explore")
      user_count: int = 1
      if plan_type == "Professional":
          # Get user count from the input box in the HTML
          import anvil.js
          user_count_raw = anvil.js.window.document.getElementById('user-count').value
          try:
              user_count = int(user_count_raw)
          except Exception:
              user_count = 1
      self.open_subscription(plan_type, user_count)

  # 4. Handle the full checkout process
  def open_subscription(self, plan_type: str, user_count: int) -> None:
      """
      1. Initiates the full checkout process in a clear, step-by-step manner.
      2. Collects payment info, creates a Stripe customer, and opens the subscription checkout.
      3. plan_type: 'Explore' or 'Professional'.
      4. user_count: Number of users for Professional plan (ignored for Explore).
      """
      from ..C_PaymentSubscription import C_PaymentSubscription
      import anvil.server
      billing_period = self.get_billing_period()

      # 1. Open the subscription checkout modal
      alert(
          content=C_PaymentSubscription(
              plan_type=plan_type,
              user_count=user_count,
              billing_period=billing_period
          ),
          large=False,
          width=500,
          buttons=[],
          dismissible=True
      )


  # 5. Determine the billing period
  def get_billing_period(self) -> str:
      """
      Returns the current billing period selected by the user ('monthly' or 'yearly').
      """
      import anvil.js
      # Detect which pricing toggle is selected in the HTML
      is_monthly = anvil.js.window.document.getElementById('pricing-toggle-monthly').classList.contains('selected')
      return 'monthly' if is_monthly else 'yearly'
