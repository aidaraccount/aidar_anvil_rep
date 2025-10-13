from ._anvil_designer import C_ActivateNotificationTemplate
from anvil import *
import anvil.server
import anvil.users
from anvil import get_open_form


class C_ActivateNotification(C_ActivateNotificationTemplate):
    def __init__(self, model_id, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        
        self.model_id = model_id

    def activate_button_click(self, **event_args):
        """Activate agent notification"""
        try:
            # Call backend to activate notification
            result = anvil.server.call('update_agent_notification', int(self.model_id), True)
            
            if result == 'success':
                # Refresh navigation to show green indicator
                get_open_form().refresh_models_components()
                
                # Show success message
                Notification("",
                    title="Agent Notification Activated!",
                    style="success").show()
                
                # Close the alert
                self.raise_event("x-close-alert")
        
        except Exception as e:
            print(f"Error activating notification: {e}")
            Notification("",
                title="Failed to activate notification",
                style="warning").show()

    def later_button_click(self, **event_args):
        """Close the alert without activating"""
        self.raise_event("x-close-alert")
