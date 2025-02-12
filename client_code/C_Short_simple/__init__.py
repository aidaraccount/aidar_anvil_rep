from ._anvil_designer import C_Short_simpleTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ..nav import click_link


class C_Short_simple(C_Short_simpleTemplate):
  def __init__(self, data, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.html += f"""
    <div class="masonry-item">
      <div anvil-slot="name-slot">
        <div anvil-if-slot-empty="name-slot">{data["name"]}</div>
      </div>
      <div anvil-role="feature">
        <p class="label-text">{data["created_date"]}</p>
      </div>
      <iframe src="{data["external_url"]}/embed/?omitscript=true&hidecaption=true"
        width="400" height="480"
        frameborder="0" scrolling="no"
        allowtransparency="true" allowfullscreen="true">
      </iframe>
    </div>
    """

    link = Link(text=data["name"])
    link.set_event_handler(
      "click", self.create_link_click_handler(data["artist_id"], link)
    )
    self.add_component(link, slot="name-slot")

  
  def create_link_click_handler(self, artist_id, link):
    def handler(**event_args):
      click_link(link, f"artists?artist_id={artist_id}", event_args)

    return handler