"""
This module authenticates with Plextrac API, searches for specific emails,
and sends an email notification.
"""

import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests


def load_config(config_path='config.json'):
    """Load configuration from a JSON file."""
    with open(config_path, encoding='utf-8') as config_file:
        return json.load(config_file)


def authenticate(config):
    """Authenticate with Plextrac API and return the authorization headers."""
    data = {
        "username": config['plextrac_username'],
        "password": config['plextrac_password']
    }
    response = requests.post(
        url=f"{config['plextrac_url']}/api/v1/authenticate",
        json=data
    )
    response.raise_for_status()
    return {
        "Authorization": f"Bearer {response.json()['token']}"
    }


def search_emails_in_data(json_obj, search_terms):
    """Search for specific emails in JSON data."""
    matches = []

    if isinstance(json_obj, dict) and 'data' in json_obj and isinstance(json_obj['data'], list):
        for item in json_obj['data']:
            if isinstance(item, dict) and 'email' in item:
                email = item['email']
                if any(term in email for term in search_terms):
                    matches.append(item)
    return matches


def get_users(config, headers):
    """Retrieve users from Plextrac API."""
    user_endpoint = requests.get(
        url=f"{config['plextrac_url']}/api/v2/tenants/{headers['Authorization'].split(' ')[1]}/users",
        params={'limit': 100},
        headers=headers
    )
    user_endpoint.raise_for_status()
    return user_endpoint.json()


def send_email(config, users):
    """Send an email listing non-compliant users."""
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    sender_email = config['gmail_username']
    sender_password = config['gmail_app_password']

    recipient_email = "user@example.com"

    subject = "MFA Non-compliant Users"

    body = (
        f"The following users are not compliant with the {config['customer']} requirement for MFA "
        "enabled on the Plextrac Platform:\n\n"
    )
    for user in users:
        if not user['mfa']['enabled']:
            body += f"Name: {user['fullName']}\nEmail: {user['email']}\n\n"

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject

    message.attach(MIMEText(body, 'plain'))

    try:
        smtp = smtplib.SMTP(smtp_server, smtp_port)
        smtp.starttls()
        smtp.login(sender_email, sender_password)
        smtp.sendmail(sender_email, recipient_email, message.as_string())
        print(f"Email sent successfully to {recipient_email}")
    except (requests.exceptions.RequestException, smtplib.SMTPException) as e:
        print(f"Error sending email: {e}")
    finally:
        smtp.quit()


def authenticate_and_send_email():
    """
    Authenticate with Plextrac API, search for specific emails, and send an email notification.

    Reads configuration from 'config.json' for Plextrac API credentials and Gmail SMTP details.
    Searches for users based on specific email criteria (customer domains).
    Sends an email listing non-compliant users to a specified recipient using Gmail SMTP.

    Raises:
        requests.exceptions.RequestException: If an error occurs during API requests.
        smtplib.SMTPException: If an error occurs during SMTP operations.

    Notes:
        - Ensure 'config.json' contains 'plextrac_username', 'plextrac_password', 'plextrac_url',
          'gmail_username', 'gmail_app_password', and 'customer_domains' fields.
        - Use TLS (port 587) for SMTP as SSL (port 465) is deprecated.
    """
    config = load_config()
    headers = authenticate(config)
    users = get_users(config, headers)
    customer_users = search_emails_in_data(users, config['customer_domains'])
    send_email(config, customer_users)


if __name__ == "__main__":
    authenticate_and_send_email()
