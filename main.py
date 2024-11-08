import os
import logging
from app.port_knocker import MainWindow
from app.port_utils import trigger_firewall_prompt
from config.logging_config import setup_logging
from config.config import DebugConfig, ReleaseConfig
from resources.resources import qInitResources, qCleanupResources
from PySide6 import QtWidgets


if __name__ == "__main__":
    config = DebugConfig if os.getenv("DEBUG") == "True" else ReleaseConfig()

    if config.DEBUG:
        print("Running in debug mode")

    setup_logging(config)

    logging.info("Loading resources.")
    qInitResources()

    try:
        trigger_firewall_prompt()

        app = QtWidgets.QApplication()

        window = MainWindow()
        window.show()
        window.ui.lineEdit.setFocus()
        
        app.exec()
    except Exception as e:
        logging.error(f"An error occurred during application startup: {e}")
    finally:
        logging.info("Cleaning up resources.")
        qCleanupResources()