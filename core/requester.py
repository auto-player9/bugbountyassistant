import requests
from config import USER_AGENT, DEFAULT_TIMEOUT, USE_PROXY, PROXIES
from core.logger import logger  

class Requester:
    def __init__(self):
        # Initialize a persistent session to maintain cookies and connection pooling
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        
        # Proxy configuration for intercepting traffic (e.g., with Burp Suite)
        if USE_PROXY:
            self.session.proxies.update(PROXIES)
            # Disable SSL verification to prevent errors with self-signed proxy certificates
            self.session.verify = False 
            # Modification 2: Suppress insecure request warnings when using proxies
            requests.packages.urllib3.disable_warnings()

    def send_request(self, method, url, **kwargs):
        """
        A wrapper for requests.request to provide global timeout and error handling.
        """
        if "timeout" not in kwargs:
            kwargs["timeout"] = DEFAULT_TIMEOUT

        try:
            response = self.session.request(method, url, **kwargs)
            return response
        except requests.exceptions.RequestException as e:
            # Modification 3: Use the logger instead of print for consistent debugging
            logger.error(f"HTTP Request Failed: {e}")
            return None

    def update_cookies(self, playwright_cookies):
        """
        Synchronizes cookies captured from the Playwright browser into the Requests session.
        """
        for cookie in playwright_cookies:
            # Mapping Playwright's dictionary format to Requests' cookie jar
            self.session.cookies.set(
                name=cookie['name'], 
                value=cookie['value'], 
                domain=cookie.get('domain', '')
            )
        logger.info("Session cookies successfully updated from browser memory.")

# Singleton instance: ensures all tools share the same session and cookies
request_engine = Requester()