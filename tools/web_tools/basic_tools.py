import subprocess
import requests
from core.logger import logger
from core.requester import request_engine

def get_system_user() -> str:
    """Executes whoami to get current OS user."""
    try:
        username = subprocess.check_output(['whoami'], text=True).strip()
        logger.info(f"System identity retrieved: {username}")
        return f"Current System User: {username}"
    except Exception as e:
        logger.error(f"Failed to execute whoami: {str(e)}")
        return f"Error: {str(e)}"

def list_captured_cookies() -> str:
    """Lists current session cookies with secure masking."""
    captured_cookies = request_engine.session.cookies.get_dict()
    
    if not captured_cookies:
        logger.warning("Session is empty.")
        return "No cookies found. Login required."

    output = "\n[+] Captured Session Cookies:\n"
    for name, value in captured_cookies.items():
        # Masking for security
        output += f"    - {name}: {value[:15]}...\n"
    
    return output

def get_raw_cookies() -> str:
    """Returns full, un-truncated cookie values for manual analysis."""
    captured_cookies = request_engine.session.cookies.get_dict()
    if not captured_cookies:
        return "No cookies found in session."

    output = "\n[!] RAW SESSION DATA (CRITICAL):\n"
    for name, value in captured_cookies.items():
        output += f"--- {name} ---\n{value}\n\n"
    
    logger.info("Raw cookies exported to terminal.")
    return output

def isolate_identity_cookie(target_url: str):
    """Differential analysis to identify critical identity cookies."""
    current_cookies = request_engine.session.cookies.get_dict()
    if not current_cookies:
        return "Error: No cookies to test."

    important_cookies = {}
    for cookie_name, cookie_value in current_cookies.items():
        test_cookies = current_cookies.copy()
        del test_cookies[cookie_name]
        try:
            # Differential testing logic
            response = requests.get(
                target_url, 
                cookies=test_cookies, 
                headers=request_engine.session.headers,
                timeout=10, 
                allow_redirects=False
            )
            # If status changes, cookie is essential (Critical Path)
            if response.status_code != 200:
                important_cookies[cookie_name] = cookie_value
        except Exception as e:
            logger.error(f"Isolation failure: {str(e)}")
            return f"Connection Error: {str(e)}"

    if important_cookies:
        return f"Isolated Essential Cookies: {important_cookies}"
    return "No single essential identity cookie identified."

