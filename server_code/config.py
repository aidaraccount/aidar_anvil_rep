"""
# --- 1. SERVER CONFIGURATION MODULE ---
# Contains configuration values for server-side code.
# This module can be imported in server-side functions.
"""

import anvil.server

# --- 2. SUBSCRIPTION PRICING ---
class PricingConfig:
    """Configuration for subscription pricing and Stripe integration."""
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
    # All price values in euros, both original and discounted
    price_values = {
        "explore": {
            "monthly_original": 39.00,
            "monthly_discounted": 29.00,
            "yearly_original_per_month": 35.00,
            "yearly_discounted_per_month": 26.00,
        },
        "professional": {
            "monthly_original_per_user": 59.00,
            "monthly_discounted_per_user": 44.00,
            "yearly_original_per_user": 53.00,
            "yearly_discounted_per_user": 39.00,
        }
    }

@anvil.server.callable
def get_plan_prices(plan: str) -> dict:
    """
    Return all price values for the specified plan for client-side use.
    Args:
        plan (str): The plan name (e.g., 'explore', 'professional')
    Returns:
        dict: Price values for the plan
    """
    return PricingConfig.price_values.get(plan, {})

def get_stripe_public_key() -> str:
    """
    1.2 Get the Stripe public (publishable) key for client-side use.
    Returns:
        str: Stripe publishable key
    """
    return PricingConfig.STRIPE_PUBLIC_KEY

def get_price_id(plan: str, frequency: str) -> str:
    """
    Get the Stripe price ID for the given plan and frequency.
    
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
    Get the plan and frequency for a given Stripe price ID.
    
    Parameters:
    -----------
    price_id : str
        The Stripe price ID to look up
        
    Returns:
    --------
    dict
        Dictionary containing 'plan' and 'frequency' keys
    """
    # Create a reverse mapping of price_id to plan/frequency
    for plan, frequencies in PricingConfig.stripe_price_ids.items():
        for frequency, pid in frequencies.items():
            if pid == price_id:
                return {
                    'plan': plan.capitalize(),  # Return with first letter capitalized
                    'frequency': frequency
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
