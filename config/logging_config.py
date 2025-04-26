import logging
import sys

def setup_logging(config = ''):
    handlers = [logging.StreamHandler(sys.stderr)]

    if config == 'DEBUG':
        handlers.append(logging.FileHandler('./logs/app.log', mode='a'))

    logging.basicConfig(
        level=logging.DEBUG if config == 'DEBUG' else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )