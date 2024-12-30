import socket
import json
import datetime
import threading
from config.settings import BIND_IP, DEFAULT_PORTS, LOG_DIR
from services.emulation import get_service_banner

class Honeypot:
    def __init__(self, bind_ip=BIND_IP, ports=None):
        self.bind_ip = bind_ip
        self.ports = ports or DEFAULT_PORTS
        self.active_connections = {}
        self.log_file = LOG_DIR / f"honeypot_{datetime.datetime.now().strftime('%Y%m%d')}.json"

    def log_activity(self, port, remote_ip, data):
        """Log suspicious activity with timestamp and details."""
        activity = {
            "timestamp": datetime.datetime.now().isoformat(),
            "remote_ip": remote_ip,
            "port": port,
            "data": data.decode('utf-8', errors='ignore')
        }

        with open(self.log_file, 'a') as f:
            json.dump(activity, f)
            f.write('\n')

    def handle_connection(self, client_socket, remote_ip, port):
        """Handle individual connections and emulate services."""
        try:
            # Get and send the banner for the current port
            banner = get_service_banner(port)
            if banner:
                client_socket.send(banner.encode())

            # Receive data from the attacker
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break

                self.log_activity(port, remote_ip, data)
                client_socket.send(b"Command not recognized.\r\n")

        except Exception as e:
            print(f"Error handling connection from {remote_ip}: {e}")
        finally:
            client_socket.close()

    def listen_on_port(self, port):
        """Listen for connections on a specific port."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.bind_ip, port))
            server_socket.listen(5)
            print(f"Listening on port {port}...")
            while True:
                client_socket, client_address = server_socket.accept()
                print(f"Connection from {client_address}")
                threading.Thread(
                    target=self.handle_connection,
                    args=(client_socket, client_address[0], port)
                ).start()

    def start(self):
        """Start the honeypot on all configured ports."""
        threads = []
        for port in self.ports:
            thread = threading.Thread(target=self.listen_on_port, args=(port,))
            thread.daemon = True  # Make the thread a daemon
            thread.start()
            threads.append(thread)

        # Keep the main thread alive to handle KeyboardInterrupt
        try:
            while True:
                pass
        except KeyboardInterrupt:
            print("\nShutting down Honeypot...")


