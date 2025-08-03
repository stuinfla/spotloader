# Spotify Music Downloader

This application takes a Spotify URL as input, retrieves metadata for the specified tracks, playlist, album, or artist, and downloads them as high-quality MP3 files.

## Features
- Downloads entire Spotify playlists
- Creates organized folder structure
- High-quality MP3 downloads
- Duplicate checking
- Robust error handling

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables in `.env` file:
```bash
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_ACCESS_TOKEN=your_access_token
SPOTIFY_REFRESH_TOKEN=your_refresh_token
YOUTUBE_COOKIE=your_youtube_cookie
DOWNLOAD_DIR=downloads
```

## Usage

1.  **Installation:**

    ```bash
    pip install -r requirements.txt
    ```

2.  **Setup:** Create a `.env` file in the root directory and add your Spotify and YouTube credentials:

    ```
    SPOTIFY_CLIENT_ID=your_client_id
    SPOTIFY_CLIENT_SECRET=your_client_secret
    SPOTIFY_ACCESS_TOKEN=your_access_token  
    SPOTIFY_REFRESH_TOKEN=your_refresh_token
    YOUTUBE_COOKIE=your_youtube_music_cookie
    DOWNLOAD_DIR="./downloads"
    ```

3. **Run:** Execute the application, providing the Spotify URL:

```bash
python3 app.py "https://open.spotify.com/playlist/..." # on macOS
```
    or 

    ```bash
    python3 app.py "https://open.spotify.com/track/..." # on macOS
    ```

    or 

    ```bash
    python3 app.py "https://open.spotify.com/album/..." # on macOS
    ```

    or

    ```bash
    python3 app.py "https://open.spotify.com/artist/..." # on macOS
    ```



## Error Handling

The application will:
- Log all errors to `error.log`
- Continue downloading even if some tracks fail
- Retry failed downloads up to 3 times
- Skip corrupted downloads
- Validate all downloaded files

## Requirements

- Python 3.8+
- Spotify Developer Account
- YouTube account with valid cookie
