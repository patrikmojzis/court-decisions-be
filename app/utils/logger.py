import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger(module_name):
    # Create logs directory
    os.makedirs("logs", exist_ok=True)

    # Get logger for the module
    logger = logging.getLogger(module_name)

    # Avoid adding handlers multiple times
    if not logger.handlers:
        # Create rotating file handler
        file_handler = RotatingFileHandler(
            os.path.join(os.getcwd(), 'logs', f"{module_name}.log"),
            maxBytes=1024 * 1024,
            backupCount=5
        )

        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)  # Set appropriate level

    return logger