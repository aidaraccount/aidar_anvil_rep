"""
# --- 1. SERVER CONFIGURATION MODULE ---
# Contains configuration values for server-side code.
# This module can be imported in server-side functions.
"""

import anvil.server

# --- 2. SUBSCRIPTION PRICING ---
class PricingConfig:
  """Configuration for subscription pricing and Stripe integration."""

  # --- 1 KEYS ---
  # 1.1 Stripe publishable key (public key for client-side Stripe.js)
  STRIPE_PUBLIC_KEY: str = "pk_test_51RDoXJQTBcqmUQgt9CqdDXQjtHKkEkEBuXSs7EqVjwkzqcWP66EgCu8jjYArvbioeYpzvS5wSvbrUsKUtjXi0gGq00M9CzHJTa"
  
  # 1.2 Stripe secret key (private key for server-side Stripe.js)
  # STRIPE_SECRET_KEY is in Anvil secrets
  
  # --- 2.1 STRIPE PRICE IDS ---
  # Price IDs from Stripe for each plan and frequency
  stripe_price_ids = {
    "explore": {
      "monthly": "price_1RE3tSQTBcqmUQgtoNyD0LgB",
      "yearly": "price_1REVjKQTBcqmUQgt4Z47P00s",
    },
    "professional": {
      "monthly": "price_1REVwmQTBcqmUQgtiBBLNZaD",
      "yearly": "price_1REVzZQTBcqmUQgtpyBz8Gky",
    }
  }
  
  # --- 2.2 PRICE VALUES ---
  # Price amounts in euros for each plan and frequency
  price_values = {
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


def get_price_value(plan: str, frequency: str, price_type: str) -> float:
  """
  1. Get the price value for the given plan and frequency.
  Returns:
    float: Price value for the given plan and frequency
  """
  print(f"[DEBUG] Getting price value for plan: {plan}, frequency: {frequency}, price type: {price_type}")
  print(f"[DEBUG] Price values: {PricingConfig.price_values[plan][frequency][price_type]}")
  return PricingConfig.price_values[plan][frequency][price_type]


def get_stripe_public_key() -> str:
  """
  1. Get the Stripe public (publishable) key for client-side use.
  Returns:
    str: Stripe publishable key
  """
  return PricingConfig.STRIPE_PUBLIC_KEY


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
  
  if plan_key in PricingConfig.stripe_price_ids and freq_key in PricingConfig.stripe_price_ids[plan_key]:
    return PricingConfig.stripe_price_ids[plan_key][freq_key]
  
  return None


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
  for plan, frequencies in PricingConfig.stripe_price_ids.items():
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
    'price_values': PricingConfig.price_values,
    'price_ids': PricingConfig.stripe_price_ids
  }
