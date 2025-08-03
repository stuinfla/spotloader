from flask import Flask, render_template, request, jsonify, send_from_directory
import threading
import os
import uuid
import zipfile
import shutil
import logging
from app import SpotifyLoader

# --- Standard Logging Setup ---
# Log to console (stdout), which is standard for cloud platforms like Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logging.info("Application starting up...")

app = Flask(__name__)

# --- In-memory Job Store ---
jobs = {}

# --- Directory Setup ---
DOWNLOADS_DIR = 'downloads'
ZIPS_DIR = 'zips'

try:
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    os.makedirs(ZIPS_DIR, exist_ok=True)
    logging.info("Downloads and zips directories ensured.")
except Exception as e:
    logging.critical(f"CRITICAL: Could not create directories: {e}")

# --- Background Worker ---
def download_worker(job_id, spotify_url):
    """The background worker function that handles the download process."""
    try:
        jobs[job_id]['status'] = 'Initializing...'
        logging.info(f"Job {job_id}: Initializing SpotifyLoader (lazy initialization)." )
        # LAZY INITIALIZATION: Create loader inside the thread.
        # This prevents a faulty Spotify setup from crashing the whole web server on startup.
        loader = SpotifyLoader()
        logging.info(f"Job {job_id}: SpotifyLoader initialized successfully.")

        class JobLogger:
            def info(self, msg):
                if msg.startswith('Downloading'):
                    jobs[job_id]['status'] = msg
                logging.info(f"Job {job_id}: {msg}")
            def error(self, msg):
                jobs[job_id]['status'] = f'Error: {msg}'
                logging.error(f"Job {job_id}: {msg}")

        loader.logger = JobLogger()

        download_path = loader.process_url(spotify_url)

        if not download_path or not os.path.exists(download_path):
            raise Exception("Download failed or returned no path.")

        jobs[job_id]['status'] = 'Zipping files...'
        zip_filename = f"{os.path.basename(download_path)}.zip"
        zip_path = os.path.join(ZIPS_DIR, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(download_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, download_path)
                    zipf.write(file_path, arcname)

        shutil.rmtree(download_path)

        jobs[job_id]['state'] = 'SUCCESS'
        jobs[job_id]['status'] = 'Download complete!'
        jobs[job_id]['zip_path'] = f'/downloads/{zip_filename}'
        jobs[job_id]['message'] = f'Successfully downloaded and zipped {os.path.basename(download_path)}.'

    except Exception as e:
        logging.error(f"Job {job_id} CRASHED: {e}", exc_info=True)
        jobs[job_id]['state'] = 'FAILURE'
        jobs[job_id]['status'] = f'An error occurred: {e}'
        logging.critical(f"Job {job_id} failed with exception:", exc_info=True)

# --- API Endpoints ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Simple health check endpoint for Railway."""
    return "OK", 200

@app.route('/download', methods=['POST'])
def download():
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
    job = jobs.get(job_id)
    if not job:
        return jsonify({'state': 'FAILURE', 'status': 'Job not found'}), 404
    return jsonify(job)

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(ZIPS_DIR, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
