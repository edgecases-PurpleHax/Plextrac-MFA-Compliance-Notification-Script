"""
This module authenticates with the Plextrac API, searches for specific emails,
and sends an email notification using Gmail SMTP.
"""

import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests


def authenticate_and_send_email():
    """
    Authenticate with Plextrac API, search for specific emails, and send an email notification.

    Reads configuration from 'config.json' for Plextrac API credentials and Gmail SMTP details.
    Searches for users based on specific email criteria specified in 'customer_domains' key in
    config. Sends an email listing non-compliant users to a specified recipient using Gmail SMTP.

    Raises:
        requests.exceptions.RequestException: If an error occurs during API requests.
        smtplib.SMTPException: If an error occurs during SMTP operations.

    Notes:
        - Ensure 'config.json' contains 'plextrac_username', 'plextrac_password', 'plextrac_url',
          'gmail_username', 'gmail_app_password', and 'customer_domains' fields.
        - Use TLS (port 587) for SMTP as SSL (port 465) is deprecated.
        - Specify customer email domains in 'customer_domains' key in config.json.
    """
    # Load configuration from config.json
    with open('config.json', encoding='utf-8') as config_file:
        config = json.load(config_file)

    # Authenticate with Plextrac API
    response = requests.post(
        url=f"{config['plextrac_url']}/api/v1/authenticate",
        json={
            "username": config['plextrac_username'],
            "password": config['plextrac_password']
        },
        timeout=10  # Add timeout
    )
    response.raise_for_status()  # Raise exception for bad response status

    # Set authorization headers for subsequent requests
    headers = {
        "Authorization": f"Bearer {response.json()['token']}"
    }

    def search_emails_in_data(json_obj):
        """
        Helper function to search for specific emails in JSON data.
        """
        search_terms = config['customer_domains']  # Read domains from config
        matches = []

        if isinstance(json_obj, dict) and 'data' in json_obj \
                and isinstance(json_obj['data'], list):
            for item in json_obj['data']:
                if isinstance(item, dict) and 'email' in item:
                    email = item['email']
                    if any(term in email for term in search_terms):
                        matches.append(item)
        return matches

    # Retrieve users from Plextrac API based on authenticated session
    user_endpoint = requests.get(
        url=f"{config['plextrac_url']}/api/v2/tenants/{response.json()['tenant_id']}/users",
        params={'limit': 100},
        headers=headers,
        timeout=10  # Add timeout
    )
    user_endpoint.raise_for_status()  # Raise exception for bad response status
    user_data = user_endpoint.json()

    # Search for users matching specified criteria
    customer_users = search_emails_in_data(user_data)

    # Prepare the email body with user information
    body = (
        f"The following users are not compliant with the {config['customer']} "
        f"requirement for MFA enabled on the Plextrac Platform:\n\n"
    )
    for user in customer_users:
        if not user['mfa']['enabled']:
            body += f"Name: {user['fullName']}\nEmail: {user['email']}\n\n"

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message['From'] = config['gmail_username']
    message['To'] = "user@example.com"  # Replace with the recipient's email address
    message['Subject'] = "MFA Non-compliant Users"

    # Add body to email
    message.attach(MIMEText(body, 'plain'))

    try:
        # Establish a SMTP connection to Gmail's server
        smtp = smtplib.SMTP('smtp.gmail.com', 587)

        # Start TLS encryption
        smtp.starttls()

        # Login to Gmail SMTP server
        smtp.login(config['gmail_username'], config['gmail_app_password'])

        # Send email
        smtp.sendmail(config['gmail_username'], "user@example.com", message.as_string())
        print(f"Email sent successfully to {config['poc_email']}")

    except (requests.exceptions.RequestException, smtplib.SMTPException) as e:
        print(f"Error sending email: {e}")

    finally:
        # Close the SMTP connection
        smtp.quit()


if __name__ == "__main__":
    authenticate_and_send_email()
