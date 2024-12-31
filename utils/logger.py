import logging

def setup_logger():
    """
    Sets up the logger to handle both console and file outputs.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("honeypot.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger()
