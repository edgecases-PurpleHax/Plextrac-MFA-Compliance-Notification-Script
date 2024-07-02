"""
Unit tests for main.py functionality.

These tests validate the behavior of functions in main.py, specifically
focusing on: - Authentication with Plextrac API - Retrieval and processing
of user data - Sending email notifications using Gmail SMTP

The tests utilize unittest framework and mock objects to simulate
interactions with external services such as API endpoints and SMTP server,
ensuring robustness and reliability of the implemented functions.

Test Cases: - test_authenticate_and_send_email: Validates the entire
workflow of authentication, data retrieval, and email sending functionality.

Note: This module assumes that main.py is the module to be tested and
requires 'config.json' for configuration data mocking during tests."""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import json  # Make sure json is imported
import main  # Assuming main.py is the module to be tested


class TestMain(unittest.TestCase):
    """
    Unit tests for main.py functionality.
    """

    @patch('main.requests.post')
    @patch('main.requests.get')
    @patch('main.smtplib.SMTP')
    @patch('builtins.open', new_callable=mock_open)
    def test_authenticate_and_send_email(self, mock_open_file, mock_smtp_class,
                                         mock_requests_get,
                                         mock_requests_post):
        """
        Test case for authenticate_and_send_email function.
        """
        # Mock configuration
        mock_config = {
            'plextrac_username': 'test_username',
            'plextrac_password': 'test_password',
            'plextrac_url': 'http://test.plextrac.com',
            'gmail_username': 'test@gmail.com',
            'gmail_app_password': 'test_app_password',
            'customer_domains': ['example.com']
        }

        # Mock return values for requests.post
        mock_token = 'mock_token'
        mock_response_post = MagicMock()
        mock_response_post.json.return_value = {'token': mock_token}
        mock_requests_post.return_value = mock_response_post

        # Mock return values for requests.get
        mock_user_data = {'data': [{'email': 'test@example.com'}]}
        mock_response_get = MagicMock()
        mock_response_get.json.return_value = mock_user_data
        mock_requests_get.return_value = mock_response_get

        # Mock open method to simulate reading config.json
        mock_open_file.return_value.read.return_value = json.dumps(mock_config)

        # Mock SMTP server
        mock_smtp_instance = mock_smtp_class.return_value

        # Call function under test
        main.authenticate_and_send_email()

        # Assertions
        mock_requests_post.assert_called_once_with(
            url=f"{mock_config['plextrac_url']}/api/v1/authenticate",
            json={'username': mock_config['plextrac_username'],
                  'password': mock_config['plextrac_password']},
            timeout=10)
        mock_requests_get.assert_called_once_with(
            url=f"{mock_config['plextrac_url']}/api/v2/tenants/"
                f"{mock_token}/users",
            params={'limit': 100},
            headers={'Authorization': f"Bearer {mock_token}"},
            timeout=10)
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with(
            mock_config['gmail_username'],
            mock_config['gmail_app_password'])
        mock_smtp_instance.sendmail.assert_called_once()


if __name__ == '__main__':
    unittest.main()
