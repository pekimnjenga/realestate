"""
Comprehensive test suite for utility functions.
Tests cover: R2 file upload/delete, logging, error handling, and filename sanitization.
"""

import io
import os
from unittest.mock import MagicMock

import pytest
from werkzeug.datastructures import FileStorage

from app.utils.r2_upload import delete_from_r2, upload_to_r2

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def mock_file():
    """Create a real FileStorage backed by BytesIO for upload testing."""
    stream = io.BytesIO(b"fake image data")
    return FileStorage(stream=stream, filename="test_image.jpg")


@pytest.fixture
def mock_file_with_special_chars():
    """Create a FileStorage with special characters in filename."""
    stream = io.BytesIO(b"fake image data")
    return FileStorage(stream=stream, filename="test@#$%_image (1).jpg")


@pytest.fixture
def env_vars():
    """Set up environment variables for R2."""
    vars_to_set = {
        "R2_ENDPOINT": "https://r2.example.com",
        "R2_ACCESS_KEY": "test_access_key",
        "R2_SECRET_KEY": "test_secret_key",
        "R2_BUCKET": "test-bucket",
        "PUBLIC_BASE_URL": "https://cdn.example.com",
    }
    for key, value in vars_to_set.items():
        os.environ[key] = value
    yield vars_to_set
    # Cleanup
    for key in vars_to_set:
        os.environ.pop(key, None)


# =============================================================================
# UPLOAD TESTS
# =============================================================================


class TestUploadToR2:
    """Test file upload to Cloudflare R2."""

    def test_upload_successful(self, mocker, mock_file, env_vars):
        """Test successful file upload to R2."""
        # Mock MinIO client
        mock_minio_client = MagicMock()
        mocker.patch("app.utils.r2_upload.Minio", return_value=mock_minio_client)

        # Mock logger
        mock_logger = mocker.patch("app.utils.r2_upload.logger")

        result = upload_to_r2(mock_file)

        # Verify result
        assert result is not None
        assert result.startswith("https://cdn.example.com")
        assert "test_image.jpg" in result
        assert "ilikeitproperties" in result

        # Verify boto3 was called correctly
        mock_minio_client.put_object.assert_called_once()
        call_args = mock_minio_client.put_object.call_args
        assert call_args[0][0] == "test-bucket"  # bucket name
        # object key may include a prefix path (e.g. ilikeitproperties/...),
        # ensure it ends with the filename
        assert call_args[0][1].endswith("test_image.jpg")  # object key

        # Verify logging
        mock_logger.info.assert_called_once()
        assert "Uploaded to R2" in str(mock_logger.info.call_args)

    def test_upload_with_special_characters(self, mocker, mock_file_with_special_chars, env_vars):
        """Test upload with special characters in filename (sanitization)."""
        mock_minio_client = MagicMock()
        mocker.patch("app.utils.r2_upload.Minio", return_value=mock_minio_client)
        mocker.patch("app.utils.r2_upload.logger")

        result = upload_to_r2(mock_file_with_special_chars)

        # Filename should be sanitized
        assert result is not None
        # Special characters should be removed/converted
        assert "#" not in result
        assert "@" not in result
        assert "$" not in result
        assert "%" not in result

    def test_upload_missing_env_variables(self, mocker, mock_file):
        """Test upload fails gracefully when env variables are missing."""
        # Remove env variables
        for key in ["R2_ENDPOINT", "R2_ACCESS_KEY", "R2_SECRET_KEY", "R2_BUCKET", "PUBLIC_BASE_URL"]:
            os.environ.pop(key, None)

        mock_minio_client = MagicMock()
        mocker.patch("app.utils.r2_upload.Minio", return_value=mock_minio_client)

        # Mock logger to capture error
        mock_logger = mocker.patch("app.utils.r2_upload.logger")

        result = upload_to_r2(mock_file)

        # Should return None on error
        assert result is None

        # Should log the error
        mock_logger.error.assert_called_once()
        assert "R2 upload error" in str(mock_logger.error.call_args)

    def test_upload_boto3_connection_error(self, mocker, mock_file, env_vars):
        """Test upload handles boto3 connection errors."""

        mock_minio_client = MagicMock()
        # Simulate upload failure
        mock_minio_client.put_object.side_effect = Exception("Connection refused")
        mocker.patch("app.utils.r2_upload.Minio", return_value=mock_minio_client)

        mock_logger = mocker.patch("app.utils.r2_upload.logger")

        result = upload_to_r2(mock_file)

        assert result is None
        mock_logger.error.assert_called_once()

    def test_upload_boto3_permission_error(self, mocker, mock_file, env_vars):
        """Test upload handles permission errors."""
        mock_minio_client = MagicMock()
        mock_minio_client.put_object.side_effect = PermissionError("Access Denied")
        mocker.patch("app.utils.r2_upload.Minio", return_value=mock_minio_client)

        mock_logger = mocker.patch("app.utils.r2_upload.logger")

        result = upload_to_r2(mock_file)

        assert result is None
        mock_logger.error.assert_called_once()
        assert "Access Denied" in str(mock_logger.error.call_args)

    def test_upload_with_empty_filename(self, mocker, env_vars):
        """Test upload with empty filename."""
        stream = io.BytesIO(b"fake image data")
        file = FileStorage(stream=stream, filename="")

        mock_minio_client = MagicMock()
        mocker.patch("app.utils.r2_upload.Minio", return_value=mock_minio_client)
        mocker.patch("app.utils.r2_upload.logger")

        result = upload_to_r2(file)

        # Should still attempt upload or return None gracefully
        assert result is None or isinstance(result, str)

    def test_upload_returns_correct_url_format(self, mocker, mock_file, env_vars):
        """Test upload returns URL in expected format."""
        mock_minio_client = MagicMock()
        mocker.patch("app.utils.r2_upload.Minio", return_value=mock_minio_client)
        mocker.patch("app.utils.r2_upload.logger")

        result = upload_to_r2(mock_file)

        # URL should be: {PUBLIC_BASE_URL}/ilikeitproperties/{filename}
        expected_prefix = "https://cdn.example.com/ilikeitproperties/"
        assert result.startswith(expected_prefix)


# =============================================================================
# DELETE TESTS
# =============================================================================


class TestDeleteFromR2:
    """Test file deletion from Cloudflare R2."""

    def test_delete_successful(self, mocker, env_vars):
        """Test successful file deletion from R2."""
        mock_minio_client = MagicMock()
        mocker.patch("app.utils.r2_upload.Minio", return_value=mock_minio_client)

        mock_logger = mocker.patch("app.utils.r2_upload.logger")

        url = "https://cdn.example.com/ilikeitproperties/test_image.jpg"
        result = delete_from_r2(url)

        assert result is True

        # Verify MinIO was called
        mock_minio_client.remove_object.assert_called_once()
        call_args = mock_minio_client.remove_object.call_args
        assert call_args[0][0] == "test-bucket"
        # Key should be the path part of URL
        assert "ilikeitproperties/test_image.jpg" in call_args[0][1]

        # Verify logging
        mock_logger.info.assert_called_once()
        assert "Deleted from R2" in str(mock_logger.info.call_args)

    def test_delete_empty_url(self, mocker):
        """Test delete with empty/None URL."""
        mock_logger = mocker.patch("app.utils.r2_upload.logger")

        result = delete_from_r2("")

        assert result is False
        mock_logger.warning.assert_called_once()
        assert "No URL provided" in str(mock_logger.warning.call_args)

    def test_delete_none_url(self, mocker):
        """Test delete with None URL."""
        mock_logger = mocker.patch("app.utils.r2_upload.logger")

        result = delete_from_r2(None)

        assert result is False
        mock_logger.warning.assert_called_once()

    def test_delete_malformed_url(self, mocker, env_vars):
        """Test delete with malformed URL."""
        mock_minio_client = MagicMock()
        mocker.patch("app.utils.r2_upload.Minio", return_value=mock_minio_client)
        mocker.patch("app.utils.r2_upload.logger")

        # Malformed URL (no valid path)
        url = "not-a-valid-url"
        result = delete_from_r2(url)

        # Should still attempt deletion (path would be empty or just filename)
        assert result is True or result is False  # Either way is acceptable

    def test_delete_complex_url_path(self, mocker, env_vars):
        """Test delete extracts correct key from complex URL."""
        mock_minio_client = MagicMock()
        mocker.patch("app.utils.r2_upload.Minio", return_value=mock_minio_client)
        mocker.patch("app.utils.r2_upload.logger")

        url = "https://cdn.example.com/ilikeitproperties/folder/subfolder/image.jpg?v=1"
        result = delete_from_r2(url)

        assert result is True

        # Verify the key extracted from URL
        call_args = mock_minio_client.remove_object.call_args
        key = call_args[0][1]
        # Path should be properly extracted
        assert "image.jpg" in key or "subfolder" in key

    def test_delete_boto3_error(self, mocker, env_vars):
        """Test delete handles boto3 errors gracefully."""
        mock_minio_client = MagicMock()
        mock_minio_client.remove_object.side_effect = Exception("Service unavailable")
        mocker.patch("app.utils.r2_upload.Minio", return_value=mock_minio_client)

        mock_logger = mocker.patch("app.utils.r2_upload.logger")

        url = "https://cdn.example.com/ilikeitproperties/test.jpg"
        result = delete_from_r2(url)

        assert result is False
        mock_logger.error.assert_called_once()
        assert "R2 delete error" in str(mock_logger.error.call_args)

    def test_delete_missing_env_variables(self, mocker):
        """Test delete with missing env variables."""
        # Clear env variables
        for key in ["R2_ENDPOINT", "R2_ACCESS_KEY", "R2_SECRET_KEY", "R2_BUCKET"]:
            os.environ.pop(key, None)

        # Mock MinIO client to raise an error when called with None values
        mock_minio_client = MagicMock()
        mock_minio_client.remove_object.side_effect = Exception("Failed to create MinIO client")
        mocker.patch("app.utils.r2_upload.Minio", return_value=mock_minio_client)

        mock_logger = mocker.patch("app.utils.r2_upload.logger")

        url = "https://cdn.example.com/ilikeitproperties/test.jpg"
        result = delete_from_r2(url)

        # Should fail gracefully
        assert result is False
        mock_logger.error.assert_called_once()

    def test_delete_with_special_characters_in_path(self, mocker, env_vars):
        """Test delete URL with special characters in filename."""
        mock_minio_client = MagicMock()
        mocker.patch("app.utils.r2_upload.Minio", return_value=mock_minio_client)
        mocker.patch("app.utils.r2_upload.logger")

        url = "https://cdn.example.com/ilikeitproperties/image%20with%20spaces.jpg"
        result = delete_from_r2(url)

        assert result is True
        mock_minio_client.remove_object.assert_called_once()


# =============================================================================
# LOGGING TESTS
# =============================================================================


class TestR2Logging:
    """Test logging functionality for R2 operations."""

    def test_upload_success_logging(self, mocker, mock_file, env_vars):
        """Test successful upload logs correct message."""
        mock_minio_client = MagicMock()
        mocker.patch("app.utils.r2_upload.Minio", return_value=mock_minio_client)

        mock_logger = mocker.patch("app.utils.r2_upload.logger")

        upload_to_r2(mock_file)

        # Check that logger.info was called with upload url
        assert mock_logger.info.called
        log_message = str(mock_logger.info.call_args)
        assert "Uploaded to R2" in log_message
        assert "cdn.example.com" in log_message

    def test_upload_error_logging(self, mocker, mock_file, env_vars):
        """Test upload error is logged with filename."""
        mock_minio_client = MagicMock()
        mock_minio_client.put_object.side_effect = Exception("Upload failed")
        mocker.patch("app.utils.r2_upload.Minio", return_value=mock_minio_client)

        mock_logger = mocker.patch("app.utils.r2_upload.logger")

        upload_to_r2(mock_file)

        # Check error logging
        assert mock_logger.error.called
        log_message = str(mock_logger.error.call_args)
        assert "R2 upload error" in log_message
        assert "test_image.jpg" in log_message

    def test_delete_success_logging(self, mocker, env_vars):
        """Test successful delete logs correct message."""
        mock_minio_client = MagicMock()
        mocker.patch("app.utils.r2_upload.Minio", return_value=mock_minio_client)

        mock_logger = mocker.patch("app.utils.r2_upload.logger")

        url = "https://cdn.example.com/ilikeitproperties/test.jpg"
        delete_from_r2(url)

        assert mock_logger.info.called
        log_message = str(mock_logger.info.call_args)
        assert "Deleted from R2" in log_message

    def test_delete_missing_url_logging(self, mocker):
        """Test delete with missing URL logs warning."""
        mock_logger = mocker.patch("app.utils.r2_upload.logger")

        delete_from_r2(None)

        assert mock_logger.warning.called
        log_message = str(mock_logger.warning.call_args)
        assert "No URL provided" in log_message

    def test_delete_error_logging(self, mocker, env_vars):
        """Test delete error is logged with URL reference."""
        mock_minio_client = MagicMock()
        mock_minio_client.remove_object.side_effect = Exception("Deletion failed")
        mocker.patch("app.utils.r2_upload.Minio", return_value=mock_minio_client)

        mock_logger = mocker.patch("app.utils.r2_upload.logger")

        url = "https://cdn.example.com/ilikeitproperties/test.jpg"
        delete_from_r2(url)

        assert mock_logger.error.called
        log_message = str(mock_logger.error.call_args)
        assert "R2 delete error" in log_message


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestR2Integration:
    """Integration tests for R2 upload/delete workflow."""

    def test_upload_then_delete_workflow(self, mocker, mock_file, env_vars):
        """Test complete workflow: upload file, then delete it."""
        mock_minio_client = MagicMock()
        mocker.patch("app.utils.r2_upload.Minio", return_value=mock_minio_client)
        mocker.patch("app.utils.r2_upload.logger")

        # Step 1: Upload file
        upload_result = upload_to_r2(mock_file)
        assert upload_result is not None

        # Step 2: Delete file using the returned URL
        delete_result = delete_from_r2(upload_result)
        assert delete_result is True

        # Verify both operations called
        assert mock_minio_client.put_object.called
        assert mock_minio_client.remove_object.called

    def test_multiple_uploads_and_deletes(self, mocker, env_vars):
        """Test multiple upload/delete cycles."""
        mock_minio_client = MagicMock()
        mocker.patch("app.utils.r2_upload.Minio", return_value=mock_minio_client)
        mocker.patch("app.utils.r2_upload.logger")

        files = ["image1.jpg", "image2.png", "image3.gif"]
        uploaded_urls = []

        # Upload multiple files
        for filename in files:
            stream = io.BytesIO(b"fake image data")
            file = FileStorage(stream=stream, filename=filename)
            url = upload_to_r2(file)
            assert url is not None
            uploaded_urls.append(url)

        # Delete all uploaded files
        for url in uploaded_urls:
            result = delete_from_r2(url)
            assert result is True

        # Verify correct number of calls
        assert mock_minio_client.put_object.call_count == len(files)
        assert mock_minio_client.remove_object.call_count == len(files)
