import os
from dotenv import load_dotenv

load_dotenv()

def save_uploaded_file(uploaded_file, save_path):
    """Saves an uploaded file to the specified path."""
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getvalue())
    return save_path
