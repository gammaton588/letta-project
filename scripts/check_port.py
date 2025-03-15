import socket

def check_port_open(host, port):
    try:
        with socket.create_connection((host, port), timeout=2) as sock:
            print(f"Port {port} on {host} is open and reachable.")
            return True
    except (socket.timeout, ConnectionRefusedError):
        print(f"Port {port} on {host} is NOT open or is not reachable.")
        return False

host = "127.0.0.1" # Localhost IP
port = 8283

check_port_open(host,port)
