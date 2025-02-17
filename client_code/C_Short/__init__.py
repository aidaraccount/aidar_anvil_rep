from ._anvil_designer import C_ShortTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ..nav import click_link, click_button


class C_Short(C_ShortTemplate):
  def __init__(self, data, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # print(data["artist_id"], data["watchlist_id"])
    
    views = '-' if data["views"] is None else f'{data["views"]:,}'
    likes = '-' if data["likes"] is None else f'{data["likes"]:,}'
    comments = '-' if data["comments"] is None else f'{data["comments"]:,}'
    
    # Any code you write here will run before the form opens.
    self.html = f"""
    <div class="masonry-item">
      <div anvil-role="social-name" class="social-name" anvil-slot="name-slot">
        <div anvil-if-slot-empty="name-slot">{data["name"]}</div>
        <div anvil-role="social-wl-button" class="social-wl-button" anvil-slot="wl-button-slot">
          <div anvil-if-slot-empty="wl-button-slot">{data["watchlist_id"]}</div>
        </div>
      </div>
      <p anvil-role="social-date" class="label-text social-date">{data["created_datetime"]}</p>
      <iframe src="{data["external_url"]}/embed/?omitscript=true&hidecaption=true"
        width="400"
        frameborder="0" scrolling="no"
        allowtransparency="true" allowfullscreen="true">
      </iframe>
      <div anvil-role="social-stats" class="social-stats">
        <p class="label-text"><i class="fas fa-bullhorn"></i> {views}</p>
        <p class="label-text"><i class="fas fa-heart"></i> {likes}</p>
        <p class="label-text"><i class="fas fa-comment"></i> {comments}</p>
      </div>
      <p anvil-role="social-desc" class="label-text social-desc">{data["description"]}</p>
    </div>
    """

    link = Link(text=data["name"])
    link.set_event_handler(
      "click", self.create_link_click_handler(data["artist_id"], link)
    )
    self.add_component(link, slot="name-slot")

    button = Button(icon='fa:address-card-o', role=['icon-button-disabled-small'])
    button.set_event_handler(
      "click", self.create_button_click_handler(data["artist_id"], data["watchlist_id"])
    )
    self.add_component(button, slot="wl-button-slot")

  
  def create_link_click_handler(self, artist_id, link):
    def handler(**event_args):
      click_link(link, f"artists?artist_id={artist_id}", event_args)
    return handler

  def create_button_click_handler(self, artist_id, watchlist_id, **event_args):
    def handler(**event_args):
      click_button(f'watchlist_details?watchlist_id={watchlist_id}&artist_id={artist_id}', event_args)
    return handler