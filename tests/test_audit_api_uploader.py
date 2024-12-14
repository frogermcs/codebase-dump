import unittest
from codebase_dump.core.audit_api_uploader import AuditApiUploader
from unittest.mock import patch, MagicMock
from io import StringIO
import sys

class TestAuditApiUploader(unittest.TestCase):
    def test_init_no_api_key(self):
        """Test that initializing without an API key raises ValueError."""
        with self.assertRaises(ValueError) as context:
            AuditApiUploader(api_key="", api_url="http://example.com/upload")

        self.assertIn("API Key is required", str(context.exception))

    def test_upload_no_audit_text(self):
        """Test that uploading without audit text raises ValueError."""
        uploader = AuditApiUploader(api_key="test_key", api_url="http://example.com/upload")
        with self.assertRaises(ValueError) as context:
            uploader.upload_audit(audit="")
        self.assertIn("Repo content is required", str(context.exception))

    @patch('requests.post')
    def test_upload_success(self, mock_post):
        """Test a successful upload."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "12345"
        mock_post.return_value = mock_response

        uploader = AuditApiUploader(api_key="test_key", api_url="http://example.com/upload")
        
        # Capture stdout to verify print statements
        captured_output = StringIO()
        sys.stdout = captured_output

        uploader.upload_audit(audit="This is a test audit.")
        
        # Restore stdout
        sys.stdout = sys.__stdout__

        # Verify requests.post call
        mock_post.assert_called_once_with(
            "http://example.com/upload",
            json={"text": "This is a test audit."},
            headers={"x-api-key": "test_key"}
        )

        # Check output content
        output = captured_output.getvalue()
        self.assertIn("Audit uploaded successfully", output)
        self.assertIn("Audit ID: 12345", output)

    @patch('requests.post')
    def test_upload_failure(self, mock_post):
        """Test a failure scenario where the server returns non-200 status."""
        # Setup mock response to fail
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Error uploading"
        mock_post.return_value = mock_response

        uploader = AuditApiUploader(api_key="test_key", api_url="http://example.com/upload")
        
        with self.assertRaises(ValueError) as context:
            uploader.upload_audit(audit="Test audit.")
        
        self.assertIn("Failed to upload audit: Error uploading", str(context.exception))
        mock_post.assert_called_once_with(
            "http://example.com/upload",
            json={"text": "Test audit."},
            headers={"x-api-key": "test_key"}
        )
