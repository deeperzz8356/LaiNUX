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

def _file_detail_for_path(path):
    """Build a metadata dictionary for one path."""
    s = path.stat()
    return {
        "name": path.name,
        "abspath": str(path.absolute()),
        "size": s.st_size,
        "created": datetime.datetime.fromtimestamp(s.st_ctime).isoformat(),
        "modified": datetime.datetime.fromtimestamp(s.st_mtime).isoformat(),
        "is_dir": path.is_dir()
    }


def get_file_details(filename=None, file_paths=None):
    """Returns metadata for one file or a list of files."""
    try:
        if file_paths is not None:
            if isinstance(file_paths, str):
                file_paths = [file_paths]
            if not isinstance(file_paths, (list, tuple)):
                return "Error: file_paths must be a list of file paths."

            details = []
            for file_path in file_paths:
                path = Path(file_path)
                if not path.exists():
                    details.append({"path": str(file_path), "error": "not found"})
                    continue
                details.append(_file_detail_for_path(path))
            return details

        if not filename:
            return "Error: Provide either filename or file_paths."

        path = Path(filename)
        if not path.exists():
            return f"Error: File '{filename}' not found."

        return _file_detail_for_path(path)
    except Exception as e:
        return f"Error getting details: {str(e)}"

def get_drive_properties():
    """Returns basic disk usage for the current drive."""
    try:
        total, used, free = shutil.disk_usage(".")
        return {
            "total_gb": total // (2**30),
            "used_gb": used // (2**30),
            "free_gb": free // (2**30)
        }
    except Exception as e:
        return f"Error getting drive properties: {str(e)}"

def parse_robust_response(response_text):
    """Utility to clean and parse unconventional LLM responses for the Executor Node."""
    try:
        if "```" in response_text:
            return response_text.split("```")[1].strip("json\n ")
        return response_text.strip()
    except:
        return response_text


def zip_directory_to_file(source_dir, output_zip_path, include_hidden=False, compression_level=6):
    """
    Creates a ZIP archive of a directory and its contents purely in Python without system commands.

    Args:
        source_dir (str): Path to the directory to be zipped.
        output_zip_path (str): Path where the ZIP file will be created.
        include_hidden (bool): Whether to include hidden files (starting with '.'). Default False.
        compression_level (int): ZIP compression level (0-9). Default 6.

    Returns:
        str: Success message with file details or error message.

    Raises:
        ValueError: If source directory doesn't exist or output path is invalid.
        OSError: If file operations fail.
    """
    import io
    import zipfile
    from pathlib import Path

    try:
        source_path = Path(source_dir).resolve()
        if not source_path.exists():
            raise ValueError(f"Source directory does not exist: {source_dir}")
        if not source_path.is_dir():
            raise ValueError(f"Source path is not a directory: {source_dir}")

        output_path = Path(output_zip_path).resolve()
        if output_path.exists() and not output_path.is_file():
            raise ValueError(f"Output path exists and is not a file: {output_zip_path}")

        # Create parent directories if they don't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=compression_level) as zipf:
            for item in source_path.rglob('*'):
                if not include_hidden and item.name.startswith('.'):
                    continue

                if item.is_file():
                    arcname = str(item.relative_to(source_path))
                    zipf.write(item, arcname)

        # Verify the zip file was created
        if not output_path.exists():
            raise OSError("ZIP file was not created")

        file_size = output_path.stat().st_size
        return f"Successfully created ZIP archive at {output_zip_path} ({file_size} bytes)"

    except zipfile.BadZipFile as e:
        return f"Failed to create valid ZIP file: {str(e)}"
    except PermissionError as e:
        return f"Permission denied during ZIP creation: {str(e)}"
    except Exception as e:
        return f"Error creating ZIP archive: {str(e)}"


def capture_screenshot(output_path=None):
    """
    Captures a screenshot of the entire screen with automatic timestamp generation and dependency checks.

    This function handles the capture of the screen using PyAutoGUI (with fallback to pyscreeze)
    and saves the screenshot to the specified path with a timestamp. If no output path is provided,
    it generates a default path in the current directory with a timestamp.

    Args:
        output_path (str, optional): Path where the screenshot will be saved. If None, a default
                                    path with timestamp will be generated.

    Returns:
        str: Path to the saved screenshot if successful, or an error message if the capture fails.

    Raises:
        RuntimeError: If neither PyAutoGUI nor pyscreeze is available for screenshot capture.
    """
    try:
        import io
        import datetime
        from pathlib import Path

        # Try to import PyAutoGUI or pyscreeze
        try:
            import pyautogui
        except ImportError:
            try:
                import pyscreeze
                import pyautogui
            except ImportError:
                raise RuntimeError("Neither PyAutoGUI nor pyscreeze is available. Please install one of them.")

        # Generate timestamp and default path if none provided
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        if output_path is None:
            output_path = Path(f"screenshot_{timestamp}.png")

        # Ensure the output directory exists
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Capture the screenshot
        screenshot = pyautogui.screenshot()

        # Save the screenshot
        screenshot.save(output_path)

        return str(output_path.absolute())

    except Exception as e:
        return f"Error capturing screenshot: {str(e)}"


def verify_file_exists(filename):
    """
    Atomically verifies if a file exists and creates it with empty content if it doesn't.
    This operation is performed in a single atomic check-and-create operation to prevent race conditions.

    Args:
        filename (str): Path to the file to verify/create.

    Returns:
        str: Success message with file path if file exists or was created, or error message if operation fails.
    """
    try:
        path = Path(filename)
        if path.exists():
            return f"File {filename} already exists."

        with open(filename, 'w', encoding='utf-8') as f:
            pass  # Create empty file

        return f"File {filename} created successfully."
    except Exception as e:
        return f"Error verifying/creating file: {str(e)}"
