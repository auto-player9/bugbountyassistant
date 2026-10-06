from tools.recon_tools.header_discovery import run_header_discovery
from tools.recon_tools.target_manager import set_active_target, get_active_target
from tools.recon_tools.crawler import run_crawl
from tools.recon_tools.sub_enum import run_sub_enumeration

class ReconToolsManager:
    def update_target_scope(self, target: str):
        """
        Sets the global target scope (URL or Wildcard). 
        This will overwrite any previous target stored in the system.
        """
        return set_active_target(target)

    def get_current_target(self):
        """
        Retrieves the current active target from storage.
        """
        target = get_active_target()
        if target:
            return f"[+] Currently auditing: {target}"
        return "[-] No active target found in storage."
    
    def start_crawl(self, authenticated: bool = False):
        """
        Runs GoSpider and Waybackurls on the active target.
        Use authenticated=True to include current session cookies.
        """
        return run_crawl(use_session=authenticated)
    
    def start_sub_enum(self):
        """
        Runs Amass, Subfinder, and Assetfinder, then filters through httpx.
        Only works if the target is a wildcard.
        """
        return run_sub_enumeration()
    
    def start_header_discovery(self, url: str, method: str = "GET", use_session: bool = False):
        """
        Discovers hidden headers on the specified URL.
        """
        return run_header_discovery(url=url, method=method, use_session=use_session)
    
    