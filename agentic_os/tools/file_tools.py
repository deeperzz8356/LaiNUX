import os
import shutil
import datetime
from pathlib import Path
from ..utils.logger import logger

def list_files(directory="."):
    """Lists all files in a directory with size and modification date."""
    try:
        path = Path(directory)
        files = []
        for item in path.iterdir():
            s = item.stat()
            files.append({
                "name": item.name,
                "type": "dir" if item.is_dir() else "file",
                "size": s.st_size,
                "modified": datetime.datetime.fromtimestamp(s.st_mtime).isoformat()
            })
        return files
    except Exception as e:
        return f"Error listing files: {str(e)}"

def read_file(filename):
    """Reads the content of a file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def create_file(filename, content=""):
    """Creates a new file with the given content."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"File {filename} created successfully."
    except Exception as e:
        return f"Error creating file: {str(e)}"

def delete_file(filename):
    """Permanently deletes a file (Standard Delete)."""
    try:
        if os.path.exists(filename):
            os.remove(filename)
            return f"File {filename} deleted."
        return "File not found."
    except Exception as e:
        return f"Error deleting: {str(e)}"

def secure_delete(file_path):
    """Securely shreds a file by overwriting with random data before deletion."""
    try:
        if not os.path.isfile(file_path):
            return "Error: Path is not a file."
        
        file_size = os.path.getsize(file_path)
        with open(file_path, "ba+", buffering=0) as f:
            # Multi-pass overwrite
            for _ in range(3):
                f.seek(0)
                f.write(os.urandom(file_size))
        os.remove(file_path)
        return f"Success: {file_path} has been SHREDDED and deleted."
    except Exception as e:
        return f"Secure Delete Failure: {str(e)}"

def search_by_name(name, root_dir='.'):
    """Recursively searches for a file by name."""
    matches = []
    for root, dirs, files in os.walk(root_dir):
        if name in files:
            matches.append(os.path.join(root, name))
    return matches or f"File '{name}' not found."

def list_downloads():
    """Lists files in the system Downloads folder."""
    home = str(Path.home())
    dl_path = os.path.join(home, "Downloads")
    return list_files(dl_path)

def segregate_files(directory="."):
    """Groups files into subfolders by their extension (e.g., .txt -> text/)."""
    try:
        path = Path(directory)
        for item in path.iterdir():
            if item.is_file():
                ext = item.suffix[1:] or "no_extension"
                target_dir = path / ext
                target_dir.mkdir(exist_ok=True)
                shutil.move(str(item), str(target_dir / item.name))
        return "Files segregated successfully."
    except Exception as e:
        return f"Segregation error: {str(e)}"
