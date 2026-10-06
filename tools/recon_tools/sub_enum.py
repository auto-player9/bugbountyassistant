import subprocess
import os
import config
from core.logger import logger
from tools.recon_tools.target_manager import get_active_target
from tools.recon_tools.visualizer import run_visual_recon

def run_sub_enumeration():
    # Retrieve the current active target from the scope manager
    target = get_active_target()
    
    # Validation: Ensure the target is a wildcard (e.g., *.example.com)
    if not target or "*" not in target:
        return "[-] Error: Target must be a wildcard (e.g., *.example.com) for enumeration."

    # Extract the base domain by removing wildcard characters
    domain = target.replace("*.", "").replace("*", "")
    
    # Ensure the results directory exists as defined in config
    os.makedirs(config.SUB_RESULTS_DIR, exist_ok=True)
    
    # Define file paths for raw and filtered (live) results
    raw_subs_file = os.path.join(config.SUB_RESULTS_DIR, f"{domain}_raw.txt")
    final_subs_file = os.path.join(config.SUB_RESULTS_DIR, f"{domain}_live.txt")
    
    # Use a set to automatically handle unique subdomains and prevent duplicates
    all_subs = set()

    # Tool configuration list
    # Note: Added -timeout to Amass to ensure it exits gracefully before the Python timeout
    tools = [
        {"name": "Subfinder", "cmd": [config.SUBFINDER_PATH, "-d", domain, "-silent"]},
        {"name": "Assetfinder", "cmd": [config.ASSETFINDER_PATH, "--subs-only", domain]},
        {"name": "Amass", "cmd": [config.AMASS_PATH, "enum", "-passive", "-d", domain]}
    ]

    # Iterate through each tool and execute
    for tool in tools:
        try:
            logger.info(f"Running {tool['name']}...")
            
            # Execute command with a timeout to prevent the bot from hanging on stalled processes
            result = subprocess.run(
                tool['cmd'], 
                capture_output=True, 
                text=True, 
                timeout=660  # 11-minute safety limit per tool
            )
            
            # If the tool exits successfully (return code 0)
            if result.returncode == 0:
                # Clean up results: strip whitespace and ignore empty lines
                subs = [s.strip() for s in result.stdout.splitlines() if s.strip()]
                all_subs.update(subs)
                logger.info(f"[+] {tool['name']} found {len(subs)} subdomains.")
            else:
                # Log a warning if a tool fails but continue with the others
                logger.warning(f"[!] {tool['name']} returned error code {result.returncode}. Skipping...")
                
        except subprocess.TimeoutExpired:
            logger.warning(f"[!] {tool['name']} timed out after 11 minutes. Moving to next tool.")
        except Exception as e:
            logger.error(f"[-] {tool['name']} execution failed: {str(e)}")

    # Check if any subdomains were found before proceeding to filtering
    if not all_subs:
        return "[-] Enumeration failed: No subdomains were discovered by any tool."

    # Store raw unique results
    unique_subs = sorted(list(all_subs))
    with open(raw_subs_file, "w") as f:
        f.write("\n".join(unique_subs))
    
    logger.info(f"[+] Total unique subdomains gathered: {len(unique_subs)}")

    # Phase 2: Filter live subdomains using httpx
    try:
        logger.info("Filtering live subdomains with httpx...")
        
        # Pass the raw file content to httpx via stdin for efficient processing
        with open(raw_subs_file, "r") as f_in:
            httpx_proc = subprocess.run(
                [config.HTTPX_PATH, "-silent", "-no-color"],
                stdin=f_in,
                capture_output=True,
                text=True
            )
        
        # Clean and collect live subdomain results
        live_subs = [s.strip() for s in httpx_proc.stdout.splitlines() if s.strip()]
        
        if not live_subs:
            return f"[!] Discovery finished. Found {len(unique_subs)} raw subs, but none are responding (Live) via httpx."

        # Save the final sorted list of live subdomains
        with open(final_subs_file, "w") as f_out:
            f_out.write("\n".join(sorted(live_subs)))

        # Clean up the raw file to keep the storage tidy (Optional)
        if os.path.exists(raw_subs_file):
            os.remove(raw_subs_file)
    
        logger.info("Triggering visual screenshot capture...")
        run_visual_recon(final_subs_file)
        
        return f"[+] Enumeration complete. {len(live_subs)} live subdomains saved to: {final_subs_file}"

    except Exception as e:
        logger.error(f"HTTpx filtering failed: {str(e)}")
        return f"[!] Enumeration finished, but httpx filtering failed. Raw results are at: {raw_subs_file}"