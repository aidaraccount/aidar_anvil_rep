"""
# --- 1. SERVER CONFIGURATION MODULE ---
# Contains configuration values for server-side code.
# This module can be imported in server-side functions.
"""

# --- 2. SUBSCRIPTION PRICING ---
class PricingConfig:
    """Configuration for subscription pricing and Stripe integration."""
    
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
            "monthly": 29.00,
            "yearly_per_month": 26.00,
        },
        "professional": {
            "monthly": 44.00,
            "yearly_per_month": 39.00,
        }
    }

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
