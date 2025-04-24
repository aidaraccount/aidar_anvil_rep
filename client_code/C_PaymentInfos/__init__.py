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
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    global user
    user = anvil.users.get_user()
    
    self.html = """
    <!-- 1. Stripe.js script -->
    <script src=\"https://js.stripe.com/v3/\"></script>
    <div id=\"payment-form-container\">
        <!-- 2. Title -->
        <h2>Enter your payment details</h2>
        <!-- 3. Stripe Elements Card Element will be inserted here -->
        <form id=\"payment-form\">
            <div id=\"card-element\"><!-- Stripe injects the card input here --></div>
            <div id=\"card-errors\" role=\"alert\"></div>
            <button id=\"submit-payment\" type=\"submit\">Save Payment Method</button>
        </form>
    </div>
    <script>
    // 4. Initialize Stripe
    var stripe = Stripe('pk_test_51RDoXJQTBcqmUQgt9CqdDXQjtHKkEkEBuXSs7EqVjwkzqcWP66EgCu8jjYArvbioeYpzvS5wSvbrUsKUtjXi0gGq00M9CzHJTa');
    var elements = stripe.elements();
    var card = elements.create('card', {
        style: {
            base: {
                fontSize: '16px',
                color: '#32325d',
                '::placeholder': { color: '#aab7c4' }
            },
            invalid: { color: '#fa755a' }
        }
    });
    card.mount('#card-element');

    // 5. Handle form submission
    var form = document.getElementById('payment-form');
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        stripe.createPaymentMethod({
            type: 'card',
            card: card,
        }).then(function(result) {
            var errorDiv = document.getElementById('card-errors');
            if (result.error) {
                errorDiv.textContent = result.error.message;
            } else {
                errorDiv.textContent = '';
                // TODO: Send result.paymentMethod.id to server via anvil.call() or anvil.server.call()
                alert('Payment method saved with id: ' + result.paymentMethod.id);
            }
        });
    });
    </script>
    """