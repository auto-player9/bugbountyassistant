import logging
import os
from datetime import datetime
from config import LOGS_DIR

class Logger:
    def __init__(self, name="Assistant"):
        # 1. Create a logger object
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # 2. Create the format for logs (Timestamp - Name - Level - Message)
        log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # 3. Console Handler (Printing to Terminal)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_format)
        self.logger.addHandler(console_handler)

        # 4. File Handler (Saving to storage/logs/)
        log_filename = f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_path = os.path.join(LOGS_DIR, log_filename)
        
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(log_format)
        self.logger.addHandler(file_handler)

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)

    def warning(self, message):
        self.logger.warning(message)

# Singleton instance
logger = Logger()