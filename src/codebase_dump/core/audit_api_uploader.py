import requests

class AuditApiUploader:
    def __init__(self, api_key, api_url, api_submitted_by):
        self.api_key = api_key
        self.api_url = api_url
        self.api_submitted_by = api_submitted_by
        
    def upload_audit(self, audit: str):
        if not audit:
            raise ValueError("Repo content is required to upload")

        print("Uploading to audits API...")        
                
        headers = {
            "x-submitted-by": self.api_submitted_by
        }

        if self.api_key:
            headers["x-api-key"] = self.api_key

        payload = {
            "text": audit
        }

        url = self.api_url + "api/repo/add"
        print(f"Headers: {headers}")
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code != 200:
            if response.status_code == 413:
                print(f"Parsed codebase is too big. Please reduce the size. You can use --ignore-top-large-files param to ignore the largest files or use ignore patterns.")
                raise ValueError(f"Parsed codebase is too big. Please reduce the size. You can use --ignore-top-large-files param to ignore the largest files or use ignore patterns.")
            else:
                print(f"Failed to upload audit: {response.text}")
                raise ValueError(f"Failed to upload audit: {response.text}")
        else:
            print("Audit uploaded successfully")
            print(f"Audit info:")
            print(response.json())
