import unittest
from codebase_dump.core.audit_api_uploader import AuditApiUploader
from unittest.mock import patch, Mock, MagicMock
from io import StringIO
import sys

class TestAuditApiUploader(unittest.TestCase):
    def test_upload_no_audit_text(self):
        """Test that uploading without audit text raises ValueError."""
        base_url = "http://custom.example.com/"
        uploader = AuditApiUploader(api_key="test_key", api_url=base_url, api_submitted_by="codebase-dumb.v1")
        with self.assertRaises(ValueError) as context:
            uploader.upload_audit(audit="")
        self.assertIn("Repo content is required", str(context.exception))

    @patch("requests.post")
    def test_upload_audit_successful(self, mock_post):
        """Test uploading an audit successfully when the server responds with a 200 status code."""
        # Mock the response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"uploaded": True, "id": "12345"}
        mock_post.return_value = mock_response

        base_url = "http://custom.example.com/"
        expected_call_url = "http://custom.example.com/api/repo/add"
        uploader = AuditApiUploader(api_key="test_key", api_url=base_url, api_submitted_by="codebase-dumb.v1")

        # We patch print to ensure we can verify calls (optional)
        with patch("builtins.print") as mock_print:
            uploader.upload_audit("Sample audit content")

            # Ensure the POST request was made as expected
            mock_post.assert_called_once_with(
                expected_call_url,
                json={"text": "Sample audit content"},
                headers={"x-api-key": "test_key", "x-submitted-by": "codebase-dumb.v1"}
            )

            # Check print calls
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            self.assertIn("Uploading to audits API...", print_calls)
            self.assertIn("Audit uploaded successfully", print_calls)
            self.assertIn("Audit info:", print_calls)
            self.assertIn({"uploaded": True, "id": "12345"}, print_calls)

    @patch('requests.post')
    def test_upload_failure(self, mock_post):
        """Test a failure scenario where the server returns non-200 status."""
        # Setup mock response to fail
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Error uploading"
        mock_post.return_value = mock_response

        base_url = "http://custom.example.com/"
        expected_call_url = "http://custom.example.com/api/repo/add"
        uploader = AuditApiUploader(api_key="test_key", api_url=base_url, api_submitted_by="codebase-dumb.v1")
        
        with self.assertRaises(ValueError) as context:
            uploader.upload_audit(audit="Test audit.")
        
        self.assertIn("Failed to upload audit: Error uploading", str(context.exception))
        mock_post.assert_called_once_with(
            expected_call_url,
            json={"text": "Test audit."},
            headers={"x-api-key": "test_key", "x-submitted-by": "codebase-dumb.v1"}
        )

    @patch("requests.post")
    def test_upload_audit_with_custom_api_url(self, mock_post):
        """Test uploading an audit successfully with a custom API URL."""
        # Mock the response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"uploaded": True, "id": "12345"}
        mock_post.return_value = mock_response

        base_url = "http://custom.example.com/"
        expected_call_url = "http://custom.example.com/api/repo/add"
        uploader = AuditApiUploader(api_key="test_key", api_url=base_url, api_submitted_by="codebase-dumb.v1")

        # We patch print to ensure we can verify calls (optional)
        with patch("builtins.print") as mock_print:
            uploader.upload_audit("Sample audit content")

            # Ensure the POST request was made as expected
            mock_post.assert_called_once_with(
                expected_call_url,
                json={"text": "Sample audit content"},
                headers={"x-api-key": "test_key", "x-submitted-by": "codebase-dumb.v1"}
            )
 
    @patch("requests.post")
    def test_upload_audit_default_api_url(self, mock_post):
        """Test uploading an audit successfully with the default API URL."""
        # Mock the response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"uploaded": True, "id": "12345"}
        mock_post.return_value = mock_response
         
        base_url = "https://codeaudits.ai/"
        expected_call_url = "https://codeaudits.ai/api/repo/add"
        uploader = AuditApiUploader(api_key="test_key", api_url=base_url, api_submitted_by="codebase-dumb.v1")

        # We patch print to ensure we can verify calls (optional)
        with patch("builtins.print") as mock_print:
            uploader.upload_audit("Sample audit content")

            # Ensure the POST request was made as expected
            mock_post.assert_called_once_with(
                expected_call_url,
                json={"text": "Sample audit content"},
                headers={"x-api-key": "test_key", "x-submitted-by": "codebase-dumb.v1"}
            )

            @patch("requests.post")
            def test_upload_audit_with_api_key(self, mock_post):
                """Test uploading an audit with an API key."""
                # Mock the response
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"uploaded": True, "id": "12345"}
                mock_post.return_value = mock_response

                base_url = "http://custom.example.com/"
                expected_call_url = "http://custom.example.com/api/repo/add"
                uploader = AuditApiUploader(api_key="test_key", api_url=base_url, api_submitted_by="codebase-dumb.v1")

                uploader.upload_audit("Sample audit content")

                # Ensure the POST request was made as expected
                mock_post.assert_called_once_with(
                    expected_call_url,
                    json={"text": "Sample audit content"},
                    headers={"x-api-key": "test_key", "x-submitted-by": "codebase-dumb.v1"}
                )

            @patch("requests.post")
            def test_upload_audit_without_api_key(self, mock_post):
                """Test uploading an audit without an API key."""
                # Mock the response
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"uploaded": True, "id": "12345"}
                mock_post.return_value = mock_response

                base_url = "http://custom.example.com/"
                expected_call_url = "http://custom.example.com/api/repo/add"
                uploader = AuditApiUploader(api_key=None, api_url=base_url, api_submitted_by="codebase-dumb.v1")

                uploader.upload_audit("Sample audit content")

                # Ensure the POST request was made as expected
                mock_post.assert_called_once_with(
                    expected_call_url,
                    json={"text": "Sample audit content"},
                    headers={"x-submitted-by": "codebase-dumb.v1"}
                )

            @patch("requests.post")
            def test_upload_audit_large_payload(self, mock_post):
                """Test uploading an audit that is too large."""
                # Mock the response
                mock_response = Mock()
                mock_response.status_code = 413
                mock_post.return_value = mock_response

                base_url = "http://custom.example.com/"
                expected_call_url = "http://custom.example.com/api/repo/add"
                uploader = AuditApiUploader(api_key="test_key", api_url=base_url, api_submitted_by="codebase-dumb.v1")

                with self.assertRaises(ValueError) as context:
                    uploader.upload_audit("A" * 1000000)  # Simulate large payload

                self.assertIn("Parsed codebase is too big", str(context.exception))
                mock_post.assert_called_once_with(
                    expected_call_url,
                    json={"text": "A" * 1000000},
                    headers={"x-api-key": "test_key", "x-submitted-by": "codebase-dumb.v1"}
                )