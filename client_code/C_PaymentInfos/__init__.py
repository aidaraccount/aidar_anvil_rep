from ._anvil_designer import C_PaymentInfosTemplate
from anvil import *
import anvil.server
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class C_PaymentInfos(C_PaymentInfosTemplate):
  def __init__(self, **properties):
    # 1. Set Form properties and Data Bindings.
    self.init_components(**properties)

    # 2. Get current user and pre-fill email
    import anvil.users
    self.user = anvil.users.get_user()
    self.customer_email = self.user["email"] if self.user and "email" in self.user else ""
    print(f"User email: {self.customer_email}")

    # 3. Get the Stripe SetupIntent client_secret from the server
    client_secret = anvil.server.call('create_setup_intent')
    print(f"SetupIntent client_secret: {client_secret}")
    self.html = f"""
    <script>
    window.stripe_setup_intent_client_secret = '{client_secret}';
    </script>
    <script src=\"https://js.stripe.com/v3/\"></script>
    <div id=\"payment-form-container\">
        <h2>Add payment details</h2>
        <div class=\"payment-info-text\">Add your credit card details below. This card will be saved to your account and can be removed at any time.</div>
        <form id=\"payment-form\">
            <!-- Customer email -->
            <div class=\"form-section\">
                <h3>Customer email</h3>
                <input id=\"customer-email\" type=\"email\" value=\"{self.customer_email}\">
            </div>
            <!-- Name on card -->
            <div class=\"form-section\">
                <h3>Name on card</h3>
                <input id=\"name-on-card\" name=\"name-on-card\" type=\"text\" autocomplete=\"cc-name\" required placeholder=\"Name on card\">
            </div>
            <!-- Card information section -->
            <div class=\"form-section\">
                <h3>Card information</h3>
                <div id=\"card-element\"></div>
            </div>
            <!-- Billing address section -->
            <div class=\"form-section\">
                <h3>Billing address</h3>
                <div class=\"field-row\">
                    <select id=\"country\" name=\"country\" placeholder=\"Country\">
                        <option value=\"DE\">Germany</option>
                        <option value=\"FR\">France</option>
                        <option value=\"IT\">Italy</option>
                        <option value=\"ES\">Spain</option>
                        <option value=\"GB\">United Kingdom</option>
                        <option value=\"US\">United States</option>
                        <option value=\"NL\">Netherlands</option>
                        <option value=\"PL\">Poland</option>
                        <option value=\"CH\">Switzerland</option>
                    </select>
                </div>
                <div class=\"field-row\">
                    <input id=\"address-line-1\" name=\"address-line-1\" type=\"text\" placeholder=\"Address line 1\">
                </div>
                <div class=\"field-row\">
                    <input id=\"address-line-2\" name=\"address-line-2\" type=\"text\" placeholder=\"Address line 2\">
                </div>
                <div class=\"two-column\">
                    <div class=\"field-row\">
                        <input id=\"city\" name=\"city\" type=\"text\" placeholder=\"City\">
                    </div>
                    <div class=\"field-row\">
                        <input id=\"postal-code\" name=\"postal-code\" type=\"text\" placeholder=\"Postal code\">
                    </div>
                </div>
            </div>
            <!-- Save button -->
            <button type=\"button\" id=\"save-payment-btn\">Save payment details</button>
            <div id=\"card-errors\" style=\"color:red;\"></div>
        </form>
    </div>
    <div id=\"payment-message\"></div>
    <script>
    // Initialize Stripe and Elements
    var stripe = Stripe('pk_test_51RDoXJQTBcqmUQgt9CqdDXQjtHKkEkEBuXSs7EqVjwkzqcWP66EgCu8jjYArvbioeYpzvS5wSvbrUsKUtjXi0gGq00M9CzHJTa');
    var elements = stripe.elements();
    var cardElement = elements.create('card');
    cardElement.mount('#card-element');
    // Save payment details handler
    document.getElementById('save-payment-btn').onclick = async function() {{
        var email = document.getElementById('customer-email').value;
        var name = document.getElementById('name-on-card').value;
        var country = document.getElementById('country').value;
        var address1 = document.getElementById('address-line-1').value;
        var address2 = document.getElementById('address-line-2').value;
        var city = document.getElementById('city').value;
        var postal = document.getElementById('postal-code').value;
        console.log('Collected email:', email);
        console.log('Collected name:', name);
        console.log('Collected country:', country);
        console.log('Collected address:', address1, address2, city, postal);
        var result = await stripe.createToken(cardElement, {{
            name: name,
            address_line1: address1,
            address_line2: address2,
            address_city: city,
            address_zip: postal,
            address_country: country,
            email: email
        }});
        if (result.error) {{
            document.getElementById('card-errors').innerText = result.error.message;
            return;
        }}
        console.log('Stripe token:', result.token.id);
        window.anvil.call('_anvilPaymentInfosTokenCallback', result.token.id, email);
    }};
    </script>
    """

  def _anvilPaymentInfosTokenCallback(self, token: str, email: str):
    """
    Called from JS when token and email are ready.
    Calls the server to create the Stripe customer and prints all info.
    Fires the custom event for the parent form.
    """
    print(f"Received token: {token}")
    print(f"Received email: {email}")
    import anvil.server
    stripe_customer = anvil.server.call('create_stripe_customer', token, email)
    print(f"Stripe customer object: {stripe_customer}")
    self.raise_event('x-payment_info_submitted', token=token, email=email)