import re
import os
import mutagen
from typing import Optional, Tuple

class Utils:
    @staticmethod
    def extract_spotify_info(url: str) -> Optional[Tuple[str, str]]:
        """Extracts content type and ID from a Spotify URL."""
        # Sanitize URL by removing duplicates from clipboard pastes
        url = url.strip()
        if url.count("https://open.spotify.com") > 1:
            url = "https://open.spotify.com" + url.split("https://open.spotify.com")[-1]

        patterns = {
            'track': r'https?://open.spotify.com/track/([a-zA-Z0-9]+)',
            'album': r'https?://open.spotify.com/album/([a-zA-Z0-9]+)',
            'playlist': r'https?://open.spotify.com/playlist/([a-zA-Z0-9]+)',
            'artist': r'https?://open.spotify.com/artist/([a-zA-Z0-9]+)'
        }
        for content_type, pattern in patterns.items():
            match = re.match(pattern, url)
            if match:
                return content_type, match.group(1)
        return None

    @staticmethod
    def clean_filename(name: str) -> str:
        """Sanitizes a string to be a valid filename."""
        return re.sub(r'[\\/*?:"<>|]',"", name)

    @staticmethod
    def ensure_directory(path: str):
        """Creates a directory if it does not exist."""
        if not os.path.exists(path):
            os.makedirs(path)

    @staticmethod
    def format_track_name(track: dict) -> str:
        """Formats track data into a 'Artist - Title' string."""
        artists = ', '.join(track.get('artists', ['Unknown Artist']))
        title = track.get('name', 'Unknown Title')
        return f"{artists} - {title}"

    @staticmethod
    def is_valid_mp3(file_path: str) -> bool:
        """Checks if a file is a valid, non-empty MP3."""
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            return False
        try:
            audio = mutagen.File(file_path)
            if audio is None:
                return False
            return True
        except Exception:
            return False
