import xml.etree.ElementTree as ET
import base64
import json
import os
import sys
import hashlib
from collections import defaultdict

class ProfessionalBurpParser:
    def __init__(self, input_file):
        self.input_file = input_file
        self.audit_data = defaultdict(list)
        self.js_links = []
        self.seen_hashes = set()

    def get_dedup_hash(self, method, url, body):
        """
        Deduplication Rules:
        - GET/DELETE: Unique per Method + URL (includes params).
        - POST/PATCH/Others: Unique per Method + URL + Body.
        """
        method = method.upper()
        if method in ["GET", "DELETE"]:
            hash_val = f"{method}|{url}"
        else:
            hash_val = f"{method}|{url}|{body}"
        return hashlib.md5(hash_val.encode('utf-8')).hexdigest()

    def parse(self):
        if not os.path.exists(self.input_file):
            print("[-] File not found.")
            return

        print("[*] Filtering noise and sorting requests...")
        context = ET.iterparse(self.input_file, events=('end',))

        for event, elem in context:
            if elem.tag == 'item':
                url = elem.find('url').text if elem.find('url') is not None else ""
                method = elem.find('method').text if elem.find('method') is not None else ""
                mimetype = elem.find('mimetype').text if elem.find('mimetype') is not None else ""
                
                # 1. Remove static noise (Images, CSS, Fonts, etc.)
                if mimetype in ['PNG', 'JPEG', 'GIF', 'CSS', 'ICO', 'FONT'] or \
                   any(ext in url.lower() for ext in ['.png', '.jpg', '.jpeg', '.css', '.woff', '.svg', '.gif']):
                    elem.clear()
                    continue

                # 2. Extract JS files to a separate list
                if mimetype == 'JS' or url.split('?')[0].endswith('.js'):
                    self.js_links.append({"method": method, "url": url})
                    elem.clear()
                    continue

                # 3. Decode full Request/Response (Fixed NoneType check)
                req_node = elem.find('request')
                res_node = elem.find('response')
                
                raw_req = base64.b64decode(req_node.text).decode('utf-8', errors='ignore') if req_node is not None and req_node.text is not None else ""
                raw_res = base64.b64decode(res_node.text).decode('utf-8', errors='ignore') if res_node is not None and res_node.text is not None else ""

                # Extract body for POST/PATCH dedup logic
                req_body = raw_req.split('\r\n\r\n', 1)[1] if '\r\n\r\n' in raw_req else ""

                # 4. Apply Deduplication Rules
                item_hash = self.get_dedup_hash(method, url, req_body)
                
                if item_hash not in self.seen_hashes:
                    self.seen_hashes.add(item_hash)
                    
                    entry = {
                        "method": method,
                        "url": url,
                        "full_request": raw_req,
                        "full_response": raw_res
                    }
                    
                    # Group by Endpoint Path (Ignoring Query Params for sorting)
                    base_path = url.split('?')[0]
                    self.audit_data[base_path].append(entry)

                elem.clear()

        self.save_outputs()

    def save_outputs(self):
        # Flatten grouped data (keeping similar endpoints together)
        final_audit = []
        for path in sorted(self.audit_data.keys()):
            final_audit.extend(self.audit_data[path])

        # Save Main Audit File
        with open("audit_full.json", 'w', encoding='utf-8') as f:
            json.dump(final_audit, f, indent=4, ensure_ascii=False)
        
        # Save JS Files separately
        with open("js_files.json", 'w', encoding='utf-8') as f:
            json.dump(self.js_links, f, indent=4, ensure_ascii=False)
        
        print(f"[+] Audit: {len(final_audit)} items -> audit_full.json")
        print(f"[+] JS Files: {len(self.js_links)} items -> js_files.json")

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "history.xml"
    ProfessionalBurpParser(path).parse()