document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('download-form');
    const urlInput = document.getElementById('spotify-url');
    const statusContainer = document.getElementById('status-container');
    const statusMessage = document.getElementById('status-message');
    const resultContainer = document.getElementById('result-container');
    const resultMessage = document.getElementById('result-message');
    const downloadLink = document.getElementById('download-link');
    const submitButton = document.getElementById('submit-button');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const spotifyUrl = urlInput.value;

        // Show status and hide form/results
        statusContainer.classList.remove('hidden');
        resultContainer.classList.add('hidden');
        form.classList.add('hidden');
        submitButton.disabled = true;
        statusMessage.textContent = 'Initializing download...';

        try {
            const response = await fetch('/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ spotify_url: spotifyUrl }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'An unknown error occurred.');
            }

            const data = await response.json();
            const jobId = data.job_id;
            statusMessage.textContent = 'Download started. Processing tracks...';

            // Poll for status
            pollStatus(jobId);

        } catch (error) {
            showError(error.message);
        }
    });

    function pollStatus(jobId) {
        const interval = setInterval(async () => {
            try {
                const response = await fetch(`/status/${jobId}`);
                if (!response.ok) {
                    // Stop polling on server error
                    clearInterval(interval);
                    showError('Failed to get status from server.');
                    return;
                }
                const data = await response.json();

                statusMessage.textContent = data.status;

                if (data.state === 'SUCCESS') {
                    clearInterval(interval);
                    showSuccess(data.message, data.zip_path);
                } else if (data.state === 'FAILURE') {
                    clearInterval(interval);
                    showError(data.status);
                }
            } catch (error) {
                clearInterval(interval);
                showError('Error checking status.');
            }
        }, 3000); // Poll every 3 seconds
    }

    function showSuccess(message, zipPath) {
        statusContainer.classList.add('hidden');
        resultContainer.classList.remove('hidden');
        form.classList.remove('hidden');
        submitButton.disabled = false;
        urlInput.value = '';

        resultMessage.textContent = message;
        downloadLink.href = zipPath;
    }

    function showError(message) {
        statusContainer.classList.add('hidden');
        resultContainer.classList.remove('hidden');
        form.classList.remove('hidden');
        submitButton.disabled = false;

        resultContainer.innerHTML = `<h2>Error</h2><p>${message}</p>`;
    }
});
