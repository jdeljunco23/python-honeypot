import socket
import json
import datetime
import threading
from config.settings import BIND_IP, DEFAULT_PORTS, LOG_DIR
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

            if port == 21:
                self.handle_ftp(client_socket, remote_ip)
            elif port == 22:
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

    def handle_ftp(self, client_socket, remote_ip):
        """Handle FTP interactions with buffered input for telnet compatibility."""
        try:
            client_socket.send(b"220 Fake FTP Server Ready\r\n")
            buffer = ""  # Buffer to accumulate input

            while True:
                chunk = client_socket.recv(1).decode("utf-8", errors="ignore")
                if not chunk:
                    break
                buffer += chunk

                if buffer.endswith("\r\n") or buffer.endswith("\n"):
                    data = buffer.strip()
                    buffer = ""
                    self.log_activity(21, remote_ip, data.encode())

                    if data.startswith("USER"):
                        username = data.split()[1]
                        ftp_sessions[remote_ip] = {"username": username}
                        client_socket.send(b"331 User name okay, need password.\r\n")
                    elif data.startswith("PASS") and remote_ip in ftp_sessions:
                        ftp_sessions[remote_ip]["authenticated"] = True
                        client_socket.send(b"230 User logged in, proceed.\r\n")
                    elif data.startswith("PASS") and remote_ip not in ftp_sessions:
                        client_socket.send(b"503 Login with USER first.\r\n")
                    elif data.upper() == "LIST":
                        client_socket.send(b"150 Here comes the directory listing.\r\n")
                        fake_files = [
                            "-rw-r--r-- 1 user group 123 Jan 01 12:34 malware.exe",
                            "-rw-r--r-- 1 user group 456 Jan 02 10:15 config.txt"
                        ]
                        for file in fake_files:
                            client_socket.send(f"{file}\r\n".encode())
                        client_socket.send(b"226 Directory send okay.\r\n")
                    elif data.upper() == "QUIT":
                        client_socket.send(b"221 Goodbye.\r\n")
                        break
                    else:
                        client_socket.send(b"500 Command not understood.\r\n")
        except Exception as e:
            print(f"[ERROR] Exception during FTP handling: {e}")
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
