import json
import requests

class AuditApiUploader:
    def __init__(self, api_key, api_url):
        self.api_key = api_key
        self.api_url = api_url
        if not self.api_key:
            raise ValueError("API Key is required to upload audit")
        
    def upload_audit(self, audit: str):
        if not audit:
            raise ValueError("Repo content is required to upload")

        print("Uploading to audits API...")        

        headers = {
            "x-api-key": self.api_key,
        }
        payload = {
            "text": audit
        }

        url = self.api_url + "api/repo/add"

        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code != 200:
            print(f"Failed to upload audit: {response.text}")
            raise ValueError(f"Failed to upload audit: {response.text}")
        
        print("Audit uploaded successfully")
        print(f"Audit info:")
        print(response.json())
