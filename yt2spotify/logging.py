import google.cloud.logging
import logging
import os

# Only initialize Google Cloud Logging if we're running in Cloud Run
if os.getenv('K_SERVICE'):  # This environment variable is set in Cloud Run
    client = google.cloud.logging.Client()
    client.setup_logging()

# Set up basic logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def get_gcp_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
