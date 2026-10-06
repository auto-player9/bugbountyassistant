import subprocess
import os
import config
from core.logger import logger

def run_visual_recon(input_file):
    """
    Takes a file of live URLs/subdomains and captures screenshots using gowitness.
    """
    if not input_file or not os.path.exists(input_file):
        return f"[-] Error: Input file {input_file} not found."

    # Create a dedicated directory for screenshots
    # e.g., storage/recon/screenshots/domain_name/
    base_name = os.path.basename(input_file).replace("_live.txt", "")
    screenshot_dir = os.path.join(config.SCREENSHOT_DIR, base_name)
    os.makedirs(screenshot_dir, exist_ok=True)

    logger.info(f"Starting visual recon for {base_name}...")

    try:
        # Gowitness Command
        # scan file: the input list
        # --screenshot-path: where to save images
        # --threads: speed of capture
        cmd = [
            config.GOWITNESS_PATH, 
            "scan",
            "file", 
            "-f", input_file, 
            "--screenshot-path", screenshot_dir,
            "--write-jsonl"
        ]

        # Execute
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            # Count images captured
            captured_count = len([f for f in os.listdir(screenshot_dir) if f.endswith('.png')])
            logger.info(f"[+] Visual recon complete. Captured {captured_count} screenshots.")
            return f"[+] Success! {captured_count} screenshots saved in: {screenshot_dir}"
        else:
            logger.error(f"Gowitness failed: {result.stderr}")
            return "[-] Error: Visual recon tool failed during execution."

    except Exception as e:
        logger.error(f"Visual recon critical failure: {str(e)}")
        return f"[-] Error: {str(e)}"