import os
import datetime
from pathlib import Path

def get_file_details(filename):
    """Returns size, last modified, and extension for a given file."""
    try:
        stats = os.stat(filename)
        size = stats.st_size
        modified = datetime.datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        ext = os.path.splitext(filename)[1]
        return f"File: {filename} | Size: {size} bytes | Modified: {modified} | Ext: {ext}"
    except Exception as e:
        return f"Error getting details for '{filename}': {str(e)}"

def list_files(directory="."):
    """Lists files in the given directory with details."""
    try:
        files = os.listdir(directory)
        if not files:
            return f"No files found in {directory}."
        
        details = []
        for f in files:
            path = os.path.join(directory, f)
            if os.path.isfile(path):
                details.append(get_file_details(path))
            else:
                details.append(f"[Dir] {f}")
        
        return f"Details of files in {directory}:\n" + "\n".join(details)
    except Exception as e:
        return f"Error listing files: {str(e)}"

def list_downloads():
    """Lists files in the user's Downloads folder (Windows)."""
    try:
        downloads_path = str(Path.home() / "Downloads")
        if not os.path.exists(downloads_path):
            return "Downloads folder not found at expected location."
        
        files = os.listdir(downloads_path)
        # Sort by creation time to find "recent" downloads
        files_with_time = []
        for f in files:
            path = os.path.join(downloads_path, f)
            if os.path.isfile(path):
                files_with_time.append((f, os.path.getmtime(path)))
        
        # Sort by mtime descending (most recent first)
        files_with_time.sort(key=lambda x: x[1], reverse=True)
        top_files = files_with_time[:10]  # Show top 10 recent
        
        result = "Recent Downloads:\n"
        for name, mtime in top_files:
            dt = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
            result += f"- {name} (Modified: {dt})\n"
        
        return result
    except Exception as e:
        return f"Error fetching downloads: {str(e)}"

def segregate_files(directory="."):
    """Groups and segregates files by their extension/type."""
    try:
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        segregated = {}
        
        for f in files:
            ext = os.path.splitext(f)[1].lower() or "no_extension"
            if ext not in segregated:
                segregated[ext] = []
            segregated[ext].append(f)
            
        result = f"Segregated Files in {directory}:\n"
        for ext, names in segregated.items():
            result += f"\n[{ext.upper()} Files]:\n - " + "\n - ".join(names) + "\n"
            
        return result if files else "No files to segregate."
    except Exception as e:
        return f"Error segregating files: {str(e)}"

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

def delete_file(filename):
    """Permanently deletes a file from the disk. Use with caution!"""
    try:
        if os.path.exists(filename):
            os.remove(filename)
            return f"File '{filename}' has been deleted."
        return "File not found."
    except Exception as e:
        return f"Error deleting file: {str(e)}"

def search_by_name(name, root_dir='.'):
    """Finds files matching the name in the given directory and subdirectories."""
    matches = []
    try:
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                if name.lower() in file.lower():
                    matches.append(os.path.join(root, file))
        return f"Found {len(matches)} matches: " + ", ".join(matches[:10]) if matches else "No matches found."
    except Exception as e:
        return f"Error searching: {str(e)}"


import json

def parse_robust_response(input_data):
    """
    Attempts to parse input as JSON. If JSON parsing fails, it gracefully falls back
    to returning the input as plain text or an error state for invalid input types.

    Args:
        input_data (str): The string response to parse.

    Returns:
        dict: A dictionary containing parsing results.
              - If successful JSON parsing: {"type": "json", "content": <parsed_json_object>}
              - If JSON parsing fails (but input is a valid non-empty string): {"type": "text", "content": <original_string>}
              - If input is not a string or is None: {"type": "error", "message": <error_description>}
              - If input is an empty or whitespace-only string: {"type": "text", "content": <original_string>}
    """
    if not isinstance(input_data, str):
        return {"type": "error", "message": "Input must be a string."}

    # Handle empty or whitespace-only strings as plain text directly
    if not input_data.strip():
        return {"type": "text", "content": input_data}

    try:
        parsed_json = json.loads(input_data)
        return {"type": "json", "content": parsed_json}
    except json.JSONDecodeError:
        # JSON parsing failed, fall back to plain text
        return {"type": "text", "content": input_data}
    except Exception as e:
        # Catch any other unexpected errors during parsing (e.g., memory errors for huge strings)
        return {"type": "error", "message": f"An unexpected error occurred during parsing: {str(e)}"}


import shutil
import platform

def get_drive_properties(path="."):
    """
    Queries comprehensive drive properties for the specified path,
    including total capacity, free space, and file system type.
    Drive type information is limited to what's easily available cross-platform
    without resorting to platform-specific low-level APIs or parsing external commands.

    Args:
        path (str): The path to a file or directory on the target drive.
                    Defaults to the current directory ('.'), which queries
                    properties of the drive where the current directory resides.

    Returns:
        dict: A dictionary containing drive properties.
              Keys include: 'total_capacity_bytes', 'used_space_bytes',
              'free_space_bytes', 'total_capacity_gb', 'used_space_gb',
              'free_space_gb', 'file_system_type', 'drive_type', 'error'.
              'file_system_type' and 'drive_type' might be 'Unknown' or
              have specific notes depending on the operating system and
              available information via standard Python libraries.
    """
    properties = {
        "total_capacity_bytes": None,
        "used_space_bytes": None,
        "free_space_bytes": None,
        "total_capacity_gb": None,
        "used_space_gb": None,
        "free_space_gb": None,
        "file_system_type": "Unknown",
        "drive_type": "Unknown (limited cross-platform support via standard libraries)",
        "error": None
    }

    try:
        # Get disk usage (cross-platform using shutil)
        total, used, free = shutil.disk_usage(path)
        properties["total_capacity_bytes"] = total
        properties["used_space_bytes"] = used
        properties["free_space_bytes"] = free
        properties["total_capacity_gb"] = round(total / (1024**3), 2)
        properties["used_space_gb"] = round(used / (1024**3), 2)
        properties["free_space_gb"] = round(free / (1024**3), 2)

        system = platform.system()

        if system in ["Linux", "Darwin"]: # Unix-like systems (Linux, macOS)
            try:
                # os.statvfs provides file system information on Unix-like systems
                # 'os' is already imported in the context.
                statvfs_info = os.statvfs(path)
                # f_fstypename is common but not strictly guaranteed by all os.statvfs implementations
                if hasattr(statvfs_info, 'f_fstypename'):
                    properties["file_system_type"] = statvfs_info.f_fstypename
                else:
                    properties["file_system_type"] = "Unknown (f_fstypename not available via os.statvfs)"
            except Exception:
                properties["file_system_type"] = "Unknown (error getting statvfs info)"
            
            # Drive type (e.g., Fixed, Removable, Network) is not easily determined
            # cross-platform using only standard Python modules without parsing
            # external commands (like `lsblk`, `df`, `diskutil`) or low-level
            # platform-specific APIs. Hence, it remains 'Unknown' here.

        elif system == "Windows":
            # For Windows, getting file system type and drive type without
            # platform-specific APIs (e.g., via ctypes or WMI) is not
            # straightforward with standard high-level Python functions.
            # os.statvfs is not available on Windows.
            properties["file_system_type"] = "Unknown (Windows: requires platform-specific APIs)"
            properties["drive_type"] = "Unknown (Windows: requires platform-specific APIs)"

    except FileNotFoundError:
        properties["error"] = f"Path '{path}' not found."
    except Exception as e:
        properties["error"] = f"Error querying drive properties for '{path}': {str(e)}"

    return properties
