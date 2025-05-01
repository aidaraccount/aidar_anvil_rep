from ._anvil_designer import C_PaymentContainerTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.js

class C_PaymentContainer(C_PaymentContainerTemplate):
    """
    1. Main container component for the payment and subscription workflow
    2. Manages navigation between different views (customer, payment, subscription)
    3. Maintains shared state across all views
    """
    def __init__(self, plan_type: str = None, user_count: int = None, billing_period: str = None, **properties):
        # 1. Set Form properties and Data Bindings
        self.init_components(**properties)
        
        # 2. Get current user
        self.user = anvil.users.get_user()
        
        # 3. Initialize state data
        self.data = {
            'plan': {
                'type': plan_type,
                'user_count': user_count,
                'billing_period': billing_period
            },
            'customer': {},
            'payment_method': {},
            'price_id': None,
            'customer_id': None,
            'default_payment_method': None
        }
        
        # 4. Initialize navigation history
        self.history = []
        self.current_view = None
        
        # 5. Get the Stripe Price ID based on plan type and billing period
        if plan_type == "Explore" and billing_period == "monthly":
            self.data['price_id'] = "price_1RE3tSQTBcqmUQgtoNyD0LgB"
        elif plan_type == "Explore" and billing_period == "yearly":
            self.data['price_id'] = "price_1REVjKQTBcqmUQgt4Z47P00s"
        elif plan_type == "Professional" and billing_period == "monthly":
            self.data['price_id'] = "price_1REVwmQTBcqmUQgtiBBLNZaD"
        elif plan_type == "Professional" and billing_period == "yearly":
            self.data['price_id'] = "price_1REVzZQTBcqmUQgtpyBz8Gky"
        
        # 6. Load existing customer data if available
        self._load_customer_data()
        
        # 7. Create container HTML structure
        self._create_container_html()
        
        # 8. Register JS-callable functions
        self._register_js_functions()
        
        # 9. Determine starting view based on available data
        self._determine_starting_view()
    
    def _create_container_html(self) -> None:
        """
        1. Creates the HTML structure for the container
        2. This includes header, content area, and navigation buttons
        """
        self.html = """
        <div id="payment-container">
            <div id="payment-header">
                <h2 id="view-title">Loading...</h2>
                <div id="payment-nav-close" title="Close">✕</div>
            </div>
            <div id="view-content"></div>
            <div id="payment-footer">
                <div class="button-row">
                    <button type="button" id="back-btn">Back</button>
                    <button type="button" id="cancel-btn">Cancel</button>
                    <button type="button" id="next-btn">Next</button>
                </div>
            </div>
            <script>
                document.getElementById('payment-nav-close').onclick = function() {
                    window.cancel_flow();
                };
                document.getElementById('back-btn').onclick = function() {
                    window.go_back();
                };
                document.getElementById('cancel-btn').onclick = function() {
                    window.cancel_flow();
                };
                document.getElementById('next-btn').onclick = function() {
                    window.next_step();
                };
            </script>
        </div>
        """
    
    def _register_js_functions(self) -> None:
        """
        Registers all JavaScript-callable functions on the window object
        """
        anvil.js.window.cancel_flow = self._cancel_flow
        anvil.js.window.go_back = self._go_back
        anvil.js.window.next_step = self._next_step
        anvil.js.window.edit_customer = self._edit_customer
        anvil.js.window.edit_payment = self._edit_payment
        anvil.js.window.submit_customer_form = self._submit_customer_form
        anvil.js.window.submit_payment_form = self._submit_payment_form
        anvil.js.window.create_subscription = self._create_subscription
    
    def _determine_starting_view(self) -> None:
        """
        1. Determines which view to start with based on available data
        2. If customer data missing -> customer view
        3. If payment method missing -> payment view
        4. Otherwise -> subscription view
        """
        if not self.data['customer_id']:
            self.show_view("customer")
        elif not self.data['default_payment_method']:
            self.show_view("payment")
        else:
            self.show_view("subscription")
    
    def _load_customer_data(self) -> None:
        """
        1. Loads existing customer data from Stripe
        2. Includes basic info, tax details, and payment methods
        """
        try:
            # Get customer data
            customer = anvil.server.call('get_stripe_customer', self.user['email'])
            if customer and customer.get('id'):
                # Store basic customer data
                self.data['customer_id'] = customer['id']
                self.data['customer'] = {
                    'id': customer['id'],
                    'name': customer.get('name', ''),
                    'email': customer.get('email', ''),
                    'address': customer.get('address', {})
                }
                
                # Extract tax info
                tax_ids = customer.get('tax_ids', {}).get('data', [])
                if tax_ids:
                    tax_id_obj = tax_ids[0]  # Use first tax ID
                    self.data['customer']['tax_id'] = tax_id_obj.get('value', '')
                    self.data['customer']['tax_country'] = tax_id_obj.get('country', '')
                
                # Get payment methods
                payment_methods = anvil.server.call('get_stripe_payment_methods', customer['id'])
                if payment_methods:
                    pm = payment_methods[0]  # Assume first is default
                    self.data['default_payment_method'] = pm.get('id')
                    card = pm.get('card', {})
                    self.data['payment_method'] = {
                        'id': pm.get('id'),
                        'brand': card.get('brand', ''),
                        'last4': card.get('last4', ''),
                        'exp_month': card.get('exp_month', ''),
                        'exp_year': card.get('exp_year', '')
                    }
        except Exception as e:
            print(f"Error loading customer data: {e}")
    
    def show_view(self, view_name: str, add_to_history: bool = True) -> None:
        """
        1. Switches to a specified view
        2. Updates navigation buttons and title
        3. Optionally adds current view to history
        
        Args:
            view_name: Name of the view to show ('customer', 'payment', or 'subscription')
            add_to_history: Whether to add the current view to history
        """
        # Add current view to history for back navigation
        if self.current_view and add_to_history:
            self.history.append(self.current_view)
        
        # Set current view
        self.current_view = view_name
        
        # Import view module and render content
        view_html = ""
        title = ""
        
        if view_name == "customer":
            from .views.CustomerView import render_customer_view
            title = "Company Profile"
            view_html = render_customer_view(self.data)
            
        elif view_name == "payment":
            from .views.PaymentView import render_payment_view
            title = "Payment Method"
            view_html = render_payment_view(self.data)
            
        elif view_name == "subscription":
            from .views.SubscriptionView import render_subscription_view
            title = "Confirm Subscription"
            view_html = render_subscription_view(self.data)
        
        # Update view content and title
        js_update = f"""
        document.getElementById('view-title').textContent = '{title}';
        document.getElementById('view-content').innerHTML = `{view_html}`;
        """
        
        # Update button visibility based on navigation state
        back_visible = len(self.history) > 0
        next_visible = view_name != "subscription"
        cancel_visible = True
        next_text = "Next" if view_name != "subscription" else "Book Subscription"
        
        js_buttons = f"""
        document.getElementById('back-btn').style.display = '{'' if back_visible else 'none'}';
        document.getElementById('next-btn').style.display = '{'' if next_visible else 'none'}';
        document.getElementById('cancel-btn').style.display = '{'' if cancel_visible else 'none'}';
        document.getElementById('next-btn').textContent = '{next_text}';
        """
        
        # Execute JS to update DOM
        anvil.js.call_js('eval', js_update + js_buttons)
        
        # Initialize view-specific JS if needed
        if view_name == "customer":
            from .views.CustomerView import init_customer_js
            init_customer_js(self.data)
        elif view_name == "payment":
            from .views.PaymentView import init_payment_js
            init_payment_js(self.data)
        elif view_name == "subscription":
            from .views.SubscriptionView import init_subscription_js
            init_subscription_js(self.data)
    
    def update_data(self, data_dict: dict) -> None:
        """
        Updates container data with new values
        
        Args:
            data_dict: Dictionary of new data to merge with existing data
        """
        for key, value in data_dict.items():
            if isinstance(value, dict) and isinstance(self.data.get(key, {}), dict):
                # Deep merge for nested dictionaries
                self.data[key].update(value)
            else:
                # Direct assignment for other types
                self.data[key] = value
    
    def _next_step(self) -> None:
        """
        1. Handles next button click based on current view
        2. Triggers form validation and submission
        """
        if self.current_view == "customer":
            # Submit customer form
            anvil.js.call_js('eval', 'window.submit_customer_form()')
        elif self.current_view == "payment":
            # Submit payment form
            anvil.js.call_js('eval', 'window.submit_payment_form()')
        elif self.current_view == "subscription":
            # Create subscription
            self._create_subscription()
    
    def _submit_customer_form(self) -> None:
        """
        1. Gets customer data from form fields
        2. Creates or updates Stripe customer
        3. Moves to next view if successful
        """
        try:
            # Get form data from JS
            js_get_data = """
            return {
                name: document.getElementById('company-name').value,
                address: {
                    line1: document.getElementById('address-line-1').value,
                    line2: document.getElementById('address-line-2').value,
                    city: document.getElementById('city').value,
                    state: document.getElementById('state').value,
                    postal_code: document.getElementById('postal-code').value,
                    country: document.getElementById('country').value
                },
                tax_id: document.getElementById('tax-id').value,
                tax_country: document.getElementById('tax-country').value,
                is_business: document.getElementById('business-checkbox').checked
            };
            """
            customer_data = anvil.js.call_js('eval', js_get_data)
            
            # Validate required fields
            if not customer_data['name'] or not customer_data['address']['line1'] or not customer_data['address']['city']:
                anvil.js.call_js('eval', "alert('Please fill all required fields')")
                return
            
            # Validate tax info if business
            if customer_data['is_business'] and (not customer_data['tax_id'] or not customer_data['tax_country']):
                anvil.js.call_js('eval', "alert('Please provide valid tax information')")
                return
            
            # Save to container data
            self.update_data({'customer': customer_data})
            
            # Create or update customer in Stripe
            if self.data['customer_id']:
                # Update existing customer
                anvil.server.call('update_stripe_customer',
                                 self.data['customer_id'],
                                 customer_data['name'],
                                 self.user['email'],
                                 customer_data['address'])
            else:
                # Create new customer
                customer = anvil.server.call('create_stripe_customer',
                                            self.user['email'],
                                            customer_data['name'],
                                            customer_data['address'])
                self.data['customer_id'] = customer['id']
            
            # Handle tax ID if provided
            if customer_data['tax_id'] and customer_data['tax_country']:
                tax_id_type = self._get_tax_id_type(customer_data['tax_country'])
                if tax_id_type:
                    anvil.server.call('update_stripe_customer_tax_id',
                                    self.data['customer_id'],
                                    customer_data['tax_id'],
                                    tax_id_type)
            
            # Reload customer data
            self._load_customer_data()
            
            # Move to next view
            self.show_view("payment")
            
        except Exception as e:
            anvil.js.call_js('eval', f'alert("Error: {str(e)}")')
    
    def _submit_payment_form(self) -> None:
        """
        1. Gets payment method ID from Stripe.js
        2. Attaches payment method to customer
        3. Moves to next view if successful
        """
        # The actual submission is handled by Stripe.js
        # This method will be called from PaymentView after Stripe confirms payment method
        pass
    
    def payment_form_submitted(self, payment_method_id: str) -> None:
        """
        Called when payment form is successfully submitted with Stripe payment method ID
        
        Args:
            payment_method_id: Stripe payment method ID
        """
        try:
            # Attach payment method to customer
            anvil.server.call('attach_payment_method_to_customer',
                             self.data['customer_id'],
                             payment_method_id)
            
            # Reload payment data
            self._load_customer_data()
            
            # Move to next view
            self.show_view("subscription")
            
        except Exception as e:
            anvil.js.call_js('eval', f'alert("Error saving payment method: {str(e)}")')
    
    def _create_subscription(self) -> None:
        """
        1. Creates Stripe subscription with all collected data
        2. Shows success message and redirects user
        """
        try:
            if not self.data['customer_id']:
                raise ValueError("No customer ID found")
            if not self.data['price_id']:
                raise ValueError("No price ID found")
            if not self.data['default_payment_method']:
                raise ValueError("No payment method found")
            
            # Create the subscription
            subscription = anvil.server.call('create_stripe_subscription',
                                           self.data['customer_id'],
                                           self.data['price_id'],
                                           self.data['plan']['type'],
                                           self.data['plan']['user_count'])
            
            # Show success message
            anvil.js.call_js('eval', f'alert("Subscription created successfully!")')
            
            # Redirect to settings page
            anvil.js.window.location.replace("/#settings?section=Subscription")
            
            # Close the container
            self.raise_event("x-close-alert", value="success")
            
        except Exception as e:
            anvil.js.call_js('eval', f'alert("Error creating subscription: {str(e)}")')
    
    def _go_back(self) -> None:
        """
        Navigates to the previous view if history exists
        """
        if self.history:
            previous = self.history.pop()
            self.show_view(previous, add_to_history=False)
    
    def _edit_customer(self) -> None:
        """
        Edit customer data from subscription view
        """
        self.show_view("customer")
    
    def _edit_payment(self) -> None:
        """
        Edit payment method from subscription view
        """
        self.show_view("payment")
    
    def _cancel_flow(self) -> None:
        """
        Cancels the entire flow and closes the container
        """
        self.raise_event("x-close-alert")
    
    def _get_tax_id_type(self, country_code: str) -> str:
        """
        Determines the tax ID type based on country code
        
        Args:
            country_code: Two-letter country code
            
        Returns:
            Stripe tax ID type string or None if not found
        """
        tax_id_type_map = {
            'GB': 'gb_vat',
            'US': 'us_ein',
            'CA': 'ca_bn',
            'AU': 'au_abn',
            'CH': 'ch_vat',
            'NO': 'no_vat',
            'IS': 'is_vat',
            'LI': 'li_uid',
            'IN': 'in_gst',
            'JP': 'jp_cn',
            'CN': 'cn_tin',
            'BR': 'br_cnpj',
            'MX': 'mx_rfc',
            'SG': 'sg_gst',
            'HK': 'hk_br',
            'NZ': 'nz_gst',
            'ZA': 'za_vat',
        }
        
        eu_countries = [
            'AT', 'BE', 'BG', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GR', 'HR', 'HU', 'IE',
            'IT', 'LT', 'LU', 'LV', 'MT', 'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK'
        ]
        
        if country_code in eu_countries:
            return 'eu_vat'
        else:
            return tax_id_type_map.get(country_code)
