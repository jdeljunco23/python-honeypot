def get_service_banner(port):
    """Return the appropriate banner for a given port."""
    service_banners = {
        21: "220 FTP server ready\r\n",
        22: "SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.1\r\n",
        80: "HTTP/1.1 200 OK\r\nServer: Apache/2.4.41 (Ubuntu)\r\n\r\n",
        443: "HTTP/1.1 200 OK\r\nServer: Apache/2.4.41 (Ubuntu)\r\n\r\n"
    }
    return service_banners.get(port, None)
