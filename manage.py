import os
import subprocess
import sys

def main():
    """
    The definitive control script for launching the application.
    It reads the PORT from the environment, provides a sensible default,
    and launches Gunicorn with the correct parameters.
    This removes all ambiguity and reliance on shell variable expansion.
    """
    # Get the port from the environment variable, defaulting to 5001 if not set.
    port = os.environ.get('PORT', '5001')
    
    print(f"INFO: Starting server on port {port}")
    
    # Construct the Gunicorn command.
    # We use sys.executable to ensure we're using the same Python environment.
    command = [
        sys.executable, 
        '-m',
        'gunicorn',
        '--bind',
        f'0.0.0.0:{port}',
        'web_app:app'
    ]
    
    try:
        # Execute the command, replacing the current process.
        # This is standard practice for this type of management script.
        os.execvp(command[0], command)
    except FileNotFoundError:
        print("ERROR: 'gunicorn' not found. Make sure it's installed in your environment.", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
