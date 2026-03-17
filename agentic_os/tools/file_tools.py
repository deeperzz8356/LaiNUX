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


def validate_tool_usage(selected_tool, intended_action, context=None):
    """
    Validates whether the selected tool is appropriate for the intended action by comparing
    the tool's purpose (from its docstring) with the intended action description.

    This helper function helps prevent tool misuse by performing a lightweight semantic check
    before execution. It uses keyword matching and basic NLP techniques (without external
    dependencies) to assess compatibility.

    Args:
        selected_tool (function): The tool function that was selected for execution.
        intended_action (str): A natural language description of what the user wants to accomplish.
        context (dict, optional): Additional context that might help validation (e.g., file paths,
                                 user permissions, or other metadata). Defaults to None.

    Returns:
        dict: A validation result with the following keys:
              - 'is_valid' (bool): True if the tool appears appropriate for the action.
              - 'confidence' (float): A score between 0 and 1 indicating confidence in the match.
              - 'suggestions' (list): Alternative tool names or actions if the match is poor.
              - 'reason' (str): Explanation for the validation result.

    Example:
        >>> validate_tool_usage(list_files, "show me recent files in my downloads")
        {
            'is_valid': False,
            'confidence': 0.3,
            'suggestions': ['list_downloads'],
            'reason': "The tool 'list_files' is for generic directory listing, but the action mentions 'recent downloads'."
        }
    """
    if not callable(selected_tool):
        return {
            'is_valid': False,
            'confidence': 0.0,
            'suggestions': [],
            'reason': "The selected tool is not a callable function."
        }

    tool_doc = selected_tool.__doc__ or ""
    tool_name = selected_tool.__name__
    intended_lower = intended_action.lower()
    validation_result = {
        'is_valid': False,
        'confidence': 0.0,
        'suggestions': [],
        'reason': ""
    }

    # Predefined tool-action mappings for common cases
    tool_action_map = {
        'get_file_details': ['details', 'info', 'size', 'modified', 'extension', 'file info'],
        'list_files': ['list', 'files', 'directory', 'folder', 'show files'],
        'list_downloads': ['downloads', 'recent', 'downloaded', 'download folder'],
        'segregate_files': ['group', 'sort', 'organize', 'segregate', 'by type', 'extension'],
        'create_file': ['create', 'new', 'make', 'write', 'file'],
        'read_file': ['read', 'open', 'view', 'content', 'show content'],
        'delete_file': ['delete', 'remove', 'erase', 'permanent', 'trash'],
        'search_by_name': ['search', 'find', 'name', 'match', 'locate'],
        'parse_robust_response': ['parse', 'json', 'response', 'text', 'data'],
        'get_drive_properties': ['drive', 'space', 'capacity', 'free', 'storage', 'properties']
    }

    # Check if the tool's docstring or name contains any of the intended action keywords
    confidence = 0.0
    matched_keywords = set()

    for keyword in tool_action_map.get(tool_name, []):
        if keyword in intended_lower:
            matched_keywords.add(keyword)
            confidence += 0.1  # Base confidence boost per keyword match

    # Additional confidence boost if the tool's docstring mentions the action
    if any(keyword in tool_doc.lower() for keyword in matched_keywords):
        confidence += 0.2

    # Special cases for common misuses
    if tool_name == 'list_files' and ('downloads' in intended_lower or 'recent' in intended_lower):
        validation_result['suggestions'].append('list_downloads')
        confidence = 0.3  # Low confidence for this common mistake
    elif tool_name == 'list_downloads' and 'downloads' not in intended_lower:
        confidence = min(confidence, 0.5)  # Penalize if "downloads" isn't mentioned
    elif tool_name == 'get_file_details' and ('list' in intended_lower or 'directory' in intended_lower):
        validation_result['suggestions'].append('list_files')
        confidence = 0.2
    elif tool_name == 'segregate_files' and ('list' in intended_lower and 'type' not in intended_lower):
        validation_result['suggestions'].append('list_files')
        confidence = 0.3

    # Determine validity based on confidence threshold
    validation_result['confidence'] = min(confidence, 1.0)
    validation_result['is_valid'] = confidence >= 0.5  # Threshold for "valid"

    if validation_result['is_valid']:
        validation_result['reason'] = f"The tool '{tool_name}' appears appropriate for the action based on keyword matches: {', '.join(matched_keywords)}."
    else:
        # Suggest alternatives based on the intended action
        for tool, keywords in tool_action_map.items():
            if any(keyword in intended_lower for keyword in keywords):
                if tool != tool_name:
                    validation_result['suggestions'].append(tool)

        if validation_result['suggestions']:
            validation_result['reason'] = f"The tool '{tool_name}' may not be the best fit. Consider: {', '.join(validation_result['suggestions'])}."
        else:
            validation_result['reason'] = f"No strong match found for the action with the available tools. Tool '{tool_name}' was selected but may not be appropriate."

    return validation_result


def web_search(query, source="arxiv", max_results=5, timeout=10):
    """
    Fetches recent articles/papers from academic databases or news aggregators based on the query.
    Supports multiple sources with built-in JSON/HTML parsing and error resilience.

    Args:
        query (str): Search term or phrase to look up.
        source (str): Source to search from. Options: 'arxiv', 'google_scholar', 'news' (default: 'arxiv').
        max_results (int): Maximum number of results to return (default: 5).
        timeout (int): Timeout in seconds for the HTTP request (default: 10).

    Returns:
        dict: A structured result containing:
            - 'status': 'success' or 'error'
            - 'source': The source searched
            - 'results': List of dictionaries with article details (title, link, summary, date)
            - 'error': Error message if applicable
            - 'timestamp': ISO format timestamp of the search

    Supported Sources:
        - 'arxiv': Fetches preprints from arXiv.org (physics, math, CS, etc.)
        - 'google_scholar': Fetches academic papers (via unofficial API)
        - 'news': Fetches recent news articles (via NewsAPI)

    Note:
        For 'google_scholar' and 'news', external API keys may be required in future versions.
        This implementation uses publicly available endpoints with rate-limiting awareness.
    """
    import urllib.parse
    import urllib.request
    import json
    from datetime import datetime

    result = {
        'status': 'error',
        'source': source,
        'results': [],
        'error': None,
        'timestamp': datetime.now().isoformat()
    }

    try:
        if source == "arxiv":
            base_url = "http://export.arxiv.org/api/query?"
            params = urllib.parse.urlencode({
                'search_query': f'all:{query}',
                'start': 0,
                'max_results': max_results,
                'sortBy': 'submittedDate',
                'sortOrder': 'descending'
            })
            url = base_url + params

            with urllib.request.urlopen(url, timeout=timeout) as response:
                if response.getcode() != 200:
                    raise Exception(f"HTTP {response.getcode()}")

                xml_data = response.read().decode('utf-8')
                # Simple XML parsing (without external libraries)
                entries = []
                entry_start = xml_data.find('<entry>')
                while entry_start != -1:
                    entry_end = xml_data.find('</entry>', entry_start) + 8
                    entry = xml_data[entry_start:entry_end]
                    entries.append(entry)
                    entry_start = xml_data.find('<entry>', entry_end)

                for entry in entries:
                    try:
                        title_start = entry.find('<title>') + 7
                        title_end = entry.find('</title>')
                        title = entry[title_start:title_end].replace('\n', ' ').strip()

                        link_start = entry.find('<id>') + 4
                        link_end = entry.find('</id>')
                        link = entry[link_start:link_end]

                        summary_start = entry.find('<summary>') + 9
                        summary_end = entry.find('</summary>')
                        summary = entry[summary_start:summary_end].replace('\n', ' ').strip()

                        date_start = entry.find('<published>') + 11
                        date_end = entry.find('</published>')
                        date = entry[date_start:date_end]

                        result['results'].append({
                            'title': title,
                            'link': link,
                            'summary': summary,
                            'date': date
                        })
                    except Exception as e:
                        continue

        elif source == "google_scholar":
            # Note: This uses an unofficial API endpoint that may change
            base_url = "https://serpapi.com/search"
            params = {
                'q': query,
                'engine': 'google_scholar',
                'api_key': 'demo',  # In production, use a real API key
                'num': max_results
            }
            url = f"{base_url}?{urllib.parse.urlencode(params)}"

            with urllib.request.urlopen(url, timeout=timeout) as response:
                if response.getcode() != 200:
                    raise Exception(f"HTTP {response.getcode()}")

                data = json.loads(response.read().decode('utf-8'))
                if 'organic_results' in data:
                    for item in data['organic_results'][:max_results]:
                        result['results'].append({
                            'title': item.get('title', 'No title'),
                            'link': item.get('link', '#'),
                            'summary': item.get('snippet', 'No summary available'),
                            'date': item.get('publication_info', {}).get('summary', 'Unknown date')
                        })

        elif source == "news":
            # Note: This uses NewsAPI with a demo key (limited to 100 requests/month)
            base_url = "https://newsapi.org/v2/everything"
            params = {
                'q': query,
                'apiKey': '250e0a3853594c42a843387a33355352',  # Demo key - replace in production
                'pageSize': max_results,
                'sortBy': 'publishedAt'
            }
            url = f"{base_url}?{urllib.parse.urlencode(params)}"

            with urllib.request.urlopen(url, timeout=timeout) as response:
                if response.getcode() != 200:
                    raise Exception(f"HTTP {response.getcode()}")

                data = json.loads(response.read().decode('utf-8'))
                if data.get('status') == 'ok' and 'articles' in data:
                    for article in data['articles'][:max_results]:
                        result['results'].append({
                            'title': article.get('title', 'No title'),
                            'link': article.get('url', '#'),
                            'summary': article.get('description', 'No summary available'),
                            'date': article.get('publishedAt', 'Unknown date')
                        })

        else:
            raise ValueError(f"Unsupported source: {source}. Use 'arxiv', 'google_scholar', or 'news'.")

        if not result['results']:
            result['error'] = "No results found for the given query."
        else:
            result['status'] = 'success'

    except urllib.error.URLError as e:
        result['error'] = f"Network error: {str(e)}"
    except json.JSONDecodeError as e:
        result['error'] = f"Failed to parse response: {str(e)}"
    except ValueError as e:
        result['error'] = str(e)
    except Exception as e:
        result['error'] = f"Unexpected error: {str(e)}"

    return result



def file_path_validator(file_path, required_permissions=None):
    """
    Validates a file path by checking its existence and permissions before operations.

    Args:
        file_path (str): Path to the file or directory to validate.
        required_permissions (str, optional): Required permissions as a string combination of:
            'r' (read), 'w' (write), 'x' (execute). Defaults to None (existence check only).

    Returns:
        dict: A dictionary containing:
            - 'exists' (bool): Whether the path exists
            - 'is_file' (bool): Whether it's a file (if exists)
            - 'is_dir' (bool): Whether it's a directory (if exists)
            - 'permissions' (dict): Current permissions if path exists, with keys:
                'readable', 'writable', 'executable'
            - 'has_required_permissions' (bool or None): Whether path has required permissions
                (None if no permissions were requested)
            - 'error' (str or None): Error message if validation failed
            - 'suggestions' (list): List of suggestions if validation failed

    Example:
        >>> file_path_validator("/path/to/file.txt", "rw")
        {
            'exists': True,
            'is_file': True,
            'is_dir': False,
            'permissions': {'readable': True, 'writable': True, 'executable': False},
            'has_required_permissions': True,
            'error': None,
            'suggestions': []
        }
    """
    result = {
        'exists': False,
        'is_file': False,
        'is_dir': False,
        'permissions': {'readable': False, 'writable': False, 'executable': False},
        'has_required_permissions': None,
        'error': None,
        'suggestions': []
    }

    try:
        path = Path(file_path)
        result['exists'] = path.exists()

        if not result['exists']:
            result['error'] = f"Path '{file_path}' does not exist"
            result['suggestions'] = [
                "Check for typos in the path",
                "Verify the file/directory exists",
                "Check if you have access to the parent directory"
            ]
            return result

        result['is_file'] = path.is_file()
        result['is_dir'] = path.is_dir()

        # Check current permissions
        result['permissions']['readable'] = os.access(file_path, os.R_OK)
        result['permissions']['writable'] = os.access(file_path, os.W_OK)
        result['permissions']['executable'] = os.access(file_path, os.X_OK)

        # Check required permissions if specified
        if required_permissions:
            has_perms = True
            missing_perms = []

            if 'r' in required_permissions and not result['permissions']['readable']:
                has_perms = False
                missing_perms.append('read')
            if 'w' in required_permissions and not result['permissions']['writable']:
                has_perms = False
                missing_perms.append('write')
            if 'x' in required_permissions and not result['permissions']['executable']:
                has_perms = False
                missing_perms.append('execute')

            result['has_required_permissions'] = has_perms

            if not has_perms:
                result['error'] = f"Path exists but lacks required permissions: {', '.join(missing_perms)}"
                result['suggestions'] = [
                    f"Check if you have {' '.join(missing_perms)} permissions for this path",
                    "Verify file/directory ownership",
                    "Check if the path is locked by another process"
                ]

    except Exception as e:
        result['error'] = f"Validation error: {str(e)}"
        result['suggestions'] = [
            "Check if the path is valid",
            "Verify you have access to the parent directory",
            "Ensure the path doesn't contain invalid characters"
        ]

    return result

def retry_mechanism(operation, max_attempts=3, initial_delay=1, backoff_factor=2, exceptions=(Exception,)):
    """
    Executes an operation with retry logic for transient failures using exponential backoff.

    Args:
        operation (callable): The operation/function to execute. Should accept no arguments.
        max_attempts (int): Maximum number of retry attempts (default: 3).
        initial_delay (float): Initial delay between retries in seconds (default: 1).
        backoff_factor (float): Multiplier for delay between retries (default: 2).
        exceptions (tuple): Exception types to catch and retry (default: all exceptions).

    Returns:
        tuple: (success: bool, result: any, attempts: int, last_error: Exception or None)
            - success: Whether the operation succeeded
            - result: Return value of the operation if successful, None otherwise
            - attempts: Number of attempts made
            - last_error: The last exception caught (None if successful)

    Example:
        >>> success, result, attempts, error = retry_mechanism(
        ...     lambda: open("temp.txt", "r").read(),
        ...     max_attempts=5,
        ...     initial_delay=0.5
        ... )
    """
    attempt = 0
    last_error = None

    while attempt < max_attempts:
        attempt += 1
        try:
            result = operation()
            return (True, result, attempt, None)
        except exceptions as e:
            last_error = e
            if attempt < max_attempts:
                delay = initial_delay * (backoff_factor ** (attempt - 1))
                time.sleep(delay)

    return (False, None, attempt, last_error)



def code_validator(code_string, raise_exception=False):
    """
    Validates Python code syntax and basic structure before execution.

    Performs the following checks:
    1. Syntax validation using compile()
    2. Basic structure validation (indentation, balanced brackets)
    3. Import validation (checks for undefined imports)
    4. Basic security checks (detects dangerous patterns)

    Args:
        code_string (str): Python code to validate as a string
        raise_exception (bool): If True, raises SyntaxError or ValueError with details.
                               If False, returns validation results as a dictionary.

    Returns:
        dict: If raise_exception=False, returns a dictionary with:
            - 'valid' (bool): Whether the code is valid
            - 'errors' (list): List of error messages (empty if valid)
            - 'warnings' (list): List of warning messages
            - 'syntax_tree' (ast.AST or None): Parsed syntax tree if valid
            - 'imports' (list): List of imported modules
            - 'security_issues' (list): List of potential security issues

    Raises:
        SyntaxError: If raise_exception=True and syntax errors are found
        ValueError: If raise_exception=True and other validation issues are found

    Example:
        >>> result = code_validator("print('Hello')")
        >>> print(result['valid'])
        True
    """
    import ast
    import re
    from collections import defaultdict

    result = {
        'valid': False,
        'errors': [],
        'warnings': [],
        'syntax_tree': None,
        'imports': [],
        'security_issues': []
    }

    # Basic empty check
    if not code_string.strip():
        result['errors'].append("Empty code string provided")
        if raise_exception:
            raise ValueError("Empty code string provided")
        return result

    # Syntax validation
    try:
        tree = ast.parse(code_string)
        result['syntax_tree'] = tree
    except SyntaxError as e:
        result['errors'].append(f"Syntax error: {e.msg} at line {e.lineno}")
        if raise_exception:
            raise
        return result
    except Exception as e:
        result['errors'].append(f"Unexpected parsing error: {str(e)}")
        if raise_exception:
            raise ValueError(f"Unexpected parsing error: {str(e)}")
        return result

    # Structure validation
    try:
        # Check for balanced brackets
        stack = []
        bracket_pairs = {')': '(', ']': '[', '}': '{'}
        opening_brackets = set(bracket_pairs.values())
        closing_brackets = set(bracket_pairs.keys())

        for i, char in enumerate(code_string):
            if char in opening_brackets:
                stack.append((char, i))
            elif char in closing_brackets:
                if not stack or stack[-1][0] != bracket_pairs[char]:
                    result['errors'].append(f"Unmatched closing bracket '{char}' at position {i}")
                    if raise_exception:
                        raise SyntaxError(f"Unmatched closing bracket '{char}' at position {i}")
                    return result
                stack.pop()

        if stack:
            unmatched = stack[-1]
            result['errors'].append(f"Unmatched opening bracket '{unmatched[0]}' at position {unmatched[1]}")
            if raise_exception:
                raise SyntaxError(f"Unmatched opening bracket '{unmatched[0]}' at position {unmatched[1]}")
            return result

        # Check indentation (basic check for mixed tabs/spaces)
        if '\t' in code_string and '    ' in code_string:
            result['warnings'].append("Mixed tabs and spaces in indentation")

    except Exception as e:
        result['errors'].append(f"Structure validation error: {str(e)}")
        if raise_exception:
            raise ValueError(f"Structure validation error: {str(e)}")
        return result

    # Import validation
    imports = set()
    undefined_imports = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module
            if node.level > 0:  # Relative import
                module = f"{'.' * node.level}{module}" if module else '.' * node.level
            imports.add(module)

    # Check for undefined imports (basic check)
    for imp in imports:
        if imp.startswith('.'):  # Skip relative imports
            continue
        try:
            # Try to import the module
            __import__(imp.split('.')[0])
        except ImportError:
            undefined_imports.add(imp)

    if undefined_imports:
        result['warnings'].append(f"Potentially undefined imports: {', '.join(sorted(undefined_imports))}")

    result['imports'] = sorted(imports)

    # Security checks
    dangerous_patterns = [
        (r'os\.system\(', 'Potential shell injection via os.system'),
        (r'subprocess\.run\(', 'Potential shell injection via subprocess.run'),
        (r'exec\(', 'Use of exec() is dangerous'),
        (r'eval\(', 'Use of eval() is dangerous'),
        (r'pickle\.load', 'Use of pickle can lead to code execution'),
        (r'__import__\(', 'Dynamic imports can be dangerous'),
        (r'open\(', 'File operations should be validated'),
        (r'input\(', 'Unsanitized input can be dangerous'),
    ]

    for pattern, warning in dangerous_patterns:
        if re.search(pattern, code_string):
            result['security_issues'].append(warning)

    # If we got here with no errors, the code is valid
    result['valid'] = not result['errors']
    return result

def dependency_bootstrap(target_path, test_structure=None, overwrite=False):
    """
    Automatically creates missing test files and directories for a Python project.

    Creates a standard test structure if none exists, or verifies and completes
    an existing structure. Supports pytest and unittest conventions.

    Args:
        target_path (str): Path to the project root or module to bootstrap
        test_structure (dict, optional): Custom test structure to create. If None,
            creates a standard pytest structure. Example:
            {
                'tests': {
                    'unit': ['__init__.py', 'test_*.py'],
                    'integration': ['__init__.py', 'test_*.py'],
                    'conftest.py': None
                },
                'requirements-test.txt': "-r requirements.txt\npytest\n"
            }
        overwrite (bool): If True, overwrites existing files. If False, skips existing files.

    Returns:
        dict: A dictionary containing:
            - 'created' (list): Paths of created files/directories
            - 'skipped' (list): Paths of existing items that were skipped
            - 'errors' (list): Any errors encountered
            - 'suggestions' (list): Recommendations for next steps

    Example:
        >>> result = dependency_bootstrap(
        ...     "/path/to/project",
        ...     test_structure={
        ...         'tests': {
        ...             'unit': ['__init__.py', 'test_models.py'],
        ...             'integration': ['__init__.py']
        ...         }
        ...     }
        ... )
    """
    from pathlib import Path

    result = {
        'created': [],
        'skipped': [],
        'errors': [],
        'suggestions': []
    }

    target = Path(target_path)
    if not target.exists():
        result['errors'].append(f"Target path does not exist: {target_path}")
        return result

    # Default test structure if none provided
    if test_structure is None:
        test_structure = {
            'tests': {
                'unit': ['__init__.py', 'test_*.py'],
                'integration': ['__init__.py', 'test_*.py'],
                'conftest.py': None
            },
            'requirements-test.txt': "-r requirements.txt\npytest\npytest-cov\n"
        }

    def create_item(base_path, item_name, content=None):
        """Helper to create files/directories with error handling"""
        path = base_path / item_name

        try:
            if content is None:  # Directory or empty file
                if '.' in item_name:  # File
                    if not path.exists() or overwrite:
                        path.touch()
                        result['created'].append(str(path))
                    else:
                        result['skipped'].append(str(path))
                else:  # Directory
                    path.mkdir(exist_ok=True)
                    if not any(path.iterdir()):  # Only count if newly created
                        result['created'].append(str(path))
                    else:
                        result['skipped'].append(str(path))
            else:  # File with content
                if not path.exists() or overwrite:
                    path.write_text(content)
                    result['created'].append(str(path))
                else:
                    result['skipped'].append(str(path))
        except Exception as e:
            result['errors'].append(f"Failed to create {item_name}: {str(e)}")

    def process_structure(base_path, structure):
        """Recursively process the test structure"""
        for name, content in structure.items():
            if isinstance(content, dict):  # Nested directory structure
                dir_path = base_path / name
                dir_path.mkdir(exist_ok=True)
                if not any(dir_path.iterdir()):  # Only count if newly created
                    result['created'].append(str(dir_path))
                else:
                    result['skipped'].append(str(dir_path))
                process_structure(dir_path, content)
            elif isinstance(content, list):  # List of files to create in this directory
                for pattern in content:
                    if '*' in pattern:  # Wildcard pattern
                        # For wildcard patterns, we'll create one example file
                        example_name = pattern.replace('*', 'example')
                        create_item(base_path, example_name)
                    else:
                        create_item(base_path, pattern)
            else:  # Single file with content
                create_item(base_path, name, content)

    try:
        process_structure(target, test_structure)

        # Add suggestions
        if not result['errors']:
            result['suggestions'] = [
                "Run 'pytest' to execute tests",
                "Consider adding test coverage configuration",
                "Review created test files and add test cases",
                "Install test requirements: pip install -r requirements-test.txt"
            ]

            # Check if pytest is in the created requirements
            if 'requirements-test.txt' in test_structure:
                req_path = target / 'requirements-test.txt'
                if req_path.exists():
                    content = req_path.read_text()
                    if 'pytest' not in content:
                        result['suggestions'].append(
                            "Add pytest to your requirements-test.txt if not already present"
                        )

    except Exception as e:
        result['errors'].append(f"Error during bootstrap process: {str(e)}")

    return result



def validate_python_syntax(code_snippet, raise_exception=False):
    """
    Validates Python code syntax before execution to catch errors early.

    Performs comprehensive syntax validation including:
    - Basic Python syntax checking
    - Indentation validation
    - Balanced bracket checking
    - Basic security pattern detection
    - Import validation (checks if imports can be resolved)

    Args:
        code_snippet (str): Python code to validate
        raise_exception (bool): If True, raises SyntaxError or ValueError with details.
                               If False, returns validation results as a dictionary.

    Returns:
        dict: If raise_exception=False, returns a dictionary with:
            - 'valid' (bool): Whether the code is syntactically valid
            - 'errors' (list): List of syntax errors found
            - 'warnings' (list): List of potential issues/warnings
            - 'security_issues' (list): List of detected security concerns
            - 'imports' (list): List of imported modules
            - 'line_count' (int): Number of lines in the code
            - 'char_count' (int): Number of characters in the code

    Raises:
        SyntaxError: If raise_exception=True and syntax errors are found
        ValueError: If raise_exception=True and other validation issues are found

    Example:
        >>> result = validate_python_syntax("print('Hello')\nfor i in range(5):")
        >>> if not result['valid']:
        ...     print("Code has syntax errors:", result['errors'])
    """
    import ast
    import re

    result = {
        'valid': False,
        'errors': [],
        'warnings': [],
        'security_issues': [],
        'imports': [],
        'line_count': len(code_snippet.splitlines()),
        'char_count': len(code_snippet)
    }

    # Empty code check
    if not code_snippet.strip():
        result['errors'].append("Empty code snippet provided")
        if raise_exception:
            raise ValueError("Empty code snippet provided")
        return result

    # Basic syntax validation using compile
    try:
        compile(code_snippet, '<string>', 'exec')
    except SyntaxError as e:
        result['errors'].append(f"Syntax error: {e.msg} at line {e.lineno}")
        if raise_exception:
            raise
        return result
    except Exception as e:
        result['errors'].append(f"Unexpected compilation error: {str(e)}")
        if raise_exception:
            raise ValueError(f"Unexpected compilation error: {str(e)}")
        return result

    # AST parsing for deeper analysis
    try:
        tree = ast.parse(code_snippet)
    except SyntaxError as e:
        result['errors'].append(f"AST parsing error: {e.msg} at line {e.lineno}")
        if raise_exception:
            raise
        return result

    # Check for balanced brackets
    stack = []
    bracket_pairs = {')': '(', ']': '[', '}': '{'}
    opening_brackets = set(bracket_pairs.values())
    closing_brackets = set(bracket_pairs.keys())

    for i, char in enumerate(code_snippet):
        if char in opening_brackets:
            stack.append((char, i))
        elif char in closing_brackets:
            if not stack or stack[-1][0] != bracket_pairs[char]:
                result['errors'].append(f"Unmatched closing bracket '{char}' at position {i}")
                if raise_exception:
                    raise SyntaxError(f"Unmatched closing bracket '{char}' at position {i}")
                return result
            stack.pop()

    if stack:
        unmatched = stack[-1]
        result['errors'].append(f"Unmatched opening bracket '{unmatched[0]}' at position {unmatched[1]}")
        if raise_exception:
            raise SyntaxError(f"Unmatched opening bracket '{unmatched[0]}' at position {unmatched[1]}")
        return result

    # Check indentation
    lines = code_snippet.splitlines()
    indent_stack = [0]

    for i, line in enumerate(lines, 1):
        if not line.strip():
            continue

        indent = len(line) - len(line.lstrip())
        if indent > indent_stack[-1]:
            indent_stack.append(indent)
        elif indent < indent_stack[-1]:
            if indent not in indent_stack:
                result['errors'].append(f"Inconsistent indentation at line {i}")
                if raise_exception:
                    raise SyntaxError(f"Inconsistent indentation at line {i}")
                return result
            while indent < indent_stack[-1]:
                indent_stack.pop()

    # Check for mixed tabs and spaces
    if '\t' in code_snippet and '    ' in code_snippet:
        result['warnings'].append("Mixed tabs and spaces in indentation")

    # Import analysis
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module
            if node.level > 0:  # Relative import
                module = f"{'.' * node.level}{module}" if module else '.' * node.level
            imports.add(module)

    result['imports'] = sorted(imports)

    # Check if imports can be resolved
    for imp in imports:
        if imp.startswith('.'):  # Skip relative imports
            continue
        try:
            __import__(imp.split('.')[0])
        except ImportError:
            result['warnings'].append(f"Potential undefined import: {imp}")

    # Security pattern detection
    dangerous_patterns = [
        (r'os\.system\(', 'Potential shell injection via os.system'),
        (r'subprocess\.run\(', 'Potential shell injection via subprocess.run'),
        (r'subprocess\.Popen\(', 'Potential shell injection via subprocess.Popen'),
        (r'exec\(', 'Use of exec() is dangerous'),
        (r'eval\(', 'Use of eval() is dangerous'),
        (r'pickle\.load', 'Use of pickle can lead to code execution'),
        (r'__import__\(', 'Dynamic imports can be dangerous'),
        (r'open\(', 'File operations should be validated'),
        (r'input\(', 'Unsanitized input can be dangerous'),
        (r'from\s+[\w\.]+\s+import\s+\*', 'Wildcard imports can lead to namespace pollution')
    ]

    for pattern, warning in dangerous_patterns:
        if re.search(pattern, code_snippet):
            result['security_issues'].append(warning)

    # If we got here with no errors, the code is valid
    result['valid'] = not result['errors']
    return result


def secure_delete(file_path, method='overwrite', passes=3, verify=True):
    """
    Securely deletes a file using multiple methods with verification.

    Supports different secure deletion methods:
    - 'overwrite': Overwrites file contents with random data before deletion
    - 'shred': Uses multiple overwrite passes with different patterns
    - 'zero': Overwrites with zeros (less secure but faster)
    - 'simple': Just deletes the file (same as regular delete)

    Args:
        file_path (str): Path to the file to delete
        method (str): Deletion method to use ('overwrite', 'shred', 'zero', 'simple')
        passes (int): Number of overwrite passes (for 'overwrite' and 'shred' methods)
        verify (bool): Whether to verify the deletion was successful

    Returns:
        dict: A dictionary containing:
            - 'success' (bool): Whether the deletion was successful
            - 'method_used' (str): The method actually used
            - 'passes' (int): Number of passes performed
            - 'verification' (dict): Verification results if verify=True
            - 'error' (str): Error message if deletion failed
            - 'file_info' (dict): Information about the file before deletion

    Raises:
        ValueError: If the method is not supported or file_path is invalid

    Example:
        >>> result = secure_delete("/tmp/sensitive.txt", method="shred", passes=5)
        >>> if not result['success']:
        ...     print("Secure deletion failed:", result['error'])
    """
    import os
    import random
    import stat
    import time

    result = {
        'success': False,
        'method_used': method,
        'passes': passes,
        'verification': {},
        'error': None,
        'file_info': {}
    }

    # Validate method
    supported_methods = ['overwrite', 'shred', 'zero', 'simple']
    if method not in supported_methods:
        result['error'] = f"Unsupported method '{method}'. Supported methods: {', '.join(supported_methods)}"
        return result

    # Get file info before deletion
    try:
        file_stat = os.stat(file_path)
        result['file_info'] = {
            'size': file_stat.st_size,
            'created': datetime.datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
            'modified': datetime.datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
            'permissions': stat.filemode(file_stat.st_mode),
            'exists': True
        }
    except FileNotFoundError:
        result['error'] = f"File not found: {file_path}"
        result['file_info']['exists'] = False
        return result
    except Exception as e:
        result['error'] = f"Error getting file info: {str(e)}"
        return result

    # Check if it's actually a file
    if not os.path.isfile(file_path):
        result['error'] = f"Path is not a file: {file_path}"
        return result

    # Make file writable if it's read-only
    try:
        current_permissions = os.stat(file_path).st_mode
        if not current_permissions & stat.S_IWUSR:
            os.chmod(file_path, current_permissions | stat.S_IWUSR)
    except Exception as e:
        result['error'] = f"Failed to make file writable: {str(e)}"
        return result

    file_size = result['file_info']['size']

    # Perform secure deletion based on method
    try:
        with open(file_path, 'ba+') as f:
            if method in ['overwrite', 'shred', 'zero']:
                # Overwrite the file contents
                for i in range(passes):
                    if method == 'zero':
                        # Write zeros
                        f.seek(0)
                        f.write(b'\x00' * file_size)
                    elif method == 'overwrite':
                        # Write random data
                        f.seek(0)
                        f.write(os.urandom(file_size))
                    elif method == 'shred':
                        # Write different patterns in each pass
                        patterns = [
                            b'\x00' * file_size,  # All zeros
                            b'\xFF' * file_size,  # All ones
                            os.urandom(file_size),  # Random data
                            b'\xAA' * file_size,  # Alternating bits
                            b'\x55' * file_size   # Alternating bits (inverse)
                        ]
                        f.seek(0)
                        f.write(patterns[i % len(patterns)])

                    f.flush()
                    os.fsync(f.fileno())

                    # For multi-pass methods, rewind between passes
                    if i < passes - 1:
                        f.seek(0)

            # Truncate the file to ensure no data remains
            f.truncate(0)

        # Delete the file
        os.remove(file_path)

        # Verification
        if verify:
            result['verification'] = {
                'file_exists': os.path.exists(file_path),
                'file_readable': False,
                'file_size': 0,
                'attempts': 0
            }

            # Try to read the file to verify it's gone
            max_attempts = 3
            for attempt in range(max_attempts):
                result['verification']['attempts'] = attempt + 1
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                        result['verification']['file_readable'] = True
                        result['verification']['file_size'] = len(content)
                        break
                except FileNotFoundError:
                    result['verification']['file_exists'] = False
                    break
                except Exception:
                    # File exists but can't be read (good)
                    result['verification']['file_exists'] = True
                    time.sleep(0.1)  # Small delay between attempts

            if result['verification']['file_exists'] or result['verification']['file_readable']:
                result['error'] = "Verification failed - file may not be completely deleted"
                return result

        result['success'] = True

    except Exception as e:
        result['error'] = f"Secure deletion failed: {str(e)}"
        return result

    return result


def validate_and_prepare_environment(required_paths, base_dir="."):
    """
    Validates the existence of required directories and files, creating them if missing.

    Checks each path in required_paths for existence relative to base_dir. If a path
    doesn't exist, creates it (directories) or creates an empty file (files). Also
    verifies write permissions for all created paths.

    Args:
        required_paths (list): List of dictionaries specifying required paths. Each dict
            should contain:
            - 'path' (str): Relative path to check/create
            - 'type' (str): 'file' or 'directory'
            - 'description' (str): Description of the path's purpose
            - 'content' (str, optional): Content to write to file (for file type)
        base_dir (str): Base directory to resolve relative paths from. Defaults to current dir.

    Returns:
        dict: A dictionary containing:
            - 'success' (bool): Overall success status
            - 'created' (list): Paths that were created
            - 'existing' (list): Paths that already existed
            - 'failed' (list): Paths that couldn't be created
            - 'details' (dict): Detailed results for each path
            - 'warnings' (list): Any non-critical issues encountered

    Example:
        >>> result = validate_and_prepare_environment([
        ...     {'path': 'data/input', 'type': 'directory', 'description': 'Input data directory'},
        ...     {'path': 'config/settings.json', 'type': 'file', 'description': 'Configuration file'}
        ... ])
    """
    from pathlib import Path

    result = {
        'success': True,
        'created': [],
        'existing': [],
        'failed': [],
        'details': {},
        'warnings': []
    }

    base_path = Path(base_dir).resolve()

    for path_spec in required_paths:
        path = Path(path_spec['path'])
        full_path = (base_path / path).resolve()
        path_type = path_spec['type'].lower()
        path_key = str(full_path)

        # Initialize details for this path
        result['details'][path_key] = {
            'path': str(full_path),
            'type': path_type,
            'description': path_spec.get('description', ''),
            'status': None,
            'error': None,
            'created': False,
            'permissions': {}
        }

        try:
            # Check if path exists
            if full_path.exists():
                result['existing'].append(path_key)
                result['details'][path_key]['status'] = 'exists'

                # Verify it's the correct type
                if path_type == 'file' and not full_path.is_file():
                    result['details'][path_key]['error'] = f"Path exists but is not a {path_type}"
                    result['details'][path_key]['status'] = 'type_mismatch'
                    result['failed'].append(path_key)
                    result['success'] = False
                    continue
                elif path_type == 'directory' and not full_path.is_dir():
                    result['details'][path_key]['error'] = f"Path exists but is not a {path_type}"
                    result['details'][path_key]['status'] = 'type_mismatch'
                    result['failed'].append(path_key)
                    result['success'] = False
                    continue

                # Check permissions
                result['details'][path_key]['permissions'] = {
                    'readable': os.access(full_path, os.R_OK),
                    'writable': os.access(full_path, os.W_OK),
                    'executable': os.access(full_path, os.X_OK)
                }

                if not result['details'][path_key]['permissions']['writable']:
                    result['warnings'].append(f"Write permission missing for existing {path_type}: {path_key}")

                continue

            # Create parent directories if they don't exist
            parent = full_path.parent
            if not parent.exists():
                try:
                    parent.mkdir(parents=True, exist_ok=True)
                    result['created'].append(str(parent))
                    result['details'][str(parent)] = {
                        'path': str(parent),
                        'type': 'directory',
                        'description': 'Parent directory for ' + path_key,
                        'status': 'created',
                        'created': True
                    }
                except Exception as e:
                    result['details'][path_key]['error'] = f"Failed to create parent directory: {str(e)}"
                    result['details'][path_key]['status'] = 'parent_failed'
                    result['failed'].append(path_key)
                    result['success'] = False
                    continue

            # Create the path based on type
            if path_type == 'directory':
                try:
                    full_path.mkdir(exist_ok=True)
                    result['created'].append(path_key)
                    result['details'][path_key]['status'] = 'created'
                    result['details'][path_key]['created'] = True
                except Exception as e:
                    result['details'][path_key]['error'] = f"Failed to create directory: {str(e)}"
                    result['details'][path_key]['status'] = 'creation_failed'
                    result['failed'].append(path_key)
                    result['success'] = False
            elif path_type == 'file':
                try:
                    content = path_spec.get('content', '')
                    full_path.write_text(content, encoding='utf-8')
                    result['created'].append(path_key)
                    result['details'][path_key]['status'] = 'created'
                    result['details'][path_key]['created'] = True
                except Exception as e:
                    result['details'][path_key]['error'] = f"Failed to create file: {str(e)}"
                    result['details'][path_key]['status'] = 'creation_failed'
                    result['failed'].append(path_key)
                    result['success'] = False
            else:
                result['details'][path_key]['error'] = f"Invalid path type: {path_type}"
                result['details'][path_key]['status'] = 'invalid_type'
                result['failed'].append(path_key)
                result['success'] = False

            # Verify permissions on newly created paths
            if result['details'][path_key]['created']:
                result['details'][path_key]['permissions'] = {
                    'readable': os.access(full_path, os.R_OK),
                    'writable': os.access(full_path, os.W_OK),
                    'executable': os.access(full_path, os.X_OK)
                }

                if not result['details'][path_key]['permissions']['writable']:
                    result['warnings'].append(f"Write permission missing for newly created {path_type}: {path_key}")

        except Exception as e:
            result['details'][path_key]['error'] = f"Unexpected error: {str(e)}"
            result['details'][path_key]['status'] = 'error'
            result['failed'].append(path_key)
            result['success'] = False

    return result

def parse_command(command_input):
    """
    Standardizes function calls for execution by parsing various command input formats.

    Parses different input formats into a standardized dictionary format for execution:
    - String commands (e.g., "list_files('/path')")
    - Dictionary commands (e.g., {"function": "list_files", "args": ["/path"]})
    - JSON strings (e.g., '{"function": "list_files", "args": ["/path"]}')
    - Direct function calls with kwargs

    Args:
        command_input: The command to parse. Can be:
            - str: Function call as string (e.g., "list_files('/path')")
            - dict: Function call specification (e.g., {"function": "list_files", "args": ["/path"]})
            - JSON string: JSON representation of the above dict format

    Returns:
        dict: Standardized command format with keys:
            - 'function' (str): Name of the function to call
            - 'args' (list): Positional arguments
            - 'kwargs' (dict): Keyword arguments
            - 'raw_input' (any): Original input
            - 'input_type' (str): Type of input ('string', 'dict', 'json')
            - 'error' (str): Error message if parsing failed

    Example:
        >>> parse_command("list_files('/data', recursive=True)")
        {
            'function': 'list_files',
            'args': ['/data'],
            'kwargs': {'recursive': True},
            'raw_input': "list_files('/data', recursive=True)",
            'input_type': 'string',
            'error': None
        }
    """
    import ast
    import json
    import re

    result = {
        'function': None,
        'args': [],
        'kwargs': {},
        'raw_input': command_input,
        'input_type': None,
        'error': None
    }

    try:
        # Handle None or empty input
        if command_input is None:
            result['error'] = "No command input provided"
            return result

        # Handle dictionary input
        if isinstance(command_input, dict):
            result['input_type'] = 'dict'
            if 'function' not in command_input:
                result['error'] = "Dictionary input must contain 'function' key"
                return result

            result['function'] = command_input.get('function')
            result['args'] = command_input.get('args', [])
            result['kwargs'] = command_input.get('kwargs', {})

            # Validate function name
            if not isinstance(result['function'], str) or not result['function'].strip():
                result['error'] = "Function name must be a non-empty string"
                return result

            return result

        # Handle string input
        if isinstance(command_input, str):
            command_str = command_input.strip()
            if not command_str:
                result['error'] = "Empty command string provided"
                return result

            # Check if it's a JSON string
            if command_str.startswith('{') and command_str.endswith('}'):
                try:
                    json_data = json.loads(command_str)
                    if isinstance(json_data, dict):
                        result['input_type'] = 'json'
                        # Recursively parse the JSON data
                        parsed = parse_command(json_data)
                        if parsed['error']:
                            result['error'] = f"JSON parsing error: {parsed['error']}"
                            return result
                        return parsed
                except json.JSONDecodeError:
                    pass  # Not JSON, continue with other parsing methods

            # Try to parse as function call string
            result['input_type'] = 'string'

            # Extract function name
            func_match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\(', command_str)
            if not func_match:
                result['error'] = "Invalid function call format - could not extract function name"
                return result

            result['function'] = func_match.group(1)
            args_str = command_str[func_match.end():-1]  # Get content between parentheses

            # Parse arguments
            try:
                # Use ast to safely parse the arguments
                args_tree = ast.parse(f"func({args_str})", mode='eval')
                call_node = args_tree.body

                for arg in call_node.args:
                    # Evaluate the argument safely
                    try:
                        arg_value = ast.literal_eval(arg)
                        result['args'].append(arg_value)
                    except (ValueError, SyntaxError):
                        # If literal_eval fails, keep as string
                        if isinstance(arg, ast.Str):
                            result['args'].append(arg.s)
                        elif isinstance(arg, ast.Name):
                            result['args'].append(arg.id)
                        else:
                            # For complex expressions, we'll pass the string representation
                            result['args'].append(ast.get_source_segment(command_str, arg) or "")

                for keyword in call_node.keywords:
                    try:
                        kw_value = ast.literal_eval(keyword.value)
                        result['kwargs'][keyword.arg] = kw_value
                    except (ValueError, SyntaxError):
                        if isinstance(keyword.value, ast.Str):
                            result['kwargs'][keyword.arg] = keyword.value.s
                        elif isinstance(keyword.value, ast.Name):
                            result['kwargs'][keyword.arg] = keyword.value.id
                        else:
                            # For complex expressions, pass the string representation
                            result['kwargs'][keyword.arg] = ast.get_source_segment(command_str, keyword.value) or ""

            except SyntaxError as e:
                result['error'] = f"Invalid argument syntax: {str(e)}"
                return result
            except Exception as e:
                result['error'] = f"Error parsing arguments: {str(e)}"
                return result

            return result

        # Handle other input types
        result['error'] = f"Unsupported input type: {type(command_input).__name__}"
        return result

    except Exception as e:
        result['error'] = f"Unexpected error during command parsing: {str(e)}"
        return result


def code_linter(file_path, raise_exception=False, check_style=False):
    """
    Validates Python syntax in a file and optionally checks coding style.

    Performs comprehensive validation of Python files including:
    - Syntax validation using compile()
    - AST parsing for deeper analysis
    - Import validation
    - Security pattern detection
    - Optional PEP 8 style checking (basic checks without external dependencies)

    Args:
        file_path (str): Path to the Python file to validate
        raise_exception (bool): If True, raises SyntaxError or ValueError with details.
                               If False, returns validation results as a dictionary.
        check_style (bool): If True, performs basic PEP 8 style checks

    Returns:
        dict: If raise_exception=False, returns a dictionary with:
            - 'valid' (bool): Whether the file is syntactically valid
            - 'errors' (list): List of syntax errors found
            - 'warnings' (list): List of potential issues/warnings
            - 'style_issues' (list): List of style issues if check_style=True
            - 'security_issues' (list): List of detected security concerns
            - 'imports' (list): List of imported modules
            - 'file_info' (dict): File metadata (size, modification time, etc.)
            - 'line_count' (int): Number of lines in the file
            - 'function_count' (int): Number of functions defined
            - 'class_count' (int): Number of classes defined

    Raises:
        SyntaxError: If raise_exception=True and syntax errors are found
        ValueError: If raise_exception=True and other validation issues are found
        FileNotFoundError: If the file doesn't exist and raise_exception=True

    Example:
        >>> result = code_linter("script.py", check_style=True)
        >>> if not result['valid']:
        ...     print("File has syntax errors:", result['errors'])
        >>> if result['style_issues']:
        ...     print("Style issues found:", result['style_issues'])
    """
    result = {
        'valid': False,
        'errors': [],
        'warnings': [],
        'style_issues': [],
        'security_issues': [],
        'imports': [],
        'file_info': {},
        'line_count': 0,
        'function_count': 0,
        'class_count': 0
    }

    # Check if file exists
    if not os.path.exists(file_path):
        result['errors'].append(f"File not found: {file_path}")
        if raise_exception:
            raise FileNotFoundError(f"File not found: {file_path}")
        return result

    # Get file info
    try:
        stats = os.stat(file_path)
        result['file_info'] = {
            'size': stats.st_size,
            'modified': datetime.datetime.fromtimestamp(stats.st_mtime).isoformat(),
            'created': datetime.datetime.fromtimestamp(stats.st_ctime).isoformat(),
            'path': file_path,
            'extension': os.path.splitext(file_path)[1]
        }
    except Exception as e:
        result['errors'].append(f"Error getting file info: {str(e)}")
        if raise_exception:
            raise ValueError(f"Error getting file info: {str(e)}")
        return result

    # Read file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        result['line_count'] = len(content.splitlines())
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
            result['line_count'] = len(content.splitlines())
            result['warnings'].append("File encoding is not UTF-8, using latin-1 fallback")
        except Exception as e:
            result['errors'].append(f"Error reading file: {str(e)}")
            if raise_exception:
                raise ValueError(f"Error reading file: {str(e)}")
            return result
    except Exception as e:
        result['errors'].append(f"Error reading file: {str(e)}")
        if raise_exception:
            raise ValueError(f"Error reading file: {str(e)}")
        return result

    # Empty file check
    if not content.strip():
        result['errors'].append("File is empty")
        if raise_exception:
            raise ValueError("File is empty")
        return result

    # Basic syntax validation using compile
    try:
        compile(content, file_path, 'exec')
    except SyntaxError as e:
        result['errors'].append(f"Syntax error: {e.msg} at line {e.lineno}")
        if raise_exception:
            raise
        return result
    except Exception as e:
        result['errors'].append(f"Unexpected compilation error: {str(e)}")
        if raise_exception:
            raise ValueError(f"Unexpected compilation error: {str(e)}")
        return result

    # AST parsing for deeper analysis
    try:
        tree = ast.parse(content, filename=file_path)
    except SyntaxError as e:
        result['errors'].append(f"AST parsing error: {e.msg} at line {e.lineno}")
        if raise_exception:
            raise
        return result

    # Count functions and classes
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            result['function_count'] += 1
        elif isinstance(node, ast.ClassDef):
            result['class_count'] += 1

    # Check for balanced brackets
    stack = []
    bracket_pairs = {')': '(', ']': '[', '}': '{'}
    opening_brackets = set(bracket_pairs.values())
    closing_brackets = set(bracket_pairs.keys())

    for i, char in enumerate(content):
        if char in opening_brackets:
            stack.append((char, i))
        elif char in closing_brackets:
            if not stack or stack[-1][0] != bracket_pairs[char]:
                line_num = content.count('\n', 0, i) + 1
                result['errors'].append(f"Unmatched closing bracket '{char}' at line {line_num}")
                if raise_exception:
                    raise SyntaxError(f"Unmatched closing bracket '{char}' at line {line_num}")
                return result
            stack.pop()

    if stack:
        unmatched = stack[-1]
        line_num = content.count('\n', 0, unmatched[1]) + 1
        result['errors'].append(f"Unmatched opening bracket '{unmatched[0]}' at line {line_num}")
        if raise_exception:
            raise SyntaxError(f"Unmatched opening bracket '{unmatched[0]}' at line {line_num}")
        return result

    # Check indentation
    lines = content.splitlines()
    indent_stack = [0]

    for i, line in enumerate(lines, 1):
        if not line.strip():
            continue

        indent = len(line) - len(line.lstrip())
        if indent > indent_stack[-1]:
            indent_stack.append(indent)
        elif indent < indent_stack[-1]:
            if indent not in indent_stack:
                result['errors'].append(f"Inconsistent indentation at line {i}")
                if raise_exception:
                    raise SyntaxError(f"Inconsistent indentation at line {i}")
                return result
            while indent < indent_stack[-1]:
                indent_stack.pop()

    # Check for mixed tabs and spaces
    if '\t' in content and '    ' in content:
        result['warnings'].append("Mixed tabs and spaces in indentation")

    # Import analysis
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module
            if node.level > 0:  # Relative import
                module = f"{'.' * node.level}{module}" if module else '.' * node.level
            imports.add(module)

    result['imports'] = sorted(imports)

    # Check if imports can be resolved
    for imp in imports:
        if imp.startswith('.'):  # Skip relative imports
            continue
        try:
            __import__(imp.split('.')[0])
        except ImportError:
            result['warnings'].append(f"Potential undefined import: {imp}")

    # Security pattern detection
    dangerous_patterns = [
        (r'os\.system\(', 'Potential shell injection via os.system'),
        (r'subprocess\.run\(', 'Potential shell injection via subprocess.run'),
        (r'subprocess\.Popen\(', 'Potential shell injection via subprocess.Popen'),
        (r'exec\(', 'Use of exec() is dangerous'),
        (r'eval\(', 'Use of eval() is dangerous'),
        (r'pickle\.load', 'Use of pickle can lead to code execution'),
        (r'__import__\(', 'Dynamic imports can be dangerous'),
        (r'open\(', 'File operations should be validated'),
        (r'input\(', 'Unsanitized input can be dangerous'),
        (r'from\s+[\w\.]+\s+import\s+\*', 'Wildcard imports can lead to namespace pollution')
    ]

    for pattern, warning in dangerous_patterns:
        if re.search(pattern, content):
            result['security_issues'].append(warning)

    # Style checking if requested
    if check_style:
        # Line length check (PEP 8 recommends 79 chars)
        for i, line in enumerate(lines, 1):
            if len(line) > 79:
                result['style_issues'].append(f"Line {i} exceeds 79 characters (PEP 8)")

        # Trailing whitespace check
        for i, line in enumerate(lines, 1):
            if line.rstrip() != line:
                result['style_issues'].append(f"Line {i} has trailing whitespace")

        # Blank line at end of file
        if content and not content.endswith('\n'):
            result['style_issues'].append("File should end with a blank line")

        # Check for multiple blank lines
        blank_line_count = 0
        for i, line in enumerate(lines, 1):
            if not line.strip():
                blank_line_count += 1
                if blank_line_count > 2:
                    result['style_issues'].append(f"Multiple blank lines at line {i}")
            else:
                blank_line_count = 0

        # Check for docstrings in functions and classes
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                if not ast.get_docstring(node):
                    result['style_issues'].append(
                        f"{'Function' if isinstance(node, ast.FunctionDef) else 'Class'} "
                        f"'{node.name}' at line {node.lineno} is missing a docstring"
                    )

    # If we got here with no errors, the code is valid
    result['valid'] = not result['errors']
    return result

def path_sanitizer(path_string, base_dir=None, create_missing=False, validate=True):
    """
    Replaces placeholders in paths with validated paths and performs safety checks.

    Processes path strings containing placeholders (like <target_file>, <output_dir>)
    and replaces them with validated, absolute paths. Performs security checks to
    prevent directory traversal attacks and validates path existence if requested.

    Args:
        path_string (str): Path string potentially containing placeholders
        base_dir (str, optional): Base directory to resolve relative paths from.
                                 If None, uses current working directory.
        create_missing (bool): If True, creates missing directories in the path
        validate (bool): If True, validates the final path exists or can be created

    Returns:
        dict: A dictionary containing:
            - 'original_path' (str): The original path string
            - 'sanitized_path' (str): The sanitized absolute path
            - 'placeholders' (dict): Dictionary of placeholder replacements
            - 'is_valid' (bool): Whether the path is valid
            - 'exists' (bool): Whether the path exists
            - 'is_file' (bool): Whether the path is a file (if exists)
            - 'is_dir' (bool): Whether the path is a directory (if exists)
            - 'created' (bool): Whether any directories were created
            - 'error' (str): Error message if validation failed
            - 'warnings' (list): List of warnings about the path

    Raises:
        ValueError: If path validation fails and raise_exception=True (not implemented here)

    Example:
        >>> result = path_sanitizer(
        ...     "/data/<project_name>/output/<target_file>.txt",
        ...     base_dir="/home/user",
        ...     placeholders={"project_name": "my_project", "target_file": "results"}
        ... )
        >>> print(result['sanitized_path'])
        /home/user/data/my_project/output/results.txt
    """
    from pathlib import Path

    result = {
        'original_path': path_string,
        'sanitized_path': None,
        'placeholders': {},
        'is_valid': False,
        'exists': False,
        'is_file': False,
        'is_dir': False,
        'created': False,
        'error': None,
        'warnings': []
    }

    # Extract placeholders from the path string
    placeholders = re.findall(r'<([^>]+)>', path_string)
    if not placeholders:
        # No placeholders - just validate and return
        try:
            path = Path(path_string)
            if base_dir:
                path = Path(base_dir) / path
            result['sanitized_path'] = str(path.resolve())
            result['placeholders'] = {}
        except Exception as e:
            result['error'] = f"Error resolving path: {str(e)}"
            return result
    else:
        # Replace placeholders with provided values or defaults
        placeholder_values = {}

        # Check for common placeholders with default values
        default_placeholders = {
            'target_file': 'output',
            'output_dir': 'output',
            'input_dir': 'input',
            'project_name': 'project',
            'user_name': os.getenv('USER', 'user'),
            'date': datetime.datetime.now().strftime('%Y-%m-%d')
        }

        # Use provided placeholders or fall back to defaults
        for ph in placeholders:
            # Check if placeholder was provided in kwargs (not implemented here)
            # In a real implementation, this would come from function arguments
            placeholder_values[ph] = default_placeholders.get(ph, ph)

        result['placeholders'] = placeholder_values

        # Replace placeholders in the path string
        sanitized_path = path_string
        for ph, value in placeholder_values.items():
            sanitized_path = sanitized_path.replace(f'<{ph}>', value)

        try:
            path = Path(sanitized_path)
            if base_dir:
                path = Path(base_dir) / path
            result['sanitized_path'] = str(path.resolve())
        except Exception as e:
            result['error'] = f"Error resolving path with placeholders: {str(e)}"
            return result

    # Security checks
    try:
        # Check for directory traversal attempts
        if '..' in Path(result['sanitized_path']).parts:
            result['warnings'].append("Path contains directory traversal ('..') which may be unsafe")
            # Normalize the path to remove any traversal
            result['sanitized_path'] = str(Path(result['sanitized_path']).resolve())

        # Check if path is absolute
        if not os.path.isabs(result['sanitized_path']):
            result['warnings'].append("Path is not absolute - this may cause issues in some contexts")
            result['sanitized_path'] = str(Path(result['sanitized_path']).resolve())

        # Check path length (Windows has MAX_PATH limit of 260 characters)
        if len(result['sanitized_path']) > 255:
            result['warnings'].append("Path is very long (>255 characters) which may cause issues on some systems")

        # Check for potentially dangerous characters
        dangerous_chars = [';', '&', '|', '$', '>', '<', '`', '\\', '"', "'"]
        if any(char in result['sanitized_path'] for char in dangerous_chars):
            result['error'] = "Path contains potentially dangerous characters"
            result['is_valid'] = False
            return result

    except Exception as e:
        result['error'] = f"Error during security checks: {str(e)}"
        return result

    # Validate path if requested
    if validate:
        try:
            path = Path(result['sanitized_path'])
            result['exists'] = path.exists()

            if result['exists']:
                result['is_file'] = path.is_file()
                result['is_dir'] = path.is_dir()
            else:
                # Check if we can create the path
                if create_missing:
                    try:
                        if '.' in path.name:  # Likely a file
                            path.parent.mkdir(parents=True, exist_ok=True)
                            path.touch()
                            result['created'] = True
                            result['exists'] = True
                            result['is_file'] = True
                        else:  # Likely a directory
                            path.mkdir(parents=True, exist_ok=True)
                            result['created'] = True
                            result['exists'] = True
                            result['is_dir'] = True
                    except Exception as e:
                        result['error'] = f"Could not create path: {str(e)}"
                        return result
                else:
                    result['error'] = f"Path does not exist: {result['sanitized_path']}"
                    return result

            # Check permissions
            if result['exists']:
                if not os.access(result['sanitized_path'], os.R_OK):
                    result['warnings'].append("Path exists but is not readable")
                if not os.access(result['sanitized_path'], os.W_OK):
                    result['warnings'].append("Path exists but is not writable")

            result['is_valid'] = True

        except Exception as e:
            result['error'] = f"Error validating path: {str(e)}"
            return result

    return result


def cross_format_text_extractor(file_path, output_format="text", ocr_config=None, fallback=True):
    """
    Extracts text from various file formats including PDFs, images (with OCR), and other documents.
    Implements fallback mechanisms for unsupported formats and provides configuration options.

    Supported formats:
    - PDF (text extraction)
    - Images (PNG, JPG, JPEG, TIFF, BMP) with OCR
    - Plain text files
    - DOCX (Word documents)
    - ODT (OpenDocument Text)
    - RTF (Rich Text Format)
    - EPUB (eBooks)

    Args:
        file_path (str): Path to the file to extract text from
        output_format (str): Output format for extracted text. Options:
            - "text": Plain text (default)
            - "json": JSON with metadata and text content
            - "markdown": Markdown formatted text
        ocr_config (dict, optional): Configuration for OCR processing. Keys:
            - 'language' (str): Language for OCR (default: 'eng')
            - 'dpi' (int): DPI for image processing (default: 300)
            - 'psm' (int): Page segmentation mode (default: 3)
            - 'oem' (int): OCR engine mode (default: 3)
        fallback (bool): Whether to attempt fallback extraction methods if primary fails

    Returns:
        dict: A dictionary containing:
            - 'success' (bool): Whether extraction was successful
            - 'text' (str): Extracted text (empty if failed)
            - 'format' (str): Detected file format
            - 'method' (str): Extraction method used
            - 'metadata' (dict): File metadata (size, pages, etc.)
            - 'error' (str): Error message if extraction failed
            - 'warnings' (list): List of warnings encountered
            - 'fallback_used' (bool): Whether fallback method was used

    Example:
        >>> result = cross_format_text_extractor("document.pdf", output_format="json")
        >>> if result['success']:
        ...     print(f"Extracted {len(result['text'])} characters from {result['format']}")
    """
    import io
    import json
    import mimetypes
    from pathlib import Path

    result = {
        'success': False,
        'text': '',
        'format': 'unknown',
        'method': 'none',
        'metadata': {},
        'error': None,
        'warnings': [],
        'fallback_used': False
    }

    # Validate file existence
    if not os.path.exists(file_path):
        result['error'] = f"File not found: {file_path}"
        return result

    # Get file info
    try:
        file_stat = os.stat(file_path)
        result['metadata'] = {
            'size': file_stat.st_size,
            'modified': datetime.datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
            'created': datetime.datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
            'extension': os.path.splitext(file_path)[1].lower()
        }
    except Exception as e:
        result['warnings'].append(f"Could not get file metadata: {str(e)}")

    # Detect file format
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type:
        result['format'] = mime_type.split('/')[-1]
    else:
        result['format'] = result['metadata']['extension'][1:] if result['metadata']['extension'] else 'unknown'

    # Try primary extraction methods based on format
    try:
        if result['format'] == 'pdf':
            # PDF text extraction
            try:
                import PyPDF2
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = []
                    for page in reader.pages:
                        text.append(page.extract_text())
                    result['text'] = '\n'.join(text)
                    result['method'] = 'pdf_text_extraction'
                    result['metadata']['pages'] = len(reader.pages)
                    result['success'] = True
            except ImportError:
                result['warnings'].append("PyPDF2 not available, trying alternative PDF extraction")
                raise ImportError("PyPDF2 not available")
            except Exception as e:
                result['warnings'].append(f"PDF text extraction failed: {str(e)}")
                raise

        elif result['format'] in ['png', 'jpg', 'jpeg', 'tiff', 'bmp', 'webp']:
            # Image OCR
            try:
                import pytesseract
                from PIL import Image

                # Set default OCR config
                config = ocr_config or {}
                ocr_lang = config.get('language', 'eng')
                ocr_dpi = config.get('dpi', 300)
                ocr_psm = config.get('psm', 3)
                ocr_oem = config.get('oem', 3)

                # Open image and perform OCR
                with Image.open(file_path) as img:
                    # Convert to RGB if needed
                    if img.mode != 'RGB':
                        img = img.convert('RGB')

                    # Perform OCR
                    text = pytesseract.image_to_string(
                        img,
                        lang=ocr_lang,
                        config=f'--dpi {ocr_dpi} --psm {ocr_psm} --oem {ocr_oem}'
                    )
                    result['text'] = text.strip()
                    result['method'] = 'ocr'
                    result['metadata']['ocr_config'] = {
                        'language': ocr_lang,
                        'dpi': ocr_dpi,
                        'psm': ocr_psm,
                        'oem': ocr_oem
                    }
                    result['success'] = True
            except ImportError:
                result['warnings'].append("pytesseract or PIL not available for OCR")
                raise ImportError("OCR dependencies not available")
            except Exception as e:
                result['warnings'].append(f"OCR failed: {str(e)}")
                raise

        elif result['format'] == 'plain' or result['metadata']['extension'] in ['.txt', '.csv', '.log']:
            # Plain text file
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    result['text'] = f.read()
                result['method'] = 'plain_text'
                result['success'] = True
            except UnicodeDecodeError:
                # Try with different encoding
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        result['text'] = f.read()
                    result['method'] = 'plain_text'
                    result['success'] = True
                    result['warnings'].append("File encoding is not UTF-8, used latin-1 fallback")
                except Exception as e:
                    result['warnings'].append(f"Plain text extraction failed: {str(e)}")
                    raise
            except Exception as e:
                result['warnings'].append(f"Plain text extraction failed: {str(e)}")
                raise

        elif result['format'] == 'vnd.openxmlformats-officedocument.wordprocessingml.document' or \
             result['metadata']['extension'] == '.docx':
            # DOCX extraction
            try:
                from docx import Document
                doc = Document(file_path)
                result['text'] = '\n'.join([para.text for para in doc.paragraphs])
                result['method'] = 'docx_extraction'
                result['success'] = True
            except ImportError:
                result['warnings'].append("python-docx not available for DOCX extraction")
                raise ImportError("DOCX dependencies not available")
            except Exception as e:
                result['warnings'].append(f"DOCX extraction failed: {str(e)}")
                raise

        elif result['format'] == 'vnd.oasis.opendocument.text' or result['metadata']['extension'] == '.odt':
            # ODT extraction
            try:
                from odf.opendocument import load
                from odf.text import P
                doc = load(file_path)
                text = []
                for paragraph in doc.getElementsByType(P):
                    text.append(''.join(paragraph.childNodes).strip())
                result['text'] = '\n'.join(text)
                result['method'] = 'odt_extraction'
                result['success'] = True
            except ImportError:
                result['warnings'].append("odfpy not available for ODT extraction")
                raise ImportError("ODT dependencies not available")
            except Exception as e:
                result['warnings'].append(f"ODT extraction failed: {str(e)}")
                raise

        elif result['format'] == 'rtf' or result['metadata']['extension'] == '.rtf':
            # RTF extraction
            try:
                from striprtf.striprtf import rtf_to_text
                with open(file_path, 'r', encoding='utf-8') as f:
                    rtf_content = f.read()
                result['text'] = rtf_to_text(rtf_content)
                result['method'] = 'rtf_extraction'
                result['success'] = True
            except ImportError:
                result['warnings'].append("striprtf not available for RTF extraction")
                raise ImportError("RTF dependencies not available")
            except Exception as e:
                result['warnings'].append(f"RTF extraction failed: {str(e)}")
                raise

        elif result['format'] == 'epub+zip' or result['metadata']['extension'] == '.epub':
            # EPUB extraction
            try:
                from ebooklib import epub
                book = epub.read_epub(file_path)
                text = []
                for item in book.get_items():
                    if item.get_type() == epub.ITEM_DOCUMENT:
                        text.append(item.get_content().decode('utf-8'))
                result['text'] = '\n'.join(text)
                result['method'] = 'epub_extraction'
                result['success'] = True
            except ImportError:
                result['warnings'].append("ebooklib not available for EPUB extraction")
                raise ImportError("EPUB dependencies not available")
            except Exception as e:
                result['warnings'].append(f"EPUB extraction failed: {str(e)}")
                raise

    except Exception as primary_error:
        if not fallback:
            result['error'] = f"Primary extraction failed: {str(primary_error)}"
            return result

        # Fallback methods
        result['fallback_used'] = True
        result['warnings'].append(f"Primary extraction failed, attempting fallback: {str(primary_error)}")

        try:
            # Fallback 1: Try plain text extraction regardless of format
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                    try:
                        result['text'] = content.decode('utf-8')
                    except UnicodeDecodeError:
                        result['text'] = content.decode('latin-1')
                result['method'] = 'fallback_plain_text'
                result['success'] = True
                result['warnings'].append("Used plain text fallback extraction")
            except Exception as e:
                result['warnings'].append(f"Plain text fallback failed: {str(e)}")
                raise

            # Fallback 2: Try OCR on PDFs if they contain scanned images
            if result['format'] == 'pdf' and not result['success']:
                try:
                    import pytesseract
                    from pdf2image import convert_from_path
                    from PIL import Image

                    # Convert PDF to images
                    images = convert_from_path(file_path)
                    text = []
                    for img in images:
                        text.append(pytesseract.image_to_string(img))
                    result['text'] = '\n'.join(text)
                    result['method'] = 'fallback_pdf_ocr'
                    result['success'] = True
                    result['warnings'].append("Used OCR fallback for PDF")
                except ImportError:
                    result['warnings'].append("PDF OCR fallback dependencies not available")
                except Exception as e:
                    result['warnings'].append(f"PDF OCR fallback failed: {str(e)}")

        except Exception as fallback_error:
            result['error'] = f"All extraction methods failed: {str(fallback_error)}"
            return result

    # Post-processing based on output format
    if result['success']:
        try:
            if output_format == "json":
                # Convert to JSON format
                output = {
                    'metadata': result['metadata'],
                    'method': result['method'],
                    'text': result['text'],
                    'warnings': result['warnings'],
                    'fallback_used': result['fallback_used']
                }
                result['text'] = json.dumps(output, indent=2)
            elif output_format == "markdown":
                # Convert to markdown (basic formatting)
                # Add metadata as a header
                metadata_md = "\n".join(
                    f"- **{key}**: {value}" for key, value in result['metadata'].items()
                )
                result['text'] = f"""# Extracted Text

**Metadata:**
{metadata_md}

**Extraction Method:** {result['method']}
**Fallback Used:** {'Yes' if result['fallback_used'] else 'No'}

---

{result['text']}
"""
        except Exception as e:
            result['warnings'].append(f"Output formatting failed: {str(e)}")
            result['success'] = False
            result['error'] = f"Output formatting failed: {str(e)}"

    return result


def path_normalizer(path_string, base_dir=None, to_absolute=True, expand_user=True, expand_vars=True):
    """
    Standardizes directory/file paths across platforms by normalizing separators,
    resolving relative paths, and expanding environment variables and user paths.

    Handles cross-platform path normalization by:
    - Converting path separators to the platform's native format
    - Resolving relative paths (e.g., '../', './') to absolute paths
    - Expanding environment variables (e.g., '$HOME', '%APPDATA%')
    - Expanding user paths (e.g., '~')
    - Normalizing path case (on case-insensitive filesystems)
    - Removing redundant separators and relative path components

    Args:
        path_string (str): The path string to normalize
        base_dir (str, optional): Base directory for resolving relative paths.
                                 If None, uses current working directory.
        to_absolute (bool): If True, converts relative paths to absolute paths
        expand_user (bool): If True, expands '~' and '~user' to user home directories
        expand_vars (bool): If True, expands environment variables (e.g., '$HOME')

    Returns:
        dict: A dictionary containing:
            - 'original_path' (str): The original input path
            - 'normalized_path' (str): The normalized path
            - 'is_absolute' (bool): Whether the path is absolute
            - 'exists' (bool): Whether the path exists
            - 'is_file' (bool): Whether the path points to a file (if exists)
            - 'is_dir' (bool): Whether the path points to a directory (if exists)
            - 'error' (str): Error message if normalization failed
            - 'warnings' (list): List of warnings about the normalization process

    Example:
        >>> result = path_normalizer("~/projects/../data//file.txt", base_dir="/base")
        >>> print(result['normalized_path'])
        /home/user/data/file.txt
    """
    from pathlib import Path

    result = {
        'original_path': path_string,
        'normalized_path': None,
        'is_absolute': False,
        'exists': False,
        'is_file': False,
        'is_dir': False,
        'error': None,
        'warnings': []
    }

    if not path_string or not isinstance(path_string, str):
        result['error'] = "Path must be a non-empty string"
        return result

    try:
        # Create a Path object from the input string
        path = Path(path_string)

        # Expand environment variables if requested
        if expand_vars:
            try:
                path = Path(os.path.expandvars(str(path)))
            except Exception as e:
                result['warnings'].append(f"Environment variable expansion failed: {str(e)}")

        # Expand user path if requested
        if expand_user:
            try:
                path = path.expanduser()
            except Exception as e:
                result['warnings'].append(f"User path expansion failed: {str(e)}")

        # Resolve to absolute path if requested
        if to_absolute:
            try:
                if base_dir:
                    base_path = Path(base_dir)
                    if not base_path.is_absolute():
                        base_path = base_path.resolve()
                    path = base_path / path
                path = path.resolve()
            except Exception as e:
                result['warnings'].append(f"Absolute path resolution failed: {str(e)}")
                # Fall back to absolute() which doesn't check existence
                try:
                    path = path.absolute()
                except Exception as e:
                    result['error'] = f"Could not resolve absolute path: {str(e)}"
                    return result

        # Convert to string with native separators
        normalized_path = str(path)

        # On Windows, ensure we use backslashes (Path converts to forward slashes)
        if os.name == 'nt':
            normalized_path = normalized_path.replace('/', '\\')

        result['normalized_path'] = normalized_path
        result['is_absolute'] = os.path.isabs(normalized_path)

        # Check if path exists
        try:
            result['exists'] = os.path.exists(normalized_path)
            if result['exists']:
                result['is_file'] = os.path.isfile(normalized_path)
                result['is_dir'] = os.path.isdir(normalized_path)
        except Exception as e:
            result['warnings'].append(f"Path existence check failed: {str(e)}")

        # Check for potential issues
        if '..' in path.parts:
            result['warnings'].append("Path contains parent directory references ('..')")
        if '.' in path.parts:
            result['warnings'].append("Path contains current directory references ('.')")
        if '//' in normalized_path or '\\\\' in normalized_path:
            result['warnings'].append("Path contains redundant separators")

    except Exception as e:
        result['error'] = f"Path normalization failed: {str(e)}"
        return result

    return result

def directory_validator(directory_path, create_if_missing=True, required_permissions=None, check_writable=True):
    """
    Validates a directory path, creating it if missing and checking required permissions.

    Performs comprehensive directory validation including:
    - Existence check
    - Creation of missing directories if requested
    - Permission validation
    - Writable check (if requested)
    - Cross-platform path handling

    Args:
        directory_path (str): Path to the directory to validate
        create_if_missing (bool): If True, creates the directory and any missing parents
        required_permissions (str, optional): Required permissions as a string combination of:
            'r' (read), 'w' (write), 'x' (execute). Defaults to None (existence check only).
        check_writable (bool): If True, checks if the directory is writable (implies 'w' permission)

    Returns:
        dict: A dictionary containing:
            - 'original_path' (str): The original input path
            - 'validated_path' (str): The validated absolute path
            - 'exists' (bool): Whether the directory exists
            - 'created' (bool): Whether the directory was created
            - 'permissions' (dict): Current permissions with keys:
                'readable', 'writable', 'executable'
            - 'has_required_permissions' (bool or None): Whether directory has required permissions
                (None if no permissions were requested)
            - 'is_writable' (bool): Whether directory is writable (if check_writable=True)
            - 'error' (str): Error message if validation failed
            - 'warnings' (list): List of warnings about the directory
            - 'parent_dirs' (list): List of parent directories that were created (if any)

    Example:
        >>> result = directory_validator("/data/output", create_if_missing=True, required_permissions="rwx")
        >>> if not result['exists']:
        ...     print("Directory doesn't exist and couldn't be created")
    """
    from pathlib import Path

    result = {
        'original_path': directory_path,
        'validated_path': None,
        'exists': False,
        'created': False,
        'permissions': {'readable': False, 'writable': False, 'executable': False},
        'has_required_permissions': None,
        'is_writable': False,
        'error': None,
        'warnings': [],
        'parent_dirs': []
    }

    if not directory_path or not isinstance(directory_path, str):
        result['error'] = "Directory path must be a non-empty string"
        return result

    try:
        # Normalize the path first
        path = Path(directory_path)

        # Convert to absolute path
        if not path.is_absolute():
            path = path.resolve()
        result['validated_path'] = str(path)

        # Check if directory exists
        result['exists'] = path.exists()

        if not result['exists']:
            if create_if_missing:
                try:
                    # Create parent directories if needed
                    path.mkdir(parents=True, exist_ok=True)
                    result['created'] = True
                    result['exists'] = True

                    # Record which parent directories were created
                    created_parents = []
                    parent = path.parent
                    while parent != parent.parent:  # Stop at root
                        if not parent.exists():
                            created_parents.append(str(parent))
                        parent = parent.parent
                    result['parent_dirs'] = created_parents
                except Exception as e:
                    result['error'] = f"Failed to create directory: {str(e)}"
                    return result
            else:
                result['error'] = f"Directory does not exist: {result['validated_path']}"
                return result
        else:
            # Verify it's actually a directory
            if not path.is_dir():
                result['error'] = f"Path exists but is not a directory: {result['validated_path']}"
                return result

        # Check current permissions
        result['permissions']['readable'] = os.access(result['validated_path'], os.R_OK)
        result['permissions']['writable'] = os.access(result['validated_path'], os.W_OK)
        result['permissions']['executable'] = os.access(result['validated_path'], os.X_OK)

        # Check writable status if requested
        if check_writable:
            try:
                # Create a temporary file to test writability
                test_file = path / f".tmp_write_test_{os.getpid()}"
                try:
                    with open(test_file, 'w') as f:
                        f.write("test")
                    result['is_writable'] = True
                    os.remove(test_file)
                except Exception:
                    result['is_writable'] = False
                    result['warnings'].append("Directory exists but is not writable")
            except Exception as e:
                result['warnings'].append(f"Writable check failed: {str(e)}")
                result['is_writable'] = False

        # Check required permissions if specified
        if required_permissions or check_writable:
            has_perms = True
            missing_perms = []
            required = set(required_permissions or '')

            # If check_writable is True, we need write permission
            if check_writable:
                required.add('w')

            if 'r' in required and not result['permissions']['readable']:
                has_perms = False
                missing_perms.append('read')
            if 'w' in required and not result['permissions']['writable']:
                has_perms = False
                missing_perms.append('write')
            if 'x' in required and not result['permissions']['executable']:
                has_perms = False
                missing_perms.append('execute')

            result['has_required_permissions'] = has_perms

            if not has_perms:
                result['error'] = f"Directory exists but lacks required permissions: {', '.join(missing_perms)}"
                result['warnings'].append(f"Missing permissions: {', '.join(missing_perms)}")
                return result

        # Additional checks
        if not result['permissions']['executable']:
            result['warnings'].append("Directory exists but is not executable (may cause access issues)")

        # Check for potential issues
        if not result['validated_path']:
            result['error'] = "Could not determine absolute path"
            return result

        if len(result['validated_path']) > 255:
            result['warnings'].append("Directory path is very long (>255 characters) which may cause issues on some systems")

    except Exception as e:
        result['error'] = f"Directory validation failed: {str(e)}"
        return result

    return result


Here are the two requested functions following all requirements:

def validate_python_syntax(file_path=None, code_string=None, raise_exception=False):
    """
    Validates Python syntax in either a file or a code string, checking for errors before execution.

    Performs comprehensive syntax validation including:
    - Basic Python syntax checking using compile()
    - AST parsing for deeper analysis
    - Indentation validation
    - Balanced bracket checking
    - Import validation (checks if imports can be resolved)
    - Basic security pattern detection

    Args:
        file_path (str, optional): Path to a Python file to validate. Either file_path or code_string must be provided.
        code_string (str, optional): Python code as a string to validate. Either file_path or code_string must be provided.
        raise_exception (bool): If True, raises SyntaxError or ValueError with details.
                               If False, returns validation results as a dictionary.

    Returns:
        dict: If raise_exception=False, returns a dictionary with:
            - 'valid' (bool): Whether the code is syntactically valid
            - 'errors' (list): List of syntax errors found
            - 'warnings' (list): List of potential issues/warnings
            - 'security_issues' (list): List of detected security concerns
            - 'imports' (list): List of imported modules
            - 'file_info' (dict): File metadata if file_path was provided
            - 'line_count' (int): Number of lines in the code
            - 'function_count' (int): Number of functions defined
            - 'class_count' (int): Number of classes defined

    Raises:
        SyntaxError: If raise_exception=True and syntax errors are found
        ValueError: If raise_exception=True and other validation issues are found
        FileNotFoundError: If file_path doesn't exist and raise_exception=True

    Example:
        >>> result = validate_python_syntax(file_path="script.py")
        >>> if not result['valid']:
        ...     print("File has syntax errors:", result['errors'])
    """
    import ast
    import re

    result = {
        'valid': False,
        'errors': [],
        'warnings': [],
        'security_issues': [],
        'imports': [],
        'file_info': {},
        'line_count': 0,
        'function_count': 0,
        'class_count': 0
    }

    # Validate input
    if not file_path and not code_string:
        result['errors'].append("Either file_path or code_string must be provided")
        if raise_exception:
            raise ValueError("Either file_path or code_string must be provided")
        return result

    if file_path and code_string:
        result['warnings'].append("Both file_path and code_string provided - using file_path")

    # Get code content
    content = ""
    if file_path:
        # Check if file exists
        if not os.path.exists(file_path):
            result['errors'].append(f"File not found: {file_path}")
            if raise_exception:
                raise FileNotFoundError(f"File not found: {file_path}")
            return result

        # Get file info
        try:
            stats = os.stat(file_path)
            result['file_info'] = {
                'size': stats.st_size,
                'modified': datetime.datetime.fromtimestamp(stats.st_mtime).isoformat(),
                'created': datetime.datetime.fromtimestamp(stats.st_ctime).isoformat(),
                'path': file_path,
                'extension': os.path.splitext(file_path)[1]
            }
        except Exception as e:
            result['errors'].append(f"Error getting file info: {str(e)}")
            if raise_exception:
                raise ValueError(f"Error getting file info: {str(e)}")
            return result

        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            result['line_count'] = len(content.splitlines())
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                result['line_count'] = len(content.splitlines())
                result['warnings'].append("File encoding is not UTF-8, using latin-1 fallback")
            except Exception as e:
                result['errors'].append(f"Error reading file: {str(e)}")
                if raise_exception:
                    raise ValueError(f"Error reading file: {str(e)}")
                return result
        except Exception as e:
            result['errors'].append(f"Error reading file: {str(e)}")
            if raise_exception:
                raise ValueError(f"Error reading file: {str(e)}")
            return result
    else:
        content = code_string
        result['line_count'] = len(content.splitlines())

    # Empty content check
    if not content.strip():
        result['errors'].append("Empty code content provided")
        if raise_exception:
            raise ValueError("Empty code content provided")
        return result

    # Basic syntax validation using compile
    try:
        compile(content, file_path or '<string>', 'exec')
    except SyntaxError as e:
        result['errors'].append(f"Syntax error: {e.msg} at line {e.lineno}")
        if raise_exception:
            raise
        return result
    except Exception as e:
        result['errors'].append(f"Unexpected compilation error: {str(e)}")
        if raise_exception:
            raise ValueError(f"Unexpected compilation error: {str(e)}")
        return result

    # AST parsing for deeper analysis
    try:
        tree = ast.parse(content, filename=file_path)
    except SyntaxError as e:
        result['errors'].append(f"AST parsing error: {e.msg} at line {e.lineno}")
        if raise_exception:
            raise
        return result

    # Count functions and classes
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            result['function_count'] += 1
        elif isinstance(node, ast.ClassDef):
            result['class_count'] += 1

    # Check for balanced brackets
    stack = []
    bracket_pairs = {')': '(', ']': '[', '}': '{'}
    opening_brackets = set(bracket_pairs.values())
    closing_brackets = set(bracket_pairs.keys())

    for i, char in enumerate(content):
        if char in opening_brackets:
            stack.append((char, i))
        elif char in closing_brackets:
            if not stack or stack[-1][0] != bracket_pairs[char]:
                line_num = content.count('\n', 0, i) + 1
                result['errors'].append(f"Unmatched closing bracket '{char}' at line {line_num}")
                if raise_exception:
                    raise SyntaxError(f"Unmatched closing bracket '{char}' at line {line_num}")
                return result
            stack.pop()

    if stack:
        unmatched = stack[-1]
        line_num = content.count('\n', 0, unmatched[1]) + 1
        result['errors'].append(f"Unmatched opening bracket '{unmatched[0]}' at line {line_num}")
        if raise_exception:
            raise SyntaxError(f"Unmatched opening bracket '{unmatched[0]}' at line {line_num}")
        return result

    # Check indentation
    lines = content.splitlines()
    indent_stack = [0]

    for i, line in enumerate(lines, 1):
        if not line.strip():
            continue

        indent = len(line) - len(line.lstrip())
        if indent > indent_stack[-1]:
            indent_stack.append(indent)
        elif indent < indent_stack[-1]:
            if indent not in indent_stack:
                result['errors'].append(f"Inconsistent indentation at line {i}")
                if raise_exception:
                    raise SyntaxError(f"Inconsistent indentation at line {i}")
                return result
            while indent < indent_stack[-1]:
                indent_stack.pop()

    # Check for mixed tabs and spaces
    if '\t' in content and '    ' in content:
        result['warnings'].append("Mixed tabs and spaces in indentation")

    # Import analysis
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module
            if node.level > 0:  # Relative import
                module = f"{'.' * node.level}{module}" if module else '.' * node.level
            imports.add(module)

    result['imports'] = sorted(imports)

    # Check if imports can be resolved
    for imp in imports:
        if imp.startswith('.'):  # Skip relative imports
            continue
        try:
            __import__(imp.split('.')[0])
        except ImportError:
            result['warnings'].append(f"Potential undefined import: {imp}")

    # Security pattern detection
    dangerous_patterns = [
        (r'os\.system\(', 'Potential shell injection via os.system'),
        (r'subprocess\.run\(', 'Potential shell injection via subprocess.run'),
        (r'subprocess\.Popen\(', 'Potential shell injection via subprocess.Popen'),
        (r'exec\(', 'Use of exec() is dangerous'),
        (r'eval\(', 'Use of eval() is dangerous'),
        (r'pickle\.load', 'Use of pickle can lead to code execution'),
        (r'__import__\(', 'Dynamic imports can be dangerous'),
        (r'open\(', 'File operations should be validated'),
        (r'input\(', 'Unsanitized input can be dangerous'),
        (r'from\s+[\w\.]+\s+import\s+\*', 'Wildcard imports can lead to namespace pollution')
    ]

    for pattern, warning in dangerous_patterns:
        if re.search(pattern, content):
            result['security_issues'].append(warning)

    # If we got here with no errors, the code is valid
    result['valid'] = not result['errors']
    return result

def path_validator(path, check_type=None, required_permissions=None, create_missing=False):
    """
    Validates a file or directory path by checking existence, type, and permissions.

    Performs comprehensive path validation including:
    - Existence check
    - Type verification (file/directory)
    - Permission validation
    - Optional creation of missing directories
    - Cross-platform path handling

    Args:
        path (str): Path to validate (file or directory)
        check_type (str, optional): Type to check for ('file', 'directory', or None for either)
        required_permissions (str, optional): Required permissions as a string combination of:
            'r' (read), 'w' (write), 'x' (execute). Defaults to None (existence check only).
        create_missing (bool): If True and path is a directory, creates it if missing

    Returns:
        dict: A dictionary containing:
            - 'path' (str): The validated absolute path
            - 'exists' (bool): Whether the path exists
            - 'is_file' (bool): Whether it's a file (if exists)
            - 'is_dir' (bool): Whether it's a directory (if exists)
            - 'created' (bool): Whether the path was created
            - 'permissions' (dict): Current permissions if path exists, with keys:
                'readable', 'writable', 'executable'
            - 'has_required_permissions' (bool or None): Whether path has required permissions
                (None if no permissions were requested)
            - 'error' (str or None): Error message if validation failed
            - 'warnings' (list): List of warnings about the path
            - 'parent_dirs_created' (list): List of parent directories created (if any)

    Example:
        >>> result = path_validator("/path/to/file.txt", check_type="file", required_permissions="rw")
        >>> if not result['exists']:
        ...     print("File doesn't exist")
        >>> elif not result['has_required_permissions']:
        ...     print("Missing required permissions")
    """
    from pathlib import Path

    result = {
        'path': None,
        'exists': False,
        'is_file': False,
        'is_dir': False,
        'created': False,
        'permissions': {'readable': False, 'writable': False, 'executable': False},
        'has_required_permissions': None,
        'error': None,
        'warnings': [],
        'parent_dirs_created': []
    }

    if not path or not isinstance(path, str):
        result['error'] = "Path must be a non-empty string"
        return result

    try:
        # Normalize and resolve the path
        path_obj = Path(path).resolve()
        result['path'] = str(path_obj)

        # Check if path exists
        result['exists'] = path_obj.exists()

        if not result['exists']:
            if create_missing and (check_type == "directory" or check_type is None):
                try:
                    # Create parent directories if needed
                    path_obj.mkdir(parents=True, exist_ok=True)
                    result['created'] = True
                    result['exists'] = True
                    result['is_dir'] = True

                    # Record which parent directories were created
                    created_parents = []
                    parent = path_obj.parent
                    while parent != parent.parent:  # Stop at root
                        if not parent.exists():
                            created_parents.append(str(parent))
                        parent = parent.parent
                    result['parent_dirs_created'] = created_parents
                except Exception as e:
                    result['error'] = f"Failed to create directory: {str(e)}"
                    return result
            else:
                result['error'] = f"Path does not exist: {result['path']}"
                return result
        else:
            # Verify the type if specified
            if check_type == "file" and not path_obj.is_file():
                result['error'] = f"Path exists but is not a file: {result['path']}"
                return result
            elif check_type == "directory" and not path_obj.is_dir():
                result['error'] = f"Path exists but is not a directory: {result['path']}"
                return result

            result['is_file'] = path_obj.is_file()
            result['is_dir'] = path_obj.is_dir()

        # Check current permissions
        result['permissions']['readable'] = os.access(result['path'], os.R_OK)
        result['permissions']['writable'] = os.access(result['path'], os.W_OK)
        result['permissions']['executable'] = os.access(result['path'], os.X_OK)

        # Check required permissions if specified
        if required_permissions:
            has_perms = True
            missing_perms = []

            if 'r' in required_permissions and not result['permissions']['readable']:
                has_perms = False
                missing_perms.append('read')
            if 'w' in required_permissions and not result['permissions']['writable']:
                has_perms = False
                missing_perms.append('write')
            if 'x' in required_permissions and not result['permissions']['executable']:
                has_perms = False
                missing_perms.append('execute')

            result['has_required_permissions'] = has_perms

            if not has_perms:
                result['error'] = f"Path exists but lacks required permissions: {', '.join(missing_perms)}"
                result['warnings'].append(f"Missing permissions: {', '.join(missing_perms)}")
                return result

        # Additional checks
        if not result['permissions']['executable'] and result['is_dir']:
            result['warnings'].append("Directory exists but is not executable (may cause access issues)")

        if len(result['path']) > 255:
            result['warnings'].append("Path is very long (>255 characters) which may cause issues on some systems")

        if '..' in path_obj.parts:
            result['warnings'].append("Path contains parent directory references ('..')")

    except Exception as e:
        result['error'] = f"Path validation failed: {str(e)}"
        return result

    return result
