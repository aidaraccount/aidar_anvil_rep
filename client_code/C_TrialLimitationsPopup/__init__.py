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
      
      # Calculate remaining recommendations
      remaining_daily = max(0, 5 - today_count)
      remaining_total = max(0, 50 - total_count)
      
      # Determine which message to show
      if total_count == 30:
        # Warning at 30 recommendations (10 left in initial batch)
        html_content = self._get_warning_message(10, remaining_daily)
      elif total_count >= 50 and today_count >= 5:
        # Daily limit reached
        html_content = self._get_daily_limit_message()
      elif total_count >= 50 and today_count > 0:
        # Daily limit warning (less than 5 left for today)
        html_content = self._get_daily_warning_message(5 - today_count)
      else:
        # Default message showing progress
        html_content = self._get_progress_message(remaining_total, remaining_daily)
      
      self.html = f"""
      <div class="trial-limit-popup">
        {html_content}
      </div>
      """
    
    def _get_progress_bar(self, percentage, current, max_value):
      """Generate HTML for progress bar"""
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
    
    def _get_warning_message(self, remaining_initial, remaining_daily):
      """Warning shown when user is approaching initial limit"""
      percentage = int((50 - remaining_initial) / 50 * 100)
      return f"""
      <h2>Trial Limit Approaching</h2>
      <p>You've used <strong>{50 - remaining_initial}</strong> of your initial 50 recommendations.</p>
      <p>Only <strong>{remaining_initial} left</strong> in your initial batch!</p>
      {self._get_progress_bar(percentage, 50 - remaining_initial, 50)}
      <div class="warning-message">
        After this, you'll get 5 free recommendations per day.
      </div>
      <button class="action-button" onclick="anvil.call('close_alert', true)">Continue</button>
      """
    
    def _get_daily_limit_message(self):
      """Message shown when daily limit is reached"""
      return """
      <h2>Daily Limit Reached</h2>
      <p>You've used all 5 of your daily recommendations.</p>
      <div class="progress-container">
          <div class="progress-bar">
            <div class="progress-fill" style="width: 100%; background: #ff6b35;"></div>
          </div>
          <div class="counter">
            <span>5/5 used today</span>
          </div>
      </div>
      <p>Come back tomorrow for more recommendations or upgrade for unlimited access!</p>
      <div class="upgrade-prompt">
        <p>Want unlimited recommendations?</p>
        <button class="action-button" style="background: #6a11cb;" onclick="anvil.call('upgrade_account')">Upgrade Now</button>
      </div>
      """
    
    def _get_daily_warning_message(self, remaining_today):
      """Warning shown when user is approaching daily limit"""
      percentage = int((5 - remaining_today) / 5 * 100)
      return f"""
      <h2>Daily Limit Approaching</h2>
      <p>You have <strong>{remaining_today} free {'recommendation' if remaining_today == 1 else 'recommendations'}</strong> left for today.</p>
      <div class="progress-container">
        <div class="progress-bar">
          <div class="progress-fill" style="width: {percentage}%;"></div>
        </div>
        <div class="counter">
          <span>{5 - remaining_today}/5 used today</span>
        </div>
      </div>
      <p>After today's limit, you'll get 5 more recommendations tomorrow.</p>
      <button class="action-button" onclick="anvil.call('close_alert', true)">Got it!</button>
      """
    
    def _get_progress_message(self, remaining_total, remaining_daily):
      """Default message showing progress"""
      percentage = int((50 - remaining_total) / 50 * 100)
      return f"""
      <h2>Your Trial Progress</h2>
      <p>You've used <strong>{50 - remaining_total}</strong> of your initial 50 recommendations.</p>
      <p>Daily recommendations: <strong>{remaining_daily} left</strong> for today.</p>
      {self._get_progress_bar(percentage, 50 - remaining_total, 50)}
      <button class="action-button" onclick="anvil.call('close_alert', true)">Continue</button>
      """

    def close_alert(self, **event_args):
      self.raise_event("x-close-alert")
