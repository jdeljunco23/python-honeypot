import socket
import json
import datetime
import threading
from config.settings import BIND_IP, DEFAULT_PORTS, LOG_DIR
from twisted.internet import reactor
from services.ftp_handler import SimpleFTPFactory
from services.emulation import get_service_banner
from services.ssh_handler import handle_ssh

ftp_sessions = {}
blacklist = ["192.168.1.100", "10.0.0.200"]

class Honeypot:
    def __init__(self, bind_ip=BIND_IP, ports=None):
        self.bind_ip = bind_ip
        self.ports = ports or DEFAULT_PORTS
        self.active_connections = {}
        self.log_file = LOG_DIR / f"honeypot_{datetime.datetime.now().strftime('%Y%m%d')}.json"

        LOG_DIR.mkdir(exist_ok=True)

    def log_activity(self, port, remote_ip, data):
        """Log suspicious activity with timestamp and details."""
        activity = {
            "timestamp": datetime.datetime.now().isoformat(),
            "remote_ip": remote_ip,
            "port": port,
            "data": data.decode('utf-8', errors='ignore')
        }
        try:
            with open(self.log_file, 'a') as f:
                json.dump(activity, f)
                f.write('\n')
        except Exception as e:
            print(f"[ERROR] Failed to write to log file: {e}")

    def handle_connection(self, client_socket, remote_ip, port):
        """Handle individual connections and emulate services."""
        try:
            if remote_ip in blacklist:
                client_socket.send(b"Connection refused.\r\n")
                client_socket.close()
                return

            if port == 22:
                handle_ssh(client_socket, remote_ip, self.log_activity)
            elif port in [80, 443]:
                self.handle_http(client_socket, remote_ip, port)
            else:
                banner = get_service_banner(port)
                if banner:
                    client_socket.send(banner.encode())

                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    self.log_activity(port, remote_ip, data)
                    client_socket.send(b"Command not recognized.\r\n")
        except Exception as e:
            print(f"[ERROR] Error handling connection from {remote_ip}: {e}")
        finally:
            client_socket.close()

    def handle_http(self, client_socket, remote_ip, port):
        """Handle HTTP/HTTPS interactions."""
        request = client_socket.recv(1024).decode("utf-8", errors="ignore")
        self.log_activity(port, remote_ip, request.encode())

        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html\r\n"
            "Content-Length: 92\r\n\r\n"
            "<html><body><h1>Welcome to the Honeypot!</h1><p>This is a fake web server.</p></body></html>"
        )
        client_socket.send(response.encode())
        
    def listen_on_port(self, port):
        """Listen for connections on a specific port."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.bind_ip, port))
            server_socket.listen(5)
            while True:
                client_socket, client_address = server_socket.accept()
                threading.Thread(
                    target=self.handle_connection,
                    args=(client_socket, client_address[0], port)
                ).start()

    def start_ftp_service(self):
        """Start the Twisted-based FTP honeypot."""
        ftp_factory = SimpleFTPFactory(self.log_activity)
        reactor.listenTCP(21, ftp_factory, interface="0.0.0.0")
        reactor.run(installSignalHandlers=False)

    def start(self):
        """Start the honeypot on all configured ports."""
        # Start FTP in a separate thread
        ftp_thread = threading.Thread(target=self.start_ftp_service, daemon=True)
        ftp_thread.start()

        # Start other ports (SSH, HTTP)
        threads = []
        for port in self.ports:
            if port != 21:  # FTP handled by Twisted
                thread = threading.Thread(target=self.listen_on_port, args=(port,))
                thread.daemon = True
                thread.start()
                threads.append(thread)

        try:
            while True:
                pass
        except KeyboardInterrupt:
            print("\nShutting down Honeypot...")
            reactor.stop()
