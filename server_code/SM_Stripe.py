import anvil.secrets
import anvil.stripe
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import json


# -----------------------------------------
# 1. SERVER MODULE FOR STRIPE
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


@anvil.server.callable
def create_stripe_customer(email: str) -> dict:
    """
    1. Create a new Stripe customer using the provided email.
    2. Print and return the customer object (as dict).
    """
    import stripe
    stripe.api_key = anvil.secrets.get_secret("stripe_secret_key")
    customer = stripe.Customer.create(email=email)
    print(f"[Stripe] Created customer: id={customer.id}, email={customer.email}, created={customer.created}, status={customer.deleted if hasattr(customer, 'deleted') else 'active'}")
    return dict(customer)

@anvil.server.callable
def get_or_create_stripe_customer(email: str) -> dict:
    """
    1. Look for an existing Stripe customer with the provided email.
    2. If found, return the customer object.
    3. If not found, create a new customer and return it.
    """
    import stripe
    stripe.api_key = anvil.secrets.get_secret("stripe_secret_key")
    # Search for customer by email
    customers = stripe.Customer.list(email=email, limit=1)
    if customers.data:
        customer = customers.data[0]
        print(f"[Stripe] Found existing customer: id={customer.id}, email={customer.email}")
        return dict(customer)
    # Not found, create new
    customer = stripe.Customer.create(email=email)
    print(f"[Stripe] Created new customer: id={customer.id}, email={customer.email}")
    return dict(customer)

@anvil.server.callable
def attach_payment_method_to_customer(customer_id: str, payment_method_id: str) -> dict:
    """
    1. Attach a PaymentMethod to a Stripe customer.
    2. Set as default payment method for invoices.
    3. Print and return the updated customer object (as dict).
    """
    import stripe
    stripe.api_key = anvil.secrets.get_secret("stripe_secret_key")
    # Attach payment method
    payment_method = stripe.PaymentMethod.attach(payment_method_id, customer=customer_id)
    print(f"[Stripe] Attached PaymentMethod: id={payment_method.id}, type={payment_method.type}, customer={payment_method.customer}, status={payment_method['card']['brand'] if payment_method.type == 'card' else ''}")
    # Set as default
    customer = stripe.Customer.modify(
        customer_id,
        invoice_settings={"default_payment_method": payment_method_id}
    )
    print(f"[Stripe] Updated customer default payment method: customer_id={customer.id}, default_payment_method={customer.invoice_settings.default_payment_method}")
    return dict(customer)
  


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
  