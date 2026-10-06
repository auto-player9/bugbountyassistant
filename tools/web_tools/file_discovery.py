import subprocess
import os
import config
from core.logger import logger

def run_file_discovery(url, filter_size=None, filter_words=None):
    """
    Perform file discovery using ffuf.
    -fc: Filter Content-Length (Size)
    -fw: Filter Word Count
    """
    if not url:
        return "[-] Error: URL is required for file discovery."

    # Setup directories
    os.makedirs(config.FILE_RESULTS_DIR, exist_ok=True)
    domain_name = url.split("//")[-1].replace("/", "_").replace(".", "_")
    output_file = os.path.join(config.FILE_RESULTS_DIR, f"{domain_name}_files.txt")

    try:
        logger.info(f"Starting File Discovery on: {url}")

        # Base Command configuration
        # -ic: Ignore wordlist comments
        ffuf_cmd = [
            config.FFUF_PATH,
            "-u", f"{url.rstrip('/')}/FUZZ",
            "-w", config.FILE_WORDLIST,
            "-mc", "200,204,301,302,307,401,403",
            "-ic",
            "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ]

        # Add Filter Content-Length (-fc) if provided
        if filter_size:
            ffuf_cmd.extend(["-fc", str(filter_size)])
            logger.info(f"Applying Size Filter: Hiding responses with size {filter_size}")

        # Add Filter Word Count (-fw) if provided
        if filter_words:
            ffuf_cmd.extend(["-fw", str(filter_words)])
            logger.info(f"Applying Word Filter: Hiding responses with {filter_words} words.")

        logger.info(f"Executing ffuf file scan for {url}...")
        
        # Execute and capture combined stdout and stderr (Important for WAF logs)
        result = subprocess.run(
            ffuf_cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True,
            check=False
        )
        
        # Write merged outputs to the result file
        with open(output_file, "w") as f:
            f.write(f"--- [ 0x4l3xAi FFUF FILE DISCOVERY OUTPUT - URL: {url} ] ---\n")
            if filter_size: f.write(f"--- [ FILTERED SIZE: {filter_size} ] ---\n")
            if filter_words: f.write(f"--- [ FILTERED WORDS: {filter_words} ] ---\n")
            f.write(result.stdout)

        # Basic logic for the AI to determine success
        if " [Status: " in result.stdout:
            logger.info(f"[+] File discovery finished. Results saved to: {output_file}")
            return f"[+] Success! Files found. Check: {output_file}"
        else:
            return "[!] File fuzzing complete. No significant files discovered (or all were filtered)."

    except Exception as e:
        logger.error(f"File discovery failed: {str(e)}")
        return f"[-] Critical Error: {str(e)}"