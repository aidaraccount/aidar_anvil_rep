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

    # Prepare description with expand/collapse functionality
    description_html = self.format_text(data.get("description", ""))
    
    # Any code you write here will run before the form opens.
    js_code = """
      // JavaScript to handle the expand/collapse functionality
      function toggleText(id) {
        const shortText = document.getElementById('short-' + id);
        const fullText = document.getElementById('full-' + id);
        const link = document.getElementById('toggle-' + id);
        
        if (shortText.style.display === 'none') {
          shortText.style.display = 'inline';
          fullText.style.display = 'none';
          link.textContent = 'show more';
        } else {
          shortText.style.display = 'none';
          fullText.style.display = 'inline';
          link.textContent = 'show less';
        }
      }
    """
    
    # Add CSS for masonry layout
    css_code = """
      .masonry-container {
        break-inside: avoid;
        margin-bottom: 10px;
        width: 100%;
      }
      
      .masonry-item {
        display: block;
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        overflow: hidden;
        margin-bottom: 10px;
        padding: 16px;
        width: 100%;
      }
    """
    
    self.html = f"""
    <style>
    {css_code}
    </style>
    <div class="masonry-container">
      <div class="masonry-item">
        <div anvil-role="social-name" class="social-name" anvil-slot="name-slot">
          <div anvil-if-slot-empty="name-slot">{data["name"]}</div>
          <div anvil-role="social-wl-button" class="social-wl-button" anvil-slot="wl-button-slot">
            <div anvil-if-slot-empty="wl-button-slot">{data["watchlist_id"]}</div>
          </div>
        </div>
        <p anvil-role="social-date" class="label-text social-date">{data["created_datetime"]}</p>
        <iframe src="{data["external_url"]}/embed/?omitscript=true&hidecaption=true"
          width="100%"
          frameborder="0" scrolling="no"
          allowtransparency="true" allowfullscreen="true">
        </iframe>
        <div anvil-role="social-stats" class="social-stats">
          <p class="label-text"><i class="fas fa-bullhorn"></i> {views}</p>
          <p class="label-text"><i class="fas fa-heart"></i> {likes}</p>
          <p class="label-text"><i class="fas fa-comment"></i> {comments}</p>
        </div>
        <div anvil-role="social-desc" class="social-desc">
          {description_html}
        </div>
      </div>
    </div>
    <script>
    {js_code}
    </script>
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
  
  def format_text(self, text):
    """
    Format text with show more/less functionality if it exceeds 200 characters.
    """
    if not text:
      return ""
      
    # Generate unique ID for this text instance
    import uuid
    text_id = str(uuid.uuid4())
    
    if len(text) <= 225:
      # Short text, no need for show more/less
      return f'<p class="text-content">{text}</p>'
    else:
      # Long text, needs truncation and toggle
      short_text = text[:200] + '... '
      
      # Use proper f-string syntax for multi-line strings
      return f'<p class="text-content">' \
             f'<span id="short-{text_id}">{short_text}</span>' \
             f'<span id="full-{text_id}" style="display:none">{text} </span>' \
             f'<a href="javascript:void(0)" id="toggle-{text_id}" ' \
             f'onclick="toggleText(\'{text_id}\')" class="text-toggle">' \
             f'show more</a></p>'