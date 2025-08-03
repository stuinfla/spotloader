import os
import yt_dlp
from typing import Optional
from utils import Utils
import logging

class YouTubeDownloader:
    def __init__(self):
        self.cookie_file = 'youtube_cookie.txt'
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '0',
            }],
            'outtmpl': '%(title)s.%(ext)s',
            'quiet': False,
            'no_warnings': True,
            'logtostderr': False,
            'ignoreerrors': True,
            'cookiefile': os.getenv('YOUTUBE_COOKIE'),
            'retries': 3,
            'socket_timeout': 30
        }

    def download_track(self, search_query: str, output_path: str) -> Optional[str]:
        """Download a track from YouTube"""
        try:
            # Update output template with full path
            self.ydl_opts['outtmpl'] = output_path.replace('.mp3', '.%(ext)s')
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(f"ytsearch:{search_query}", download=True)
                except yt_dlp.utils.DownloadError as e:
                    logging.error(f"yt-dlp download failed for '{search_query}'. Reason: {e}")
                    # Clean up partially downloaded file if it exists
                    if os.path.exists(output_path):
                        try:
                            os.remove(output_path)
                        except OSError as oe:
                            logging.warning(f"Could not remove partial file {output_path}: {oe}")
                    return None
                
                if not info or 'entries' not in info or not info['entries']:
                    raise ValueError(f"No results found for: {search_query}")
                    
                # Verify downloaded file
                mp3_path = output_path.replace('.%(ext)s', '.mp3')
                if not Utils.is_valid_mp3(mp3_path):
                    raise RuntimeError(f"Invalid MP3 file: {mp3_path}")
                    
                return mp3_path
                
        except Exception as e:
            # Clean up failed downloads
            if os.path.exists(output_path):
                os.remove(output_path)
            raise RuntimeError(f"Failed to download {search_query}: {str(e)}")
