import requests
import socket
from ..utils.logger import logger

def check_site_status(url):
    """Checks if a website or local API is responding (HTTP 200)."""
    try:
        if not url.startswith('http'):
            url = f"http://{url}"
        response = requests.get(url, timeout=5)
        return f"Network Site Status: {url} is {response.status_code} (OK)."
    except Exception as e:
        return f"Network Site Link Failure: {str(e)}"

def get_local_ip():
    """Retrieves the local network IP address of the OS."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return f"System IP: {ip}"
    except Exception:
        return "Network: Unable to retrieve local IP."

def scan_port(host, port):
    """Checks if a specific network port is open/listening on a host."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, int(port)))
        sock.close()
        return f"Network Port {port} on {host}: {'OPEN' if result == 0 else 'CLOSED'}"
    except Exception as e:
        return f"Network Port Error: {str(e)}"
