import subprocess
import os
import config
from core.logger import logger

def run_dir_discovery(url, wordlist=None, filter_size=None, filter_words=None):
    """
    Perform directory discovery using ffuf.
    -fc: Filter Content-Length (Size)
    -fw: Filter Word Count
    """
    if not url:
        return "[-] Error: URL is required for directory discovery."

    # Use default wordlist from config if none provided
    wordlist = wordlist or config.DIR_WORDLIST
    
    if not os.path.exists(wordlist):
        return f"[-] Error: Wordlist not found at {wordlist}"

    # Setup results directory
    os.makedirs(config.DIR_RESULTS_DIR, exist_ok=True)
    
    # Generate safe filename
    domain_name = url.split("//")[-1].replace("/", "_").replace(".", "_")
    output_file = os.path.join(config.DIR_RESULTS_DIR, f"{domain_name}_dirs.txt")

    try:
        logger.info(f"Starting Directory Discovery on: {url}")

        # Base Command
        ffuf_cmd = [
            config.FFUF_PATH,
            "-u", f"{url.rstrip('/')}/FUZZ",
            "-w", wordlist,
            "-mc", "200,204,301,302,307,401,403",
            "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ]

        # Add Filter Content-Length if provided
        if filter_size:
            ffuf_cmd.extend(["-fc", str(filter_size)])
            logger.info(f"Applying Size Filter: Hiding responses with size {filter_size}")

        # Add Filter Word Count if provided
        if filter_words:
            ffuf_cmd.extend(["-fw", str(filter_words)])
            logger.info(f"Applying Word Filter: Hiding responses with {filter_words} words.")

        logger.info(f"Executing ffuf for {url}...")
        
        # Execute and capture combined stdout and stderr
        result = subprocess.run(
            ffuf_cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True,
            check=False
        )
        
        # Write everything to the output file
        with open(output_file, "w") as f:
            f.write(f"--- [ FFUF RAW OUTPUT - URL: {url} ] ---\n")
            if filter_size: f.write(f"--- [ FILTERED SIZE: {filter_size} ] ---\n")
            if filter_words: f.write(f"--- [ FILTERED WORDS: {filter_words} ] ---\n")
            f.write(result.stdout)

        # Check for findings
        if " [Status: " in result.stdout:
            logger.info(f"[+] Discovery finished. Results saved to: {output_file}")
            return f"[+] Success! Check results: {output_file}"
        else:
            return "[!] Fuzzing complete, but no interesting directories were found."

    except Exception as e:
        logger.error(f"Directory discovery failed: {str(e)}")
        return f"[-] Critical Error: {str(e)}"