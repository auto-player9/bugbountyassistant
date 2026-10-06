import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# AI Agent Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-flash-latest"

# Network Settings
DEFAULT_TIMEOUT = 30
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Project Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.join(BASE_DIR, "tools")
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
LOGS_DIR = os.path.join(STORAGE_DIR, "logs")
LOOT_DIR = os.path.join(STORAGE_DIR, "loot")
WORDLISTS_DIR = os.path.join(STORAGE_DIR, "wordlists")

# Audit Files Paths
AUDIT_INPUT_FILE = os.path.join(STORAGE_DIR, "loot/audit_full.json")
AUDIT_OUTPUT_FILE = os.path.join(STORAGE_DIR, "loot/audit_result.md")

# SQLmap Configuration
SQLMAP_REQUEST_FILE = os.path.join(LOOT_DIR, "sqlmap_target.txt")
SQLMAP_OUTPUT_DIR = os.path.join(LOOT_DIR, "sqlmap_reports")

# Crawler Configuration
CRAWL_RESULTS_DIR = os.path.join(STORAGE_DIR, "crawl_results")
GOSPIDER_PATH = "gospider" 
WAYBACKURLS_PATH = "/home/alex/go/bin/waybackurls"

# Parameter Discovery Configuration
PARAM_RESULTS_DIR = os.path.join(STORAGE_DIR, "param_discovery")
PARAM_WORLDLIST = os.path.join(WORDLISTS_DIR, "burp-parameter-names.txt")
X8_PATH = "/home/alex/.cargo/bin/x8" 
ARJUN_PATH = "arjun" 

# Subdomain Enumeration Configuration
SUB_RESULTS_DIR = os.path.join(STORAGE_DIR, "subdomain_results")
AMASS_PATH = "/snap/bin/amass"
SUBFINDER_PATH = "subfinder"
ASSETFINDER_PATH = "assetfinder"
HTTPX_PATH = "/home/alex/go/bin/httpx"


# Header Discovery Configuration
HEADER_RESULTS_DIR = os.path.join(STORAGE_DIR, "recon/headers")
HEADER_WORLDLIST = os.path.join(WORDLISTS_DIR, "headers-names.txt")

# Screenshot Configuration
GOWITNESS_PATH = "/home/alex/go/bin/gowitness"
SCREENSHOT_DIR = os.path.join(STORAGE_DIR, "recon/screenshots")

# Directory Discovery Configuration
FFUF_PATH = "ffuf"
DIR_WORDLIST = "/home/alex/bugbountyassistant/storage/wordlists/raft-medium-directories.txt" 
DIR_RESULTS_DIR = os.path.join(STORAGE_DIR, "web/directories")

# File Discovery Configuration
FILE_WORDLIST = "/home/alex/bugbountyassistant/storage/wordlists/raft-medium-files.txt"
FILE_RESULTS_DIR = os.path.join(STORAGE_DIR, "web/files")

# Proxy Settings
USE_PROXY = False
PROXIES = {
    "http": "http://127.0.0.1:8080",
    "https": "http://127.0.0.1:8080",
}

# JWT Tool Specifics
JWT_WORDLIST = os.path.join(TOOLS_DIR, "web_tools/jwt_tool/wordlists/common_secrets.txt")