import subprocess
import os
import config
from core.logger import logger

def run_param_discovery(url, method="GET", body=None, use_session=False):
    """
    Parameter Discovery - RAW MODE.
    Saves every line from x8 and Arjun without any filtering.
    """
    if not url:
        return "[-] Error: URL is required."

    method = method.upper()
    if method in ["POST", "PATCH", "PUT"] and body is None:
        body = "{}"

    os.makedirs(config.PARAM_RESULTS_DIR, exist_ok=True)
    domain_name = url.split("//")[-1].replace("/", "_").replace(".", "_")
    output_file = os.path.join(config.PARAM_RESULTS_DIR, f"{domain_name}_params.txt")

    all_outputs = []

    try:
        logger.info(f"Starting RAW Discovery on: {url} ({method})")

        x8_cmd = [
            config.X8_PATH, "-u", url, "-X", method, 
            "--follow-redirects", "-w", config.PARAM_WORLDLIST,
            "--disable-progress-bar"
        ]
        
        if body:
            x8_cmd.extend(["-d", body])
            if body.startswith("{"): x8_cmd.extend(["--body"]) 

        logger.info("Executing x8...")
        proc_x8 = subprocess.run(x8_cmd, capture_output=True, text=True)
        
        all_outputs.append("--- [ x8 RAW OUTPUT ] ---")
        all_outputs.append(proc_x8.stdout)
        if proc_x8.stderr:
            all_outputs.append("--- [ x8 ERRORS/LOGS ] ---")
            all_outputs.append(proc_x8.stderr)

        logger.info("Executing Arjun...")
        arjun_cmd = [config.ARJUN_PATH, "-u", url, "-m", method, "--stable", "-w", config.PARAM_WORLDLIST]
        if body: arjun_cmd.extend(["--data", body])
        
        proc_arjun = subprocess.run(arjun_cmd, capture_output=True, text=True)
        
        all_outputs.append("\n--- [ Arjun RAW OUTPUT ] ---")
        all_outputs.append(proc_arjun.stdout)
        if proc_arjun.stderr:
            all_outputs.append("--- [ Arjun ERRORS/LOGS ] ---")
            all_outputs.append(proc_arjun.stderr)

        with open(output_file, "w") as f:
            f.write("\n".join(all_outputs))

        return f"[+] Discovery finished. All raw data saved to: {output_file}"

    except Exception as e:
        logger.error(f"Discovery failed: {str(e)}")
        return f"[-] Critical Error: {str(e)}"