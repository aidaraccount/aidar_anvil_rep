import anvil.secrets
import anvil.stripe
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import json
from datetime import datetime


# -----------------------------------------
# 1. SERVER MODULE FOR STRIPE
# -----------------------------------------


@anvil.server.callable
def create_setup_intent():
  import stripe
  import anvil.secrets
  from datetime import datetime

  print(f"[STRIPE_DEBUG_SERVER] {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - create_setup_intent started")
  
  # Get API key
  print(f"[STRIPE_DEBUG_SERVER] {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Getting Stripe API key")
  stripe.api_key = anvil.secrets.get_secret("stripe_secret_key")
  
  # Create intent
  print(f"[STRIPE_DEBUG_SERVER] {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Creating Stripe SetupIntent")
  try:
    intent = stripe.SetupIntent.create(
      usage="off_session"
    )
    print(f"[STRIPE_DEBUG_SERVER] {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - SetupIntent created successfully: {intent.id}")
  except Exception as e:
    print(f"[STRIPE_DEBUG_SERVER] {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Error creating SetupIntent: {str(e)}")
    raise

  print(f"[STRIPE_DEBUG_SERVER] {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Returning client_secret: {intent.client_secret[:10]}...")
  return intent.client_secret


@anvil.server.callable
def create_stripe_customer(email: str, name: str = None, address: dict = None) -> dict:
  """
  1. Create a new Stripe stripe_customer using the provided email, name, and address.
  2. Print and return the stripe_customer object (as dict).
  """
  import stripe
  stripe.api_key = anvil.secrets.get_secret("stripe_secret_key")

  user = anvil.users.get_user()

  # Add customer to Stripe
  customer_data = {"email": email}
  if name:
    customer_data["name"] = name
  if address:
    customer_data["address"] = address
  stripe_customer = stripe.Customer.create(**customer_data)

  # Set invoice footer for EU customers
  EU_COUNTRIES = {
    "AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "ES", "FI", "FR", "GR",
    "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PL", "PT", "RO", "SE", "SI", "SK"
  }
  country = stripe_customer.address.country if stripe_customer.address and hasattr(stripe_customer.address, 'country') else None
  if country in EU_COUNTRIES:
    stripe.Customer.modify(
      stripe_customer.id,
      invoice_settings={
        "footer": "Reverse charge: VAT to be accounted for by the recipient according to EU Directive 2006/112/EC."
      }
    )

  # if Stripe Customer successfully created
  if stripe_customer.id:
    # create customer in backend db
    customer_id = anvil.server.call('create_customer', user['user_id'], name, user['email'])

    # fill Anvil Users
    user['customer_id'] = customer_id
    user['customer_name'] = name
    user['admin'] = True
    
  print(f"[Stripe] Created customer: id={customer_id}, email={user['email']}, name={name}, address={stripe_customer.address}")
  return dict(stripe_customer)


@anvil.server.callable
def update_stripe_customer(customer_id: str, name: str = None, address: dict = None) -> dict:
  """
  Update an existing Stripe customer with new name, and/or address.
  """
  import stripe
  stripe.api_key = anvil.secrets.get_secret("stripe_secret_key")

  user = anvil.users.get_user()

  # update Stripe customer
  update_data = {}
  if name:
    update_data['name'] = name
  if address:
    update_data['address'] = address
  stripe_customer = stripe.Customer.modify(customer_id, **update_data)

  # update customer in backend db
  anvil.server.call('update_customer', user['customer_id'], name)

  # update Anvil
  users_with_same_customer_id = app_tables.users.search(customer_id=user['customer_id'])
  for u in users_with_same_customer_id:
    u['customer_name'] = name

  print(f"[Stripe] Updated customer: id={user['customer_id']}, name={name}, address={address}")
  return dict(stripe_customer)


@anvil.server.callable
def update_stripe_customer_tax_id(customer_id: str, tax_id: str, tax_id_type: str) -> dict:
  """
  Add or update a tax ID for a Stripe customer. Handles duplicate tax ID errors gracefully.
  """

  print(f"[Stripe] Updating Stripe Customer tax ID {tax_id} of type {tax_id_type} for customer {customer_id}")

  import stripe
  stripe.api_key = anvil.secrets.get_secret("stripe_secret_key")

  # Check for existing tax IDs
  existing_tax_ids = stripe.Customer.list_tax_ids(customer_id)

  # First, delete existing tax IDs of the same type (to update instead of just adding)
  for tid in existing_tax_ids['data']:
    if tid['type'] == tax_id_type:
      print(f"[Stripe] Deleting existing tax ID {tid['id']} of type {tax_id_type} for customer {customer_id}")
      stripe.Customer.delete_tax_id(customer_id, tid['id'])

  # Now create the new tax ID
  stripe_tax_id_obj = None
  try:
    stripe_tax_id_obj = stripe.Customer.create_tax_id(customer_id, type=tax_id_type, value=tax_id)
    print(f"[Stripe] Created new tax ID for customer {customer_id}: {tax_id_type} {tax_id}")
  except stripe.error.InvalidRequestError as e:
    if 'already exists' not in str(e):
      raise
    # If we somehow still have a duplicate (race condition), get the existing one
    refreshed_tax_ids = stripe.Customer.list_tax_ids(customer_id)
    matches = [tid for tid in refreshed_tax_ids['data'] if tid['type'] == tax_id_type and tid['value'] == tax_id]
    if matches:
      stripe_tax_id_obj = matches[0]
      print(f"[Stripe] Using existing tax ID for customer {customer_id}: {tax_id_type} {tax_id}")
  if not stripe_tax_id_obj:
    raise Exception("Could not create or retrieve the Stripe tax ID object.")
  return dict(stripe_tax_id_obj)


@anvil.server.callable
def get_stripe_customer(email: str) -> dict:
  """
  Look for an existing Stripe customer with the provided email. If found, return the customer object as dict. If not found, return empty dict.
  """
  import stripe
  from datetime import datetime

  print(f"[STRIPE_DEBUG_SERVER] {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - get_stripe_customer started with email={email}")
  
  # Get API key
  print(f"[STRIPE_DEBUG_SERVER] {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Getting Stripe API key")
  stripe.api_key = anvil.secrets.get_secret("stripe_secret_key")

  try:
    # Search for customer
    print(f"[STRIPE_DEBUG_SERVER] {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Searching for customer with email={email}")
    start_time = datetime.now()
    stripe_customers = stripe.Customer.list(email=email, limit=1)
    duration = (datetime.now() - start_time).total_seconds()
    print(f"[STRIPE_DEBUG_SERVER] {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Stripe API call took {duration:.2f} seconds")
    
    # Process results
    if stripe_customers.data:
      stripe_customer = stripe_customers.data[0]
      print(f"[STRIPE_DEBUG_SERVER] {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Found existing customer: id={stripe_customer.id}, email={stripe_customer.email}")
      print(f"[STRIPE_DEBUG_SERVER] {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Customer data size: {len(str(stripe_customer))} characters")
      return dict(stripe_customer)
    else:
      print(f"[STRIPE_DEBUG_SERVER] {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - No customer found for email={email}")
      return {}
  except Exception as e:
    print(f"[STRIPE_DEBUG_SERVER] {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} - Error in get_stripe_customer: {str(e)}")
    raise


@anvil.server.callable
def get_stripe_customer_with_tax_info(email: str) -> dict:
  """
  Look up a Stripe customer by email and return their address country and tax ID info (if available).
  Returns a dict with keys: id, email, address, tax_country, tax_id, tax_id_type
  """
  import stripe
  stripe.api_key = anvil.secrets.get_secret("stripe_secret_key")

  stripe_customers = stripe.Customer.list(email=email, limit=1)
  if stripe_customers.data:
    stripe_customer = stripe_customers.data[0]
    result = dict(stripe_customer)
    # Get country from address
    address = getattr(stripe_customer, 'address', None)
    tax_country = address.country if address and hasattr(address, 'country') else None
    # Get tax id info
    tax_id = None
    tax_id_type = None
    try:
      tax_ids = stripe.Customer.list_tax_ids(stripe_customer.id)
      if tax_ids.data:
        stripe_tax_id_obj = tax_ids.data[0]
        tax_id = stripe_tax_id_obj['value']
        tax_id_type = stripe_tax_id_obj['type']
    except Exception as e:
      print(f"[Stripe] Could not fetch tax IDs: {e}")
    result['tax_country'] = tax_country
    result['tax_id'] = tax_id
    result['tax_id_type'] = tax_id_type
    return result
  return {}


@anvil.server.callable
def get_stripe_payment_methods(customer_id: str) -> list:
  """
  1. Get all PaymentMethods associated with a customer.
  2. Print and return the list of PaymentMethods (as list of dicts).
  """
  import stripe
  stripe.api_key = anvil.secrets.get_secret("stripe_secret_key")

  stripe_payment_methods = stripe.PaymentMethod.list(customer=customer_id)
  print(f"[Stripe] Found {len(stripe_payment_methods.data)} payment methods for customer_id={customer_id}")
  return [dict(stripe_payment_method) for stripe_payment_method in stripe_payment_methods.data]


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
  stripe_payment_method = stripe.PaymentMethod.attach(payment_method_id, customer=customer_id)
  print(f"[Stripe] Attached PaymentMethod: id={stripe_payment_method.id}, type={stripe_payment_method.type}, customer={stripe_payment_method.customer}, status={stripe_payment_method['card']['brand'] if stripe_payment_method.type == 'card' else ''}")
  # Set as default
  stripe_customer = stripe.Customer.modify(
    customer_id,
    invoice_settings={"default_payment_method": payment_method_id}
  )
  print(f"[Stripe] Updated customer default payment method: customer_id={stripe_customer.id}, default_payment_method={stripe_customer.invoice_settings.default_payment_method}")
  return dict(stripe_customer)


@anvil.server.callable
def create_stripe_subscription(customer_id: str, price_id: str, plan_type: str, frequency: str, user_count: int = 1) -> dict:
  """
  1. Create a new subscription for a customer, applying a fixed tax rate for German customers.
  2. Print and return the subscription object (as dict).
  
  Args:
    customer_id (str): Stripe customer ID
    price_id (str): Stripe price ID
    plan_type (str): Plan type ('Explore' or 'Professional')
    frequency (str): Billing frequency ('monthly' or 'yearly')
    user_count (int, optional): Number of users/licenses. Defaults to 1.
      
  Returns:
    dict: The created Stripe subscription object
  """
  import stripe
  stripe.api_key = anvil.secrets.get_secret("stripe_secret_key")

  user = anvil.users.get_user()

  # Fetch customer to get country
  stripe_customer = stripe.Customer.retrieve(customer_id)
  country = stripe_customer.address.country if stripe_customer.address and hasattr(stripe_customer.address, 'country') else None

  # Only apply the fixed tax rate for German customers
  items = [{"price": price_id, "quantity": user_count}]
  subscription_args = {
    "customer": customer_id,
    "items": items,
    "discounts": [{"coupon": "I1ivrR97"}]
  }
  if country == "DE":
    subscription_args["default_tax_rates"] = ["txr_1RHo7sQTBcqmUQgtajAz0voj"]

  # Create subscription
  stripe_subscription = stripe.Subscription.create(**subscription_args)

  # Updates
  if stripe_subscription.id:
    # Anvil Users Update: parameters of all users with the same customer_id
    users_with_same_customer_id = app_tables.users.search(customer_id=user['customer_id'])
    for u in users_with_same_customer_id:
      u['plan'] = plan_type
      u['expiration_date'] = None

    # Update the subscription in db
    anvil.server.call('update_subscription_db', user['customer_id'], plan_type, user_count, frequency, None)

    print(f"[Stripe] Created subscription: id={stripe_subscription.id}, customer={stripe_subscription.customer}, status={stripe_subscription.status}, tax_rates={stripe_subscription.default_tax_rates}")
  return dict(stripe_subscription)


@anvil.server.callable
def update_subscription(target_plan: str, user_count: int, billing_period: str) -> dict:
  """
  1. Update an existing subscription with new plan, user count, or billing period
  2. Returns a dict with success status and relevant information
  
  Args:
    target_plan (str): The plan to switch to ('Explore' or 'Professional')
    user_count (int): Number of users/licenses for Professional plan
    billing_period (str): 'monthly' or 'yearly'
  
  Returns:
    dict: Result with keys:
      - success (bool): Whether the update was successful
      - message (str): Descriptive message about the result
  """
  import stripe
  stripe.api_key = anvil.secrets.get_secret("stripe_secret_key")

  # Get the current user
  user = anvil.users.get_user()
  if not user:
    return {"success": False, "message": "User not authenticated"}

  try:
    # Get user's email
    email = user.get('email')
    if not email:
      return {"success": False, "message": "User email not available"}

    # Find customer in Stripe
    customer = get_stripe_customer(email)
    if not customer or not customer.get('id'):
      return {"success": False, "message": "No Stripe customer found for this user"}

    # Find active subscriptions for this customer
    subscriptions = stripe.Subscription.list(
      customer=customer['id'],
      status='active',
      limit=1
    )

    if not subscriptions or not subscriptions.data:
      return {"success": False, "message": "No active subscription found"}

    # Determine price ID based on plan and billing period
    price_id = None
    if target_plan == "Explore":
      price_id = anvil.secrets.get_secret(f"stripe_explore_{billing_period}_price")
    elif target_plan == "Professional":
      price_id = anvil.secrets.get_secret(f"stripe_professional_{billing_period}_price")
    else:
      return {"success": False, "message": f"Unknown plan: {target_plan}"}

    # Get current subscription to modify
    subscription_id = subscriptions.data[0].id

    # Create new subscription item with updated price
    subscription = stripe.Subscription.modify(
      subscription_id,
      cancel_at_period_end=False,
      proration_behavior='create_prorations',
      items=[{
        'id': subscriptions.data[0]['items']['data'][0].id,
        'price': price_id,
        'quantity': user_count if target_plan == "Professional" else 1
      }]
    )

    print(f"Subscription {subscription.id} updated to {target_plan} plan with {user_count} users")
    return {
      "success": True,
      "message": f"Subscription updated to {target_plan} plan",
      "subscription_id": subscription.id
    }

  except Exception as e:
    print(f"Error updating subscription: {e}")
    return {"success": False, "message": f"Error: {str(e)}"}


@anvil.server.callable
def cancel_subscription() -> dict:
  """
  1. Cancel the current subscription for the authenticated user
  2. Returns a dict with success status and relevant information
  
  Returns:
    dict: Result with keys:
      - success (bool): Whether the cancellation was successful
      - message (str): Descriptive message about the result
  """
  import stripe
  stripe.api_key = anvil.secrets.get_secret("stripe_secret_key")

  # Get the current user
  user = anvil.users.get_user()

  try:
    # Get company email
    company = json.loads(anvil.server.call('get_settings_subscription2', user['user_id']))
    email = company[0]['mail']
    if not email:
      return {"success": False, "message": "Company email not available"}

    # Find customer in Stripe
    customer = get_stripe_customer(email)
    if not customer or not customer.get('id'):
      return {"success": False, "message": "No Stripe customer found for this company"}

    # Find active subscriptions for this customer
    subscriptions = stripe.Subscription.list(
      customer=customer['id'],
      status='active',
      limit=1
    )

    if not subscriptions or not subscriptions.data:
      return {"success": False, "message": "No active subscription found"}
  
    # Cancel the subscription at period end (won't renew)
    subscription = stripe.Subscription.modify(
      subscriptions.data[0].id,
      cancel_at_period_end=True
    )

    expiration_date = subscription["items"]["data"][0]["current_period_end"]
    expiration_date = datetime.fromtimestamp(expiration_date).date()

    # Anvil Users Update: user['expiration_date'] of all users with the same customer_id
    users_with_same_customer_id = app_tables.users.search(customer_id=user['customer_id'])
    for u in users_with_same_customer_id:
      u['expiration_date'] = expiration_date

    # DB Update: company['expiration_date']
    result = anvil.server.call('cancel_subscription', user['customer_id'], expiration_date)

    # return success
    if result == 'Subscription cancelled successfully':
      print(f"Subscription {subscription.id} will be cancelled on {expiration_date}")
      return {
        "success": True,
        "message": "Subscription will be cancelled at the end of the current billing period",
        "subscription_id": subscription.id,
        "expiration_date": expiration_date
      }
    else:
      print(f"Error cancelling subscription: {result}")
      return {"success": False, "message": "Error cancelling subscription"}
  except Exception as e:
    print(f"Error cancelling subscription: {e}")
    return {"success": False, "message": f"Error: {str(e)}"}


@anvil.server.callable
@anvil.server.expose_client_side
def ensure_stripe_js_loaded():
  """
  1. Ensures Stripe.js is loaded only once in the client
  2. Provides detailed logging of the loading process
  3. Returns the Stripe public key
  
  This function is client-only and manages the single loading of Stripe.js
  across the application to prevent duplicate loading issues.
  
  Returns:
    str: The Stripe public key to use for initialization
  """
  import anvil.js
  
  # Stripe public key
  pk_key = 'pk_test_51RDoXJQTBcqmUQgt9CqdDXQjtHKkEkEBuXSs7EqVjwkzqcWP66EgCu8jjYArvbioeYpzvS5wSvbrUsKUtjXi0gGq00M9CzHJTa'
  
  # Check if Stripe.js is already loaded or loading
  stripe_status = anvil.js.call('eval', """
    (function() {
      if (window._stripeLoadStatus === 'loaded') {
        console.log("[STRIPE_LOADER] " + new Date().toISOString() + " - Stripe already loaded");
        return 'loaded';
      } else if (window._stripeLoadStatus === 'loading') {
        console.log("[STRIPE_LOADER] " + new Date().toISOString() + " - Stripe is currently loading");
        return 'loading';
      }
      return 'not_loaded';
    })();
  """)
  
  # If already loaded or loading, return
  if stripe_status in ['loaded', 'loading']:
    return pk_key
    
  # Set status to loading
  anvil.js.call('eval', "window._stripeLoadStatus = 'loading';")
  
  # Load Stripe.js
  anvil.js.call('eval', f"""
    (function() {{
      console.log("[STRIPE_LOADER] " + new Date().toISOString() + " - Starting to load Stripe.js");
      
      // Record start time
      window._stripeLoadStart = new Date();
      
      // Create the script element
      var script = document.createElement('script');
      script.src = 'https://js.stripe.com/v3/';
      script.async = true;
      
      // Set up onload handler
      script.onload = function() {{
        var loadTime = new Date() - window._stripeLoadStart;
        console.log("[STRIPE_LOADER] " + new Date().toISOString() + " - Stripe.js loaded in " + loadTime + "ms");
        window._stripeLoadStatus = 'loaded';
        window._stripeLoadTime = loadTime;
        
        // Track when Stripe is actually ready to use
        var checkStartTime = new Date();
        var stripeReadyInterval = setInterval(function() {{
          try {{
            if (typeof Stripe === 'function') {{
              var test = Stripe('{pk_key}');
              if (test) {{
                var readyTime = new Date() - checkStartTime;
                console.log("[STRIPE_LOADER] " + new Date().toISOString() + " - Stripe function initialized after " + readyTime + "ms");
                window._stripeReadyTime = readyTime;
                clearInterval(stripeReadyInterval);
                
                // Monitor when card elements are fully ready
                try {{
                  var elementsCheckStart = new Date();
                  var elements = test.elements();
                  var card = elements.create('card', {{}});
                  if (card) {{
                    var elementsTime = new Date() - elementsCheckStart;
                    console.log("[STRIPE_LOADER] " + new Date().toISOString() + " - Stripe Elements initialization took " + elementsTime + "ms");
                    window._stripeElementsTime = elementsTime;
                  }}
                }} catch (elemErr) {{
                  console.log("[STRIPE_LOADER] " + new Date().toISOString() + " - Could not initialize Elements: " + elemErr.message);
                }}
              }}
            }}
          }} catch (e) {{
            // Ignore errors during testing
          }}
        }}, 100);
        
        // Timeout after 15 seconds
        setTimeout(function() {{
          clearInterval(stripeReadyInterval);
          console.log("[STRIPE_LOADER] " + new Date().toISOString() + " - Timed out waiting for Stripe initialization");
        }}, 15000);
      }};
      
      // Set up error handler
      script.onerror = function() {{
        console.error("[STRIPE_LOADER] " + new Date().toISOString() + " - Failed to load Stripe.js");
        window._stripeLoadStatus = 'error';
      }};
      
      // Append to document head
      document.head.appendChild(script);
    }})();
  """)
  
  return pk_key
