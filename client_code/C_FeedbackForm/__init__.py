from ._anvil_designer import C_FeedbackFormTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from anvil_extras import routing
from ..nav import load_var


class C_FeedbackForm(C_FeedbackFormTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    
    
  def submit_feedback_click(self, **event_args):
    user = anvil.users.get_user()
    model_id = load_var("model_id")
    model_id_view = load_var("model_id_view")
    watchlist_id = load_var("watchlist_id")
    
    # add_feedback(user_id: int, rating: int | None, feedback: str, details: str)
    anvil.server.call('add_feedback',
                      user_id=user["user_id"],
                      rating=None,  # cannot access the notes
                      feedback='my feedback',  # cannot access the test box
                      details=f"url={routing.get_url_components()[0]}, model_id={model_id}, model_id_view={model_id_view}, watchlist_id={watchlist_id}"
    )
    
    self.raise_event("x-close-alert")
    