import subprocess
import os
import config
from core.logger import logger

def run_header_discovery(url, method="GET", body=None, use_session=False):
    """
    Advanced Header Discovery tool using x8.
    FULL RAW MODE: Captures combined stdout and stderr to match terminal output.
    """
    if not url:
        return "[-] Error: URL is required for header discovery."

    # Standardize HTTP method
    method = method.upper()
    
    # Logic for handling bodies in POST/PATCH/PUT
    if method in ["POST", "PATCH", "PUT"] and body is None:
        body = "{}" 

    # Setup directory for header results
    os.makedirs(config.HEADER_RESULTS_DIR, exist_ok=True)
    
    # Generate a safe filename from the URL
    domain_name = url.split("//")[-1].replace("/", "_").replace(".", "_")
    output_file = os.path.join(config.HEADER_RESULTS_DIR, f"{domain_name}_headers.txt")

    try:
        logger.info(f"Starting FULL RAW Recon: Header Discovery on {url} ({method})")

        # Command configuration for x8
        x8_cmd = [
            config.X8_PATH, 
            "-u", url, 
            "-X", method, 
            "--headers", 
            "-w", config.HEADER_WORLDLIST,
            "--follow-redirects",
            "--disable-progress-bar"
        ]

        # Inject body if provided
        if body:
            x8_cmd.extend(["-d", body])
            if body.startswith("{"):
                x8_cmd.extend(["--body"])

        # Inject session cookies if required
        if use_session:
            from core.requester import request_engine
            cookies = request_engine.session.cookies.get_dict()
            cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
            if cookie_str:
                # Direct Header injection is more reliable for x8
                x8_cmd.extend(["-H", f"Cookie: {cookie_str}"])

        logger.info(f"Executing x8 for {domain_name}. Capturing all output streams...")
        
        # Execution with stderr merged into stdout
        # stdout=subprocess.PIPE + stderr=subprocess.STDOUT ensures all terminal output is captured
        process = subprocess.run(
            x8_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, 
            text=True,
            check=False
        )
        
        # Write merged outputs directly to the file
        with open(output_file, "w") as f:
            f.write(f"--- [ 0x4l3xAi x8 FULL TERMINAL OUTPUT - METHOD: {method} ] ---\n")
            f.write(process.stdout)

        # Check if output is empty (Target unreachable or WAF block)
        if not process.stdout.strip():
            logger.warning("x8 returned empty output. Check target accessibility or WAF.")
            return f"[-] Header discovery finished but output was empty. Target: {url}"

        logger.info(f"Header discovery finished. Full terminal data saved to: {output_file}")
        return f"[+] Header discovery complete. Results: {output_file}"

    except Exception as e:
        logger.error(f"Header discovery execution error: {str(e)}")
        return f"[-] Critical Error: {str(e)}"