from pathlib import Path

# Default IP and ports
BIND_IP = "0.0.0.0"
DEFAULT_PORTS = [21, 22, 80, 443]

# Log directory
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
