import anvil.email
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

  stripe.api_key = anvil.secrets.get_secret(anvil.server.call("get_stripe_secret_key_name"))
  intent = stripe.SetupIntent.create(
    usage="off_session"
  )

  return intent.client_secret


# -----------------------------------------
# 2. CUSTOMER
# -----------------------------------------
@anvil.server.callable
def create_stripe_customer(email: str, name: str = None, address: dict = None) -> dict:
  """
  1. Create a new Stripe stripe_customer using the provided email, name, and address.
  2. Print and return the stripe_customer object (as dict).
  """
  import stripe
  stripe.api_key = anvil.secrets.get_secret(anvil.server.call("get_stripe_secret_key_name"))

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
  if country in EU_COUNTRIES and country != "DE":
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
  stripe.api_key = anvil.secrets.get_secret(anvil.server.call("get_stripe_secret_key_name"))

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
  stripe.api_key = anvil.secrets.get_secret(anvil.server.call("get_stripe_secret_key_name"))

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
  stripe.api_key = anvil.secrets.get_secret(anvil.server.call("get_stripe_secret_key_name"))

  stripe_customers = stripe.Customer.list(email=email, limit=1)
  if stripe_customers.data:
    stripe_customer = stripe_customers.data[0]
    print(f"[Stripe] Found existing customer: id={stripe_customer.id}, email={stripe_customer.email}")
    return dict(stripe_customer)
  else:
    print(f"[Stripe] No customer found for email={email}")
    return {}


@anvil.server.callable
def get_stripe_customer_with_tax_info(email: str) -> dict:
  """
  Look up a Stripe customer by email and return their address country and tax ID info (if available).
  Returns a dict with keys: id, email, address, tax_country, tax_id, tax_id_type
  """
  import stripe
  stripe.api_key = anvil.secrets.get_secret(anvil.server.call("get_stripe_secret_key_name"))

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


# -----------------------------------------
# 2. PAYMENT METHODS
# -----------------------------------------
@anvil.server.callable
def get_stripe_payment_methods(customer_id: str) -> list:
  """
  1. Get all PaymentMethods associated with a customer.
  2. Print and return the list of PaymentMethods (as list of dicts).
  """
  import stripe
  stripe.api_key = anvil.secrets.get_secret(anvil.server.call("get_stripe_secret_key_name"))

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
  stripe.api_key = anvil.secrets.get_secret(anvil.server.call("get_stripe_secret_key_name"))

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


# -----------------------------------------
# 4. SUBSCRIPTIONS
# -----------------------------------------
@anvil.server.callable
def create_stripe_subscription(customer_id: str, price_id: str, plan_type: str, frequency: str, user_count: int = 1, trial_end: int = 0) -> dict:
  """
  1. Create a new subscription for a customer, applying a fixed tax rate for German customers.
  2. Print and return the subscription object (as dict).
  
  Args:
    customer_id (str): Stripe customer ID
    price_id (str): Stripe price ID
    plan_type (str): Plan type ('Explore' or 'Professional')
    frequency (str): Billing frequency ('monthly' or 'yearly')
    user_count (int, optional): Number of users/licenses. Defaults to 1.
    trial_end (int, optional): Timestamp when the subscription should start. Defaults to 0 (immediate start).
      
  Returns:
    dict: The created Stripe subscription object
  """
  import stripe
  stripe.api_key = anvil.secrets.get_secret(anvil.server.call("get_stripe_secret_key_name"))

  user = anvil.users.get_user()

  # Fetch customer to get country
  stripe_customer = stripe.Customer.retrieve(customer_id)
  country = stripe_customer.address.country if stripe_customer.address and hasattr(stripe_customer.address, 'country') else None

  # Only apply the fixed tax rate for German customers
  items = [{"price": price_id, "quantity": user_count}]
  subscription_args = {
    "customer": customer_id,
    "items": items,
    "discounts": [{"coupon": anvil.server.call("get_public_launch_coupon_id")}]
  }
  if country == "DE":
    subscription_args["default_tax_rates"] = [anvil.server.call("get_tax_rate")]

  # Set future start date if requested
  if trial_end > 0:
    import time
    from datetime import datetime, timedelta
    
    # Calculate future timestamp (current time + start_days)
    future_date = datetime.now() + timedelta(days=trial_end)
    future_timestamp = int(future_date.timestamp())
    
    # Use trial_end to delay the first billing until the future date
    subscription_args["trial_end"] = future_timestamp
  
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
def reactivate_stripe_subscription() -> dict:
  """
  # --- 1. REACTIVATE SUBSCRIPTION ---
  1. Reactivates a subscription that was scheduled to be cancelled at the end of the billing period
  2. Sets cancel_at_period_end=false on the subscription
  3. Returns a dict with success status and relevant information
  
  Returns:
    dict: Result with keys:
      - success (bool): Whether the reactivation was successful
      - message (str): Descriptive message about the result
      - subscription_id (str): The Stripe subscription ID
  """
  import stripe
  stripe.api_key = anvil.secrets.get_secret(anvil.server.call("get_stripe_secret_key_name"))

  # --- 2. GET USER DATA ---
  # Get the current user
  user = anvil.users.get_user()

  try:
    # --- 2.1 GET COMPANY DATA ---
    # Get company email
    company = json.loads(anvil.server.call('get_settings_subscription', user['user_id']))
    email = company[0]['mail']
    if not email:
      return {"success": False, "message": "Company email not available"}

    # --- 2.2 GET STRIPE CUSTOMER ---
    # Find customer in Stripe
    customer = get_stripe_customer(email)
    print(f"[STRIPE_DEBUG] Stripe customer found: {customer is not None}, ID: {customer.get('id') if customer else None}")
    
    if not customer or not customer.get('id'):
      return {"success": False, "message": "No Stripe customer found for this company"}

    # --- 2.3 FIND SUBSCRIPTION (ACTIVE OR TRIALING) ---
    # Find subscriptions that can be reactivated
    # When cancel_at_period_end=true, the subscription remains in its current status until the end of the billing period
    customer_id = customer.get('id')
    print(f"[STRIPE_DEBUG] Finding active or trialing subscriptions for customer ID: {customer_id}")
    
    # First check for active subscriptions
    active_subscriptions = stripe.Subscription.list(
      customer=customer_id,
      status='active',
      limit=1
    )
    print(f"[STRIPE_DEBUG] Active subscription result: {len(active_subscriptions.data) if active_subscriptions and hasattr(active_subscriptions, 'data') else 0} found")
    
    # If no active subscriptions, check for trialing subscriptions
    if not active_subscriptions or not active_subscriptions.data:
      print(f"[STRIPE_DEBUG] No active subscriptions found, checking for trialing subscriptions")
      trialing_subscriptions = stripe.Subscription.list(
        customer=customer_id,
        status='trialing',
        limit=1
      )
      print(f"[STRIPE_DEBUG] Trialing subscription result: {len(trialing_subscriptions.data) if trialing_subscriptions and hasattr(trialing_subscriptions, 'data') else 0} found")
      
      # Use trialing subscriptions if found
      if trialing_subscriptions and trialing_subscriptions.data:
        subscriptions = trialing_subscriptions
      else:
        print(f"[STRIPE_DEBUG] Error: No active or trialing subscription found for customer ID {customer_id}")
        return {"success": False, "message": "No active or trialing subscription found"}
    else:
      # Use active subscriptions if found
      subscriptions = active_subscriptions
      
    print(f"[STRIPE_DEBUG] Using subscription with status: {subscriptions.data[0].status}")
    subscription = subscriptions.data[0]
    
    # --- 3. CHECK IF SUBSCRIPTION IS SCHEDULED TO CANCEL ---
    if not subscription.get('cancel_at_period_end'):
      return {"success": False, "message": "Subscription is not scheduled to cancel"}
    
    # --- 4. REACTIVATE SUBSCRIPTION ---
    # Update the subscription to not cancel at period end
    print(f"[STRIPE_DEBUG] Attempting to reactivate subscription: {subscription.id}")
    try:
      updated_subscription = stripe.Subscription.modify(
        subscription.id,
        cancel_at_period_end=False
      )
      print(f"[STRIPE_DEBUG] Successfully reactivated subscription: {updated_subscription.id}")
    except Exception as e:
      print(f"[STRIPE_DEBUG] Error modifying subscription: {e}")
      return {"success": False, "message": f"Error modifying subscription: {str(e)}"}
    
    # --- 5. UPDATE USER RECORDS ---
    # Remove expiration_date from user records
    users_with_same_customer_id = app_tables.users.search(customer_id=user['customer_id'])
    for u in users_with_same_customer_id:
      u['expiration_date'] = None
    
    # --- 6. UPDATE SUBSCRIPTION IN DB ---
    # Extract subscription data for db update
    subscription_item = updated_subscription['items']['data'][0]
    price_id = subscription_item['price']['id']
    
    # Get plan type and frequency from price_id
    from . import config
    price_data = config.get_price_from_id(price_id)
    plan_type = price_data.get('plan', user['plan'])  # Default to current plan if not found
    frequency = price_data.get('frequency', 'monthly')  # Default to monthly if not found
    
    # Get user count from subscription quantity
    user_count = subscription_item.get('quantity', 1)
    
    # Update subscription in database
    print(f"[STRIPE_DEBUG] Updating subscription in DB: plan={plan_type}, user_count={user_count}, frequency={frequency}")
    anvil.server.call('update_subscription_db', 
                      user['customer_id'], 
                      plan_type, 
                      user_count, 
                      frequency, 
                      None)  # No expiration date since we're reactivating
    
    # --- 7. RETURN SUCCESS ---
    print(f"[STRIPE_DEBUG] Reactivation complete for subscription {updated_subscription.id}")
    return {
      "success": True,
      "message": "Your subscription has been successfully reactivated.",
      "subscription_id": updated_subscription.id
    }
  except Exception as e:
    print(f"[Stripe] Error reactivating subscription: {e}")
    return {"success": False, "message": f"Error: {str(e)}"}


@anvil.server.callable
def update_stripe_subscription(target_plan: str, target_user_count: int, target_frequency: str, trial_end: int = 0,
                        current_plan: str = None, current_frequency: str = None) -> dict:
  """
  # --- 1. UPDATE SUBSCRIPTION ---
  1. Update an existing subscription with new plan, user count, billing period
  2. Returns a dict with success status and relevant information
  
  Args:
    target_plan (str): The plan to switch to ('Explore' or 'Professional')
    target_user_count (int): Number of users/licenses for Professional plan
    target_frequency (str): 'monthly' or 'yearly'
    trial_end (int, optional): Days to delay subscription activation. Defaults to 0 (immediate).
    current_plan (str, optional): The current plan type. Useful for comparison. Defaults to None.
    current_frequency (str, optional): The current billing frequency. Useful for comparison. Defaults to None.
  
  Returns:
    dict: Result with keys:
      - success (bool): Whether the update was successful
      - message (str): Descriptive message about the result
      - subscription_id (str): The updated or new subscription ID
  """
  import stripe
  stripe.api_key = anvil.secrets.get_secret(anvil.server.call("get_stripe_secret_key_name"))

  # Get the current user
  user = anvil.users.get_user()

  try:
    company = json.loads(anvil.server.call('get_settings_subscription', user['user_id']))
    email = company[0]['mail']
    if not email:
      return {"success": False, "message": "Company email not available"}
    
    # Find customer in Stripe
    customer = get_stripe_customer(email)
    if not customer or not customer.get('id'):
      return {"success": False, "message": "No Stripe customer found for this company"}

    # --- 2. FIND SUBSCRIPTION TO UPDATE ---
    # --- 2.1 GET ALL POSSIBLE SUBSCRIPTIONS ---
    print(f"[Stripe] Finding subscription to update for customer: {customer['id']}")
    
    # Get subscriptions in different states
    active_subscriptions = stripe.Subscription.list(
      customer=customer['id'],
      status='active',
      limit=10  # Get more to have options to choose from
    )
    
    trialing_subscriptions = stripe.Subscription.list(
      customer=customer['id'],
      status='trialing',
      limit=5
    )
    
    # --- 2.2 DETERMINE WHICH SUBSCRIPTION TO UPDATE ---
    subscription_to_update = None
    subscription_status = ""
    
    # Check active subscriptions first
    if active_subscriptions and active_subscriptions.data:
        # Look for subscriptions that are scheduled to cancel (cancel_at_period_end=True)
        scheduled_to_cancel = [sub for sub in active_subscriptions.data 
                              if sub.get('cancel_at_period_end', False)]
        
        # Look for subscriptions that are not scheduled to cancel
        normal_active = [sub for sub in active_subscriptions.data 
                        if not sub.get('cancel_at_period_end', False)]
        
        if normal_active:
            # Prefer active subscriptions that are not scheduled to cancel
            subscription_to_update = normal_active[0]
            subscription_status = "active"
            print(f"[Stripe] Found active subscription: {subscription_to_update.id}")
        elif scheduled_to_cancel:
            # Use a subscription that's scheduled to be canceled if no normal active found
            subscription_to_update = scheduled_to_cancel[0]
            subscription_status = "scheduled_to_cancel"
            print(f"[Stripe] Found subscription scheduled for cancellation: {subscription_to_update.id}")
    
    # If no active found, check trialing subscriptions
    if not subscription_to_update and trialing_subscriptions and trialing_subscriptions.data:
        subscription_to_update = trialing_subscriptions.data[0]
        subscription_status = "trialing"
        print(f"[Stripe] Found subscription in trial: {subscription_to_update.id}")
    
    # --- 2.3 HANDLE NO SUBSCRIPTION CASE ---
    if not subscription_to_update:
        # No subscription found in any of the expected states
        print(f"[Stripe] No active or trialing subscription found for customer: {customer['id']}")
        return {"success": False, "message": "No active, trialing, or scheduled-for-cancellation subscription found."}
    
    # Use the found subscription
    subscription = subscription_to_update
    print(f"[Stripe] Selected subscription to update: {subscription.id} (Status: {subscription_status})")
    
    # Add status to operation details for later
    subscription_data = {
        "id": subscription.id,
        "status": subscription_status
    }
    
    # --- 3.1 DETERMINE PRICE ID ---
    # Get price ID from the central configuration module
    from . import config
    price_id = config.get_price_id(target_plan, target_frequency)
    
    # Check if the plan is valid
    if not price_id:
      return {"success": False, "message": f"Unknown plan or frequency: {target_plan} - {target_frequency}"}
    print(f"[Stripe] Using price ID: {price_id}") 
    
    # Set the quantity based on the plan (Professional plans can have multiple users)
    quantity = target_user_count if target_plan == "Professional" else 1
    print(f"[Stripe] Using quantity: {quantity}")

    # --- 3. PREPARE OPERATION DETAILS ---
    # --- 3.2 COLLECT OPERATION DETAILS ---
    # Prepare operation description for logging and user messaging
    operation_details = []
    
    # Add subscription status information
    if subscription_status == "active":
      operation_details.append("Updating active subscription")
    elif subscription_status == "scheduled_to_cancel":
      operation_details.append("Updating subscription that was scheduled for cancellation")
    elif subscription_status == "trialing":
      operation_details.append("Updating subscription in trial period")
    
    # Add plan change information
    if current_plan and current_plan != target_plan:
      operation_details.append(f"Plan change from {current_plan} to {target_plan}")
    
    # Add frequency change information
    if current_frequency and current_frequency != target_frequency:
      operation_details.append(f"Frequency change from {current_frequency} to {target_frequency}")
    
    # Add user count information for Professional plans
    if target_user_count > 1 and target_plan == "Professional":
      operation_details.append(f"User count set to {target_user_count}")
    
    print(f"[Stripe] Using operation details: {operation_details}")
    
    # --- 4. UPDATE SUBSCRIPTION ---
    # Update existing subscription
    subscription_id = subscription.id
      
    # Prepare update parameters
    update_params = {
      "cancel_at_period_end": False,
      "proration_behavior": 'create_prorations',
      "items": [{
        'id': subscription['items']['data'][0].id,
        'price': price_id,
        'quantity': quantity
      }]
    }
    
    # Add trial_end if specified (future restart date)
    if trial_end > 0:
      import time
      from datetime import datetime, timedelta
      future_date = datetime.now() + timedelta(days=trial_end)
      future_timestamp = int(future_date.timestamp())
      update_params["trial_end"] = future_timestamp
      
    # Modify the subscription
    subscription = stripe.Subscription.modify(subscription_id, **update_params)
    message = "Subscription successfully updated"
    
    # Update user records in Anvil database
    users_with_same_customer_id = app_tables.users.search(customer_id=user['customer_id'])
    for u in users_with_same_customer_id:
      u['plan'] = target_plan
      if trial_end > 0:
        from datetime import datetime, timedelta
        future_date = datetime.now() + timedelta(days=trial_end)
        u['expiration_date'] = future_date.date()
      else:
        u['expiration_date'] = None
    
    # Update subscription in database
    print(f"[STRIPE_DEBUG] Updating subscription in DB: plan={target_plan}, user_count={target_user_count}, frequency={target_frequency}")
    anvil.server.call('update_subscription_db', 
                      user['customer_id'], 
                      target_plan, 
                      target_user_count, 
                      target_frequency, 
                      None)
    # Log the operation details
    operation_summary = ", ".join(operation_details) if operation_details else "Subscription update"
    print(f"[Stripe] {operation_summary}: id={subscription.id}, customer={subscription.customer}, status={subscription.status}")
    
    return {
      "success": True,
      "message": f"{message}: {operation_summary}",
      "subscription_id": subscription.id
    }

  except Exception as e:
    print(f"Error updating subscription: {e}")
    return {"success": False, "message": f"Error: {str(e)}"}


@anvil.server.callable
def cancel_stripe_subscription() -> dict:
  """
  1. Cancel the current subscription for the authenticated user
  2. Returns a dict with success status and relevant information
  
  Returns:
    dict: Result with keys:
      - success (bool): Whether the cancellation was successful
      - message (str): Descriptive message about the result
  """
  import stripe
  stripe.api_key = anvil.secrets.get_secret(anvil.server.call("get_stripe_secret_key_name"))

  # Get the current user
  user = anvil.users.get_user()

  try:
    print(f"[STRIPE_DEBUG] Starting subscription cancellation for user_id: {user['user_id']}")
    
    # Get company email
    company = json.loads(anvil.server.call('get_settings_subscription', user['user_id']))
    
    email = company[0]['mail'] if company and len(company) > 0 and 'mail' in company[0] else None
    
    if not email:
      return {"success": False, "message": "Company email not available"}

    # --- 1. FIND CUSTOMER IN STRIPE ---
    customer = get_stripe_customer(email)
    
    if not customer or not customer.get('id'):
      print(f"[STRIPE_DEBUG] Error: No Stripe customer found for email {email}")
      return {"success": False, "message": "No Stripe customer found for this company"}
    
    # First check for active subscriptions
    active_subscriptions = stripe.Subscription.list(
      customer=customer['id'],
      status='active',
      limit=1
    )
    
    # If no active subscriptions, check for trialing subscriptions
    if not active_subscriptions or not active_subscriptions.data:
      print("[STRIPE_DEBUG] No active subscriptions found, checking for trialing subscriptions")
      trialing_subscriptions = stripe.Subscription.list(
        customer=customer['id'],
        status='trialing',
        limit=1
      )
      
      # Use trialing subscriptions if found
      if trialing_subscriptions and trialing_subscriptions.data:
        subscriptions = trialing_subscriptions
      else:
        print(f"[STRIPE_DEBUG] Error: No active or trialing subscription found for customer ID {customer['id']}")
        return {"success": False, "message": "No active or trialing subscription found"}
    else:
      # Use active subscriptions if found
      subscriptions = active_subscriptions
  
    # --- 3. CANCEL SUBSCRIPTION ---
    subscription_id = subscriptions.data[0].id
    try:
      subscription = stripe.Subscription.modify(
        subscription_id,
        cancel_at_period_end=True
      )
      print(f"[STRIPE_DEBUG] Successfully set subscription {subscription_id} to cancel at period end")
    except Exception as e:
      print(f"[STRIPE_DEBUG] Error modifying subscription: {e}")
      return {"success": False, "message": f"Error modifying subscription: {str(e)}"}

    # --- 4. DETERMINE EXPIRATION DATE ---
    expiration_date = subscription["items"]["data"][0]["current_period_end"]
    expiration_date = datetime.fromtimestamp(expiration_date).date()

    # --- 5. UPDATE USER RECORDS ---
    users_with_same_customer_id = app_tables.users.search(customer_id=user['customer_id'])
    user_count = len(users_with_same_customer_id)
    
    try:
      for u in users_with_same_customer_id:
        u['expiration_date'] = expiration_date
    except Exception as e:
      print(f"[STRIPE_DEBUG] Error updating user records: {e}")
      return {"success": False, "message": f"Error updating user records: {str(e)}"}

    # --- 6. UPDATE SUBSCRIPTION IN DATABASE ---
    try:
      result = anvil.server.call('cancel_subscription', user['customer_id'], expiration_date)
    except Exception as e:
      print(f"[STRIPE_DEBUG] Error calling cancel_subscription database function: {e}")
      return {"success": False, "message": f"Error updating subscription in database: {str(e)}"}

    # --- 7. RETURN RESULT ---
    if result == 'Subscription cancelled successfully':
      print(f"[STRIPE_DEBUG] Subscription {subscription.id} will be cancelled on {expiration_date}")
      return {
        "success": True,
        "message": "Subscription will be cancelled at the end of the current billing period",
        "subscription_id": subscription.id,
        "expiration_date": expiration_date
      }
    else:
      print(f"[STRIPE_DEBUG] Error in database update: {result}")
      return {"success": False, "message": f"Error in database: {result}"}
  except Exception as e:
    print(f"[STRIPE_DEBUG] Global exception in cancel_stripe_subscription: {e}")
    print(f"[STRIPE_DEBUG] Exception type: {type(e).__name__}")
    print(f"[STRIPE_DEBUG] Exception args: {e.args}")
    # Include traceback for easier debugging
    import traceback
    print(f"[STRIPE_DEBUG] Traceback: {traceback.format_exc()}")
    return {"success": False, "message": f"Error: {str(e)}"}

