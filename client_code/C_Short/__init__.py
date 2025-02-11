from ._anvil_designer import C_ShortTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class C_Short(C_ShortTemplate):
  def __init__(self, external_url, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    # print('external_url:', external_url)

    # adding the shorts to the html base
    self.html += """
    <div class="masonry-container">
    """

    for url in external_url[:10]:
      self.html += f"""
        <div class="masonry-item">
          <blockquote class="instagram-media" data-instgrm-permalink="{url}" data-instgrm-version="14"></blockquote>
        </div>
      """
      # self.html += f"""
      # <div class="masonry-item">
      #   <iframe src="{url}/embed/" width="300" height="360" frameborder="0" scrolling="no" allowtransparency="true" allowfullscreen="true"></iframe>
      # </div>
      # """
    
    self.html += """
    </div>
    <script async src="https://www.instagram.com/embed.js"></script>
    """
    