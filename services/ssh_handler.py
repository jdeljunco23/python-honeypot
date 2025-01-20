import paramiko

# Save key (run this once)
HOST_KEY = paramiko.RSAKey.generate(2048)
HOST_KEY.write_private_key_file("server.key")

# Load key
HOST_KEY = paramiko.RSAKey(filename="server.key")


class SSHServer(paramiko.ServerInterface):
    """Custom SSH Server Interface to handle SSH interactions."""
    def __init__(self, remote_ip, log_activity):
        self.remote_ip = remote_ip
        self.log_activity = log_activity
        self.authenticated = False

    def check_auth_password(self, username, password):
        """Simulate authentication."""
        print(f"[DEBUG] Login attempt from {self.remote_ip}: {username}/{password}")
        self.log_activity(22, self.remote_ip, f"Login attempt: {username}/{password}".encode())
        
        # Match fake credentials
        if username == "testuser" and password == "testpassword":
            print("[DEBUG] Authentication successful")
            self.authenticated = True
            return paramiko.AUTH_SUCCESSFUL
        
        print("[DEBUG] Authentication failed")
        return paramiko.AUTH_FAILED


    def check_channel_request(self, kind, chanid):
        """Allow only session channels."""
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_shell_request(self, channel):
        """Acknowledge shell requests."""
        return True

def handle_ssh(client_socket, remote_ip, log_activity):
    """Handle SSH connections using Paramiko."""
    transport = paramiko.Transport(client_socket)
    transport.add_server_key(HOST_KEY)

    server = SSHServer(remote_ip, log_activity)
    try:
        print("[DEBUG] Starting SSH transport")
        transport.start_server(server=server)
        print("[DEBUG] Waiting for channel")
        channel = transport.accept(20)  # Wait for client channel
        if channel is None:
            print(f"[DEBUG] No channel was opened by {remote_ip}")
            return
        print("[DEBUG] Channel successfully opened")


        # Send welcome message
        channel.send("Welcome to the fake SSH server!\nType 'exit' to disconnect.\n")

        while True:
            data = channel.recv(1024).decode("utf-8").strip()
            if not data:
                break

            # Log the received command
            log_activity(22, remote_ip, data.encode())

            if data == "exit":
                channel.send("Goodbye!\n")
                break
            elif data == "ls":
                channel.send("file1.txt\nfile2.txt\nscript.sh\n")
            elif data == "pwd":
                channel.send("/home/fake_user\n")
            else:
                channel.send(f"Command '{data}' not recognized.\n")
    except Exception as e:
        print(f"[SSH] Error with {remote_ip}: {e}")
    finally:
        transport.close()
        client_socket.close()
