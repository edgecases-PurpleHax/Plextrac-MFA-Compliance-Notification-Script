"""
Security tests for main.py module.
"""

import unittest
import os
import json
from unittest.mock import patch, MagicMock

import main


class TestMainSecurity(unittest.TestCase):
    """
    Unit tests for security aspects of main.py module.
    """

    def setUp(self):
        """
        Set up test environment.
        """
        # Create a mock configuration file
        self.mock_config = {
            'plextrac_username': 'test_username',
            'plextrac_password': 'test_password',
            'plextrac_url': 'http://test.plextrac.com',
            'gmail_username': 'test@gmail.com',
            'gmail_app_password': 'test_app_password',
            'customer_domains': ['example.com']
        }
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(self.mock_config, f)

    def tearDown(self):
        """
        Clean up after each test.
        """
        # Remove the mock configuration file
        os.remove('config.json')

    @patch('main.requests.post')
    @patch('main.requests.get')
    @patch('main.smtplib.SMTP')
    def test_input_validation(
            self, mock_smtp_class, mock_r_post
    ):
        """
        Test input validation and error handling.
        """
        # Test with malformed JSON in config.json
        with open('config.json', 'w', encoding='utf-8') as f:
            f.write("invalid_json")

        with self.assertRaises(json.JSONDecodeError):
            main.authenticate_and_send_email()

        # Test robust error handling for network errors
        mock_r_post.side_effect = main.requests.exceptions.RequestException(
            "Network error")
        with self.assertRaises(main.requests.exceptions.RequestException):
            main.authenticate_and_send_email()

        # Test robust error handling for SMTP errors
        mock_smtp_instance = mock_smtp_class.return_value
        mock_smtp_instance.starttls.side_effect = main.smtplib.SMTPException(
            "SMTP error"
        )
        with self.assertRaises(main.smtplib.SMTPException):
            main.authenticate_and_send_email()

    @patch('main.requests.post')
    @patch('main.requests.get')
    @patch('main.smtplib.SMTP')
    def test_secure_communication(
            self, mock_smtp_class, mock_requests_get, mock_requests_post
    ):
        """
        Test secure communication practices.
        """
        # Mock responses for requests.post and requests.get
        mock_token = 'mock_token'
        mock_response_post = MagicMock()
        mock_response_post.json.return_value = {'token': mock_token}
        mock_requests_post.return_value = mock_response_post

        mock_user_data = {
            'data': [{'email': 'test@example.com', 'mfa': {'enabled': False}}]
        }
        mock_response_get = MagicMock()
        mock_response_get.json.return_value = mock_user_data
        mock_requests_get.return_value = mock_response_get

        # Mock SMTP server
        mock_smtp_instance = mock_smtp_class.return_value

        # Call function under test
        main.authenticate_and_send_email()

        # Assertions for secure communication
        mock_requests_post.assert_called_once()
        mock_requests_get.assert_called_once()
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once()


if __name__ == '__main__':
    unittest.main()
