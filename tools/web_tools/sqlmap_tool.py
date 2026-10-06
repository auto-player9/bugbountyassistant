import subprocess
import os
import time
import config
from core.logger import logger

def run_sqlmap_scan(mode="url", target_url=None, p_var=None, tamper=None, risk=1, level=1):
    """
    Automated SQL Injection Engine (0x4l3xAi Wrapper).
    
    This function orchestrates external sqlmap processes to identify and exploit 
    SQL injection vulnerabilities using either direct URI analysis or raw HTTP 
    request files for complex interactions (POST, Headers, Cookies).

    Args:
        mode (str): Execution context - 'url' for standard GET requests or 
        'file' to process the static config.SQLMAP_REQUEST_FILE (-r).
        target_url (str, optional): The target URI for 'url' mode.
        p_var (str, optional): Specific HTTP parameter(s) to test (e.g., 'id,user').
        tamper (str, optional): Comma-separated SQLmap tamper scripts for WAF/IPS evasion.
        risk (int): Risk level (1-3) for testing depth (Default: 1).
        level (int): Level of tests to perform (1-5) (Default: 1).

    Returns:
        str: A technical summary of findings or the path to the detailed audit log.
    """
    os.makedirs(config.SQLMAP_OUTPUT_DIR, exist_ok=True)
    
    # Base Command with essential bug bounty flags
    cmd = ["sqlmap", "--batch", "--random-agent", f"--risk={risk}", f"--level={level}", "--flush-session"]

    # Mode Selection
    if mode == "file":
        if not os.path.exists(config.SQLMAP_REQUEST_FILE):
            return f"[-] Error: Request file not found at {config.SQLMAP_REQUEST_FILE}"
        cmd.extend(["-r", config.SQLMAP_REQUEST_FILE])
    else:
        if not target_url:
            return "[-] Error: URL mode selected but no URL provided."
        cmd.extend(["-u", target_url])

    # Parameter Targeting (-p)
    if p_var:
        cmd.extend(["-p", p_var])

    # WAF Bypass (Tamper)
    if tamper:
        cmd.extend(["--tamper", tamper])

    try:
        logger.info(f"Launching SQLmap: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        # Log management
        log_filename = f"sql_report_{int(time.time())}.log"
        log_path = os.path.join(config.SQLMAP_OUTPUT_DIR, log_filename)
        
        with open(log_path, "w") as f:
            f.write(result.stdout)
            if result.stderr: f.write(f"\nERRORS:\n{result.stderr}")

        if "is vulnerable" in result.stdout or "Payload:" in result.stdout:
            return f"[+] VULNERABILITY FOUND! Report: {log_path}\n\nTechnical Snippet:\n{result.stdout[-1500:]}"
        
        return f"[*] Scan finished. No clear injection found. Full log: {log_path}"

    except subprocess.TimeoutExpired:
        return "[-] SQLmap scan timed out (10 min limit)."
    except Exception as e:
        return f"[-] Execution Error: {str(e)}"