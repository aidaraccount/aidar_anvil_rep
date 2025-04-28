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
    # Set invoice footer for EU customers
    EU_COUNTRIES = {
        "AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "ES", "FI", "FR", "GR",
        "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PL", "PT", "RO", "SE", "SI", "SK"
    }
    country = customer.address.country if customer.address and hasattr(customer.address, 'country') else None
    if country in EU_COUNTRIES:
        stripe.Customer.modify(
            customer.id,
            invoice_settings={
                "footer": "Reverse charge: VAT to be accounted for by the recipient according to EU Directive 2006/112/EC."
            }
        )
    print(f"[Stripe] Created customer: id={customer.id}, email={customer.email}, name={customer.name}, address={customer.address}")
    return dict(customer)


@anvil.server.callable
def update_stripe_customer(customer_id: str, name: str = None, email: str = None, address: dict = None) -> dict:
    """
    Update an existing Stripe customer with new name, email, and/or address.
    """
    import stripe
    stripe.api_key = anvil.secrets.get_secret("stripe_secret_key")
    update_data = {}
    if name:
        update_data['name'] = name
    if email:
        update_data['email'] = email
    if address:
        update_data['address'] = address
    customer = stripe.Customer.modify(customer_id, **update_data)
    print(f"[Stripe] Updated customer: id={customer.id}, email={customer.email}, name={customer.name}, address={customer.address}")
    return dict(customer)


@anvil.server.callable
def update_stripe_customer_tax_id(customer_id: str, tax_id: str, tax_id_type: str) -> dict:
    """
    Add or update a tax ID for a Stripe customer. Handles duplicate tax ID errors gracefully.
    """
    import stripe
    stripe.api_key = anvil.secrets.get_secret("stripe_secret_key")
    # Check for existing tax IDs
    existing_tax_ids = stripe.Customer.list_tax_ids(customer_id)
    already_exists = any((tid['type'] == tax_id_type and tid['value'] == tax_id) for tid in existing_tax_ids['data'])
    if not already_exists:
        try:
            tax_id_obj = stripe.Customer.create_tax_id(customer_id, type=tax_id_type, value=tax_id)
        except stripe.error.InvalidRequestError as e:
            if 'already exists' not in str(e):
                raise
    else:
        tax_id_obj = [tid for tid in existing_tax_ids['data'] if tid['type'] == tax_id_type and tid['value'] == tax_id][0]
    print(f"[Stripe] Updated/added tax ID for customer {customer_id}: {tax_id_type} {tax_id}")
    return dict(tax_id_obj)


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
    1. Create a new subscription for a customer, applying a fixed tax rate for German customers.
    2. Print and return the subscription object (as dict).
    """
    import stripe
    stripe.api_key = anvil.secrets.get_secret("stripe_secret_key")
    # Fetch customer to get country
    customer = stripe.Customer.retrieve(customer_id)
    country = customer.address.country if customer.address and hasattr(customer.address, 'country') else None
    # Only apply the fixed tax rate for German customers
    items = [{"price": price_id, "quantity": user_count}]
    subscription_args = {
        "customer": customer_id,
        "items": items,
        "discounts": [{"coupon": "I1ivrR97"}]
    }
    if country == "DE":
        subscription_args["default_tax_rates"] = ["txr_1RHo7sQTBcqmUQgtajAz0voj"]
    subscription = stripe.Subscription.create(**subscription_args)
    print(f"[Stripe] Created subscription: id={subscription.id}, customer={subscription.customer}, status={subscription.status}, tax_rates={subscription.default_tax_rates}")
    return dict(subscription)


@anvil.server.callable
def add_stripe_customer_tax_id(customer_id: str, tax_id: str, tax_id_type: str = 'eu_vat') -> dict:
    """
    Add a tax ID (e.g., VAT) to a Stripe customer.
    :param customer_id: The Stripe customer ID
    :param tax_id: The customer's tax ID (e.g., VAT number)
    :param tax_id_type: The type of tax ID (default 'eu_vat')
    :return: The created tax ID object as a dict
    """
    import stripe
    stripe.api_key = anvil.secrets.get_secret("stripe_secret_key")
    tax_id_obj = stripe.Customer.create_tax_id(
        customer_id,
        type=tax_id_type,
        value=tax_id
    )
    print(f"[Stripe] Added tax ID: {tax_id_obj.id} for customer {customer_id}, type={tax_id_type}, value={tax_id}")
    return dict(tax_id_obj)



#   # # charge customer
#   # c = customer.charge(amount=999, currency="EUR")
#   # print(c)

#   # create subscription
#   subscription = stripe_customer.new_subscription("price_1RH2eaKpYockGiqNOasQNTNj")
#   print(subscription)
#   print(subscription[0])
  