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
def create_stripe_customer(email: str, name: str = None, address: dict = None) -> dict:
    """
    1. Create a new Stripe customer using the provided email, name, and address.
    2. Print and return the customer object (as dict).
    """
    import stripe
    stripe.api_key = anvil.secrets.get_secret("stripe_secret_key")
    customer_data = {"email": email}
    if name:
        customer_data["name"] = name
    if address:
        customer_data["address"] = address
    customer = stripe.Customer.create(**customer_data)
    print(f"[Stripe] Created customer: id={customer.id}, email={customer.email}, name={customer.name}, address={customer.address}")
    return dict(customer)

@anvil.server.callable
def get_stripe_customer(email: str) -> dict:
    """
    Look for an existing Stripe customer with the provided email. If found, return the customer object as dict. If not found, return empty dict.
    """
    import stripe
    stripe.api_key = anvil.secrets.get_secret("stripe_secret_key")
    customers = stripe.Customer.list(email=email, limit=1)
    if customers.data:
        customer = customers.data[0]
        print(f"[Stripe] Found existing customer: id={customer.id}, email={customer.email}")
        return dict(customer)
    print(f"[Stripe] No customer found for email={email}")
    return {}

@anvil.server.callable
def get_stripe_payment_methods(customer_id: str) -> list:
    """
    1. Get all PaymentMethods associated with a customer.
    2. Print and return the list of PaymentMethods (as list of dicts).
    """
    import stripe
    stripe.api_key = anvil.secrets.get_secret("stripe_secret_key")
    payment_methods = stripe.PaymentMethod.list(customer=customer_id)
    print(f"[Stripe] Found {len(payment_methods.data)} payment methods for customer_id={customer_id}")
    return [dict(payment_method) for payment_method in payment_methods.data]

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

@anvil.server.callable
def create_stripe_subscription(customer_id: str, price_id: str, user_count: int = 1) -> dict:
    """
    1. Create a new subscription for a customer.
    2. Print and return the subscription object (as dict).
    """
    import stripe
    stripe.api_key = anvil.secrets.get_secret("stripe_secret_key")
    subscription = stripe.Subscription.create(
        customer=customer_id,
        items=[{"price": price_id, "quantity": user_count}],
        discounts=[{"coupon": "I1ivrR97"}]
    )
    print(f"[Stripe] Created subscription: id={subscription.id}, customer={subscription.customer}, status={subscription.status}")
    return dict(subscription)



#   # # charge customer
#   # c = customer.charge(amount=999, currency="EUR")
#   # print(c)

#   # create subscription
#   subscription = stripe_customer.new_subscription("price_1RH2eaKpYockGiqNOasQNTNj")
#   print(subscription)
#   print(subscription[0])
  