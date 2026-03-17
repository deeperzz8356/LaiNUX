import subprocess
import os
import platform
from ..utils.logger import logger

def run_shell_command(command, timeout=10):
    """Executes a system shell command (CMD/PowerShell on Windows, Bash on Linux)."""
    try:
        # On Windows, we need shell=True for some built-in commands
        is_windows = platform.system() == "Windows"
        
        # Use powershell if windows, else bash
        if is_windows:
            process = subprocess.Popen(['powershell', '-Command', command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        else:
            process = subprocess.Popen(['bash', '-c', command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            return "Shell Error: Command timed out. Ensure it isn't an interactive command."
            
        if process.returncode == 0:
            return f"Shell Success: \n{stdout or '[No Output]'}"
        else:
            return f"Shell Command Failed (returncode {process.returncode}): \n{stderr}"
            
    except Exception as e:
        return f"System Execution Error: {str(e)}"

def list_registry(key_path):
    """(Windows Only) Lists a registry key's values. Useful for system exploration."""
    if platform.system() != "Windows": return "Registry access is Windows-only."
    return run_shell_command(f"Get-ItemProperty -Path '{key_path}'")
