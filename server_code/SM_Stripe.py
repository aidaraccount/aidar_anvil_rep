import anvil.secrets
import anvil.stripe
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import json
import stripe


# -----------------------------------------
# SERVER MODULE FOR STRIPE
# -----------------------------------------


@anvil.server.callable
def create_setup_intent():
  import stripe
  import anvil.secrets

  stripe.api_key = anvil.secrets.get_secret("stripe_secret_key")
  intent = stripe.SetupIntent.create(
      usage="off_session"
  )
  
  return intent.client_secret


# @anvil.server.callable
# def create_stripe_customer(token, email):
#   # create stripe customer
#   stripe_customer = anvil.stripe.new_customer(email, token)
#   print(stripe_customer)
#   print(stripe_customer['id'])
  
#   # # get stripe customer
#   # customer = anvil.stripe.get_customer(stripe_customer['id'])
#   # print(customer)
#   # print(customer['id'])

#   # # charge customer
#   # c = customer.charge(amount=999, currency="EUR")
#   # print(c)

#   # create subscription
#   subscription = stripe_customer.new_subscription("price_1RH2eaKpYockGiqNOasQNTNj")
#   print(subscription)
#   print(subscription[0])


@anvil.server.callable
def create_checkout_session(price_id: str, quantity: int) -> dict:
    """
    1. Creates a Stripe Checkout Session for the given price_id and quantity.
    2. Returns the session ID and client secret for use in the client-side payment flow.
    """
    stripe.api_key = anvil.secrets.get_secret("stripe_secret_key")
    session = stripe.checkout.Session.create(
        ui_mode='custom',
        line_items=[{
            'price': price_id,
            'quantity': quantity,
        }],
        mode='payment',
        return_url='https://aidar.anvil.app/_/theme/return.html?session_id={CHECKOUT_SESSION_ID}',
        automatic_tax={'enabled': True},
    )
    print(session)
    return {
        'client_secret': session.client_secret,
        'session_id': session.id
    }