# **Python Honeypot**

A lightweight, customizable honeypot written in Python to simulate and monitor malicious activity on various network protocols, including HTTP, SSH, and FTP.

## **Features**
- **HTTP Honeypot**: Simulates a basic web server with customizable responses.
- **SSH Honeypot**: Mimics an SSH server with fake authentication and command logging.
- **FTP Honeypot**: Emulates an FTP server, logging commands and interactions.
- **Activity Logging**: Captures and stores all interactions in a `logging.json` file for analysis.
- **Network Monitoring**: Tracks connections and logs suspicious behavior.

## **Getting Started**
### Prerequisites
- Python 3.8+
- Installed dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### Installation
1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd python-honeypot
   ```
2. (Optional) Create and activate a virtual environment:
   ```bash
   # Create a virtual environment
   python -m venv venv

   # Activate the virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Honeypot
1. Start the honeypot:
   ```bash
   python honeypot.py
   ```
2. The honeypot listens on:
   - **Port 21**: FTP
   - **Port 22**: SSH
   - **Port 80/443**: HTTP/HTTPS

### Deployment with Docker
1. Ensure Docker is installed and running on your system.
2. Build and start the Docker containers:
   ```bash
   docker compose -f docker/docker-compose.yml up -d --build
   ```
3. The honeypot will run in a Docker container, listening on:
   - **Port 21**: FTP
   - **Port 22**: SSH
   - **Port 80**: HTTP
   - **Port 443**: HTTPS

### Configuration
- Modify `config/settings.py` to adjust:
  - Listening IPs and ports.
  - Logging directory.
  - Blacklist for blocking specific IPs.

## **Usage**
- Simulate network services and log malicious interactions.
- Monitor attacker behavior for research or security purposes.
- Analyze logs for patterns and insights.

## **Limitations**
- **Sandboxing**: Ensure the honeypot runs in an isolated environment (e.g., VM or Docker) to avoid exposing your host system.
- **Detection**: Advanced attackers may identify the honeypot. Ensure configurations mimic real-world services.

## **Planned Enhancements**
- Dockerize the honeypot.
- Build a dashboard for monitoring and visualization.
- Implement SMTP and DNS protocols.

