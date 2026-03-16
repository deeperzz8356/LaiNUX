import os

def list_files(directory="."):
    """Lists files in the given directory."""
    try:
        files = os.listdir(directory)
        return f"Files in {directory}: {', '.join(files)}"
    except Exception as e:
        return f"Error listing files: {str(e)}"

def create_file(filename, content=""):
    """Creates a file with the given content."""
    try:
        with open(filename, 'w') as f:
            f.write(content)
        return f"File '{filename}' created successfully."
    except Exception as e:
        return f"Error creating file: {str(e)}"

def read_file(filename):
    """Reads the content of a file."""
    try:
        with open(filename, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"
