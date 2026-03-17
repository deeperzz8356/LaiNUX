import os
import subprocess
import platform
import psutil
from ..utils.logger import logger

def open_application(app_name):
    """Launches an application by name (e.g., 'notepad', 'calc')."""
    try:
        if platform.system() == "Windows":
            # Try start command first for common things
            subprocess.Popen(['start', app_name], shell=True)
        else:
            return "Application launching is currently only optimized for Windows."
        return f"Attempted to open {app_name}."
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
