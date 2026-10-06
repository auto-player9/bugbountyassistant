import os
import config
from core.logger import logger

TARGET_FILE = os.path.join(config.STORAGE_DIR, "active_target.txt")

def set_active_target(target):
    try:
        os.makedirs(os.path.dirname(TARGET_FILE), exist_ok=True)
        with open(TARGET_FILE, "w") as f:
            f.write(target.strip())
        logger.info(f"Target scope updated: {target}")
        return f"[+] Target scope successfully updated to: {target}"
    except Exception as e:
        return f"[-] File Error: {str(e)}"

def get_active_target():
    if os.path.exists(TARGET_FILE):
        with open(TARGET_FILE, "r") as f:
            return f.read().strip()
    return None