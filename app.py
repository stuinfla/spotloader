import os
import logging
from dotenv import load_dotenv
from spotify import SpotifyClient
from youtube import YouTubeDownloader
from utils import Utils
from colorama import Fore, Style

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('spotify_loader.log'),
        logging.StreamHandler()
    ]
)

class SpotifyLoader:
    def __init__(self):
        load_dotenv()
        self.spotify_client = SpotifyClient()
        self.youtube_downloader = YouTubeDownloader()
        self.logger = logging

    def process_url(self, spotify_url: str) -> str:
        """Processes a Spotify URL and returns the path to the downloaded content."""
        download_path = None
        try:
            content_type, content_id = Utils.get_spotify_content_type_and_id(spotify_url)
            if not content_type:
                self.logger.error("Invalid or unsupported Spotify URL.")
                return None

            if content_type == 'track':
                track_info = self.spotify_client.get_track_info(content_id)
                download_path = self._process_track(track_info)
            elif content_type == 'album':
                album_info = self.spotify_client.get_album_info(content_id)
                download_path = self._process_album(album_info)
            elif content_type == 'playlist':
                playlist_info = self.spotify_client.get_playlist_info(content_id)
                download_path = self._process_playlist(playlist_info)
            elif content_type == 'artist':
                artist_info = self.spotify_client.get_artist_info(content_id)
                download_path = self._process_artist(artist_info)
            
            return download_path

        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            return None

    def _process_track(self, track_info):
        artist_name = Utils.clean_filename(track_info['artists'][0]['name'])
        download_dir = os.path.join('downloads', artist_name)
        self._download_track_with_metadata(track_info, download_dir)
        return download_dir

    def _process_album(self, album_info):
        album_name = Utils.clean_filename(album_info['name'])
        artist_name = Utils.clean_filename(album_info['artists'][0]['name'])
        download_dir = os.path.join('downloads', f"{artist_name} - {album_name}")
        
        self.logger.info(f"Processing album: {album_name} by {artist_name}")
        tracks = self.spotify_client.get_album_tracks(album_info['id'])
        for i, track in enumerate(tracks):
            self._download_track_with_metadata(track, download_dir, i, len(tracks))
        return download_dir

    def _process_playlist(self, playlist_info):
        playlist_name = Utils.clean_filename(playlist_info['name'])
        download_dir = os.path.join('downloads', playlist_name)

        self.logger.info(f"Processing playlist: {playlist_name}")
        tracks = self.spotify_client.get_playlist_tracks(playlist_info['id'])
        for i, track in enumerate(tracks):
            if track and track.get('track'):
                self._download_track_with_metadata(track['track'], download_dir, i, len(tracks))
        return download_dir

    def _process_artist(self, artist_info):
        artist_name = Utils.clean_filename(artist_info['name'])
        download_dir = os.path.join('downloads', artist_name)

        self.logger.info(f"Processing artist: {artist_name}")
        albums = self.spotify_client.get_artist_albums(artist_info['id'])
        for album in albums:
            album_name = Utils.clean_filename(album['name'])
            album_dir = os.path.join(download_dir, album_name)
            tracks = self.spotify_client.get_album_tracks(album['id'])
            self.logger.info(f"-- Processing album: {album_name}")
            for i, track in enumerate(tracks):
                self._download_track_with_metadata(track, album_dir, i, len(tracks))
        return download_dir

    def _download_track_with_metadata(self, track_info, download_dir, index=0, total=1):
        if not track_info or not track_info.get('name'):
            self.logger.warning("Skipping invalid track info.")
            return

        track_name = Utils.clean_filename(track_info['name'])
        artist_name = Utils.clean_filename(track_info['artists'][0]['name'])
        search_query = f"{artist_name} - {track_name}"

        Utils.create_directory(download_dir)
        file_path = os.path.join(download_dir, f"{search_query}.mp3")

        if os.path.exists(file_path) and Utils.is_valid_mp3(file_path):
            self.logger.info(f"'{track_name}' already exists. Skipping.")
            return

        self.logger.info(f"Downloading {index + 1} of {total}: {track_name}")

        try:
            success = self.youtube_downloader.download_track(search_query, file_path)
            if success:
                self.logger.info(f"✔ Successfully downloaded: {track_name}.mp3")
            else:
                raise Exception(f"Download failed, no valid MP3 created for: {file_path}")
        except Exception as e:
            self.logger.error(f"Error processing track {track_name}: {e}")


def print_colored(message, color):
    print(f"{color}{message}{Style.RESET_ALL}")


if __name__ == "__main__":
    loader = SpotifyLoader()
    spotify_url = input("Enter Spotify URL (Playlist, Album, Track, or Artist): ")
    if spotify_url:
        download_path = loader.process_url(spotify_url)
        if download_path:
            print_colored(f"Downloaded content saved to: {download_path}", Fore.CYAN)
