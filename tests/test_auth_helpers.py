"""
Unit tests for Firebase authentication helpers and error translation in app.py
All tests use mocking to ensure zero live network calls or credential modifications.
"""

from unittest.mock import patch, MagicMock
import urllib.error
import json
from app import translate_firebase_error, firebase_auth_sign_in, firebase_auth_sign_up

def test_translate_firebase_error_known_codes():
    """Verify friendly error messages are returned for Firebase authentication error codes."""
    assert "Incorrect email" in translate_firebase_error("INVALID_LOGIN_CREDENTIALS")
    assert "Incorrect email" in translate_firebase_error("INVALID_PASSWORD")
    assert "No account" in translate_firebase_error("EMAIL_NOT_FOUND")
    assert "already exists" in translate_firebase_error("EMAIL_EXISTS")
    assert "6 characters" in translate_firebase_error("WEAK_PASSWORD")
    assert "valid email" in translate_firebase_error("INVALID_EMAIL")
    assert "Too many failed attempts" in translate_firebase_error("TOO_MANY_ATTEMPTS_TRY_LATER")
    assert "disabled" in translate_firebase_error("USER_DISABLED")
    assert "not enabled" in translate_firebase_error("OPERATION_NOT_ALLOWED")
    assert "UNKNOWN_ERROR" in translate_firebase_error("UNKNOWN_ERROR")

@patch("urllib.request.urlopen")
def test_mock_firebase_auth_sign_in_success(mock_urlopen):
    """Test successful sign-in returns True and user payload."""
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "idToken": "fake-jwt-token-12345",
        "email": "advisor@school.edu",
        "localId": "firebase-uid-999"
    }).encode("utf-8")
    mock_response.__enter__.return_value = mock_response
    mock_urlopen.return_value = mock_response

    success, data = firebase_auth_sign_in("advisor@school.edu", "validpass123")
    assert success is True
    assert data["email"] == "advisor@school.edu"
    assert data["localId"] == "firebase-uid-999"

@patch("urllib.request.urlopen")
def test_mock_firebase_auth_sign_in_failure(mock_urlopen):
    """Test failed sign-in handles HTTPError cleanly and returns False with error code."""
    err_body = json.dumps({
        "error": {
            "code": 400,
            "message": "INVALID_LOGIN_CREDENTIALS"
        }
    }).encode("utf-8")
    mock_error = urllib.error.HTTPError("url", 400, "Bad Request", {}, MagicMock())
    mock_error.read = MagicMock(return_value=err_body)
    mock_urlopen.side_effect = mock_error

    success, err = firebase_auth_sign_in("advisor@school.edu", "wrongpass")
    assert success is False
    assert err == "INVALID_LOGIN_CREDENTIALS"

@patch("urllib.request.urlopen")
def test_mock_firebase_auth_sign_up_success(mock_urlopen):
    """Test successful sign-up returns True and user payload."""
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "idToken": "fake-jwt-token-signup",
        "email": "newadvisor@school.edu",
        "localId": "firebase-uid-new"
    }).encode("utf-8")
    mock_response.__enter__.return_value = mock_response
    mock_urlopen.return_value = mock_response

    success, data = firebase_auth_sign_up("newadvisor@school.edu", "securepass123", display_name="New Advisor")
    assert success is True
    assert data["email"] == "newadvisor@school.edu"
