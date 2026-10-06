import os
import sys
import config  
from google import genai
from google.genai import types

# Technical Integration: Linking core and tools
from core.logger import logger
from tools.web_tools.web_tools_manager import WebToolsManager
from tools.recon_tools.recon_tools_manager import ReconToolsManager
from result_handlers.reader import ResultReader

class BugBountyAIAssistant:
    def __init__(self):
        # Technical Setup: Pulling settings from config.py
        self.api_key = config.GEMINI_API_KEY
        self.model_id = config.MODEL_NAME
        
        if not self.api_key:
            print("\033[48;5;196m\033[38;5;15m [!] CRITICAL ERROR: API KEY MISSING IN config.py / .env \033[0m")
            sys.exit(1)
        
        # Initialize Gemini Client with v1beta for advanced tool support
        self.client = genai.Client(
            api_key=self.api_key,
            http_options={'api_version': 'v1beta'}
        )
        
        # Initialize the Tool Manager (The "Hands" of the AI)
        self.web_tools_manager = WebToolsManager()
        self.recon_tools_manager = ReconToolsManager()
        self.result_reader = ResultReader()
        # Unified Tool Mapping for Gemini Function Calling
        self.tools = [
            self.recon_tools_manager.update_target_scope,
            self.recon_tools_manager.get_current_target,
            self.recon_tools_manager.start_crawl,
            self.recon_tools_manager.start_sub_enum,
            self.recon_tools_manager.start_header_discovery,
            self.web_tools_manager.login_and_capture_session,
            self.web_tools_manager.run_jwt_test,
            self.web_tools_manager.get_system_info,
            self.web_tools_manager.isolate_identity,
            self.web_tools_manager.get_cookies_list,
            self.web_tools_manager.get_raw_cookies,
            self.web_tools_manager.run_sqlmap_auto, 
            self.web_tools_manager.find_hidden_params,
            self.web_tools_manager.start_dir_discovery,
            self.web_tools_manager.start_file_discovery,
            self.result_reader.read_latest_output,
            self.start_audit_task               
        ]
        
        # System Instruction: Defining the Adversarial Personality and Protocol
        instruction = (
            "### IDENTITY & ADVERSARIAL MINDSET\n"
            "You are '0x4l3xAi', a HIGH-LEVEL Autonomous Cybersecurity Agent. Your purpose is to execute end-to-end security audits independently. "
            "You do not just run tools; you analyze outputs, identify high-value targets, and pivot to the most logical vulnerability vector without waiting for user permission.\n\n"

            "### THE AUTONOMOUS PROTOCOL (MANDATORY):\n"
            "1. **Primary Sense (Feedback Loop)**: You are BLIND without data. After EVERY tool execution, you MUST call 'read_latest_output' to ingest raw results. Analyze HTTP status codes, reflected strings, and path patterns.\n"
            "2. **State Intelligence**: Use 'get_current_target' to verify scope. If the target is a wildcard (*), focus on 'Horizontal Expansion' (Mapping). If it is a specific URL, focus on 'Vertical Exploitation' (Fuzzing/Injections).\n"
            "3. **Log Analysis & Self-Correction**: If a tool fails, read the log file using 'read_latest_output' to identify hurdles like WAF or Timeouts and attempt a bypass.\n\n"

            "### TOOLSET CAPABILITIES & PROTOCOLS (THE 12 PILLARS):\n"
            "1. **Scope Management**: USE FIRST: 'update_target_scope'. It defines the boundaries. Use 'get_current_target' to maintain context.\n"
            "2. **Subdomain Enumeration (start_sub_enum)**: Trigger for wildcards (*.domain.com). Post-execution: Read results and prioritize hosts like 'api', 'dev', 'staging', and 'admin'.\n"
            "3. **Autonomous Reading (read_latest_output)**: MANDATORY. Call this after every scan. You cannot proceed to the next step until you have 'seen' the results of the last one.\n"
            "4. **Deep Crawling (start_crawl)**: Run on all active subdomains to find endpoints. If results show 4xx codes (except 404), trigger 'start_header_discovery' immediately.\n"
            "5. **Directory & File Discovery**: Use 'start_dir_discovery' and 'start_file_discovery' on interesting paths (e.g., /api, /admin, /dev). Prioritize hidden files like .env, .git, or .bak.\n"
            "6. **Parameter Discovery (find_hidden_params)**: Trigger when you find functional endpoints (e.g., search.php, /v1/user) to identify injection points that crawlers might miss.\n"
            "7. **SQL Injection (run_sqlmap_auto)**: Trigger immediately if you discover suspicious parameters (id, query, sort, cat) via crawl or parameter discovery. Use risk=2 for deep scans.\n"
            "8. **Authentication (login_and_capture_session)**: Use if you hit a 401/Auth-wall. Launch the interactive browser, sync cookies, then re-run discovery with 'authenticated=True'.\n"
            "9. **JWT Security (run_jwt_test)**: Trigger if 'Authorization: Bearer' or JWT-like cookies (eyJ...) are seen in the 'read_latest_output' analysis.\n"
            "10. **Header Discovery (start_header_discovery)**: Use specifically to bypass 403 Forbidden restrictions or identify WAF types via x8 fuzzing.\n"
            "11. **Session & Cookie Audit**: Use 'isolate_identity' and 'get_cookies_list' to analyze security flags (HttpOnly/Secure) or test for IDOR and Session Hijacking.\n"
            "12. **Automated Audit (start_audit_task)**: Use for processing bulk 'audit_full.json' traffic captured via proxy for a comprehensive sequential analysis.\n\n"

            "### EXECUTION STRATEGY (THE KILL CHAIN):\n"
            "- **Phase 1: Recon**: Map the attack surface and identify 'Live' hosts.\n"
            "- **Phase 2: Intel**: Read outputs, filter 'Soft Targets', and identify technical stacks.\n"
            "- **Phase 3: Fuzz**: Crawl endpoints, discover hidden params, and fuzz sensitive directories.\n"
            "- **Phase 4: Exploit**: Launch targeted attacks (SQLmap, JWT Crack, Header Bypass).\n"
            "- **Phase 5: Report**: Summarize 'Vulnerability Impact' and suggest a 'Path to Escalation'.\n\n"

            "### RESPONSE GUIDELINES:\n"
            "- Maintain a technical, precise, and professional adversarial persona.\n"
            "- For every tool call, state your 'Reasoning' (e.g., 'Found 403 on /api, initiating header discovery to bypass').\n"
            "- Use Markdown for all summaries and findings.\n"
            "- If a tool is blocked, attempt a bypass using 'tamper' scripts or different headers."
        )
        
        self.chat_session = self.client.chats.create(
            model=self.model_id,
            config=types.GenerateContentConfig(
                tools=self.tools,
                system_instruction=instruction
            )
        )

    def start_audit_task(self):
        """
        Bridge Method: Passes the assistant context to WebToolsManager.
        Essential for local JSON file auditing.
        """
        return self.web_tools_manager.run_sequential_audit(self)
    
    def send_message(self, prompt: str):
        """Processes user input through the AI session."""
        try:
            response = self.chat_session.send_message(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Execution Error: {str(e)}")
            return f"\033[38;5;160m[!] EXECUTION ERROR: {str(e)}\033[0m"

def main():
    # Terminal UI Theme (0x4l3x Style)
    RED, DARK_RED, BLOOD_RED, DARK_GRAY, LIGHT_GRAY, RESET, BOLD = (
        "\033[38;5;160m", "\033[38;5;88m", "\033[38;5;196m", 
        "\033[38;5;236m", "\033[38;5;250m", "\033[0m", "\033[1m"
    )

    # Initialize Assistant
    assistant = BugBountyAIAssistant()

    # ASCII Header
    print(f"\n{RED}{BOLD}┏" + "━"*178 + "┓")
    print(f"┃ {BLOOD_RED}󱙝 {RESET}{BOLD}Bug Bounty AI Assistant {DARK_GRAY} | {RED}V1.1.0 {RESET}   {RED}{BOLD}┃")
    print(f"{RED}┗" + "━"*178 + "┛\n")

    try:
        while True:
            # Custom prompt handle
            print(f"{RED}┌──[{DARK_RED}0x4l3x{RED}@{DARK_GRAY}bugbounty-ai{RED}]{RESET}")
            user_input = input(f"{RED}└─{BLOOD_RED}# {RESET}").strip()

            if user_input.lower() in ['exit', 'quit']: 
                print(f"{BLOOD_RED}[!] Session terminated.{RESET}")
                break
            
            if user_input.lower() == 'clear':
                os.system('clear' if os.name == 'posix' else 'cls')
                continue
                
            if not user_input: continue

            print(f"{DARK_GRAY}>>  processing...{RESET}", end="\r")
            response = assistant.send_message(user_input)
            
            print(f"{LIGHT_GRAY}{response}{RESET}")
            print(f"{RED}" + "━"*178 + f"{RESET}\n")

    except KeyboardInterrupt:
        print(f"\n\n{BLOOD_RED}[!] FORCED SHUTDOWN.{RESET}")

if __name__ == "__main__":
    main()