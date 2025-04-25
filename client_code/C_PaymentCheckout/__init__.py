from ._anvil_designer import C_PaymentCheckoutTemplate
from anvil import *
import anvil.server
import anvil.js

class C_PaymentCheckout(C_PaymentCheckoutTemplate):
    def __init__(self, plan_type: str = None, user_count: int = 1, billing_period: str = 'monthly', **properties):
        """
        1. Initializes the payment checkout popup for the selected plan and user count.
        2. Requests a Stripe Checkout Session from the server and renders the payment form.
        """
        self.init_components(**properties)
        self.plan_type: str = plan_type
        self.user_count: int = user_count
        self.billing_period: str = billing_period
        self.price_id: str = self.get_price_id(plan_type, billing_period)

        # 2. Create Stripe Checkout session via server
        session: dict = anvil.server.call('create_checkout_session', self.price_id, self.user_count)
        self.session_id: str = session['session_id']
        self.client_secret: str = session['client_secret']

        # 3. Render Stripe Payment Element in HTML slot
        self.html = f'''
        <!-- 1. Payment Form Container -->
        <div id="payment-form-container">
            <form id="payment-form">
                <label>Email <input type="email" id="email" required></label>
                <div id="payment-element"></div>
                <button id="submit">Pay</button>
                <div id="payment-message" class="hidden"></div>
            </form>
        </div>
        <!-- 2. Stripe.js -->
        <script src="https://js.stripe.com/v3/"></script>
        <script>
        // 2.1. Wait for DOMContentLoaded
        document.addEventListener("DOMContentLoaded", function() {{
            // 2.2. Initialize Stripe
            var stripe = Stripe("pk_test_51RDoXJQTBcqmUQgt9CqdDXQjtHKkEkEBuXSs7EqVjwkzqcWP66EgCu8jjYArvbioeYpzvS5wSvbrUsKUtjXi0gGq00M9CzHJTa");
            var elements = stripe.elements();
            var paymentElement = elements.create("payment");
            paymentElement.mount("#payment-element");

            var form = document.getElementById("payment-form");
            form.addEventListener("submit", async function(e) {{
                e.preventDefault();
                const {{error}} = await stripe.confirmPayment({{
                    elements,
                    confirmParams: {{
                        return_url: "https://your-app.anvil.app/_/theme/return.html?session_id={self.session_id}",
                    }},
                }});
                if (error) {{
                    document.getElementById("payment-message").textContent = error.message;
                    document.getElementById("payment-message").classList.remove("hidden");
                }}
            }});
        }});
        </script>
        '''

    def get_price_id(self, plan_type: str, billing_period: str = 'monthly') -> str:
        """
        Maps plan_type and billing period to Stripe price_id.
        Requires self.plan_type and self.billing_period to be set.
        """
        # 1. Define your Stripe price IDs here
        price_ids = {
            ("Explore", "monthly"): "price_1RE3tSQTBcqmUQgtoNyD0LgB",
            ("Explore", "yearly"): "price_1REVjKQTBcqmUQgt4Z47P00s",
            ("Professional", "monthly"): "price_1REVwmQTBcqmUQgtiBBLNZaD",
            ("Professional", "yearly"): "price_1REVzZQTBcqmUQgtpyBz8Gky",
        }
        # 2. Determine billing period (default to monthly)
        billing_period = billing_period if billing_period else 'monthly'
        return price_ids.get((plan_type, billing_period), "")
