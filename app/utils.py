import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def save_uploaded_file(uploaded_file, save_path: str) -> str:
    """
    Saves an uploaded file to the specified path.

    Args:
        uploaded_file: The file uploaded (Streamlit FileUploader or raw bytes).
        save_path (str): Path where the file should be saved.

    Returns:
        str: Path to the saved file if successful.

    Raises:
        Exception: If the file cannot be saved.
    """
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # Save file
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getvalue())  # Works for Streamlit file uploads

        logging.info(f"File successfully saved: {save_path}")
        return save_path

    except Exception as e:
        logging.error(f"Error saving file {save_path}: {str(e)}")
        raise Exception(f"Failed to save file: {str(e)}")
