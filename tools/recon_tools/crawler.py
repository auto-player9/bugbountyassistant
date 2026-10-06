import subprocess
import os
import config
from core.logger import logger
from tools.recon_tools.target_manager import get_active_target
import tkinter as tk
from tkinter import simpledialog

def run_crawl(use_session=False):
    target = get_active_target()
    if not target:
        return "[-] Error: No active target set."

    # Target Logic: Handling Wildcards vs Direct URLs
    final_url = target
    if "*" in target:
        root = tk.Tk()
        root.withdraw()
        base_domain = target.replace("*.", "").replace("*", "")
        subdomain = simpledialog.askstring("Crawl Target", f"Enter subdomain for {base_domain} (Leave blank for main domain):")
        final_url = f"{subdomain.strip()}.{base_domain}" if subdomain else base_domain
        root.destroy()
    
    if not final_url.startswith("http"):
        final_url = f"https://{final_url}"

    # Prepare output paths
    os.makedirs(config.CRAWL_RESULTS_DIR, exist_ok=True)
    filename = final_url.split("//")[-1].replace(".", "_").replace("/", "")
    output_file = os.path.join(config.CRAWL_RESULTS_DIR, f"{filename}_crawl.txt")

    unique_urls = set()

    try:
        logger.info(f"Starting crawl for: {final_url}")

        # 1. Waybackurls execution
        logger.info("Executing Waybackurls...")
        wayback_proc = subprocess.Popen(['echo', final_url], stdout=subprocess.PIPE)
        wayback_out = subprocess.check_output([config.WAYBACKURLS_PATH], stdin=wayback_proc.stdout)
        unique_urls.update(wayback_out.decode().splitlines())

        # 2. GoSpider execution
        logger.info("Executing GoSpider...")
        gospider_cmd = [config.GOSPIDER_PATH, "-s", final_url, "-w", "--include-subs"]
        
        # Add Session Cookies if authenticated crawl is requested
        if use_session:
            from core.requester import request_engine
            cookie_dict = request_engine.session.cookies.get_dict()
            cookie_str = "; ".join([f"{k}={v}" for k, v in cookie_dict.items()])
            if cookie_str:
                gospider_cmd.extend(["--cookie", cookie_str])
                logger.info("Session cookies injected into crawler.")

        gospider_out = subprocess.check_output(gospider_cmd)
        
        # Parse GoSpider output to extract URLs only
        for line in gospider_out.decode().splitlines():
            if "[url]" in line or "[href]" in line:
                extracted_url = line.split("-")[-1].strip()
                unique_urls.add(extracted_url)

        # 3. Save unique results (Removes duplicates automatically via set)
        with open(output_file, "w") as f:
            for url in sorted(unique_urls):
                if url.strip():
                    f.write(url + "\n")

        return f"[+] Success: {len(unique_urls)} unique URLs saved to {output_file}"

    except Exception as e:
        logger.error(f"Crawl process failed: {str(e)}")
        return f"[-] Error: {str(e)}"