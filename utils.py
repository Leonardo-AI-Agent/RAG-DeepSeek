def save_uploaded_file(uploaded_file, save_path="temp.pdf"):
    """Saves an uploaded PDF file to the specified path."""
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getvalue())
    return save_path
