"""
File Operations Toolkit Documentation
===================================

This file documents the expected input/output formats and edge case behaviors
for all file operation tools in the toolkit.

General Conventions:
- All paths can be absolute or relative
- Paths use forward slashes (/) on all platforms
- Empty strings are treated as invalid input unless specified
- All functions return None on failure unless specified otherwise


@list_files(directory=".")
----------------------------
Input:
    directory (str): Path to directory to list (default: current directory)
Output:
    list: Sorted list of filenames (strings) in directory
Edge Cases:
    - Non-existent directory: Returns empty list
    - File instead of directory: Returns empty list
    - Permission denied: Returns empty list
    - Hidden files: Included in results
    - Symlinks: Followed (returns contents of linked directory)


@read_file(filename)
---------------------
Input:
    filename (str): Path to file to read
Output:
    str: File contents as string
Edge Cases:
    - Non-existent file: Returns empty string
    - Directory instead of file: Returns empty string
    - Permission denied: Returns empty string
    - Binary files: Returns raw bytes as string (may contain non-printable chars)
    - Empty file: Returns empty string
    - Very large files: May hit memory limits (no size limit enforced)


@create_file(filename, content="")
----------------------------------
Input:
    filename (str): Path to new file
    content (str): Initial content (default: empty string)
Output:
    bool: True if successful, False otherwise
Edge Cases:
    - File already exists: Overwrites existing file
    - Directory doesn't exist: Creates parent directories as needed
    - Permission denied: Returns False
    - Invalid path characters: Returns False
    - Empty filename: Returns False


@delete_file(filename)
----------------------
Input:
    filename (str): Path to file to delete
Output:
    bool: True if successful, False otherwise
Edge Cases:
    - Non-existent file: Returns False
    - Directory instead of file: Returns False
    - Permission denied: Returns False
    - File in use: Returns False (Windows)
    - Symlinks: Deletes the symlink, not the target


@list_downloads()
-----------------
Input:
    None
Output:
    list: Sorted list of filenames in downloads folder
Edge Cases:
    - Downloads folder not found: Returns empty list
    - Permission denied: Returns empty list
    - Platform-specific behavior:
        * Windows: %USERPROFILE%\Downloads
        * Mac: ~/Downloads
        * Linux: ~/Downloads or XDG_DOWNLOAD_DIR


@segregate_files(directory=".")
---------------------------------
Input:
    directory (str): Path to directory to process
Output:
    dict: {extension: [filenames]} (extension includes the dot)
Edge Cases:
    - Non-existent directory: Returns empty dict
    - File instead of directory: Returns empty dict
    - Files without extension: Grouped under key ""
    - Hidden files: Included (extension determined normally)
    - Case sensitivity: Extensions treated case-sensitively


@get_file_details(filename)
--------------------------
Input:
    filename (str): Path to file
Output:
    dict: {
        'name': str,
        'size': int (bytes),
        'created': datetime,
        'modified': datetime,
        'accessed': datetime,
        'is_file': bool,
        'is_dir': bool,
        'is_symlink': bool,
        'permissions': str (e.g., 'rw-r--r--')
    }
Edge Cases:
    - Non-existent file: Returns None
    - Permission denied: Returns None
    - Symlinks: Returns details about the symlink itself


@search_by_name(name, root_dir='.')
----------------------------------
Input:
    name (str): Filename to search for (supports * and ? wildcards)
    root_dir (str): Directory to start search from
Output:
    list: Full paths of matching files
Edge Cases:
    - No matches: Returns empty list
    - Permission denied: Skips inaccessible directories
    - Circular symlinks: Handled gracefully (no infinite loops)
    - Case sensitivity: Platform-dependent behavior


@open_application(app_name)
--------------------------
Input:
    app_name (str): Name of application to launch
Output:
    bool: True if successful, False otherwise
Edge Cases:
    - App not found: Returns False
    - App already running: Behavior depends on OS (may open new instance)
    - Permission denied: Returns False
    - Platform-specific behavior:
        * Windows: Uses start command
        * Mac: Uses open command
        * Linux: Uses xdg-open or available desktop launcher


@get_system_stats()
-------------------
Input:
    None
Output:
    dict: {
        'cpu': float (percentage),
        'ram': {
            'total': int (bytes),
            'used': int (bytes),
            'free': int (bytes)
        },
        'disk': {
            'total': int (bytes),
            'used': int (bytes),
            'free': int (bytes)
        }
    }
Edge Cases:
    - Permission denied: Returns partial data where possible
    - Platform-specific behavior: Some stats may not be available
    - Virtual environments: May show container stats instead of host


@kill_process(process_name)
--------------------------
Input:
    process_name (str): Name of process to terminate
Output:
    bool: True if successful, False otherwise
Edge Cases:
    - Process not found: Returns False
    - Permission denied: Returns False
    - Multiple instances: Terminates all instances
    - System processes: May fail to terminate
    - Platform-specific behavior: Different process name formats


@run_tests(test_file)
---------------------
Input:
    test_file (str): Path to test file to execute
Output:
    dict: {
        'passed': int,
        'failed': int,
        'errors': int,
        'details': list of test results
    }
Edge Cases:
    - Test file not found: Returns {'passed': 0, 'failed': 0, 'errors': 1, ...}
    - Syntax errors: Returns error details
    - Permission denied: Returns error details
    - Test dependencies missing: Returns error details
"""