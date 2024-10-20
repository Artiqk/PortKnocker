import logging
import sys

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,  # Adjust this to change the default log level
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stderr),  # Log to standard error
            # logging.FileHandler('app.log', mode='a'),
        ]
    )