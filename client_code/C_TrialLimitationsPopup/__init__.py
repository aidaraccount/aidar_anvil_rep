from ._anvil_designer import C_TrialLimitationsPopupTemplate
from anvil import *
import stripe.checkout
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json
import anvil

from anvil_extras import routing
from ..nav import click_link, click_button, logout, save_var, load_var


class C_TrialLimitationsPopup(C_TrialLimitationsPopupTemplate):
    def __init__(self, total_count, today_count, **properties):
      # Set Form properties and Data Bindings.
      self.init_components(**properties)

      global user
      user = anvil.users.get_user()
 
      # total_count = 51
      # today_count = 5
      
      # Determine which message to show
      if total_count == 35:
        # Warning at 35 recommendations (15 left in initial batch)
        html_content = self._get_warning_message()

      elif total_count == 50:
        # Daily limit reached
        html_content = self._get_initial_limit_message()

      elif total_count < 50:
        # Default message showing progress
        html_content = self._get_initial_progress_message(total_count)

      elif total_count > 50 and today_count == 0:
        # Default message showing progress
        html_content = self._get_welcome_back_message()

      elif total_count > 50 and today_count < 5:
        # Default message showing progress
        html_content = self._get_daily_progress_message(today_count)

      elif total_count > 50 and today_count >= 5:
        # Daily limit reached
        html_content = self._get_daily_limit_message()
        
      self.html = f"""
      <div class="trial-limit-popup">
        {html_content}
      </div>
      """

      # Expose close_alert method to JavaScript
      anvil.js.window.closeAlert = self._js_close_alert

    
    def _get_progress_bar(self, percentage, current, max_value):
      return f"""
        <div class="progress-container">
          <div class="progress-bar">
            <div class="progress-fill" style="width: {max(1, percentage)}%;"></div>
          </div>
          <div class="counter">
            <span>{current}/{max_value} recommendations used</span>
          </div>
        </div>
      """
    
    def _get_warning_message(self):
      return f"""
        <h2>Trial Limit Approaching</h2>
        <p>You've used <strong>35</strong> of your initial 50 recommendations.</p>
        {self._get_progress_bar(percentage=70, current=35, max_value=50)}
        <p>Continue exporing<br>or upgrade for unlimited access!</p>
        <button class="pop-button-disabled" onclick="window.closeAlert()">Continue</button>
        <button class="pop-button-enabled" onclick="window.location.href='https://app.aidar.ai/#settings?section=Subscription'">Upgrade now</button>
      """

    def _get_initial_limit_message(self):
      return f"""
        <h2>Initial Trial Limit Reached</h2>
        <p>You've used all 50 of your initial recommendations.</p>
        {self._get_progress_bar(percentage=100, current=50, max_value=50)}      
        <p>Come back tomorrow for 5 new recommendations<br>or upgrade for unlimited access!</p>
        <button class="pop-button-enabled" onclick="window.location.href='https://app.aidar.ai/#settings?section=Subscription'">Upgrade now</button>
      """

    def _get_initial_progress_message(self, total_count):
      return f"""
      <h2>Your Trial Progress</h2>
      <p>You've used <strong>{total_count}</strong> of your initial 50 recommendations.</p>
      {self._get_progress_bar(percentage=int(total_count / 50 * 100), current=total_count, max_value=50)}
      <p>Continue exporing<br>or upgrade for unlimited access!</p>
        <button class="pop-button-disabled" onclick="window.closeAlert()">Continue</button>
        <button class="pop-button-enabled" onclick="window.location.href='https://app.aidar.ai/#settings?section=Subscription'">Upgrade now</button>
      """

    def _get_welcome_back_message(self):
      return """
        <h2>Welcome back!</h2>
        <p>You've got..</p>
        <p class="big-number">5</p>
        <p>daily recommendations left.</p>
        <button class="pop-button-disabled" onclick="window.closeAlert()">Continue</button>
        <button class="pop-button-enabled" onclick="window.location.href='https://app.aidar.ai/#settings?section=Subscription'">Upgrade now</button>
      """
    
    def _get_daily_progress_message(self, today_count):
      return f"""
        <h2>Your Trial Progress</h2>
        <p>You've used <strong>{today_count}</strong> of your daily 5 recommendations.</p>
        {self._get_progress_bar(percentage=int(today_count / 5 * 100), current=today_count, max_value=5)}
        <p>Continue exporing<br>or upgrade for unlimited access!</p>      
        <button class="pop-button-disabled" onclick="window.closeAlert()">Continue</button>
        <button class="pop-button-enabled" onclick="window.location.href='https://app.aidar.ai/#settings?section=Subscription'">Upgrade now</button>
      """

    def _get_daily_limit_message(self):
      return f"""
        <h2>Daily Trial Limit Reached</h2>
        <p>You've used all 5 of your daily recommendations.</p>
        {self._get_progress_bar(percentage=100, current=5, max_value=5)}
        <p>Come back tomorrow for 5 new recommendations<br>or upgrade for unlimited access!</p>
        <button class="pop-button-enabled" onclick="window.location.href='https://app.aidar.ai/#settings?section=Subscription'">Upgrade now</button>
      """

    def close_alert(self, **event_args):
        """Close the alert dialog from Python."""
        self.raise_event('x-close-alert')
        
    def _js_close_alert(self):
        """Close the alert dialog from JavaScript."""
        self.close_alert()
        return True
