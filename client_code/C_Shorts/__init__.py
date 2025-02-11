from ._anvil_designer import C_ShortsTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ..nav import click_link, click_button, logout, login_check, save_var, load_var


class C_Shorts(C_ShortsTemplate):
  def __init__(self, data, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.    
    # print('external_url:', external_url)
    artist_ids = [item["artist_id"] for item in data]
    created_dates = [item["created_date"] for item in data]
    external_urls = [item["external_url"] for item in data]
    names = [item["name"] for item in data]
    print('created_dates:', created_dates[0])
    
    # adding the shorts to the html base    
    self.html += """
    <div class="masonry-container">
    """

    for big_i in range(0, int(min(len(artist_ids), 9) / 3)):
      for small_i in range(0, min(len(artist_ids), 9), 3):
        
        i = small_i + big_i
        print(big_i, small_i, i, external_urls[i])

        # Version A: blockquote
        self.html += f"""
          <div class="masonry-item">
            <div anvil-slot="name-slot-{i}">
              <div anvil-if-slot-empty="name-slot-{i}">{names[i]}</div>
            </div>
            <div anvil-role="feature">
              <p class="label-text">{created_dates[i]}</p>
            </div>
            <blockquote class="instagram-media" data-instgrm-permalink="{external_urls[i]}" data-instgrm-version="14"></blockquote>
          </div>
        """
        
        # # Version B: iframe
        # self.html += f"""
        #   <div class="masonry-item">
        #     <div anvil-slot="name-slot-{i}">
        #       <div anvil-if-slot-empty="name-slot-{i}">{names[i]}</div>
        #     </div>
        #     <div anvil-role="feature">
        #       <p class="label-text">{created_dates[i]}</p>
        #     </div>
        #     <iframe src="{external_urls[i]}/embed/?omitscript=true&hidecaption=true"
        #       width="400" height="480"
        #       frameborder="0" scrolling="no"
        #       allowtransparency="true" allowfullscreen="true">
        #     </iframe>
        #   </div>
        # """
            
        link = Link(
          text=names[i]
        )
        link.set_event_handler('click', self.create_link_click_handler(artist_ids[i], link))      
        self.add_component(link, slot=f"name-slot-{i}")
      
    # Version A: blockquote
    self.html += """
    </div>
    <script async src="https://www.instagram.com/embed.js"></script>
    """
    
    # # Version B: iframe
    # self.html += """
    # </div>
    # """
  
  def create_link_click_handler(self, artist_id, link):
    def handler(**event_args):
      click_link(link, f'artists?artist_id={artist_id}', event_args)
    return handler
