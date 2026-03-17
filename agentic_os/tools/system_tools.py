import os
import subprocess
import platform
import psutil
from ..utils.logger import logger

def open_application(app_name):
    """Launches an application by name (e.g., 'notepad', 'calc'). Handles common aliases."""
    
    # Common mappings to avoid "Windows cannot find" errors
    APP_MAPPING = {
        "browser": "msedge", # Defaulting to Edge on Windows, could be chrome
        "web": "msedge",
        "chrome": "chrome",
        "explorer": "explorer",
        "notepad": "notepad",
        "calculator": "calc",
        "terminal": "cmd"
    }
    
    actual_app = APP_MAPPING.get(app_name.lower(), app_name)
    
    try:
        if platform.system() == "Windows":
            # Using start command
            subprocess.Popen(['start', actual_app], shell=True)
        else:
            return f"Opening {app_name} is only optimized for Windows right now."
        return f"System: Executed 'start {actual_app}'."
    except Exception as e:
        return f"Error opening application: {str(e)}"

def get_system_stats():
    """Returns CPU and Memory usage details."""
    try:
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        return f"System Stats -> CPU: {cpu}% | RAM: {mem}% | Disk: {disk}%"
    except Exception as e:
        return f"Error getting system stats: {str(e)}"

def kill_process(process_name):
    """Stops a running process by name."""
    try:
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == process_name:
                proc.terminate()
                return f"Process {process_name} has been terminated."
        return f"Process {process_name} not found."
    except Exception as e:
        return f"Error killing process: {str(e)}"
