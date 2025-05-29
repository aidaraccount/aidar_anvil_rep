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

# Import CSS
from anvil.js.window import document, setInterval

# Add CSS to the document
css = """
.trial-limit-popup {
  background: linear-gradient(to top left, rgb(43, 24, 72) 50%, rgb(134, 59, 59));
  color: white;
  padding: 30px;
  border-radius: 12px;
  margin: 0 auto;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
  text-align: center;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.trial-limit-popup h2 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 24px;
  font-weight: 600;
  color: #fff;
}

.trial-limit-popup p {
  margin: 10px 0;
  line-height: 1.6;
  font-size: 16px;
}

.progress-container {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 15px;
  margin: 20px 0;
}

.progress-bar {
  height: 10px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 5px;
  margin: 10px 0;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #4CAF50;
  border-radius: 5px;
  transition: width 0.5s ease;
  min-width: 1%;
}

.counter {
  display: flex;
  justify-content: space-between;
  margin-top: 5px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.action-button {
  background: #ff6b35;
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 25px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 15px;
  transition: all 0.3s ease;
}

.action-button:hover {
  background: #ff8c5a;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.warning-message {
  color: #ffcc00;
  font-weight: 500;
  margin: 15px 0;
}

.upgrade-prompt {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

@media (max-width: 600px) {
  .trial-limit-popup {
    padding: 20px 15px;
    margin: 0 10px;
  }
  
  .trial-limit-popup h2 {
    font-size: 20px;
  }
  
  .trial-limit-popup p {
    font-size: 14px;
  }
}
"""

# Add the styles to the document
style = document.createElement('style')
style.type = 'text/css'
style.appendChild(document.createTextNode(css))
document.head.appendChild(style)


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
      """Message shown when user first starts using the trial"""
      return f"""
      <h2>🎉 Welcome to Your Trial!</h2>
      <p>You have <strong>50 recommendations</strong> to start with.</p>
      <p>After that, you'll receive <strong>5 free recommendations per day</strong>.</p>
      {self._get_progress_bar(0)}
      <p>Start discovering amazing artists now!</p>
      <button class="action-button" onclick="anvil.call('close_alert', true)">Get Started</button>
      """
  
  def _get_warning_message(self, remaining_initial, remaining_daily):
      """Warning shown when user is approaching initial limit"""
      return f"""
      <h2>⚠️ Trial Limit Approaching</h2>
      <p>You've used <strong>{50 - remaining_initial}</strong> of your initial 50 recommendations.</p>
      <p>Only <strong>{remaining_initial} left</strong> in your initial batch!</p>
      {self._get_progress_bar(int((50 - remaining_initial) / 50 * 100))}
      <div class="warning-message">
          After this, you'll get 5 free recommendations per day.
      </div>
      <button class="action-button" onclick="anvil.call('close_alert', true)">Continue</button>
      """
  
  def _get_daily_limit_message(self):
      """Message shown when daily limit is reached"""
      return """
      <h2>⏳ Daily Limit Reached</h2>
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
      return f"""
      <h2>🔔 Daily Limit Approaching</h2>
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
  
  def _get_progress_message(self, remaining_total, remaining_daily):
      """Default message showing progress"""
      return f"""
      <h2>📊 Your Progress</h2>
      <p>You've used <strong>{50 - remaining_total}</strong> of your initial 50 recommendations.</p>
      <p>You have <strong>{remaining_total} left</strong> in your initial batch.</p>
      <p>Daily recommendations: <strong>{remaining_daily} left</strong> for today.</p>
      {self._get_progress_bar(int((50 - remaining_total) / 50 * 100))}
      <button class="action-button" onclick="anvil.call('close_alert', true)">Continue</button>
      """

  def close_alert(self, **event_args):
    self.raise_event("x-close-alert")
