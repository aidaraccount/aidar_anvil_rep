from ._anvil_designer import C_TrialLimitationsPopupTemplate
from anvil import *
import stripe.checkout
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import json

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
    if total_count == 0:
      # Initial message when no recommendations used yet
      html_content = self._get_initial_message()
    elif total_count == 40:
      # Warning at 40 recommendations (10 left in initial batch)
      html_content = self._get_warning_message(10, remaining_daily)
    elif total_count >= 50 and today_count == 0:
      # Daily limit info (less than 5 left for today)
      html_content = self._get_daily_info_message(5 - today_count)
    elif total_count >= 50 and today_count >= 5:
      # Daily limit reached
      html_content = self._get_daily_limit_message()
    else:
      # Default message showing progress
      html_content = self._get_progress_message(remaining_total, remaining_daily)

    self.html = f"""
    <div class="trial-limit-popup">
      {html_content}
    </div>
    """

  def _get_progress_bar(self, percentage):
    """Generate HTML for progress bar"""
    return f"""
    <div class="progress-container">
      <div class="progress-bar">
        <div class="progress-fill" style="width: {percentage}%;"></div>
      </div>
      <div class="counter">
        <span>{percentage}% Complete</span>
      </div>
    </div>
    """

  def _get_initial_message(self):
    """
    total_count == 0
    Message shown when user first starts using the trial
    """
    return f"""
    <h2>Welcome to Your Trial!</h2>
    <p>You have <strong>50 recommendations</strong> to start with.</p>
    <p>After that, you'll receive <strong>5 free recommendations per day</strong>.</p>
    {self._get_progress_bar(0)}
    <p>Have fun discovering!</p>
    <button class="action-button" onclick="anvil.call('close_alert', true)">Get Started</button>
    """

  def _get_warning_message(self, remaining_initial, remaining_daily):
    """
    total_count == 40
    Warning shown when user is approaching initial limit
    """
    
    return f"""
      <h2>Trial Limit Approaching</h2>
      <p>You've used <strong>{50 - remaining_initial}</strong> of your initial 50 recommendations.</p>
      <p>Only <strong>{remaining_initial} left</strong> in your initial batch!</p>
      {self._get_progress_bar(int((50 - remaining_initial) / 50 * 100))}
      <div class="warning-message">
          After this, you'll get 5 free recommendations per day.
      </div>
      <button class="action-button" onclick="anvil.call('close_alert', true)">Continue</button>
    """

  def _get_daily_info_message(self, remaining_today):
    """
    total_count >= 50 and today_count == 0
    Warning shown when user is approaching daily limit
    """
    
    return f"""
      <h2>Welcome back!</h2>
      <p>You have <strong>{remaining_today} free {'recommendation' if remaining_today == 1 else 'recommendations'}</strong> left for today.</p>
      <div class="progress-container">
        <div class="progress-bar">
          <div class="progress-fill" style="width: {(5 - remaining_today) / 5 * 100}%;"></div>
        </div>
        <div class="counter">
          <span>{5 - remaining_today}/5 used today</span>
        </div>
      </div>
      <p>After today's limit, you'll get 5 more recommendations tomorrow.</p>
      <button class="action-button" onclick="anvil.call('close_alert', true)">Got it!</button>
    """

  def _get_daily_limit_message(self):
    """
    total_count >= 50 and today_count >= 5
    Message shown when daily limit is reached
    """
    
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

  def _get_progress_message(self, remaining_total, remaining_daily):
    """
    else
    Default message showing progress
    """
    
    return f"""
      <h2>Your Progress</h2>
      <p>You've used <strong>{50 - remaining_total}</strong> of your initial 50 recommendations.</p>
      <p>You have <strong>{remaining_total} left</strong> in your initial batch.</p>
      <p>Daily recommendations: <strong>{remaining_daily} left</strong> for today.</p>
      {self._get_progress_bar(int((50 - remaining_total) / 50 * 100))}
      <button class="action-button" onclick="anvil.call('close_alert', true)">Continue</button>
    """

  def close_alert(self, **event_args):
    self.raise_event("x-close-alert")
