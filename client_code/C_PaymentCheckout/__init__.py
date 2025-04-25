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

        # 3. Render Stripe Payment Element in HTML slot (full quickstart form)
        self.html = f'''
        <!-- 1. Payment Form Container -->
        <form id="payment-form">
            <!-- Email -->
            <label>
                Email
                <input type="email" id="email" placeholder="you@example.com" required />
            </label>
            <div type="text" id="email-errors"></div>
            <!-- Billing Address -->
            <h4>Billing Address</h4>
            <div id="billing-address-element"></div>
            <!-- Payment Element -->
            <h4>Payment</h4>
            <div id="payment-element"></div>
            <button id="submit">
                <div class="spinner hidden" id="spinner"></div>
                <span id="button-text">Pay now</span>
            </button>
            <div id="payment-message" class="hidden"></div>
        </form>
        <script src="https://js.stripe.com/v3/"></script>
        <script>
        const stripe = Stripe("pk_test_51RDoXJQTBcqmUQgt9CqdDXQjtHKkEkEBuXSs7EqVjwkzqcWP66EgCu8jjYArvbioeYpzvS5wSvbrUsKUtjXi0gGq00M9CzHJTa");
        let checkout;
        initialize();
        // Fetches a Checkout Session and captures the client secret
        async function initialize() {{
            const clientSecret = "{self.client_secret}";
            const appearance = {{ theme: 'stripe' }};
            checkout = await stripe.initCheckout({{
                fetchClientSecret: () => Promise.resolve(clientSecret),
                elementsOptions: {{ appearance }},
            }});
            document.querySelector("#button-text").textContent = `Pay ${{checkout.session().total.total.amount}} now`;
            const emailInput = document.getElementById("email");
            const emailErrors = document.getElementById("email-errors");
            emailInput.addEventListener("input", () => {{ emailErrors.textContent = ""; }});
            emailInput.addEventListener("blur", async () => {{
                const newEmail = emailInput.value;
                if (!newEmail) return;
                const updateResult = await checkout.updateEmail(newEmail);
                if (updateResult.type === "error") {{
                    emailErrors.textContent = updateResult.error.message;
                }}
            }});
            const paymentElement = checkout.createPaymentElement();
            paymentElement.mount("#payment-element");
            const billingAddressElement = checkout.createBillingAddressElement();
            billingAddressElement.mount("#billing-address-element");
        }}
        document.querySelector("#payment-form").addEventListener("submit", handleSubmit);
        async function handleSubmit(e) {{
            e.preventDefault();
            setLoading(true);
            const email = document.getElementById("email").value;
            const updateResult = await checkout.updateEmail(email);
            if (updateResult.type === "error") {{
                showMessage(updateResult.error.message);
                setLoading(false);
                return;
            }}
            const {{ error }} = await checkout.confirm();
            if (error) {{ showMessage(error.message); }}
            setLoading(false);
        }}
        function showMessage(messageText) {{
            const messageContainer = document.querySelector("#payment-message");
            messageContainer.classList.remove("hidden");
            messageContainer.textContent = messageText;
            setTimeout(function () {{
                messageContainer.classList.add("hidden");
                messageContainer.textContent = "";
            }}, 4000);
        }}
        function setLoading(isLoading) {{
            if (isLoading) {{
                document.querySelector("#submit").disabled = true;
                document.querySelector("#spinner").classList.remove("hidden");
                document.querySelector("#button-text").classList.add("hidden");
            }} else {{
                document.querySelector("#submit").disabled = false;
                document.querySelector("#spinner").classList.add("hidden");
                document.querySelector("#button-text").classList.remove("hidden");
            }}
        }}
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
