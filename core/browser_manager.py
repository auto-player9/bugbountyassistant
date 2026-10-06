from playwright.sync_api import sync_playwright
from core.logger import logger
import tkinter as tk 
from tkinter import messagebox, simpledialog
import re

class BrowserManager:
    def __init__(self):
        self.headless = False

    def capture_cookies_interactively(self, target_url=None):
        """
        Launches browser for manual login. 
        Handles Wildcards by prompting for subdomains.
        """
        # If no URL is passed, try to fetch the stored active target
        if not target_url:
            from tools.recon_tools.target_manager import get_active_target
            target_url = get_active_target()
            if not target_url:
                return "[-] No target specified and no active target found."

        # Wildcard Handling Logic
        final_url = target_url
        if "*" in target_url:
            root = tk.Tk()
            root.withdraw()
            
            # Extract the base domain (e.g., from *.example.com to example.com)
            base_domain = target_url.replace("*.", "").replace("*", "")
            
            # Prompt the user for a specific subdomain
            subdomain = simpledialog.askstring("Subdomain Required",  f"Target is a Wildcard: {target_url}\nEnter subdomain (leave blank for base domain):")
            
            if subdomain:
                # Construct the subdomain URL (ensuring it has a protocol)
                if not subdomain.startswith("http"):
                    final_url = f"https://{subdomain.strip()}.{base_domain}"
                else:
                    final_url = subdomain # User entered full URL
            else:
                # Default to base domain
                final_url = f"https://{base_domain}" if not base_domain.startswith("http") else base_domain
            
            root.destroy()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context()
            page = context.new_page()

            logger.info(f"Navigating to: {final_url} for session sync.")
            page.goto(final_url)

            print(f"\n[!] Browser opened at: {final_url}")
            input(">>> Press ENTER in this terminal AFTER successful login to capture cookies...")

            cookies = context.cookies()
            logger.info("Session cookies successfully extracted.")

            # GUI Confirmation
            root = tk.Tk()
            root.withdraw()
            response = messagebox.askyesno("Capture Success", "Cookies captured! Close browser?")
            if response: browser.close()
            root.destroy()

            return cookies