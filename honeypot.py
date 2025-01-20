from services.socket_server import Honeypot

if __name__ == "__main__":
    try:
        print("Starting Honeypot...")
        honeypot = Honeypot()
        honeypot.start()
    except KeyboardInterrupt:
        print("\nShutting down Honeypot...")
