from twisted.internet import protocol
from twisted.protocols import basic
from twisted.python import log

class SimpleFTPProtocol(basic.LineReceiver):
    delimiter = b"\r\n"
    maxAttempts = 3

    def __init__(self):
        self.attempts = 0
        self.userReceived = False
        self.authenticated = False
        self.current_user = None

    def connectionMade(self):
        log.msg(f"FTP NEW Connection - Client IP: {self.client_ip}")
        if hasattr(self, "log_activity"):
            self.log_activity(21, self.client_ip, b"New FTP connection established.")
        self.sendLine(b"220 Welcome to the FTP Honeypot")

    def lineReceived(self, line):
        line_str = line.decode("utf-8", errors="ignore").strip()
        log.msg(f"Raw command received: {line}")
        log.msg(f"Decoded command: {line_str}")

        # Get client details
        client_ip = self.transport.getPeer().host
        port = 21

        # Log all received commands
        if hasattr(self, "log_activity"):
            self.log_activity(port, client_ip, f"Command received: {line_str}".encode())

        # Split command into verb and arguments
        parts = line_str.split(" ", 1)
        command = parts[0].upper()
        argument = parts[1] if len(parts) > 1 else None

        if command == "USER":
            self.userReceived = True
            self.current_user = argument  # Store the username
            self.sendLine(b"331 Username okay, need password")
        elif command == "PASS" and self.userReceived:
            if self.current_user == "testuser" and argument == "testpassword":
                self.authenticated = True
                self.sendLine(b"230 Login successful")
            else:
                self.sendLine(b"530 Login incorrect")
                self.userReceived = False  # Reset authentication flow
        elif command == "QUIT":
            log.msg("FTP QUIT command received. Closing connection.")
            self.sendLine(b"221 Goodbye.")
            self.transport.loseConnection()
        else:
            log.msg(f"Unhandled command: {command}")
            self.sendLine(b"500 Syntax error, command unrecognized")

    def sendLine(self, line):
        """Send a line to the client."""
        self.transport.write(line + self.delimiter)

    def connectionLost(self, reason):
        log.msg("Connection lost")


class SimpleFTPFactory(protocol.ServerFactory):
    def __init__(self, log_activity):
        self.log_activity = log_activity

    def buildProtocol(self, addr):
        protocol = SimpleFTPProtocol()
        protocol.log_activity = self.log_activity
        protocol.client_ip = addr.host
        return protocol
