from core.logger import logger
from core.requester import request_engine
from core.browser_manager import BrowserManager
from tools.web_tools.jwt_tool.wrapper import JWTToolWrapper
import tools.web_tools.basic_tools as basic
from tools.web_tools.audit import run_sequential_audit_logic
from tools.web_tools.sqlmap_tool import run_sqlmap_scan
from tools.recon_tools.target_manager import get_active_target
from tools.web_tools.param_miner import run_param_discovery
from tools.web_tools.dir_discovery import run_dir_discovery
from tools.web_tools.file_discovery import run_file_discovery

class WebToolsManager:
    def __init__(self):
        self.browser = BrowserManager()
        self.jwt_wrapper = JWTToolWrapper()

    def login_and_capture_session(self):
            """
            Technical Flow: 
            1. Open Browser -> 2. Manual Login -> 3. Capture Cookies -> 4. Sync with Requester
            """
            target = get_active_target()
            if not target:
                return "[-] Error: No target set. Run update_target_scope first."
            
            logger.info(f"Initiating interactive login for: {target}")
    
            cookies = self.browser.capture_cookies_interactively(target)
            
            if cookies:
                request_engine.update_cookies(cookies)
                return f"[+] Session for {target} captured and synchronized successfully."
            
            return "[-] Failed to capture session."
    
    def run_jwt_test(self, target_url: str):
        """
        Logic: Find JWT in current session and run full suite.
        """
        return self.jwt_wrapper.run_full_test(target_url)

    def get_system_info(self):
        """
        Wrapper for basic system tools.
        """
        return basic.get_system_user()

    def isolate_identity(self, target_url: str):
        """
        Wrapper for cookie isolation logic.
        """
        return basic.isolate_identity_cookie(target_url)

    def get_cookies_list(self):
        """
        Wrapper for get cookies list.
        """
        return basic.list_captured_cookies()

    def get_raw_cookies(self):
        """
        Returns full, un-truncated cookie values for manual analysis.
        """
        return basic.get_raw_cookies()

    def run_sequential_audit(self, assistant_instance):
        """
        Wrapper for Sequential Audit.
        Passes the assistant context to the logic engine.
        """
        return run_sequential_audit_logic(assistant_instance)

    def run_sqlmap_auto(self, url: str = None, use_request_file: bool = False, parameter: str = None, tamper: str = None, risk: int = 1, level: int = 1):
        """
        Advanced SQL Injection Detection & Exploitation Engine.

        This tool automates the discovery of SQLi vulnerabilities by orchestrating sqlmap 
        sessions. It supports both direct URL targeting and raw HTTP request file processing 
        for complex adversarial testing (e.g., bypassing WAFs or testing authenticated POST bodies).

        Args:
            url (str, optional): The target URI for standard GET-based analysis. Required if use_request_file is False.
            use_request_file (bool): If True, the engine processes the raw HTTP request stored in 
            config.SQLMAP_REQUEST_FILE (-r). Ideal for POST requests and custom headers.
            parameter (str, optional): Targeted HTTP parameter(s) to isolate for testing (e.g., 'id,session_id'). 
            Equivalent to sqlmap '-p' flag.
            tamper (str, optional): Comma-separated list of sqlmap evasion scripts (e.g., 'space2comment,randomcase') 
            used to bypass signature-based WAF/IPS protections.
            risk (int): Risk level (1-3) for testing depth. Higher values add heavy payloads that may 
            impact DB integrity. (Default: 1).
            level (int): Level of tests to perform (1-5). Higher levels expand the test scope to include 
            HTTP headers like Cookies and User-Agent. (Default: 1).

        Returns:
            str: Technical summary of findings, including vulnerable payloads or paths to detailed logs.
        """
        from tools.web_tools.sqlmap_tool import run_sqlmap_scan
        mode = "file" if use_request_file else "url"
        
        return run_sqlmap_scan(
            mode=mode, 
            target_url=url, 
            p_var=parameter, 
            tamper=tamper, 
            risk=risk, 
            level=level
        )
        
    def find_hidden_params(self, url: str, method: str = "GET", authenticated: bool = False):
        """
        Scans a URL for hidden parameters using x8 and Arjun.
        Useful for finding IDOR, Mass Assignment, or hidden debug flags.
        """
        return run_param_discovery(url, method, authenticated)
    
    def start_dir_discovery(self, url: str, filter_size: int = None, filter_words: int = None):
        """
        Runs ffuf to discover hidden directories with optional WAF filtering.
        """
        return run_dir_discovery(url, filter_size=filter_size, filter_words=filter_words)
    
    def start_file_discovery(self, url: str, filter_size: int = None, filter_words: int = None):
        """
        Runs ffuf to discover hidden files with optional WAF filtering.
        """
        return run_file_discovery(url, filter_size=filter_size, filter_words=filter_words)