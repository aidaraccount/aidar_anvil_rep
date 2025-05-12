"""
# --- 1. CENTRAL CONFIGURATION MODULE ---
# Contains configuration values for the entire application.
# This module can be imported anywhere in the Anvil application.
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
