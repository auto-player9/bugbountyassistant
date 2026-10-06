import subprocess
import os
import re 
from core.logger import logger
from core.requester import request_engine

class JWTToolWrapper:
    def __init__(self):
        self.script_path = os.path.join(os.path.dirname(__file__), "jwt_tool.py")
        self.loot_dir = "storage/loot/jwt/"
        os.makedirs(self.loot_dir, exist_ok=True)

    def extract_jwt_from_session(self):
        """
        Technical Scanning: Search for JWT patterns in the current session cookies.
        JWTs typically start with 'eyJ' (Base64 for {"alg"...)
        """
        # Get cookies from our singleton request engine
        cookies_dict = request_engine.session.cookies.get_dict()
        
        # Regex to find JWT pattern: Header.Payload.Signature
        jwt_pattern = r"eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*"
        
        for name, value in cookies_dict.items():
            if re.match(jwt_pattern, value):
                logger.info(f"JWT found in cookie: {name}")
                return value
        
        logger.warning("No JWT found in the current session cookies.")
        return None

    def run_full_test(self, target_url):
        """
        The 'Nuclear' Option: Finds the token and runs ALL jwt_tool tests.
        """
        # 1. Automatically find the token
        token = self.extract_jwt_from_session()
        
        if not token:
            logger.error("Scan aborted: No JWT detected to test.")
            return None

        # 2. Prepare the command with ALL tests (-A for All, -M for Mode)
        # We use -M at for analysis and -A for all known common attacks
        command = ["python3", self.script_path, token, "-M", "at", "-A"]

        logger.info(f"Launching Full JWT Attack Suite against: {target_url}")

        try:
            # Running the process and piping output back to our system
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"Execution failed: {e.stderr}")
            return None