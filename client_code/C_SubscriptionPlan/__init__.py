from ._anvil_designer import C_SubscriptionPlanTemplate
from anvil import *
import anvil.server
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class C_SubscriptionPlan(C_SubscriptionPlanTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()


    self.html = """
    <!-- 1. Pricing Header -->
    <div class='pricing-header'>
        <span class='orange-dot'></span>
        <span>Pricing</span>
    </div>
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
            <a href='https://app.aidar.ai/#register?license_key=None' class='cta-button cta-primary center'>Start 14-day Free Trial</a>
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
            <a href='https://app.aidar.ai/#register?license_key=None' class='cta-button cta-primary center'>Start 14-day Free Trial</a>
        </div>
    </div>
    <!-- 4. Call to Action -->
    <div class='pricing-cta'>
        <div class='demo-text'>Curious how AIDAR fits your process? Let's chat.</div>
        <div>
            <a href='/book-demo.html' class='cta-button cta-secondary'>Book a demo</a>
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
        document.querySelector('.pricing-plan.recommended .original-price').innerHTML = '<span class="euro-symbol">€</span><span class="price-number">59</span>';
        document.querySelector('.pricing-plan.recommended .plan-price').innerHTML = '<span class="euro-symbol">€</span>44';
        document.querySelector('.pricing-plan.recommended .price-period').textContent = '/user & month';
    }
    function setYearly() {
        document.getElementById('pricing-toggle-monthly').classList.remove('selected');
        document.getElementById('pricing-toggle-yearly').classList.add('selected');
        document.querySelector('.pricing-plan.left .original-price').innerHTML = '<span class="euro-symbol">€</span><span class="price-number">35</span>';
        document.querySelector('.pricing-plan.left .plan-price').innerHTML = '<span class="euro-symbol">€</span>26';
        document.querySelector('.pricing-plan.left .price-period').textContent = '/month';
        document.querySelector('.pricing-plan.recommended .original-price').innerHTML = '<span class="euro-symbol">€</span><span class="price-number">53</span>';
        document.querySelector('.pricing-plan.recommended .plan-price').innerHTML = '<span class="euro-symbol">€</span>39';
        document.querySelector('.pricing-plan.recommended .price-period').textContent = '/user & month';
    }
    document.getElementById('pricing-toggle-monthly').addEventListener('click', setMonthly);
    document.getElementById('pricing-toggle-yearly').addEventListener('click', setYearly);
    setMonthly();
    </script>
    """
