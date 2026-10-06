import os
import config
from core.logger import logger

class ResultReader:
    def __init__(self):
        # Map tool types to their respective storage directories defined in config.py
        self.tool_map = {
            "subdomain": config.SUB_RESULTS_DIR,
            "crawl": config.CRAWL_RESULTS_DIR,
            "dir_discovery": config.DIR_RESULTS_DIR,
            "file_discovery": config.FILE_RESULTS_DIR,
            "params": config.PARAM_RESULTS_DIR,
            "headers": config.HEADER_RESULTS_DIR
        }

    def read_latest_output(self, tool_type: str, target_name: str):
        """
        Retrieves the content of the most recent result file for a specific tool and target.
        Used by the AI to make autonomous decisions based on tool output.
        """
        if tool_type not in self.tool_map:
            return f"[-] Error: Tool type '{tool_type}' is not recognized by the ResultReader."

        folder_path = self.tool_map[tool_type]
        
        # Format the target name to match your file naming convention (e.g., neon_tech)
        formatted_target = target_name.replace(".", "_")
        
        try:
            # List all files in the directory that match the target name
            files = [f for f in os.listdir(folder_path) if formatted_target in f]
            
            if not files:
                return f"[!] Analysis Alert: No result files found for {target_name} in {tool_type} storage."

            # Identify the most recently created file in the list
            latest_file_path = max(
                [os.path.join(folder_path, f) for f in files], 
                key=os.path.getctime
            )
            
            file_name = os.path.basename(latest_file_path)
            
            with open(latest_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Smart Data Handling: If the file is too large, truncate it to save LLM tokens.
            # We prioritize the first 100 lines as they usually contain the most critical findings.
            lines = content.splitlines()
            if len(lines) > 100:
                summary = "\n".join(lines[:100])
                logger.info(f"AI requested data from {file_name} (Truncated for efficiency).")
                return (
                    f"[+] Analysis of {file_name}:\n"
                    f"{summary}\n"
                    f"... [Output truncated. Total lines: {len(lines)}]"
                )
            
            logger.info(f"AI requested full data from {file_name}.")
            return f"[+] Full Results from {file_name}:\n{content}"

        except Exception as e:
            logger.error(f"Autonomous Read Error: {str(e)}")
            return f"[-] Critical Error reading {tool_type} results: {str(e)}"