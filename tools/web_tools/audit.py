import json
import os
import time
import config
from core.logger import logger

def run_sequential_audit_logic(assistant):
    """
    Reads items from audit_full.json and audits them one by one.
    Uses the assistant instance to access the active chat session.
    """
    input_path = config.AUDIT_INPUT_FILE
    output_path = config.AUDIT_OUTPUT_FILE

    if not os.path.exists(input_path):
        return f"[-] Error: Audit file not found at {input_path}"

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            items = json.load(f)
        
        if not items:
            return "[-] The audit file is empty."

        logger.info(f"Starting sequential audit for {len(items)} items.")
        
        with open(output_path, 'w', encoding='utf-8') as f_out:
            f_out.write(f"# 0x4l3xAi Security Audit Report\n\n")

            for i, item in enumerate(items):
                # Progress indicator in terminal
                print(f"[*] Auditing ({i+1}/{len(items)}): {item['method']} {item['url']}", end="\r")
                
                prompt = (
                    "Perform an adversarial security audit on this HTTP interaction. "
                    "Focus on IDOR, Business Logic, Data Leakage, and Injection vulnerabilities.\n\n"
                    f"ENDPOINT: {item['method']} {item['url']}\n"
                    f"REQUEST:\n{item['full_request']}\n"
                    f"RESPONSE:\n{item['full_response']}\n\n"
                    "Verdict Rules: Be technical, concise, and identify misconfigurations."
                )
                
                # Use the passed assistant session for the audit
                response = assistant.chat_session.send_message(prompt)
                
                f_out.write(f"## [{i+1}] {item['method']} {item['url']}\n")
                f_out.write(f"### AI Analysis:\n{response.text}\n")
                f_out.write("\n" + "---" * 15 + "\n\n")
                f_out.flush()

        return f"[+] Audit complete! Report saved at: {output_path}"

    except Exception as e:
        logger.error(f"Audit logic execution failed: {str(e)}")
        return f"[-] Audit failed: {str(e)}"