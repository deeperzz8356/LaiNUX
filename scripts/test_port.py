import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.bind(('0.0.0.0', 8000))
    print("Successfully bound to 0.0.0.0:8000")
    s.close()
except Exception as e:
    print(f"Failed to bind: {e}")
