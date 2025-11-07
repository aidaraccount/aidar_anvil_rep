import anvil.email
"""
# --- 1. SERVER CONFIGURATION MODULE ---
# Contains configuration values for server-side code.
# This module can be imported in server-side functions.
"""

import anvil.server

class Config:

  # --- STRIPE ENVIRONMENT (sandbox or live) ---
  STRIPE_ENVIRONMENT: str = "live"
  
  # --- 1. Stripe public keys (public keys for client-side Stripe.js) ---
  STRIPE_PUBLIC_KEYS: dict = {
    "sandbox": "pk_test_51RDoXJQTBcqmUQgt9CqdDXQjtHKkEkEBuXSs7EqVjwkzqcWP66EgCu8jjYArvbioeYpzvS5wSvbrUsKUtjXi0gGq00M9CzHJTa",
    "live": "pk_live_51RDoXAKpYockGiqNWesxhdEaYp4LeKuY3h76XStenrsmf4JWVu5KeEQPwPSqAPv5eGrZTlNajaL3JPg8W1cnvRaZ00A2b0frOh"
  }
  STRIPE_PUBLIC_KEY: str = STRIPE_PUBLIC_KEYS[STRIPE_ENVIRONMENT]
  
  # --- 2. Stripe secret key name ---
  # STRIPE_SECRET_KEY is in Anvil secrets
  STRIPE_SECRET_KEY_NAMES: dict = {
    "sandbox": "STRIPE_SECRET_KEY_SANDBOX",
    "live": "STRIPE_SECRET_KEY_LIVE"
  }
  STRIPE_SECRET_KEY_NAME: str = STRIPE_SECRET_KEY_NAMES[STRIPE_ENVIRONMENT]

  # --- 3. Stripe price IDs ---
  stripe_price_ids_config: dict = {
    "sandbox": {
      "explore": {
        "monthly": "price_1RE3tSQTBcqmUQgtoNyD0LgB",
        "yearly": "price_1REVjKQTBcqmUQgt4Z47P00s",
      },
      "professional": {
        "monthly": "price_1REVwmQTBcqmUQgtiBBLNZaD",
        "yearly": "price_1REVzZQTBcqmUQgtpyBz8Gky",
      }
    },
    "live": {
      "explore": {
        "monthly": "price_1RP3zlKpYockGiqNzNiA4qcr",
        "yearly": "price_1RP3zcKpYockGiqNbIKImcdu",
      },
      "professional": {
        "monthly": "price_1RP3zhKpYockGiqNe3IY5qrF",
        "yearly": "price_1RP3zWKpYockGiqNw0tAHgnO",
      }
    }
  }
  stripe_price_ids: dict = stripe_price_ids_config[STRIPE_ENVIRONMENT]
  
  # --- 4. Price values ---
  price_values: dict = {
    "explore": {
      "monthly": {
        "original": 39.00,
        "discounted": 29.00
      },
      "yearly": {
        "original": 35.00,
        "discounted": 26.00
      }
    },
    "professional": {
      "monthly": {
        "original": 59.00,
        "discounted": 44.00
      },
      "yearly": {
        "original": 53.00,
        "discounted": 39.00
      }
    }
  }

  # NOTE: There are still individual prices in C_SubscriptionPlan - see:
  # // Monthly and yearly price per user (Professional)
  # var monthlyOriginalPerUser = 59.00;
  # var monthlyDiscountedPerUser = 44.00;
  # var yearlyOriginalPerUser = 53.00;
  # var yearlyDiscountedPerUser = 39.00;

  # --- 5. Coupons ---
  coupon_ids: dict = {
    "sandbox": {
      "public_launch_discount": "I1ivrR97"
    },
    "live": {
      "public_launch_discount": "Wb8JWkWM"
    }
  }
  public_launch_coupon_id: str = coupon_ids[STRIPE_ENVIRONMENT]["public_launch_discount"]

  # --- 6. Tax rates ---
  tax_rates: dict = {
    "sandbox": "txr_1RHo7sQTBcqmUQgtajAz0voj",
    "live": "txr_1RP46rKpYockGiqN7IlyAWrK"
  }
  tax_rate: str = tax_rates[STRIPE_ENVIRONMENT]


# --- 1. Stripe public keys (public keys for client-side Stripe.js) ---
@anvil.server.callable
def get_stripe_public_key() -> str:
  """
  1. Get the Stripe public (publishable) key for client-side use.
  Returns:
    str: Stripe publishable key
  """
  return Config.STRIPE_PUBLIC_KEY


# --- 2. Stripe secret key name ---
@anvil.server.callable
def get_stripe_secret_key_name() -> str:
  """
  1. Get the Stripe secret key name.
  Returns:
    str: Stripe secret key name
  """
  return Config.STRIPE_SECRET_KEY_NAME


# --- 3. Stripe price IDs ---
def get_price_id(plan: str, frequency: str) -> str:
  """
  1. Get the Stripe price ID for the given plan and frequency.
  
  Parameters:
  -----------
  plan : str
    The plan type ('Explore' or 'Professional')
  frequency : str
    The billing frequency ('monthly' or 'yearly')
      
  Returns:
  --------
  str
    The Stripe price ID
  """
  plan_key = plan.lower() if plan else ""
  freq_key = frequency.lower() if frequency else ""
  
  if plan_key in Config.stripe_price_ids and freq_key in Config.stripe_price_ids[plan_key]:
    return Config.stripe_price_ids[plan_key][freq_key]
  
  return None


def get_price_value(plan: str, frequency: str, price_type: str) -> float:
  """
  1. Get the price value for the given plan and frequency.
  Returns:
    float: Price value for the given plan and frequency
  """
  print(f"[DEBUG] Getting price value for plan: {plan}, frequency: {frequency}, price type: {price_type}")
  print(f"[DEBUG] Price values: {Config.price_values[plan][frequency][price_type]}")
  return Config.price_values[plan][frequency][price_type]


def get_price_from_id(price_id: str) -> dict:
  """
  # --- 2.3 LOOKUP PRICE DETAILS FROM ID ---
  Get the plan, frequency, and price type for a given Stripe price ID.
  
  Parameters:
  -----------
  price_id : str
    The Stripe price ID to look up
      
  Returns:
  --------
  dict
    Dictionary containing 'plan', 'frequency', and 'price_type' keys
  """
  # Create a reverse mapping of price_id to plan/frequency
  for plan, frequencies in Config.stripe_price_ids.items():
    for frequency, price_types in frequencies.items():
      for price_type, pid in price_types.items():
        if pid == price_id:
          return {
            'plan': plan.capitalize(),
            'frequency': frequency,
            'price_type': price_type
          }
  # Return empty dict if not found
  return {}

# --- 3. CLIENT ACCESS TO CONFIGURATION ---
@anvil.server.callable
def get_pricing_config():
  """
  # --- 3.1 SHARE CONFIG WITH CLIENT ---
  Returns safe pricing configuration data for client-side use
  
  Returns:
  --------
  dict
    Dictionary containing price values and price IDs for client use
  """
  return {
    'price_values': Config.price_values,
    'price_ids': Config.stripe_price_ids
  }


# --- 5. Coupons ---
@anvil.server.callable
def get_public_launch_coupon_id() -> str:
  """
  1. Get the public launch coupon ID.
  Returns:
    str: Public launch coupon ID
  """
  return Config.public_launch_coupon_id


# --- 6. Tax rates ---
@anvil.server.callable
def get_tax_rate() -> str:
  """
  1. Get the tax rate.
  Returns:
    str: Tax rate
  """
  return Config.tax_rate
