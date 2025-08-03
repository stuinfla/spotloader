from flask import Flask, render_template, request, jsonify, send_from_directory
import threading
import os
import uuid
import zipfile
import shutil
import logging
from app import SpotifyLoader

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# In-memory dictionary to track job status and results.
# For a production app, a more persistent solution like Redis would be better.
jobs = {}

DOWNLOADS_DIR = 'downloads'
ZIPS_DIR = 'zips'

# Ensure directories exist
os.makedirs(DOWNLOADS_DIR, exist_ok=True)
os.makedirs(ZIPS_DIR, exist_ok=True)

def download_worker(job_id, spotify_url):
    """The background worker function that handles the download process."""
    try:
        jobs[job_id]['status'] = 'Starting...'
        loader = SpotifyLoader()

        # Define a custom logger to capture progress updates
        class JobLogger:
            def info(self, msg):
                if msg.startswith('Downloading'):
                    jobs[job_id]['status'] = msg
                logging.info(msg)
            def error(self, msg):
                jobs[job_id]['status'] = f'Error: {msg}'
                logging.error(msg)

        loader.logger = JobLogger()

        # The process_url method returns the path to the downloaded content
        download_path = loader.process_url(spotify_url)

        if not download_path or not os.path.exists(download_path):
            raise Exception("Download failed or returned no path.")

        # Create a ZIP file of the downloaded content
        jobs[job_id]['status'] = 'Zipping files...'
        zip_filename = f"{os.path.basename(download_path)}.zip"
        zip_path = os.path.join(ZIPS_DIR, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(download_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, download_path)
                    zipf.write(file_path, arcname)

        # Clean up the original downloaded folder
        shutil.rmtree(download_path)

        jobs[job_id]['state'] = 'SUCCESS'
        jobs[job_id]['status'] = 'Download complete!'
        jobs[job_id]['zip_path'] = f'/downloads/{zip_filename}'
        jobs[job_id]['message'] = f'Successfully downloaded and zipped {os.path.basename(download_path)}.'

    except Exception as e:
        logging.error(f"Job {job_id} failed: {e}")
        jobs[job_id]['state'] = 'FAILURE'
        jobs[job_id]['status'] = f'An error occurred: {e}'

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    """Start a new download job."""
    spotify_url = request.json.get('spotify_url')
    if not spotify_url:
        return jsonify({'error': 'Spotify URL is required'}), 400

    job_id = str(uuid.uuid4())
    jobs[job_id] = {'state': 'PENDING', 'status': 'Queued'}

    thread = threading.Thread(target=download_worker, args=(job_id, spotify_url))
    thread.start()

    return jsonify({'job_id': job_id})

@app.route('/status/<job_id>')
def status(job_id):
    """Check the status of a download job."""
    job = jobs.get(job_id)
    if not job:
        return jsonify({'state': 'FAILURE', 'status': 'Job not found'}), 404
    return jsonify(job)

@app.route('/downloads/<filename>')
def serve_zip(filename):
    """Serve the final ZIP file."""
    return send_from_directory(ZIPS_DIR, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
