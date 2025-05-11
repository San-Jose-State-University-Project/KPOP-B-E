import lyricsgenius
import os
from dotenv import load_dotenv

load_dotenv()

class GeniusAdapter:
    def __init__(self):
        token = os.getenv("GENIUS_ACCESS_TOKEN")
        self.genius = lyricsgenius.Genius(token)

