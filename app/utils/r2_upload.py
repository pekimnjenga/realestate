import boto3, os
import logging
from werkzeug.utils import secure_filename
from urllib.parse import urlparse

#-- Setting up a logger for my Cloudfare's r2 actions
# What r2_logger Your  Tracks
# • 	When a file is uploaded to R2
# • 	When a file is deleted from R2
# • 	If an upload or deletion fails, you’ll see the error
# • 	If a deletion is attempted with a missing or invalid URL, it logs a warning
# Where It Logs
# • 	Console: You see it live while developing
# • 	File (): You have a permanent record for audits, debugging, or monitoring
# Why It’s Smart
# • 	Keeps your image storage transparent and accountable
# • 	Helps you troubleshoot issues like missing
# --- Logger Setup ---
logger = logging.getLogger('r2_logger')
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# File handler
file_handler = logging.FileHandler('r2.log')
file_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Attach handlers (avoid duplicates)
if not logger.handlers:
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

# --- Upload Function ---
def upload_to_r2(file):
    try:
        filename = secure_filename(os.path.basename(file.filename))
        object_key = filename  # Let Cloudflare apply its prefix

        s3 = boto3.client(
            's3',
            endpoint_url=os.environ.get('R2_ENDPOINT'),
            aws_access_key_id=os.environ.get('R2_ACCESS_KEY'),
            aws_secret_access_key=os.environ.get('R2_SECRET_KEY')
        )

        s3.upload_fileobj(file, os.environ.get('R2_BUCKET'), object_key)

        public_base_url = os.environ.get('PUBLIC_BASE_URL')
        public_url = f'{public_base_url}/ilikeitproperties/{filename}' 
        logger.info(f"Uploaded to R2: {public_url}")
        return public_url

    except Exception as e:
        logger.error(f"R2 upload error for {file.filename}: {e}")
        return None


# --- Delete Function ---
def delete_from_r2(public_url):
    """
    Deletes an object from Cloudflare R2 given its public URL.
    Logs success or failure to both console and file.
    """
    if not public_url:
        logger.warning("No URL provided for R2 deletion.")
        return False

    try:
        parsed_url = urlparse(public_url)
        key = parsed_url.path.lstrip('/')

        s3 = boto3.client(
            's3',
            endpoint_url=os.environ.get('R2_ENDPOINT'),
            aws_access_key_id=os.environ.get('R2_ACCESS_KEY'),
            aws_secret_access_key=os.environ.get('R2_SECRET_KEY')
        )

        s3.delete_object(Bucket=os.environ.get('R2_BUCKET'), Key=key)
        logger.info(f"Deleted from R2: {key}")
        return True

    except Exception as e:
        logger.error(f"R2 delete error for {public_url}: {e}")
        return False
    


