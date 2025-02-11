from ._anvil_designer import C_ShortTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ..nav import click_link, click_button, logout, login_check, save_var, load_var


class C_Short(C_ShortTemplate):
  def __init__(self, i, artist_id, created_date, external_url, name, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    # adding the shorts to the html base
    self.html += f"""
    <div class="masonry-container">
      <div class="masonry-item">
        <div anvil-slot="name-slot-{i}">
          <div anvil-if-slot-empty="name-slot-{i}">{name}</div>
        </div>
        <div anvil-role="feature">
          <p class="label-text">{created_date}</p>
        </div>
        <iframe src="{external_url}/embed/?omitscript=true&hidecaption=true"
          width="400" height="480"
          frameborder="0" scrolling="no"
          allowtransparency="true" allowfullscreen="true">
        </iframe>
      </div>
    """

    link = Link(text=name)
    link.set_event_handler(
      "click", self.create_link_click_handler(artist_id, link)
    )
    self.add_component(link, slot=f"name-slot-{i}")

    self.html += """
    </div>
    """

  
  def create_link_click_handler(self, artist_id, link):
    def handler(**event_args):
      click_link(link, f"artists?artist_id={artist_id}", event_args)

    return handler
