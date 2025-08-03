import os
import re
from urllib.parse import urlparse
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from typing import List, Dict


class SpotifyClient:
    def __init__(self):

        self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        self.redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:3001/callback')

        if not all([self.client_id, self.client_secret]):
            raise EnvironmentError("Spotify API credentials are not set in the environment.")

        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope='playlist-read-private',
            cache_path='.spotify_cache'
        ))

    def get_playlist_tracks(self, playlist_id: str) -> List[Dict]:
        """Get all tracks from a Spotify playlist."""
        results = self.sp.playlist_tracks(playlist_id)
        tracks = []
        while results:
            for item in results['items']:
                track = item.get('track')
                if track:
                    tracks.append(self._format_track_data(track))
            if results['next']:
                results = self.sp.next(results)
            else:
                break
        return tracks

    def get_album_tracks(self, album_id: str) -> List[Dict]:
        """Get all tracks from a Spotify album."""
        results = self.sp.album_tracks(album_id)
        tracks = []
        while results:
            for track in results['items']:
                tracks.append(self._format_track_data(track))
            if results['next']:
                results = self.sp.next(results)
            else:
                break
        return tracks

    def get_artist_top_tracks(self, artist_id: str) -> List[Dict]:
        """Get top tracks for a Spotify artist."""
        results = self.sp.artist_top_tracks(artist_id)
        return [self._format_track_data(track) for track in results['tracks']]

    def get_track(self, track_id: str) -> List[Dict]:
        """Get a single track's data."""
        track = self.sp.track(track_id)
        return [self._format_track_data(track)]

    def _format_track_data(self, track: dict) -> dict:
        """Format track data into a consistent dictionary."""
        return {
            'name': track.get('name'),
            'artists': [artist.get('name') for artist in track.get('artists', [])],
            'album': track.get('album', {}).get('name') if 'album' in track else 'Unknown Album',
            'id': track.get('id')
        }